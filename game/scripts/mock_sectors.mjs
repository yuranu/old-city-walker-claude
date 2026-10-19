// Mock sector set for testing the streaming loader before the build writes the real base/*.glb:
// splits the legacy city.glb into a palette and the always-resident base, and lists the real
// per-sector GLBs that already exist in public/sectors/ (bounds from public/sectors.json when the
// sector is listed there, else from the GLB's content).
//
//   node game/scripts/mock_sectors.mjs [--city public/city.glb] [--out public/mock]
//   then open /?sectors=mock
//
// Output (all under --out, git-ignored):
//   base/materials.glb   every material of city.glb with its textures, one tiny quad each, far
//                        below the city (y = -2000), like the build's palette
//   base/ground.glb      the ground node            } materials as name-only placeholders
//   base/walls.glb       city wall, Citadel, gate   } (no images), as the contract says
//   base/context.glb     context massing + city.glb props outside every listed sector
//   sectors.json         manifest: the base above + ../sectors/<id>.glb / _lo.glb
//   real.json            the build's public/sectors.json re-rooted here, with the build's own
//                        base (public/base/*.glb) filled in when the manifest lacks it
//                        (open /?sectors=mock/real.json)
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseGLB, buildGLB, BinWriter, materialTextures, remapMaterialTextures, mat4, GltfDoc } from '../src/gltf.js';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const GAME = path.resolve(HERE, '..');
const arg = (k, d) => { const i = process.argv.indexOf('--' + k); return i > 0 ? process.argv[i + 1] : d; };
const CITY = path.resolve(GAME, arg('city', 'public/city.glb'));
const OUT = path.resolve(GAME, arg('out', 'public/mock'));
const SECTORS = path.resolve(GAME, 'public/sectors');
const MANIFEST = path.resolve(GAME, 'public/sectors.json');

const WALLS = /^(city_wall|citadel|jaffa_gate)\b/;
const CONTEXT = /^context_massing/;
const GROUND = /^ground$/;

function readGLB(file) {
  const buf = fs.readFileSync(file);
  const ab = buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength);
  const { json, bin } = parseGLB(ab);
  return { json, bin, doc: new GltfDoc(json, [bin]) };
}

// plan-frame AABB [x0, y0, x1, y1] of a root node subtree (accessor min/max through the matrices)
function nodeBounds(src, ni, parent = mat4.identity(), out = [Infinity, Infinity, -Infinity, -Infinity]) {
  const j = src.json, n = j.nodes[ni];
  const local = n.matrix ? Float32Array.from(n.matrix) : mat4.compose(n.translation || [0, 0, 0], n.rotation || [0, 0, 0, 1], n.scale || [1, 1, 1]);
  const m = mat4.multiply(parent, local);
  if (n.mesh !== undefined) {
    for (const p of j.meshes[n.mesh].primitives) {
      const a = j.accessors[p.attributes.POSITION];
      for (let c = 0; c < 8; c++) {
        const x = c & 1 ? a.max[0] : a.min[0], y = c & 2 ? a.max[1] : a.min[1], z = c & 4 ? a.max[2] : a.min[2];
        const wx = m[0] * x + m[4] * y + m[8] * z + m[12], wz = m[2] * x + m[6] * y + m[10] * z + m[14];
        out[0] = Math.min(out[0], wx); out[2] = Math.max(out[2], wx);
        out[1] = Math.min(out[1], -wz); out[3] = Math.max(out[3], -wz);
      }
    }
  }
  for (const c of n.children || []) nodeBounds(src, c, m, out);
  return out;
}

