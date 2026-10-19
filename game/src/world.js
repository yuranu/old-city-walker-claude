// GLB -> renderable city + collision BVH + ground height texture.
//  - static geometry is merged per (material name, nocol); large groups are split into spatial
//    chunks so frustum culling (view, AO prepass, near shadow cascade) can skip them
//  - every merged geometry has position/normal/uv/color; a missing COLOR_0 becomes white so the
//    old and the new GLB both work (the vertex colour multiplies the base colour)
//  - meshes under a node with extras {"nocol": 1} stay out of the collision BVH
import * as THREE from 'three';
import { MeshBVH } from 'three-mesh-bvh';
import { setupMaterial, U } from './materials.js';

export const LAYER_NO_AO = 1;     // meshes that are not drawn into the AO depth/normal prepass
// opaque draw order: city, then the sky dome (only where nothing was drawn), then the cut-out
// depth twins, then the cut-outs themselves (alpha-to-coverage edges then blend over the sky)
export const RENDER_ORDER = { sky: 1, cutoutDepth: 2, cutout: 3 };
let CHUNK = 96;                   // metres
let CHUNK_MIN_TRIS = 16000;       // only split groups bigger than this

const depthMats = new Map();
function depthOnly(m) {
  if (!depthMats.has(m)) {
    depthMats.set(m, new THREE.MeshBasicMaterial({
      name: m.name + '-z', map: m.map, alphaTest: m.alphaTest || 0.5, side: m.side,
      colorWrite: false, polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 1,
    }));
  }
  return depthMats.get(m);
}

function isNoCol(o) {
  for (let p = o; p; p = p.parent) if (p.userData && p.userData.nocol) return true;
  return false;
}

// copy any (possibly normalised / interleaved) attribute into a float array; missing -> fill
function readAttr(attr, n, size, out, offset, fill) {
  if (!attr) {
    for (let i = 0; i < n * size; i++) out[offset + i] = fill;
    return;
  }
  if (!attr.isInterleavedBufferAttribute && !attr.normalized && attr.itemSize === size &&
      attr.array instanceof Float32Array) {
    out.set(attr.array.subarray(0, n * size), offset);
    return;
  }
  const get = [attr.getX, attr.getY, attr.getZ, attr.getW];
  const k = Math.min(size, attr.itemSize);
  for (let i = 0; i < n; i++) {
    for (let c = 0; c < k; c++) out[offset + i * size + c] = get[c].call(attr, i);
    for (let c = k; c < size; c++) out[offset + i * size + c] = fill;
  }
}

function mergeParts(parts, posOnly = false) {
  let nv = 0, ni = 0;
  for (const { g } of parts) {
    const n = g.attributes.position.count;
    nv += n;
    ni += g.index ? g.index.count : n;
  }
  const pos = new Float32Array(nv * 3);
  const nrm = posOnly ? null : new Float32Array(nv * 3);
  const uv = posOnly ? null : new Float32Array(nv * 2);
  const col = posOnly ? null : new Float32Array(nv * 3);
  const idx = new Uint32Array(ni);
  const nm = new THREE.Matrix3();
  let vo = 0, io = 0;
  for (const { g: g0, m } of parts) {
    let g = g0;
    if (!posOnly && !g.attributes.normal) { g = g0.clone(); g.computeVertexNormals(); }
    const n = g.attributes.position.count;
    readAttr(g.attributes.position, n, 3, pos, vo * 3, 0);
    const e = m.elements;
    for (let i = vo * 3; i < (vo + n) * 3; i += 3) {
      const x = pos[i], y = pos[i + 1], z = pos[i + 2];
      pos[i] = e[0] * x + e[4] * y + e[8] * z + e[12];
      pos[i + 1] = e[1] * x + e[5] * y + e[9] * z + e[13];
      pos[i + 2] = e[2] * x + e[6] * y + e[10] * z + e[14];
    }
    if (!posOnly) {
      readAttr(g.attributes.normal, n, 3, nrm, vo * 3, 0);
      readAttr(g.attributes.uv, n, 2, uv, vo * 2, 0);
      readAttr(g.attributes.color, n, 3, col, vo * 3, 1);
      const k = nm.getNormalMatrix(m).elements;
      for (let i = vo * 3; i < (vo + n) * 3; i += 3) {
        const x = nrm[i], y = nrm[i + 1], z = nrm[i + 2];
        const nx = k[0] * x + k[3] * y + k[6] * z, ny = k[1] * x + k[4] * y + k[7] * z, nz = k[2] * x + k[5] * y + k[8] * z;
        const l = Math.hypot(nx, ny, nz) || 1;
        nrm[i] = nx / l; nrm[i + 1] = ny / l; nrm[i + 2] = nz / l;
      }
    }
    const flip = m.determinant() < 0;
    const ia = g.index ? g.index.array : null;
    const cnt = ia ? g.index.count : n;
    for (let i = 0; i < cnt; i += 3) {
      const a = ia ? ia[i] : i, b = ia ? ia[i + 1] : i + 1, c = ia ? ia[i + 2] : i + 2;
      idx[io + i] = vo + a;
      idx[io + i + 1] = vo + (flip ? c : b);
      idx[io + i + 2] = vo + (flip ? b : c);
    }
    vo += n; io += cnt;
  }
  return { pos, nrm, uv, col, idx };
}

