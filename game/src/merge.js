// Geometry crunching shared by the loader worker: merge primitives per material into world-space
// arrays, split big groups into spatial cells, compact the vertex formats, and rasterise a ground
// height field. Pure typed-array code (no three.js objects), so it runs anywhere.

// ------------------------------------------------------------------ merge
// parts: [{ pos, nrm|null, uv|null, col|null, colSize, idx|null, m (column-major mat4),
//          pal (optional palette index of a merged flat material, kept per vertex),
//          bake (optional { w, h, rgb }: texture colour baked into the vertex colours) }]
export function mergeParts(parts, posOnly = false) {
  let nv = 0, ni = 0;
  for (const p of parts) {
    const n = p.pos.length / 3;
    nv += n;
    ni += p.idx ? p.idx.length : n;
  }
  const pos = new Float32Array(nv * 3);
  const nrm = posOnly ? null : new Float32Array(nv * 3);
  const uv = posOnly ? null : new Float32Array(nv * 2);
  const col = posOnly ? null : new Float32Array(nv * 3);
  const pal = !posOnly && parts.some((p) => p.pal !== undefined) ? new Uint8Array(nv).fill(255) : null;
  const idx = new Uint32Array(ni);
  const k = new Float32Array(9);
  let vo = 0, io = 0;
  for (const p of parts) {
    const n = p.pos.length / 3, e = p.m;
    const src = p.pos;
    for (let i = 0; i < n; i++) {
      const x = src[i * 3], y = src[i * 3 + 1], z = src[i * 3 + 2], o = (vo + i) * 3;
      pos[o] = e[0] * x + e[4] * y + e[8] * z + e[12];
      pos[o + 1] = e[1] * x + e[5] * y + e[9] * z + e[13];
      pos[o + 2] = e[2] * x + e[6] * y + e[10] * z + e[14];
    }
    if (!posOnly) {
      const pn = p.nrm || vertexNormals(p.pos, p.idx);
      normalMatrix(e, k);
      for (let i = 0; i < n; i++) {
        const x = pn[i * 3], y = pn[i * 3 + 1], z = pn[i * 3 + 2], o = (vo + i) * 3;
        const nx = k[0] * x + k[3] * y + k[6] * z, ny = k[1] * x + k[4] * y + k[7] * z, nz = k[2] * x + k[5] * y + k[8] * z;
        const l = Math.hypot(nx, ny, nz) || 1;
        nrm[o] = nx / l; nrm[o + 1] = ny / l; nrm[o + 2] = nz / l;
      }
      if (p.uv) uv.set(p.uv.subarray(0, n * 2), vo * 2);
      if (p.col) {
        const cs = p.colSize;
        for (let i = 0; i < n; i++) {
          const o = (vo + i) * 3;
          col[o] = p.col[i * cs]; col[o + 1] = p.col[i * cs + 1]; col[o + 2] = p.col[i * cs + 2];
        }
      } else col.fill(1, vo * 3, (vo + n) * 3);
      if (pal && p.pal !== undefined) pal.fill(p.pal, vo, vo + n);
      if (p.bake) bakeTexture(p.bake, p.uv, p.idx, n, col, vo);
    }
    const flip = det3(e) < 0;
    const ia = p.idx;
    const cnt = ia ? ia.length : n;
    for (let i = 0; i + 2 < cnt; i += 3) {
      const a = ia ? ia[i] : i, b = ia ? ia[i + 1] : i + 1, c = ia ? ia[i + 2] : i + 2;
      idx[io + i] = vo + a;
      idx[io + i + 1] = vo + (flip ? c : b);
      idx[io + i + 2] = vo + (flip ? b : c);
    }
    vo += n; io += cnt;
  }
  return { pos, nrm, uv, col, idx, pal };
}