// new GLB with the given root nodes; materials: 'placeholder' (name + factors) or 'full'
function subset(src, roots, materials = 'placeholder') {
  const j = src.json;
  const out = { asset: { version: '2.0', generator: 'oc-walker mock_sectors' }, scene: 0, scenes: [{ nodes: [] }], nodes: [], meshes: [], accessors: [], bufferViews: [], buffers: [], materials: [] };
  const bin = new BinWriter();
  const maps = { node: new Map(), mesh: new Map(), acc: new Map(), view: new Map(), mat: new Map(), tex: new Map(), img: new Map(), smp: new Map() };
  const view = (vi) => {
    if (maps.view.has(vi)) return maps.view.get(vi);
    const bv = j.bufferViews[vi];
    const bytes = src.bin.subarray(bv.byteOffset || 0, (bv.byteOffset || 0) + bv.byteLength);
    const o = { buffer: 0, byteOffset: bin.add(bytes), byteLength: bv.byteLength };
    if (bv.byteStride) o.byteStride = bv.byteStride;
    if (bv.target) o.target = bv.target;
    out.bufferViews.push(o);
    maps.view.set(vi, out.bufferViews.length - 1);
    return out.bufferViews.length - 1;
  };
  const acc = (ai) => {
    if (maps.acc.has(ai)) return maps.acc.get(ai);
    const a = { ...j.accessors[ai] };
    if (a.bufferView !== undefined) a.bufferView = view(a.bufferView);
    out.accessors.push(a);
    maps.acc.set(ai, out.accessors.length - 1);
    return out.accessors.length - 1;
  };
  const material = (mi) => {
    if (maps.mat.has(mi)) return maps.mat.get(mi);
    const d = JSON.parse(JSON.stringify(j.materials[mi]));
    let def;
    if (materials === 'full') {
      def = d;
      const texs = materialTextures(def);
      for (const ti of texs) texture(ti);
      remapMaterialTextures(def, maps.tex);
    } else {
      // what the build writes: the name (plus plain factors), no textures
      const pbr = d.pbrMetallicRoughness || {};
      def = { name: d.name, pbrMetallicRoughness: { baseColorFactor: pbr.baseColorFactor || [0.8, 0.8, 0.8, 1], metallicFactor: pbr.metallicFactor ?? 0, roughnessFactor: pbr.roughnessFactor ?? 0.9 } };
      if (d.alphaMode) def.alphaMode = d.alphaMode;
    }
    out.materials.push(def);
    maps.mat.set(mi, out.materials.length - 1);
    return out.materials.length - 1;
  };
  const image = (ii) => {
    if (maps.img.has(ii)) return maps.img.get(ii);
    const im = { ...j.images[ii] };
    if (im.bufferView !== undefined) im.bufferView = view(im.bufferView);
    (out.images ||= []).push(im);
    maps.img.set(ii, out.images.length - 1);
    return out.images.length - 1;
  };
  const texture = (ti) => {
    if (maps.tex.has(ti)) return maps.tex.get(ti);
    const t = JSON.parse(JSON.stringify(j.textures[ti]));
    if (t.source !== undefined) t.source = image(t.source);
    for (const e of Object.values(t.extensions || {})) if (e && e.source !== undefined) e.source = image(e.source);
    if (t.sampler !== undefined) {
      if (!maps.smp.has(t.sampler)) { (out.samplers ||= []).push(j.samplers[t.sampler]); maps.smp.set(t.sampler, out.samplers.length - 1); }
      t.sampler = maps.smp.get(t.sampler);
    }
    (out.textures ||= []).push(t);
    maps.tex.set(ti, out.textures.length - 1);
    return out.textures.length - 1;
  };
  const mesh = (mi) => {
    if (maps.mesh.has(mi)) return maps.mesh.get(mi);
    const m = JSON.parse(JSON.stringify(j.meshes[mi]));
    for (const p of m.primitives) {
      for (const k of Object.keys(p.attributes)) p.attributes[k] = acc(p.attributes[k]);
      if (p.indices !== undefined) p.indices = acc(p.indices);
      if (p.material !== undefined) p.material = material(p.material);
    }
    out.meshes.push(m);
    maps.mesh.set(mi, out.meshes.length - 1);
    return out.meshes.length - 1;
  };
  const node = (ni) => {
    const n = JSON.parse(JSON.stringify(j.nodes[ni]));
    if (n.mesh !== undefined) n.mesh = mesh(n.mesh);
    if (n.children) n.children = n.children.map(node);
    out.nodes.push(n);
    return out.nodes.length - 1;
  };
  for (const r of roots) out.scenes[0].nodes.push(node(r));
  return finish(out, bin, j);
}