function toGeometry({ pos, nrm, uv, col, idx }) {
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  g.setAttribute('normal', new THREE.BufferAttribute(nrm, 3));
  g.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
  g.setAttribute('color', new THREE.BufferAttribute(col, 3));
  g.setIndex(new THREE.BufferAttribute(idx, 1));
  g.computeBoundingBox();
  g.computeBoundingSphere();
  return g;
}

// split merged arrays into CHUNK x CHUNK cells by triangle centroid
function splitChunks(data) {
  const { pos, idx } = data;
  const nt = idx.length / 3;
  if (nt < CHUNK_MIN_TRIS) return [data];
  const cells = new Map();
  for (let t = 0; t < nt; t++) {
    const a = idx[t * 3] * 3, b = idx[t * 3 + 1] * 3, c = idx[t * 3 + 2] * 3;
    const cx = Math.floor((pos[a] + pos[b] + pos[c]) / 3 / CHUNK);
    const cz = Math.floor((pos[a + 2] + pos[b + 2] + pos[c + 2]) / 3 / CHUNK);
    const key = cx * 4096 + cz;
    let list = cells.get(key);
    if (!list) cells.set(key, (list = []));
    list.push(t);
  }
  if (cells.size < 2) return [data];
  const remap = new Int32Array(pos.length / 3).fill(-1);
  const out = [];
  for (const tris of cells.values()) {
    const used = [];
    const nidx = new Uint32Array(tris.length * 3);
    tris.forEach((t, k) => {
      for (let j = 0; j < 3; j++) {
        const vi = idx[t * 3 + j];
        if (remap[vi] < 0) { remap[vi] = used.length; used.push(vi); }
        nidx[k * 3 + j] = remap[vi];
      }
    });
    const n = used.length;
    const sub = { pos: new Float32Array(n * 3), nrm: new Float32Array(n * 3), uv: new Float32Array(n * 2), col: new Float32Array(n * 3), idx: nidx };
    used.forEach((vi, k) => {
      for (let c = 0; c < 3; c++) {
        sub.pos[k * 3 + c] = data.pos[vi * 3 + c];
        sub.nrm[k * 3 + c] = data.nrm[vi * 3 + c];
        sub.col[k * 3 + c] = data.col[vi * 3 + c];
      }
      sub.uv[k * 2] = data.uv[vi * 2];
      sub.uv[k * 2 + 1] = data.uv[vi * 2 + 1];
      remap[vi] = -1;
    });
    out.push(sub);
  }
  return out;
}

