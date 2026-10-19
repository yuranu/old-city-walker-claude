// Loader worker: everything heavy about a GLB happens here, off the main thread.
//   fetch (with progress) -> read accessors -> merge per (material name, nocol) in world space ->
//   split big groups into CHUNK-metre cells -> compact vertex formats -> collision geometry
//   (nocol filtered) + MeshBVH, serialised -> optional ground height field -> optional
//   material-only GLB for material names the main thread does not have yet.
// Everything is posted back as transferable typed arrays; the main thread only wraps them.
import { BufferGeometry, BufferAttribute, DataUtils } from 'three';
import { MeshBVH } from 'three-mesh-bvh';
import { GltfDoc, mat4, toTriangles, materialTextures, remapMaterialTextures, buildGLB, BinWriter, GEOMETRY_EXTENSIONS } from './gltf.js';
import { mergeParts, splitCells, splitCellsPos, finishPiece, bounds, heightField } from './merge.js';

let meshopt = null;

async function fetchBytes(url, onProgress) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`${url}: HTTP ${r.status}`);
  const total = +r.headers.get('content-length') || 0;
  if (!r.body || !onProgress) return r.arrayBuffer();
  const reader = r.body.getReader();
  const parts = [];
  let got = 0, last = 0;
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    parts.push(value);
    got += value.length;
    const now = performance.now();
    if (now - last > 80) { last = now; onProgress(got, total); }
  }
  onProgress(got, total || got);
  const out = new Uint8Array(got);
  let o = 0;
  for (const p of parts) { out.set(p, o); o += p.length; }
  return out.buffer;
}

// world-space bounding-box diagonal of a mesh node (POSITION accessor min/max, glTF requires them)
function nodeSize(j, mesh, m) {
  let d = 0;
  for (const p of mesh.primitives) {
    const a = j.accessors[p.attributes.POSITION];
    if (!a || !a.min || !a.max) return Infinity;
    const ex = [a.max[0] - a.min[0], a.max[1] - a.min[1], a.max[2] - a.min[2]];
    const wx = Math.abs(m[0]) * ex[0] + Math.abs(m[4]) * ex[1] + Math.abs(m[8]) * ex[2];
    const wy = Math.abs(m[1]) * ex[0] + Math.abs(m[5]) * ex[1] + Math.abs(m[9]) * ex[2];
    const wz = Math.abs(m[2]) * ex[0] + Math.abs(m[6]) * ex[1] + Math.abs(m[10]) * ex[2];
    d = Math.max(d, Math.hypot(wx, wy, wz));
  }
  return d;
}