// multiply each vertex colour by the mean texture colour over its triangles' uv footprints
// (bounding rectangle, repeat wrapping, from a summed-area table), averaged over the triangles
// sharing the vertex: big tiled faces get the texture's mean, atlas regions their own colour
function bakeTexture(tex, uv, idx, n, col, vo) {
  if (!uv) return;
  const sat = tex.sat || (tex.sat = summedArea(tex));
  const acc = new Float32Array(n * 3), cnt = new Uint16Array(n), c3 = [0, 0, 0];
  const tri = idx ? idx.length : n;
  for (let t = 0; t + 2 < tri; t += 3) {
    const a = idx ? idx[t] : t, b = idx ? idx[t + 1] : t + 1, c = idx ? idx[t + 2] : t + 2;
    const u0 = Math.min(uv[a * 2], uv[b * 2], uv[c * 2]), u1 = Math.max(uv[a * 2], uv[b * 2], uv[c * 2]);
    const v0 = Math.min(uv[a * 2 + 1], uv[b * 2 + 1], uv[c * 2 + 1]), v1 = Math.max(uv[a * 2 + 1], uv[b * 2 + 1], uv[c * 2 + 1]);
    rectMean(sat, tex.w, tex.h, u0, u1, v0, v1, c3);
    for (const vi of [a, b, c]) {
      acc[vi * 3] += c3[0]; acc[vi * 3 + 1] += c3[1]; acc[vi * 3 + 2] += c3[2];
      if (cnt[vi] < 65535) cnt[vi]++;
    }
  }
  for (let i = 0; i < n; i++) {
    if (!cnt[i]) continue;
    const o = (vo + i) * 3;
    for (let k = 0; k < 3; k++) col[o + k] *= acc[i * 3 + k] / cnt[i];
  }
}

function summedArea({ w, h, rgb }) {
  const S = new Float64Array((w + 1) * (h + 1) * 3);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) for (let k = 0; k < 3; k++) {
    const i = ((y + 1) * (w + 1) + x + 1) * 3 + k;
    S[i] = rgb[(y * w + x) * 3 + k] + S[i - 3] + S[i - (w + 1) * 3] - S[i - (w + 2) * 3];
  }
  return S;
}

// mean over texel range [x0, x1) x [y0, y1) (integers within the texture)
function boxSum(S, w, x0, x1, y0, y1, out) {
  const W = w + 1;
  for (let k = 0; k < 3; k++) out[k] += S[(y1 * W + x1) * 3 + k] - S[(y0 * W + x1) * 3 + k] - S[(y1 * W + x0) * 3 + k] + S[(y0 * W + x0) * 3 + k];
  return (x1 - x0) * (y1 - y0);
}

// [lo, hi) texel spans covering [a, b] in repeat-wrapped texture space of size n
function spans(a, b, n) {
  if (b - a >= 1) return [[0, n]];
  const f = Math.floor(a);
  let x0 = Math.floor((a - f) * n), x1 = Math.ceil((b - f) * n);
  if (x1 <= x0) x1 = x0 + 1;
  if (x1 <= n) return [[x0, x1]];
  return [[x0, n], [0, Math.min(n, x1 - n)]];
}

function rectMean(S, w, h, u0, u1, v0, v1, out) {
  out[0] = out[1] = out[2] = 0;
  let area = 0;
  for (const [x0, x1] of spans(u0, u1, w)) for (const [y0, y1] of spans(v0, v1, h)) area += boxSum(S, w, x0, x1, y0, y1, out);
  for (let k = 0; k < 3; k++) out[k] /= area || 1;
}

function det3(m) {
  return m[0] * (m[5] * m[10] - m[9] * m[6]) - m[4] * (m[1] * m[10] - m[9] * m[2]) + m[8] * (m[1] * m[6] - m[5] * m[2]);
}