export function buildWorld(gltf, { anisotropy = 8, chunk = CHUNK, chunkMinTris = CHUNK_MIN_TRIS } = {}) {
  CHUNK = chunk;
  CHUNK_MIN_TRIS = chunkMinTris;
  const root = gltf.scene;
  root.updateMatrixWorld(true);
  const mats = new Map();          // name -> representative material
  const groups = new Map();        // name|nocol -> parts
  const collideParts = [];
  root.traverse((o) => {
    if (!o.isMesh || !o.geometry?.attributes.position) return;
    const m = Array.isArray(o.material) ? o.material[0] : o.material;
    const name = m.name || m.uuid;
    if (!mats.has(name)) mats.set(name, m);
    const nocol = isNoCol(o);
    const key = name + (nocol ? '|nocol' : '');
    if (!groups.has(key)) groups.set(key, { name, nocol, parts: [] });
    // EXT_mesh_gpu_instancing comes in as an InstancedMesh: bake every instance
    const xforms = [];
    if (o.isInstancedMesh) {
      const im = new THREE.Matrix4();
      for (let i = 0; i < o.count; i++) { o.getMatrixAt(i, im); xforms.push(o.matrixWorld.clone().multiply(im)); }
    } else xforms.push(o.matrixWorld);
    for (const mw of xforms) {
      groups.get(key).parts.push({ g: o.geometry, m: mw });
      if (!nocol) collideParts.push({ g: o.geometry, m: mw });
    }
  });

  const flags = new Map();
  for (const [name, m] of mats) {
    m.vertexColors = true;
    flags.set(name, setupMaterial(m, anisotropy));
  }

  const city = new THREE.Group();
  city.name = 'city';
  const stats = { groups: 0, meshes: 0, tris: 0, byMaterial: {} };
  for (const { name, nocol, parts } of groups.values()) {
    const m = mats.get(name);
    const f = flags.get(name);
    const merged = mergeParts(parts);
    const pieces = splitChunks(merged);
    for (const p of pieces) {
      const geom = toGeometry(p);
      const mesh = new THREE.Mesh(geom, m);
      mesh.name = name + (nocol ? ' (nocol)' : '');
      mesh.castShadow = f.castShadow;
      mesh.receiveShadow = true;
      mesh.matrixAutoUpdate = false;
      if (!f.ao || nocol) mesh.layers.set(LAYER_NO_AO);
      city.add(mesh);
      if (f.cutout) {
        // depth-only twin drawn first (alpha tested, pushed back a hair), so the shaded pass
        // only shades the front-most layer of stacked foliage cards / grilles
        const twin = new THREE.Mesh(geom, depthOnly(m));
        twin.name = mesh.name + ' (z)';
        twin.matrixAutoUpdate = false;
        twin.layers.set(LAYER_NO_AO);
        twin.renderOrder = RENDER_ORDER.cutoutDepth;
        mesh.renderOrder = RENDER_ORDER.cutout;
        // no depth writes in the shaded pass: a shader with discard + depth writes loses early-z
        m.depthWrite = false;
        city.add(twin);
      }
    }
    const nt = merged.idx.length / 3;
    stats.groups++;
    stats.meshes += pieces.length;
    stats.tris += nt;
    stats.byMaterial[mesh_key(name, nocol)] = { tris: nt, chunks: pieces.length };
  }
  city.updateMatrixWorld(true);

  // collision: positions only
  let collideGeom;
  if (collideParts.length) {
    const c = mergeParts(collideParts, true);
    collideGeom = new THREE.BufferGeometry();
    collideGeom.setAttribute('position', new THREE.BufferAttribute(c.pos, 3));
    collideGeom.setIndex(new THREE.BufferAttribute(c.idx, 1));
  } else {
    collideGeom = new THREE.BufferGeometry();
    collideGeom.setAttribute('position', new THREE.BufferAttribute(new Float32Array(9), 3));
  }
  const bvh = new MeshBVH(collideGeom);
  const bounds = new THREE.Box3().setFromObject(city);
  return { city, bvh, bounds, stats };
}

