// Minimal glTF 2.0 / GLB reader and writer without three.js scene objects. Used by the loader
// worker (geometry is merged straight from the accessors, nothing is decoded twice) and by the
// Node mock-sector script. Supports: GLB and external/data-URI buffers, every accessor
// component type (normalized or not, interleaved, sparse), KHR_mesh_quantization (it only
// widens the accessor types), EXT_meshopt_compression (decoder passed in), node TRS/matrix
// hierarchies and EXT_mesh_gpu_instancing.

const GLB_MAGIC = 0x46546c67, CHUNK_JSON = 0x4e4f534a, CHUNK_BIN = 0x004e4942;

export function parseGLB(buf) {
  const dv = new DataView(buf);
  if (buf.byteLength < 20 || dv.getUint32(0, true) !== GLB_MAGIC) throw new Error('not a GLB file');
  const len = Math.min(dv.getUint32(8, true), buf.byteLength);
  let off = 12, json = null, bin = null;
  while (off + 8 <= len) {
    const clen = dv.getUint32(off, true), type = dv.getUint32(off + 4, true);
    if (type === CHUNK_JSON) json = JSON.parse(new TextDecoder().decode(new Uint8Array(buf, off + 8, clen)));
    else if (type === CHUNK_BIN && !bin) bin = new Uint8Array(buf, off + 8, clen);
    off += 8 + clen;
  }
  if (!json) throw new Error('GLB without JSON chunk');
  return { json, bin };
}

// GLB from a JSON object and one binary blob (Uint8Array or null)
export function buildGLB(json, bin) {
  const enc = new TextEncoder().encode(JSON.stringify(json));
  const jlen = (enc.length + 3) & ~3;
  const blen = bin ? (bin.length + 3) & ~3 : 0;
  const total = 12 + 8 + jlen + (bin ? 8 + blen : 0);
  const out = new Uint8Array(total);
  const dv = new DataView(out.buffer);
  dv.setUint32(0, GLB_MAGIC, true); dv.setUint32(4, 2, true); dv.setUint32(8, total, true);
  dv.setUint32(12, jlen, true); dv.setUint32(16, CHUNK_JSON, true);
  out.set(enc, 20);
  for (let i = 20 + enc.length; i < 20 + jlen; i++) out[i] = 0x20;
  if (bin) {
    const o = 20 + jlen;
    dv.setUint32(o, blen, true); dv.setUint32(o + 4, CHUNK_BIN, true);
    out.set(bin, o + 8);
  }
  return out.buffer;
}

// growable byte sink for assembling a BIN chunk with 4-byte aligned views
export class BinWriter {
  constructor() { this.parts = []; this.length = 0; }
  add(bytes) {
    const pad = (4 - (this.length & 3)) & 3;
    if (pad) { this.parts.push(new Uint8Array(pad)); this.length += pad; }
    const offset = this.length;
    this.parts.push(bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes.buffer, bytes.byteOffset, bytes.byteLength));
    this.length += bytes.byteLength;
    return offset;
  }
  bytes() {
    const out = new Uint8Array(this.length);
    let o = 0;
    for (const p of this.parts) { out.set(p, o); o += p.length; }
    return out;
  }
}

const TYPES = { 5120: Int8Array, 5121: Uint8Array, 5122: Int16Array, 5123: Uint16Array, 5125: Uint32Array, 5126: Float32Array };
const SIZES = { SCALAR: 1, VEC2: 2, VEC3: 3, VEC4: 4, MAT2: 4, MAT3: 9, MAT4: 16 };
const NORM = { 5120: (v) => Math.max(v / 127, -1), 5121: (v) => v / 255, 5122: (v) => Math.max(v / 32767, -1), 5123: (v) => v / 65535 };

export class GltfDoc {
  // buffers: array of Uint8Array (index = glTF buffer index); meshopt: MeshoptDecoder (ready)
  constructor(json, buffers, { meshopt = null } = {}) {
    this.json = json;
    this.buffers = buffers;
    this.meshopt = meshopt;
    this._views = new Map();
  }

  static async load(url, buf, fetchBuffer, opts) {
    const { json, bin } = parseGLB(buf);
    const buffers = [];
    for (const [i, b] of (json.buffers || []).entries()) {
      if (b.uri === undefined) buffers[i] = bin;
      else buffers[i] = new Uint8Array(await fetchBuffer(new URL(b.uri, url).href));
    }
    return new GltfDoc(json, buffers, opts);
  }