// inverse transpose of the upper 3x3 (column-major out, like three's Matrix3.getNormalMatrix)
function normalMatrix(m, out) {
  const a = m[0], b = m[1], c = m[2], d = m[4], e = m[5], f = m[6], g = m[8], h = m[9], i = m[10];
  const A = e * i - f * h, B = -(d * i - f * g), C = d * h - e * g;
  const det = a * A + b * B + c * C || 1e-20;
  const s = 1 / det;
  // inverse (column-major) then transpose
  const inv = [
    A * s, -(b * i - c * h) * s, (b * f - c * e) * s,
    B * s, (a * i - c * g) * s, -(a * f - c * d) * s,
    C * s, -(a * h - b * g) * s, (a * e - b * d) * s,
  ];
  out[0] = inv[0]; out[1] = inv[3]; out[2] = inv[6];
  out[3] = inv[1]; out[4] = inv[4]; out[5] = inv[7];
  out[6] = inv[2]; out[7] = inv[5]; out[8] = inv[8];
  return out;
}

// area-weighted vertex normals (three's computeVertexNormals)
function vertexNormals(pos, idx) {
  const n = pos.length / 3;
  const out = new Float32Array(n * 3);
  const cnt = idx ? idx.length : n;
  for (let t = 0; t + 2 < cnt; t += 3) {
    const a = idx ? idx[t] : t, b = idx ? idx[t + 1] : t + 1, c = idx ? idx[t + 2] : t + 2;
    const ax = pos[a * 3], ay = pos[a * 3 + 1], az = pos[a * 3 + 2];
    const e1x = pos[c * 3] - pos[b * 3], e1y = pos[c * 3 + 1] - pos[b * 3 + 1], e1z = pos[c * 3 + 2] - pos[b * 3 + 2];
    const e2x = ax - pos[b * 3], e2y = ay - pos[b * 3 + 1], e2z = az - pos[b * 3 + 2];
    const nx = e1y * e2z - e1z * e2y, ny = e1z * e2x - e1x * e2z, nz = e1x * e2y - e1y * e2x;
    for (const v of [a, b, c]) { out[v * 3] += nx; out[v * 3 + 1] += ny; out[v * 3 + 2] += nz; }
  }
  for (let i = 0; i < n; i++) {
    const l = Math.hypot(out[i * 3], out[i * 3 + 1], out[i * 3 + 2]) || 1;
    out[i * 3] /= l; out[i * 3 + 1] /= l; out[i * 3 + 2] /= l;
  }
  return out;
}

// ------------------------------------------------------------------ spatial split
// split merged arrays into cell x cell (metres, world xz) pieces by triangle centroid. Every piece
// carries its cell [cx, cz], or null when the group was too small to split (minTris) and spans
// whatever cells it covers.
export function splitCells(data, cell, minTris) {
  const { pos, idx } = data;
  const nt = idx.length / 3;
  if (nt < minTris || nt === 0) return [{ ...data, cell: null }];
  const cells = new Map();
  for (let t = 0; t < nt; t++) {
    const a = idx[t * 3] * 3, b = idx[t * 3 + 1] * 3, c = idx[t * 3 + 2] * 3;
    const cx = Math.floor((pos[a] + pos[b] + pos[c]) / 3 / cell);
    const cz = Math.floor((pos[a + 2] + pos[b + 2] + pos[c + 2]) / 3 / cell);
    const key = (cx + 2048) * 4096 + (cz + 2048);
    let rec = cells.get(key);
    if (!rec) cells.set(key, (rec = { cx, cz, tris: [] }));
    rec.tris.push(t);
  }
  if (cells.size < 2) {
    const r = cells.values().next().value;
    return [{ ...data, cell: [r.cx, r.cz] }];
  }
  const remap = new Int32Array(pos.length / 3).fill(-1);
  const out = [];
  for (const { cx, cz, tris } of cells.values()) {
    const used = [];
    const nidx = new Uint32Array(tris.length * 3);
    for (let k = 0; k < tris.length; k++) {
      const t = tris[k];
      for (let j = 0; j < 3; j++) {
        const vi = idx[t * 3 + j];
        if (remap[vi] < 0) { remap[vi] = used.length; used.push(vi); }
        nidx[k * 3 + j] = remap[vi];
      }
    }
    const n = used.length;
    const sub = { pos: new Float32Array(n * 3), nrm: new Float32Array(n * 3), uv: new Float32Array(n * 2), col: new Float32Array(n * 3), idx: nidx, cell: [cx, cz] };
    if (data.pal) sub.pal = new Uint8Array(n);
    for (let k = 0; k < n; k++) {
      const vi = used[k];
      for (let c = 0; c < 3; c++) {
        sub.pos[k * 3 + c] = data.pos[vi * 3 + c];
        sub.nrm[k * 3 + c] = data.nrm[vi * 3 + c];
        sub.col[k * 3 + c] = data.col[vi * 3 + c];
      }
      sub.uv[k * 2] = data.uv[vi * 2];
      sub.uv[k * 2 + 1] = data.uv[vi * 2 + 1];
      if (data.pal) sub.pal[k] = data.pal[vi];
      remap[vi] = -1;
    }
    out.push(sub);
  }
  return out;
}