async function job(msg) {
  const { id, url, opts } = msg;
  const T = { start: performance.now() };
  const buf = await fetchBytes(url, (loaded, total) => postMessage({ type: 'progress', id, loaded, total }));
  T.fetch = performance.now();
  const head = new TextDecoder().decode(new Uint8Array(buf, 0, Math.min(4, buf.byteLength)));
  if (head !== 'glTF') throw new Error(`${url}: not a GLB (${buf.byteLength} bytes, starts "${head}")`);
  const doc = await GltfDoc.load(url, buf, (u) => fetchBytes(u));
  const j = doc.json;
  if ((j.extensionsUsed || []).some((e) => /meshopt_compression/.test(e))) {
    if (!meshopt) {
      const m = await import('three/examples/jsm/libs/meshopt_decoder.module.js');
      meshopt = m.MeshoptDecoder;
      await meshopt.ready;
    }
    doc.meshopt = meshopt;
  }
  const known = new Set(opts.known || []);
  const flat = opts.flat || null;    // name -> [palette index, merged material name]
  const bake = opts.bake || null;    // textured name -> [palette index, merged name, { w, h, rgb }]
  // opts.bakeAll: the whole chunk draws baked flat (a sector's LOD); otherwise the bake table is
  // only used for the far copy (opts.far)

  // ---- gather primitives per (material, nocol)
  const prims = new Map();           // "mesh:prim" -> arrays (meshes are shared by many nodes)
  const groups = new Map();
  const collide = [];
  const farParts = new Map();        // opts.far: merged flat class -> parts (textures baked)
  const casters = [];                // opts.shadowProxy: opaque collidable casters, positions only
  const usedMats = new Map();        // name -> glTF material index (-1: default)
  let nodes = 0;
  for (const mn of doc.meshNodes(mat4)) {
    nodes++;
    const mesh = j.meshes[mn.mesh];
    mesh.primitives.forEach((p, pi) => {
      const mode = p.mode ?? 4;
      if (mode < 4 || p.attributes.POSITION === undefined) return;   // points / lines
      const key = mn.mesh + ':' + pi;
      let a = prims.get(key);
      if (!a) {
        const pos = doc.readFloat(p.attributes.POSITION);
        let idx = p.indices !== undefined ? doc.readIndex(p.indices) : null;
        if (mode !== 4) idx = toTriangles(idx || Uint32Array.from({ length: pos.length / 3 }, (_, i) => i), mode);
        const ca = p.attributes.COLOR_0;
        a = {
          pos, idx,
          nrm: p.attributes.NORMAL !== undefined ? doc.readFloat(p.attributes.NORMAL) : null,
          uv: p.attributes.TEXCOORD_0 !== undefined ? doc.readFloat(p.attributes.TEXCOORD_0) : null,
          col: ca !== undefined ? doc.readFloat(ca) : null,
          colSize: ca !== undefined ? (j.accessors[ca].type === 'VEC4' ? 4 : 3) : 3,
        };
        prims.set(key, a);
      }
      const md = p.material !== undefined ? j.materials[p.material] : null;
      let name = md ? (md.name || `__mat${p.material}`) : '__default';
      // untextured palette materials draw as one merged material (two: with / without the sky
      // reflection), the material picked per vertex from a palette index
      // far LOD geometry (opts.bake): textured materials too, their texture baked per triangle
      const bk = !flat || flat[name] || !opts.bakeAll ? null : bake && bake[name];
      const fl = (flat && flat[name]) || bk;
      if (fl) name = fl[1];
      if (!usedMats.has(name)) usedMats.set(name, fl ? -1 : (p.material ?? -1));
      // tiny props (spouts, AC units, dishes, litter: node smaller than opts.tinySize) get their
      // own group with a shorter draw and shadow distance
      const tiny = mn.nocol && opts.tinySize > 0 && nodeSize(j, mesh, mn.matrices[0]) < opts.tinySize;
      const dd = mn.drawDist || 0;
      const gk = name + (mn.nocol ? '|nocol' : '') + (tiny ? '|tiny' : '') + (dd ? '|d' + dd : '');
      if (!groups.has(gk)) groups.set(gk, { name, nocol: mn.nocol, tiny, drawDist: dd, parts: [] });
      for (const m of mn.matrices) {
        groups.get(gk).parts.push(fl ? { ...a, m, pal: fl[0], bake: bk ? bk[2] : undefined } : { ...a, m });
        if (!mn.nocol) collide.push({ pos: a.pos, idx: a.idx, m });
        if (opts.shadowProxy && !mn.nocol && !mn.drawDist && !(opts.noProxy || []).includes(md ? md.name : '')) casters.push({ pos: a.pos, idx: a.idx, m });
        // far copy: everything but props and cut-outs, flat with textures baked
        const src = md ? (md.name || `__mat${p.material}`) : '__default';
        const ff = opts.far && !mn.nocol && !mn.drawDist && ((flat && flat[src]) || (bake && bake[src]));
        if (ff) {
          if (!farParts.has(ff[1])) farParts.set(ff[1], []);
          farParts.get(ff[1]).push({ ...a, m, pal: ff[0], bake: ff[2] });
        }
      }
    });
  }
  T.parse = performance.now();

  // ---- render pieces
  const transfer = [];
  const outGroups = [];
  let tris = 0, verts = 0, gpuBytes = 0;
  const box = [Infinity, Infinity, Infinity, -Infinity, -Infinity, -Infinity];
  // opts.whole: also emit the unsplit group (a sector's LOD: drawn whole while the sector is far,
  // per cell while its full detail is resident)
  for (const { name, nocol, tiny, drawDist, parts } of groups.values()) {
    const merged = mergeParts(parts);
    const split = splitCells(merged, opts.cell, opts.minTris);
    const pieces = split.map((pc) => finishPiece(pc, opts.compact));
    let whole = null;
    if (opts.whole && split.length > 1) whole = [finishPiece({ ...merged, cell: null }, opts.compact)];
    let gt = 0;
    for (const pc of pieces.concat(whole || [])) {
      transfer.push(pc.pos.buffer, pc.nrm.buffer, pc.uv.buffer, pc.col.buffer, pc.idx.buffer);
      verts += pc.verts; gpuBytes += pc.bytes;
      for (let k = 0; k < 3; k++) { box[k] = Math.min(box[k], pc.box[k]); box[k + 3] = Math.max(box[k + 3], pc.box[k + 3]); }
    }
    for (const pc of pieces) gt += pc.tris;
    tris += gt;
    outGroups.push({ name, nocol, tiny, drawDist, tris: gt, pieces, whole });
  }
  // one shadow caster per render cell: the shadow pass needs depth only, so every opaque material
  // of the cell merges into one draw
  const shadow = [];
  if (casters.length) {
    for (const pc of splitCellsPos(mergeParts(casters, true), opts.cell)) { transfer.push(pc.pos.buffer, pc.idx.buffer); gpuBytes += pc.pos.byteLength + pc.idx.byteLength; shadow.push(pc); }
  }
  // far LOD copy of an always-resident chunk, per cell, drawn beyond rFar
  const far = [];
  for (const [name, parts] of farParts) {
    const pieces = splitCells(mergeParts(parts), opts.cell, 0).map((pc) => finishPiece(pc, opts.compact));
    for (const pc of pieces) { transfer.push(pc.pos.buffer, pc.nrm.buffer, pc.uv.buffer, pc.col.buffer, pc.idx.buffer); gpuBytes += pc.bytes; }
    far.push({ name, nocol: false, pieces });
    if (!usedMats.has(name)) usedMats.set(name, -1);
  }
  T.merge = performance.now();

  // ---- collision: positions only, nocol filtered
  let collision = null, height = null;
  if (collide.length) {
    const c = mergeParts(collide, true);
    const cbox = bounds(c.pos);
    if (opts.height) {
      height = heightField(c.pos, c.idx, opts.height.box || (box[0] < Infinity ? box : cbox), opts.height);
      const half = new Uint16Array(height.h.length);
      for (let k = 0; k < half.length; k++) half[k] = DataUtils.toHalfFloat(height.h[k]);
      height.half = half;
      transfer.push(height.h.buffer, half.buffer);
    }
    T.height = performance.now();
    const g = new BufferGeometry();
    g.setAttribute('position', new BufferAttribute(c.pos, 3));
    g.setIndex(new BufferAttribute(c.idx, 1));
    const bvh = new MeshBVH(g);
    const ser = MeshBVH.serialize(bvh, { cloneBuffers: false });
    collision = { pos: c.pos, bvh: ser, box: cbox, tris: c.idx.length / 3 };
    transfer.push(c.pos.buffer, ...ser.roots);
    if (ser.index) transfer.push(ser.index.buffer);
    if (ser.indirectBuffer) transfer.push(ser.indirectBuffer.buffer);
  } else if (opts.height) {
    height = null;
  }
  T.bvh = performance.now();

  // ---- material-only GLB for names the main thread lacks
  const missing = [...usedMats.keys()].filter((n) => !known.has(n));
  if (opts.allMaterials) for (const [i, m] of (j.materials || []).entries()) {
    const n = m.name || `__mat${i}`;
    if (!known.has(n) && !missing.includes(n)) { missing.push(n); usedMats.set(n, i); }
  }
  const materials = missing.length ? materialGLB(doc, missing.map((n) => [n, usedMats.get(n)]), url) : null;
  if (materials) transfer.push(materials.glb);
  T.end = performance.now();

  const ms = {
    fetch: Math.round(T.fetch - T.start), parse: Math.round(T.parse - T.fetch), merge: Math.round(T.merge - T.parse),
    height: height ? height.ms.total : 0, bvh: Math.round(T.bvh - T.merge) - (height ? height.ms.total : 0),
    total: Math.round(T.end - T.start),
  };
  return {
    result: {
      groups: outGroups, far, shadow, collision, height, materials, usedMaterials: [...usedMats.keys()],
      box, stats: { nodes, tris, verts, gpuBytes, colTris: collision ? collision.tris : 0, download: buf.byteLength, ms },
    },
    transfer,
  };
}