  // bytes of a bufferView (decoded when meshopt compressed)
  view(i) {
    let v = this._views.get(i);
    if (v) return v;
    const bv = this.json.bufferViews[i];
    const mo = bv.extensions && (bv.extensions.EXT_meshopt_compression || bv.extensions.KHR_meshopt_compression);
    if (mo) {
      if (!this.meshopt) throw new Error('EXT_meshopt_compression without a decoder');
      const src = this.buffers[mo.buffer];
      const source = src.subarray(mo.byteOffset || 0, (mo.byteOffset || 0) + mo.byteLength);
      const out = new Uint8Array(mo.count * mo.byteStride);
      this.meshopt.decodeGltfBuffer(out, mo.count, mo.byteStride, source, mo.mode, mo.filter);
      v = { bytes: out, stride: mo.byteStride };
    } else {
      const src = this.buffers[bv.buffer];
      v = { bytes: src.subarray(bv.byteOffset || 0, (bv.byteOffset || 0) + bv.byteLength), stride: bv.byteStride || 0 };
    }
    this._views.set(i, v);
    return v;
  }

  // accessor -> Float32Array (count * itemSize), normalised ints mapped to floats
  readFloat(ai) {
    const a = this.json.accessors[ai];
    const size = SIZES[a.type], n = a.count, T = TYPES[a.componentType];
    const out = new Float32Array(n * size);
    if (a.bufferView !== undefined) {
      const { bytes, stride } = this.view(a.bufferView);
      const es = T.BYTES_PER_ELEMENT, st = stride || size * es;
      const base = bytes.byteOffset + (a.byteOffset || 0);
      const norm = a.normalized ? NORM[a.componentType] : null;
      if (T === Float32Array && st === size * es && base % 4 === 0) {
        out.set(new Float32Array(bytes.buffer, base, n * size));
      } else if ((base % es) === 0 && (st % es) === 0) {
        const arr = new T(bytes.buffer, base, ((n - 1) * st) / es + size);
        const k = st / es;
        for (let i = 0; i < n; i++) for (let c = 0; c < size; c++) {
          const v = arr[i * k + c];
          out[i * size + c] = norm ? norm(v) : v;
        }
      } else {
        const dv = new DataView(bytes.buffer, base);
        const get = { 5120: 'getInt8', 5121: 'getUint8', 5122: 'getInt16', 5123: 'getUint16', 5125: 'getUint32', 5126: 'getFloat32' }[a.componentType];
        for (let i = 0; i < n; i++) for (let c = 0; c < size; c++) {
          const v = dv[get](i * st + c * es, true);
          out[i * size + c] = norm ? norm(v) : v;
        }
      }
    }
    if (a.sparse) {
      const s = a.sparse;
      const idx = this._readRaw(s.indices.bufferView, s.indices.byteOffset || 0, s.indices.componentType, s.count);
      const vals = this._readRaw(s.values.bufferView, s.values.byteOffset || 0, a.componentType, s.count * size);
      const norm = a.normalized ? NORM[a.componentType] : null;
      for (let i = 0; i < s.count; i++) for (let c = 0; c < size; c++) {
        const v = vals[i * size + c];
        out[idx[i] * size + c] = norm ? norm(v) : v;
      }
    }
    return out;
  }

  _readRaw(view, offset, componentType, count) {
    const { bytes } = this.view(view);
    const T = TYPES[componentType];
    const base = bytes.byteOffset + offset;
    if (base % T.BYTES_PER_ELEMENT === 0) return new T(bytes.buffer, base, count);
    return new T(bytes.slice(offset, offset + count * T.BYTES_PER_ELEMENT).buffer);
  }

  readIndex(ai) {
    const a = this.json.accessors[ai];
    const raw = this._readRaw(a.bufferView, a.byteOffset || 0, a.componentType, a.count);
    return raw instanceof Uint32Array ? raw : Uint32Array.from(raw);
  }