// position-only split (shadow casters): [{ pos, idx, cell }]
export function splitCellsPos(data, cell) {
  const { pos, idx } = data;
  const nt = idx.length / 3;
  const cells = new Map();
  for (let t = 0; t < nt; t++) {
    const a = idx[t * 3] * 3, b = idx[t * 3 + 1] * 3, c = idx[t * 3 + 2] * 3;
    const cx = Math.floor((pos[a] + pos[b] + pos[c]) / 3 / cell);
    const cz = Math.floor((pos[a + 2] + pos[b + 2] + pos[c + 2]) / 3 / cell);
    const key = (cx + 2048) * 4096 + (cz + 2048);
    let rec = cells.get(key);
    if (!rec) cells.set(key, (rec = { cx, cz, tris: [] }));
    rec.tris.push(t);
  }
  const remap = new Int32Array(pos.length / 3).fill(-1);
  const out = [];
  for (const { cx, cz, tris } of cells.values()) {
    const used = [];
    const nidx = new Uint32Array(tris.length * 3);
    for (let k = 0; k < tris.length; k++) {
      for (let j = 0; j < 3; j++) {
        const vi = idx[tris[k] * 3 + j];
        if (remap[vi] < 0) { remap[vi] = used.length; used.push(vi); }
        nidx[k * 3 + j] = remap[vi];
      }
    }
    const p = new Float32Array(used.length * 3);
    used.forEach((vi, k) => { p[k * 3] = pos[vi * 3]; p[k * 3 + 1] = pos[vi * 3 + 1]; p[k * 3 + 2] = pos[vi * 3 + 2]; remap[vi] = -1; });
    const box = bounds(p);
    const sx = (box[0] + box[3]) / 2, sy = (box[1] + box[4]) / 2, sz = (box[2] + box[5]) / 2;
    let r2 = 0;
    for (let i = 0; i < p.length; i += 3) r2 = Math.max(r2, (p[i] - sx) ** 2 + (p[i + 1] - sy) ** 2 + (p[i + 2] - sz) ** 2);
    out.push({ pos: p, idx: used.length < 65536 ? Uint16Array.from(nidx) : nidx, cell: [cx, cz], box, sphere: [sx, sy, sz, Math.sqrt(r2)] });
  }
  return out;
}