// glTF holding only the given materials (+ their textures, samplers and images); names keep the
// first-seen definition. Images embedded in the source are copied, external ones keep their URI
// (resolved against the source GLB).
function materialGLB(doc, list, srcUrl) {
  const j = doc.json;
  const out = { asset: { version: '2.0', generator: 'oc-walker material extract' }, materials: [], textures: [], images: [], samplers: [], bufferViews: [], buffers: [] };
  const bin = new BinWriter();
  const texMap = new Map(), imgMap = new Map(), smpMap = new Map();
  const names = {};
  const image = (ii) => {
    if (imgMap.has(ii)) return imgMap.get(ii);
    const im = { ...j.images[ii] };
    if (im.bufferView !== undefined) {
      const { bytes } = doc.view(im.bufferView);
      const off = bin.add(bytes.slice());
      out.bufferViews.push({ buffer: 0, byteOffset: off, byteLength: bytes.byteLength });
      im.bufferView = out.bufferViews.length - 1;
    } else if (im.uri !== undefined && !im.uri.startsWith('data:')) {
      im.uri = new URL(im.uri, srcUrl).href;
    }
    out.images.push(im);
    imgMap.set(ii, out.images.length - 1);
    return out.images.length - 1;
  };
  const texture = (ti) => {
    if (texMap.has(ti)) return texMap.get(ti);
    const t = JSON.parse(JSON.stringify(j.textures[ti]));
    if (t.source !== undefined) t.source = image(t.source);
    for (const e of Object.values(t.extensions || {})) if (e && e.source !== undefined) e.source = image(e.source);
    if (t.sampler !== undefined) {
      if (!smpMap.has(t.sampler)) { out.samplers.push(j.samplers[t.sampler]); smpMap.set(t.sampler, out.samplers.length - 1); }
      t.sampler = smpMap.get(t.sampler);
    }
    out.textures.push(t);
    texMap.set(ti, out.textures.length - 1);
    return out.textures.length - 1;
  };
  for (const [name, mi] of list) {
    const def = mi >= 0 ? JSON.parse(JSON.stringify(j.materials[mi])) : {};
    def.name = name;
    for (const ti of materialTextures(def)) texture(ti);
    remapMaterialTextures(def, texMap);
    names[name] = out.materials.length;
    out.materials.push(def);
  }
  const ext = (j.extensionsUsed || []).filter((e) => !GEOMETRY_EXTENSIONS.has(e));
  if (ext.length) out.extensionsUsed = ext;
  const req = (j.extensionsRequired || []).filter((e) => !GEOMETRY_EXTENSIONS.has(e));
  if (req.length) out.extensionsRequired = req;
  for (const k of ['textures', 'images', 'samplers', 'bufferViews']) if (!out[k].length) delete out[k];
  const bytes = bin.length ? bin.bytes() : null;
  if (bytes) out.buffers.push({ byteLength: bytes.length }); else delete out.buffers;
  return { glb: buildGLB(out, bytes), index: names, images: out.images ? out.images.length : 0 };
}

self.onmessage = async (e) => {
  const msg = e.data;
  if (msg.type !== 'job') return;
  try {
    const { result, transfer } = await job(msg);
    postMessage({ type: 'done', id: msg.id, result }, [...new Set(transfer)]);
  } catch (err) {
    postMessage({ type: 'error', id: msg.id, message: String(err && err.stack || err) });
  }
};