function finish(out, bin, j) {
  const bytes = bin.length ? bin.bytes() : null;
  if (bytes) out.buffers.push({ byteLength: bytes.length }); else delete out.buffers;
  for (const k of ['meshes', 'accessors', 'bufferViews', 'materials']) if (out[k] && !out[k].length) delete out[k];
  const ext = (j.extensionsUsed || []).filter((e) => (e !== 'EXT_texture_webp' || out.textures));
  if (ext.length) out.extensionsUsed = ext;
  const req = (j.extensionsRequired || []).filter((e) => (e !== 'EXT_texture_webp' || out.textures));
  if (req.length) out.extensionsRequired = req;
  return Buffer.from(buildGLB(out, bytes));
}

// the palette: every material with its textures, each on a tiny quad far below the city
function palette(src) {
  const j = src.json;
  // fake a source with one quad mesh per material and let subset() copy what they reference
  const quad = new BinWriter();
  const P = new Float32Array([0, 0, 0, 1, 0, 0, 1, 0, -1, 0, 0, -1]);
  const N = new Float32Array([0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0]);
  const T = new Float32Array([0, 0, 1, 0, 1, 1, 0, 1]);
  const I = new Uint16Array([0, 1, 2, 0, 2, 3]);
  const views = [P, N, T, I].map((a) => ({ buffer: 0, byteOffset: quad.add(a), byteLength: a.byteLength }));
  const binQuad = quad.bytes();
  const merged = new Uint8Array(src.bin.length + 4 + binQuad.length);
  const base = (src.bin.length + 3) & ~3;
  merged.set(src.bin, 0); merged.set(binQuad, base);
  const fake = JSON.parse(JSON.stringify(j));
  const v0 = fake.bufferViews.length;
  for (const v of views) fake.bufferViews.push({ ...v, byteOffset: v.byteOffset + base });
  const a0 = fake.accessors.length;
  fake.accessors.push(
    { bufferView: v0, componentType: 5126, count: 4, type: 'VEC3', min: [0, 0, -1], max: [1, 0, 0] },
    { bufferView: v0 + 1, componentType: 5126, count: 4, type: 'VEC3' },
    { bufferView: v0 + 2, componentType: 5126, count: 4, type: 'VEC2' },
    { bufferView: v0 + 3, componentType: 5123, count: 6, type: 'SCALAR' });
  const roots = [];
  fake.materials.forEach((m, mi) => {
    fake.meshes.push({ name: 'palette_' + m.name, primitives: [{ attributes: { POSITION: a0, NORMAL: a0 + 1, TEXCOORD_0: a0 + 2 }, indices: a0 + 3, material: mi }] });
    fake.nodes.push({ name: 'palette_' + m.name, mesh: fake.meshes.length - 1, translation: [mi * 2, -2000, -50] });
    roots.push(fake.nodes.length - 1);
  });
  return subset({ json: fake, bin: merged }, roots, 'full');
}