// ------------------------------------------------------------------ GPU-ready piece
// compact: normals as normalised int8x4, colours as unorm8x4 (4-byte aligned formats every
// backend takes natively), 16-bit indices when they fit. 28 instead of 44 bytes per vertex.
// The colour's alpha byte is 255, or the palette index of a merged flat material.
export function finishPiece(p, compact) {
  const n = p.pos.length / 3;
  const box = bounds(p.pos);
  const cx = (box[0] + box[3]) / 2, cy = (box[1] + box[4]) / 2, cz = (box[2] + box[5]) / 2;
  let r2 = 0;
  for (let i = 0; i < n; i++) {
    const dx = p.pos[i * 3] - cx, dy = p.pos[i * 3 + 1] - cy, dz = p.pos[i * 3 + 2] - cz;
    const d = dx * dx + dy * dy + dz * dz;
    if (d > r2) r2 = d;
  }
  const out = { pos: p.pos, uv: p.uv, box, sphere: [cx, cy, cz, Math.sqrt(r2)], verts: n, tris: p.idx.length / 3, cell: p.cell || null };
  if (compact) {
    const nrm = new Int8Array(n * 4), col = new Uint8Array(n * 4);
    for (let i = 0; i < n; i++) {
      for (let c = 0; c < 3; c++) {
        nrm[i * 4 + c] = Math.max(-127, Math.min(127, Math.round(p.nrm[i * 3 + c] * 127)));
        col[i * 4 + c] = Math.max(0, Math.min(255, Math.round(p.col[i * 3 + c] * 255)));
      }
      col[i * 4 + 3] = p.pal ? p.pal[i] : 255;
    }
    out.nrm = nrm; out.col = col;
    out.idx = n < 65536 ? Uint16Array.from(p.idx) : p.idx;
  } else {
    out.nrm = p.nrm; out.col = p.col; out.idx = p.idx;
  }
  out.bytes = out.pos.byteLength + out.nrm.byteLength + out.uv.byteLength + out.col.byteLength + out.idx.byteLength;
  return out;
}

export function bounds(pos) {
  const b = [Infinity, Infinity, Infinity, -Infinity, -Infinity, -Infinity];
  for (let i = 0; i < pos.length; i += 3) {
    const x = pos[i], y = pos[i + 1], z = pos[i + 2];
    if (x < b[0]) b[0] = x; if (y < b[1]) b[1] = y; if (z < b[2]) b[2] = z;
    if (x > b[3]) b[3] = x; if (y > b[4]) b[4] = y; if (z > b[5]) b[5] = z;
  }
  return b;
}

// ------------------------------------------------------------------ ground height field
// Lowest upward-facing surface (normal.y > 0.5, by winding) under every cell centre, among the
// given triangles, accepted only below `cutoff` (the single-GLB city needs +3 m to skip roofs;
// a ground-only GLB needs none). Equivalent to the old per-cell downward raycast, but a
// triangle rasteriser: O(triangles + covered cells) instead of a BVH query per cell. Holes
// (under buildings, outside the model) are filled by push-pull over a mip pyramid.
export function heightField(pos, idx, box, { cell = 1, cutoff = Infinity, maxRes = 2048, margin = 2 } = {}) {
  const t0 = performance.now();
  const ext = Math.max(box[3] - box[0], box[5] - box[2]) + 2 * margin;
  cell = Math.max(cell, Math.ceil((ext / maxRes) * 8) / 8);
  const minX = Math.floor(box[0]) - margin, minZ = Math.floor(box[2]) - margin;
  const W = Math.min(maxRes, Math.ceil((box[3] + margin - minX) / cell));
  const H = Math.min(maxRes, Math.ceil((box[5] + margin - minZ) / cell));
  const h = new Float32Array(W * H).fill(Infinity);
  const nt = idx.length / 3;
  for (let t = 0; t < nt; t++) {
    const a = idx[t * 3] * 3, b = idx[t * 3 + 1] * 3, c = idx[t * 3 + 2] * 3;
    const ax = pos[a], ay = pos[a + 1], az = pos[a + 2];
    const bx = pos[b], by = pos[b + 1], bz = pos[b + 2];
    const cx = pos[c], cy = pos[c + 1], cz = pos[c + 2];
    // normal (b - a) x (c - a): y component vs length
    const e1x = bx - ax, e1y = by - ay, e1z = bz - az, e2x = cx - ax, e2y = cy - ay, e2z = cz - az;
    const nx = e1y * e2z - e1z * e2y, ny = e1z * e2x - e1x * e2z, nz = e1x * e2y - e1y * e2x;
    const nl = Math.hypot(nx, ny, nz);
    if (!(nl > 0) || ny / nl <= 0.5) continue;
    if (Math.min(ay, by, cy) >= cutoff) continue;
    // 2D barycentrics in xz
    const d = (bz - cz) * (ax - cx) + (cx - bx) * (az - cz);
    if (Math.abs(d) < 1e-12) continue;
    const i0 = Math.max(0, Math.ceil((Math.min(ax, bx, cx) - minX) / cell - 0.5));
    const i1 = Math.min(W - 1, Math.floor((Math.max(ax, bx, cx) - minX) / cell - 0.5));
    const j0 = Math.max(0, Math.ceil((Math.min(az, bz, cz) - minZ) / cell - 0.5));
    const j1 = Math.min(H - 1, Math.floor((Math.max(az, bz, cz) - minZ) / cell - 0.5));
    const eps = -1e-6;
    for (let j = j0; j <= j1; j++) {
      const pz = minZ + (j + 0.5) * cell;
      for (let i = i0; i <= i1; i++) {
        const px = minX + (i + 0.5) * cell;
        const l1 = ((bz - cz) * (px - cx) + (cx - bx) * (pz - cz)) / d;
        const l2 = ((cz - az) * (px - cx) + (ax - cx) * (pz - cz)) / d;
        const l3 = 1 - l1 - l2;
        if (l1 < eps || l2 < eps || l3 < eps) continue;
        const y = l1 * ay + l2 * by + l3 * cy;
        const k = j * W + i;
        if (y < cutoff && y < h[k]) h[k] = y;
      }
    }
  }
  const tRaster = performance.now() - t0;
  fillHoles(h, W, H);
  return { h, W, H, minX, minZ, cell, ms: { raster: Math.round(tRaster), total: Math.round(performance.now() - t0) } };
}

