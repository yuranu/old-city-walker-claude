// Material registry keyed by material name. Every GLB of the sectored city references materials
// by name only (placeholders without maps); the real definitions come from the palette
// (base/materials.glb), are run once through materials.js, and every mesh of every chunk uses
// the registry's instance, so each texture atlas is decoded and uploaded once.
// A name missing from the palette falls back to the first GLB's own definition (with a warning)
// and is reference counted: it is disposed with its textures when no resident chunk uses it.
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { setupMaterial, setupFlat, makePalette } from './materials.js';

const TEX_SLOTS = ['map', 'normalMap', 'roughnessMap', 'metalnessMap', 'aoMap', 'emissiveMap', 'alphaMap', 'bumpMap',
  'lightMap', 'displacementMap', 'clearcoatMap', 'clearcoatNormalMap', 'clearcoatRoughnessMap', 'sheenColorMap',
  'sheenRoughnessMap', 'specularIntensityMap', 'specularColorMap', 'transmissionMap', 'thicknessMap',
  'iridescenceMap', 'iridescenceThicknessMap', 'anisotropyMap'];

export function materialTextures(m) {
  const out = [];
  for (const k of TEX_SLOTS) if (m[k] && m[k].isTexture) out.push(m[k]);
  return out;
}

export class Library {
  constructor(pipe, anisotropy) {
    this.pipe = pipe;
    this.anisotropy = anisotropy;
    this.entries = new Map();      // name -> { name, mat, depth, flags, refs, pinned, source, ready, compiled }
    this.texRefs = new Map();      // Texture -> number of registry materials using it
    this.uploads = [];             // textures not yet on the GPU (uploaded by the streamer's pump)
    this.loader = new GLTFLoader();
    this.flatTable = null;         // flat palette material name -> [palette index, merged material name]
    this.bakeTable = null;         // textured name -> [palette index, merged material name, 32x32 linear rgb]
    this.twins = true;             // depth-only twins for cut-outs (early-z for stacked cards)
  }

  // Merge the untextured palette materials into two draw materials ('__flat' without and
  // '__flat_env' with the sky reflection), indexed per vertex (see materials.js setupFlat). Call
  // once the palette is registered; the loader worker remaps those names with flatTable.
  //
  // Textured palette materials get a palette slot too, plus a 32x32 downsample of their base
  // colour map (bakeTable): far LOD geometry can then draw flat too, with each triangle's
  // texture colour baked into its vertex colours by the worker.
  buildFlat() {
    const flat = [], textured = [];
    for (const e of this.entries.values()) {
      const m = e.mat;
      if (!e.pinned || !m || !m.isMeshStandardMaterial || e.flags.cutout || !e.flags.castShadow || !e.flags.ao) continue;
      if (m.transparent || m.alphaTest > 0 || e.name.startsWith('__')) continue;
      if (materialTextures(m).length) { if (m.map && m.map.image) textured.push(e); } else flat.push(e);
    }
    if (!flat.length) return null;
    const all = flat.concat(textured).slice(0, 255);
    makePalette(all);
    this.flatTable = {};
    for (const [name, env] of [['__flat', false], ['__flat_env', true]]) {
      const m = new THREE.MeshStandardMaterial({ name, color: 0xffffff, roughness: 1, metalness: 0 });
      const e = { name, mat: m, depth: null, flags: setupFlat(m), refs: 0, pinned: true, source: 'flat', compiled: false };
      if (env) this.pipe.addReflective(m);
      e.ready = Promise.resolve(e);
      this.entries.set(name, e);
    }
    flat.forEach((e, i) => { this.flatTable[e.name] = [i, e.mat.envMap ? '__flat_env' : '__flat']; });
    this.bakeTable = {};
    textured.forEach((e, k) => {
      const i = flat.length + k;
      if (i > 254) return;
      const img = e.mat.map.image, N = 32;
      try {
        const cv = new OffscreenCanvas(N, N), g = cv.getContext('2d');
        g.drawImage(img, 0, 0, N, N);
        const d = g.getImageData(0, 0, N, N).data;
        // sRGB bytes -> linear floats (vertex colours are linear)
        const lin = new Float32Array(N * N * 3);
        for (let p = 0; p < N * N; p++) for (let c = 0; c < 3; c++) {
          const v = d[p * 4 + c] / 255;
          lin[p * 3 + c] = v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
        }
        this.bakeTable[e.name] = [i, e.mat.envMap ? '__flat_env' : '__flat', { w: N, h: N, rgb: lin }];
      } catch (err) {
        console.warn('bake: cannot read texture of', e.name, err);
      }
    });
    return this.flatTable;
  }