function main() {
  const src = readGLB(CITY);
  const j = src.json;
  const roots = j.scenes[j.scene || 0].nodes;
  // sectors: every public/sectors/<id>.glb (not _lo)
  let listed = {};
  try { for (const s of JSON.parse(fs.readFileSync(MANIFEST, 'utf8')).sectors || []) listed[s.id] = s; } catch { listed = {}; }
  const sectors = [];
  for (const f of fs.existsSync(SECTORS) ? fs.readdirSync(SECTORS).sort() : []) {
    if (!f.endsWith('.glb') || f.endsWith('_lo.glb')) continue;
    const id = f.replace(/\.glb$/, '');
    const hi = readGLB(path.join(SECTORS, f));
    let b = [Infinity, Infinity, -Infinity, -Infinity];
    for (const r of hi.json.scenes[hi.json.scene || 0].nodes) nodeBounds(hi, r, mat4.identity(), b);
    if (listed[id]?.bounds) b = listed[id].bounds;
    let tris = 0;
    for (const n of hi.json.nodes) if (n.mesh !== undefined) for (const p of hi.json.meshes[n.mesh].primitives) tris += hi.json.accessors[p.indices].count / 3;
    const lo = fs.existsSync(path.join(SECTORS, id + '_lo.glb')) ? `../sectors/${id}_lo.glb` : null;
    sectors.push({ id, name: listed[id]?.name || id, bounds: b.map((v) => Math.round(v * 10) / 10), hi: `../sectors/${f}`, lo, tris_hi: Math.round(tris) });
  }
  const inSector = (bb) => {
    const cx = (bb[0] + bb[2]) / 2, cy = (bb[1] + bb[3]) / 2;
    return sectors.some((s) => cx >= s.bounds[0] && cx <= s.bounds[2] && cy >= s.bounds[1] && cy <= s.bounds[3]);
  };
  const pick = { ground: [], walls: [], context: [] };
  let dropped = 0;
  for (const r of roots) {
    const name = j.nodes[r].name || '';
    if (GROUND.test(name)) pick.ground.push(r);
    else if (WALLS.test(name)) pick.walls.push(r);
    else if (CONTEXT.test(name)) pick.context.push(r);
    else if (!inSector(nodeBounds(src, r))) pick.context.push(r);
    else dropped++;
  }
  fs.mkdirSync(path.join(OUT, 'base'), { recursive: true });
  const write = (rel, buf) => { fs.writeFileSync(path.join(OUT, rel), buf); console.log(`  ${rel.padEnd(20)} ${(buf.length / 1048576).toFixed(1)} MB`); };
  console.log(`city.glb: ${roots.length} root nodes -> ground ${pick.ground.length}, walls ${pick.walls.length}, context ${pick.context.length}, ${dropped} left to the real sectors`);
  write('base/materials.glb', palette(src));
  for (const k of ['ground', 'walls', 'context']) write(`base/${k}.glb`, subset(src, pick[k]));
  const manifest = {
    version: 1, mock: 'written by game/scripts/mock_sectors.mjs from city.glb + public/sectors/*.glb',
    materials: 'base/materials.glb',
    always: ['base/ground.glb', 'base/walls.glb', 'base/context.glb'],
    sectors,
  };
  fs.writeFileSync(path.join(OUT, 'sectors.json'), JSON.stringify(manifest, null, 1));
  console.log(`  sectors.json         ${sectors.length} sectors: ${sectors.map((s) => s.id).join(', ')}`);
  // the build's manifest with its own base
  try {
    const real = JSON.parse(fs.readFileSync(MANIFEST, 'utf8'));
    const BASE = path.resolve(GAME, 'public/base');
    const re = (p) => (p ? '../' + p : p);
    if (!real.always || !real.always.length) {
      real.always = ['ground', 'walls', 'context'].filter((k) => fs.existsSync(path.join(BASE, k + '.glb'))).map((k) => `base/${k}.glb`);
    }
    const out = { ...real, mock: 'public/sectors.json re-rooted by mock_sectors.mjs', materials: re(real.materials), always: real.always.map(re),
      sectors: real.sectors.map((s) => ({ ...s, hi: re(s.hi), lo: re(s.lo) })) };
    fs.writeFileSync(path.join(OUT, 'real.json'), JSON.stringify(out, null, 1));
    console.log(`  real.json            ${out.sectors.length} sectors, always: ${out.always.join(', ')}`);
  } catch (e) {
    console.log('  real.json            skipped:', e.message);
  }
}

main();