// push-pull: average valid cells down a pyramid, then fill invalid cells from the coarser level
function fillHoles(h, W, H) {
  const levels = [{ v: h, w: Float32Array.from(h, (x) => (x === Infinity ? 0 : 1)), W, H }];
  for (const L of levels) if (L.v === h) for (let k = 0; k < h.length; k++) if (h[k] === Infinity) h[k] = 0;
  while (levels[levels.length - 1].W > 1 || levels[levels.length - 1].H > 1) {
    const P = levels[levels.length - 1];
    const w2 = Math.max(1, Math.ceil(P.W / 2)), h2 = Math.max(1, Math.ceil(P.H / 2));
    const v = new Float32Array(w2 * h2), w = new Float32Array(w2 * h2);
    for (let j = 0; j < P.H; j++) for (let i = 0; i < P.W; i++) {
      const k = j * P.W + i, kk = (j >> 1) * w2 + (i >> 1);
      v[kk] += P.v[k] * P.w[k];
      w[kk] += P.w[k];
    }
    for (let k = 0; k < v.length; k++) { if (w[k] > 0) v[k] /= w[k]; w[k] = Math.min(1, w[k]); }
    levels.push({ v, w, W: w2, H: h2 });
  }
  if (levels[levels.length - 1].w[0] === 0) return;   // nothing valid at all
  for (let l = levels.length - 2; l >= 0; l--) {
    const L = levels[l], C = levels[l + 1];
    for (let j = 0; j < L.H; j++) for (let i = 0; i < L.W; i++) {
      const k = j * L.W + i;
      if (L.w[k] >= 1) continue;
      // bilinear from the coarse level (cell centres at (i + 0.5) / 2 - 0.5)
      const fx = Math.min(Math.max((i + 0.5) / 2 - 0.5, 0), C.W - 1), fz = Math.min(Math.max((j + 0.5) / 2 - 0.5, 0), C.H - 1);
      const i0 = Math.floor(fx), j0 = Math.floor(fz), i1 = Math.min(i0 + 1, C.W - 1), j1 = Math.min(j0 + 1, C.H - 1);
      const u = fx - i0, t = fz - j0;
      const c = (C.v[j0 * C.W + i0] * (1 - u) + C.v[j0 * C.W + i1] * u) * (1 - t) + (C.v[j1 * C.W + i0] * (1 - u) + C.v[j1 * C.W + i1] * u) * t;
      L.v[k] = L.w[k] > 0 ? L.v[k] * L.w[k] + c * (1 - L.w[k]) : c;
      L.w[k] = 1;
    }
  }
}