function mesh_key(name, nocol) { return name + (nocol ? '|nocol' : ''); }

// Ground height field: raycast the collision BVH straight down on a `cell` grid, keep the lowest
// upward-facing hit (so roofs, arches and awnings above the street are skipped) as long as it is
// below +3 m; columns that only hit roofs (no ground under buildings) are filled from their
// neighbours. Returns a HalfFloat R texture and a CPU sampler.
export function buildGround(bvh, bounds, cell = 1) {
  const t0 = performance.now();
  const minX = Math.floor(bounds.min.x) - 2, minZ = Math.floor(bounds.min.z) - 2;
  const W = Math.min(2048, Math.ceil((bounds.max.x + 2 - minX) / cell));
  const H = Math.min(2048, Math.ceil((bounds.max.z + 2 - minZ) / cell));
  const h = new Float32Array(W * H);
  const ok = new Uint8Array(W * H);
  const ray = new THREE.Ray(new THREE.Vector3(), new THREE.Vector3(0, -1, 0));
  const top = bounds.max.y + 1;
  for (let j = 0; j < H; j++) {
    for (let i = 0; i < W; i++) {
      ray.origin.set(minX + (i + 0.5) * cell, top, minZ + (j + 0.5) * cell);
      const hits = bvh.raycast(ray, THREE.DoubleSide);
      let best = Infinity;
      for (const hit of hits) if (hit.face.normal.y > 0.5 && hit.point.y < best) best = hit.point.y;
      if (best < 3) { h[j * W + i] = best; ok[j * W + i] = 1; }
    }
  }
  const tRay = performance.now() - t0;
  // fill holes (inside buildings, outside the model) from valid neighbours, ring by ring
  let todo = ok.length - ok.reduce((a, b) => a + b, 0);
  const next = new Uint8Array(ok);
  for (let pass = 0; pass < 400 && todo > 0; pass++) {
    let changed = 0;
    for (let j = 0; j < H; j++) {
      for (let i = 0; i < W; i++) {
        const k = j * W + i;
        if (ok[k]) continue;
        let s = 0, n = 0;
        for (let dj = -1; dj <= 1; dj++) for (let di = -1; di <= 1; di++) {
          const ii = i + di, jj = j + dj;
          if (ii < 0 || jj < 0 || ii >= W || jj >= H) continue;
          const kk = jj * W + ii;
          if (ok[kk]) { s += h[kk]; n++; }
        }
        if (n) { h[k] = s / n; next[k] = 1; changed++; }
      }
    }
    ok.set(next);
    todo -= changed;
    if (!changed) break;
  }
  const half = new Uint16Array(W * H);
  for (let k = 0; k < half.length; k++) half[k] = THREE.DataUtils.toHalfFloat(h[k]);
  const tex = new THREE.DataTexture(half, W, H, THREE.RedFormat, THREE.HalfFloatType);
  tex.minFilter = tex.magFilter = THREE.LinearFilter;
  tex.wrapS = tex.wrapT = THREE.ClampToEdgeWrapping;
  tex.needsUpdate = true;
  U.ocGround.value = tex;
  U.ocGroundXf.value.set(minX, minZ, 1 / (W * cell), 1 / (H * cell));
  // bilinear CPU lookup at world (x, z)
  const at = (x, z) => {
    const fx = THREE.MathUtils.clamp((x - minX) / cell - 0.5, 0, W - 1.001);
    const fz = THREE.MathUtils.clamp((z - minZ) / cell - 0.5, 0, H - 1.001);
    const i = Math.floor(fx), j = Math.floor(fz), u = fx - i, v = fz - j;
    const k = j * W + i;
    return (h[k] * (1 - u) + h[k + 1] * u) * (1 - v) + (h[k + W] * (1 - u) + h[k + W + 1] * u) * v;
  };
  return { tex, W, H, minX, minZ, cell, at, ms: { rays: Math.round(tRay), total: Math.round(performance.now() - t0) } };
}