  // [{node, mesh, matrices: [Float32Array(16)...], nocol, ground, drawDist}] for every mesh node
  // of the default scene; matrices are column-major world transforms (several when instanced);
  // drawDist: extras.draw_dist (m) of the node or an ancestor, 0 when none
  meshNodes(mat4) {
    const j = this.json;
    const out = [];
    const scene = (j.scenes || [])[j.scene || 0];
    if (!scene) return out;
    const walk = (ni, parent, nocol, ground, drawDist) => {
      const n = j.nodes[ni];
      const local = n.matrix ? Float32Array.from(n.matrix) : mat4.compose(n.translation || [0, 0, 0], n.rotation || [0, 0, 0, 1], n.scale || [1, 1, 1]);
      const world = mat4.multiply(parent, local);
      const ex = n.extras || {};
      const meshEx = n.mesh !== undefined ? (j.meshes[n.mesh].extras || {}) : {};
      const nc = nocol || !!ex.nocol || !!meshEx.nocol;
      const gr = ground || !!ex.ground || !!meshEx.ground;
      const dd = +(ex.draw_dist ?? meshEx.draw_dist ?? drawDist ?? 0) || 0;
      if (n.mesh !== undefined) {
        let matrices = [world];
        const inst = n.extensions && n.extensions.EXT_mesh_gpu_instancing;
        if (inst) {
          const at = inst.attributes || {};
          const T = at.TRANSLATION !== undefined ? this.readFloat(at.TRANSLATION) : null;
          const R = at.ROTATION !== undefined ? this.readFloat(at.ROTATION) : null;
          const S = at.SCALE !== undefined ? this.readFloat(at.SCALE) : null;
          const cnt = j.accessors[at.TRANSLATION ?? at.ROTATION ?? at.SCALE].count;
          matrices = [];
          for (let i = 0; i < cnt; i++) {
            const m = mat4.compose(T ? [T[i * 3], T[i * 3 + 1], T[i * 3 + 2]] : [0, 0, 0],
              R ? [R[i * 4], R[i * 4 + 1], R[i * 4 + 2], R[i * 4 + 3]] : [0, 0, 0, 1],
              S ? [S[i * 3], S[i * 3 + 1], S[i * 3 + 2]] : [1, 1, 1]);
            matrices.push(mat4.multiply(world, m));
          }
        }
        out.push({ node: ni, name: n.name || '', mesh: n.mesh, matrices, nocol: nc, ground: gr, drawDist: dd });
      }
      for (const c of n.children || []) walk(c, world, nc, gr, dd);
    };
    for (const r of scene.nodes || []) walk(r, mat4.identity(), false, false, 0);
    return out;
  }
}

// small column-major mat4 helpers (no three.js objects needed)
export const mat4 = {
  identity: () => Float32Array.of(1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1),
  compose([tx, ty, tz], [x, y, z, w], [sx, sy, sz]) {
    const x2 = x + x, y2 = y + y, z2 = z + z;
    const xx = x * x2, xy = x * y2, xz = x * z2, yy = y * y2, yz = y * z2, zz = z * z2;
    const wx = w * x2, wy = w * y2, wz = w * z2;
    return Float32Array.of(
      (1 - (yy + zz)) * sx, (xy + wz) * sx, (xz - wy) * sx, 0,
      (xy - wz) * sy, (1 - (xx + zz)) * sy, (yz + wx) * sy, 0,
      (xz + wy) * sz, (yz - wx) * sz, (1 - (xx + yy)) * sz, 0,
      tx, ty, tz, 1);
  },
  multiply(a, b) {
    const o = new Float32Array(16);
    for (let c = 0; c < 4; c++) for (let r = 0; r < 4; r++) {
      o[c * 4 + r] = a[r] * b[c * 4] + a[4 + r] * b[c * 4 + 1] + a[8 + r] * b[c * 4 + 2] + a[12 + r] * b[c * 4 + 3];
    }
    return o;
  },
  determinant(m) {
    return m[0] * (m[5] * m[10] - m[9] * m[6]) - m[4] * (m[1] * m[10] - m[9] * m[2]) + m[8] * (m[1] * m[6] - m[5] * m[2]);
  },
};

// triangle list from strips / fans (glTF modes 5, 6)
export function toTriangles(index, mode) {
  if (mode === 4) return index;
  const out = [];
  if (mode === 5) {
    for (let i = 0; i + 2 < index.length; i++) {
      if (i % 2 === 0) out.push(index[i], index[i + 1], index[i + 2]);
      else out.push(index[i + 1], index[i], index[i + 2]);
    }
  } else if (mode === 6) {
    for (let i = 1; i + 1 < index.length; i++) out.push(index[0], index[i], index[i + 1]);
  }
  return Uint32Array.from(out);
}

// every texture index referenced by a material definition (core slots and extensions)
export function materialTextures(def) {
  const out = new Set();
  const walk = (o, key) => {
    if (!o || typeof o !== 'object') return;
    if (/Texture$/.test(key || '') && typeof o.index === 'number') out.add(o.index);
    for (const [k, v] of Object.entries(o)) walk(v, k);
  };
  walk(def, '');
  return out;
}

export function remapMaterialTextures(def, map) {
  const walk = (o, key) => {
    if (!o || typeof o !== 'object') return;
    if (/Texture$/.test(key || '') && typeof o.index === 'number') o.index = map.get(o.index);
    for (const [k, v] of Object.entries(o)) walk(v, k);
  };
  walk(def, '');
  return def;
}

// extensions that only concern geometry: the material-only GLB must not declare them
export const GEOMETRY_EXTENSIONS = new Set(['KHR_draco_mesh_compression', 'EXT_meshopt_compression',
  'KHR_meshopt_compression', 'KHR_mesh_quantization', 'EXT_mesh_gpu_instancing']);