  has(name) { return this.entries.has(name); }
  get(name) { return this.entries.get(name); }
  names() { return [...this.entries.keys()]; }

  // register the materials of a GLB (the palette, or a worker's material-only extract).
  // names: which to take (null = all); first definition of a name wins.
  async addGLB(buf, path, names = null, { pinned = false, source = '' } = {}) {
    const gltf = await this.loader.parseAsync(buf, path);
    const defs = gltf.parser.json.materials || [];
    const waits = [];
    defs.forEach((d, i) => {
      const name = d.name || `__mat${i}`;
      if ((names && !names.includes(name))) return;
      const have = this.entries.get(name);
      if (have) { waits.push(have.ready); return; }
      const e = { name, mat: null, depth: null, flags: null, refs: 0, pinned, source, compiled: false };
      e.ready = gltf.parser.getDependency('material', i).then((m) => this._finish(e, m));
      this.entries.set(name, e);
      waits.push(e.ready);
    });
    await Promise.all(waits);
    // the palette GLB's own meshes (tiny quads far below the city) are never used
    gltf.scene?.traverse((o) => { if (o.isMesh) o.geometry.dispose(); });
    return gltf;
  }

  // a name nobody defines: glTF's default material
  addDefault(name) {
    if (this.entries.has(name)) return this.entries.get(name);
    const m = new THREE.MeshStandardMaterial({ color: 0xffffff, metalness: 1, roughness: 1 });
    const e = { name, mat: null, depth: null, flags: null, refs: 0, pinned: false, source: 'default', compiled: false };
    this._finish(e, m);
    e.ready = Promise.resolve(e);
    this.entries.set(name, e);
    return e;
  }

  _finish(e, m) {
    m.name = e.name;
    // as GLTFLoader's assignFinalMaterial does for meshes without tangents (ours never have
    // any after merging): vertex colours on, derivative tangents need the flipped green
    m.vertexColors = true;
    if (m.normalScale) m.normalScale.y *= -1;
    e.flags = setupMaterial(m, this.anisotropy);
    if (e.flags.cutout && this.twins) {
      // depth-only twin drawn first (alpha tested, pushed back a hair), so the shaded pass only
      // shades the front-most layer of stacked foliage cards / grilles; no depth writes in the
      // shaded pass (a shader with discard + depth writes loses early-z)
      e.depth = new THREE.MeshBasicMaterial({
        name: m.name + '-z', map: m.map, alphaTest: m.alphaTest || 0.5, side: m.side,
        colorWrite: false, polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 1,
      });
      m.depthWrite = false;
    }
    if (m.isMeshStandardMaterial && (m.metalness >= 0.3 || m.roughness < 0.35)) this.pipe.addReflective(m);
    for (const t of materialTextures(m)) {
      const n = this.texRefs.get(t) || 0;
      this.texRefs.set(t, n + 1);
      if (!n) this.uploads.push(t);
    }
    e.mat = m;
    return e;
  }

  acquire(names) { for (const n of names) { const e = this.entries.get(n); if (e) e.refs++; } }

  release(names) {
    for (const n of names) {
      const e = this.entries.get(n);
      if (!e) continue;
      e.refs--;
      if (e.refs <= 0 && !e.pinned) this._dispose(e);
    }
  }

  _dispose(e) {
    this.entries.delete(e.name);
    const m = e.mat;
    this.pipe.removeReflective(m);
    for (const t of materialTextures(m)) {
      const n = (this.texRefs.get(t) || 1) - 1;
      if (n > 0) { this.texRefs.set(t, n); continue; }
      this.texRefs.delete(t);
      const i = this.uploads.indexOf(t);
      if (i >= 0) this.uploads.splice(i, 1);
      t.dispose();
      if (t.image && typeof t.image.close === 'function') t.image.close();
    }
    m.dispose();
    if (e.depth) e.depth.dispose();
  }

  stats() {
    let texBytes = 0;
    for (const t of this.texRefs.keys()) {
      const w = t.image?.width || 0, h = t.image?.height || 0;
      texBytes += w * h * 4 * (t.generateMipmaps !== false ? 4 / 3 : 1);
    }
    let pinned = 0;
    for (const e of this.entries.values()) if (e.pinned) pinned++;
    return { materials: this.entries.size, pinned, textures: this.texRefs.size, texMB: texBytes / 1048576 };
  }
}
