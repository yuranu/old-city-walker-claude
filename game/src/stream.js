// Sector streaming. The city is a set of chunks (one GLB each):
//   always  ground, walls, context: loaded at start, resident forever
//   lo      every sector's massing LOD: loaded at start, resident, hidden while its hi is shown
//   hi      a sector's full detail: streams in within rIn of the player (distance to the
//           sector bounds), out beyond rOut
// A pool of workers does fetch, merge, split and the collision BVH (chunk.worker.js). The main
// thread only wraps the arrays and spreads the rest over frames through a small task pump:
// mesh creation, GPU upload (a 1x1 warm-up render, a few MB per frame), program compiles for
// materials nobody has drawn yet, then the swap: hi shown, lo hidden and the sector's collision
// switched from lo to hi in the same frame (everything is already on the GPU, so no pop and no
// gap). Unloading swaps back first, then disposes geometry and releases the materials.
// Inside a resident sector, render cells (96 m) farther than rCell from the camera show the
// matching cells of the sector's lo instead (per-cell LOD), so "hi near, lo far" holds within a
// sector too; collision stays full detail for the whole sector.
// Draw-call and triangle budget (the iGPU / ANGLE backend is CPU-bound on submission):
//  - untextured palette materials draw as two merged materials, picked per vertex from a palette
//    (library.buildFlat); the lo draws that way too, its textures baked into vertex colours
//  - always-resident chunks keep a baked flat copy per cell, drawn beyond rFar
//  - one merged position-only shadow caster per render cell (LAYER_SHADOW) instead of one per
//    material; cut-outs and props cast themselves
//  - per-frame distance rules (_distanceCull): AO prepass within rAO, props drawn within rProps
//    (tiny ones rTiny), prop shadows within rPropShadow / rTinyShadow, nothing casts beyond rCast;
//    nodes may carry extras.draw_dist (m) from the build
// When the page is hidden (rAF paused) the pump keeps going on a MessageChannel loop, so
// teleports, loadAll() and the benches work in background tabs too.
// A base or LOD chunk that fails to load is retried a few times (the build may be rewriting it);
// start() fails if the base still is not in. A sector's bounds grow to the extent of what it
// loaded (the build may give a sector geometry outside its plan bounds, e.g. stairs); until its
// full detail has been in once, unsure() counts it as possibly reaching spots outside every plan.
//
// Manifest (sectors.json, written by pipeline/write_manifest.py; paths relative to it):
//   { "version": 1, "materials": "base/materials.glb",          palette: every material by name
//     "always": ["base/ground.glb", "base/walls.glb", ...],     resident; *ground* -> height field
//     "ground": "base/ground.glb",                              optional, overrides the guess
//     "stream": { "r_in": 150, "r_out": 220 },                  optional
//     "sectors": [{ "id", "name", "bounds": [x0, y0, x1, y1],   local plan frame (x east, y north)
//                   "hi", "lo", "tris_hi", "tris_lo" }] }
// GLBs other than the palette carry name-only placeholder materials; nodes with extras.nocol stay
// out of collision.
import * as THREE from 'three';
import { MeshBVH } from 'three-mesh-bvh';
import { LAYER_NO_AO, LAYER_FAR, LAYER_SHADOW, RENDER_ORDER } from './world.js';
import { U } from './materials.js';

export const STREAM_DEFAULTS = {
  rIn: 150, rOut: 220,      // metres to the sector bounds
  rHold: 40,                // a teleport holds the player until sectors this close are in
  retries: 3,               // base and LOD chunks: attempts after a failed load (2, 4, 8 s apart)
  workers: Math.min(4, Math.max(2, Math.floor((navigator.hardwareConcurrency || 4) / 4))),
  cell: 96,                 // sector render cells (m): frustum culling and the per-cell LOD swap
  cellBase: 192, minTris: 16000,   // always-resident chunks: coarser cells, small groups unsplit (384 m: -60 calls, +0.4M tris: worse)
  lod: true, rCell: 140,    // resident sectors: cells beyond rCell (m, from the camera) show the LOD
  mergeFlat: true,          // untextured palette materials draw as two merged materials
  bakeLo: true,             // ... and so does the LOD, its textures baked into vertex colours
  farLod: true, rFar: 170,  // always-resident chunks: baked flat copy per cell beyond rFar (m)
  farGround: false,         // ... the ground too
  shadowProxy: true,        // one merged depth-only caster per render cell instead of one per material
  rAO: 90,                  // AO prepass only within this distance (m)
  rProps: 120,              // small props (nocol) are drawn within this distance (m)
  rPropShadow: 50,          // ... and cast shadows within this one
  rCast: 210,               // nothing farther casts shadows (shadow range 170 m + sun-ward reach)
  tinySize: 1.5,            // props smaller than this (m, node diagonal) are "tiny":
  rTiny: 50, rTinyShadow: 20,   // ... drawn within rTiny, casting within rTinyShadow
  compact: true,            // int8 normals, unorm8 colours, 16-bit indices where possible
  uploadBytes: 4 << 20,     // GPU upload per pump step (~3 ms on an iGPU)
  budget: 4,                // ms of main-thread work per frame (more while someone waits)
  freeArrays: true,         // drop CPU copies of render attributes once uploaded
};

function freeArray() { this.array = null; }

// cells of a sector in either representation: { hi: meshes, lo: meshes, box: [x0, z0, x1, z1] }
function cellUnion(hi, lo) {
  const map = new Map();
  for (const [which, c] of [['hi', hi], ['lo', lo]]) {
    for (const [k, r] of c.cells) {
      let u = map.get(k);
      if (!u) map.set(k, (u = { hi: [], lo: [], box: [Infinity, Infinity, -Infinity, -Infinity], near: undefined }));
      u[which].push(...r.meshes);
      u.box[0] = Math.min(u.box[0], r.box[0]); u.box[1] = Math.min(u.box[1], r.box[1]);
      u.box[2] = Math.max(u.box[2], r.box[2]); u.box[3] = Math.max(u.box[3], r.box[3]);
    }
  }
  return [...map.values()];
}

// near cells (camera within R of the cell box, 15 m hysteresis) show u.hi, far ones u.lo
function swapCells(union, x, z, R, force) {
  const H = 15;
  let nearCells = 0;
  for (const u of union) {
    const b = u.box;
    const d = Math.hypot(Math.max(b[0] - x, 0, x - b[2]), Math.max(b[1] - z, 0, z - b[3]));
    let near = u.near;
    if (near === undefined || force) near = d < R;
    else if (near && d > R + H) near = false;
    else if (!near && d < R) near = true;
    if (near !== u.near || force) {
      u.near = near;
      for (const m of u.hi) m.visible = near;
      for (const m of u.lo) m.visible = !near;
    }
    if (near) nearCells++;
  }
  return nearCells;
}

const distRect = (x, y, b) => Math.hypot(Math.max(b[0] - x, 0, x - b[2]), Math.max(b[1] - y, 0, y - b[3]));

class Chunk {
  constructor(kind, url, sector = null) {
    this.kind = kind;          // 'always' | 'lo' | 'hi'
    this.url = url;
    this.sector = sector;
    this.key = kind === 'always' ? 'base:' + url.split('/').pop() : `${kind}:${sector.id}`;
    this.state = 'new';        // queued -> fetch -> build -> active | dropped | failed
    this.progress = 0;
    this.priority = 0;
    this.group = null;
    this.bvh = null;
    this.colBox = null;
    this.matNames = [];
    this.acquired = false;
    this.stats = null;
    this.gpuBytes = 0;
    this.colBytes = 0;
    this.height = null;        // height-field options for ground chunks
    this.cancelled = false;
    this.t0 = performance.now();
    this.ms = null;
    this.done = new Promise((r) => (this._done = r));
  }
}

export class Streamer {
  constructor({ pipe, library, collider, opts = {} }) {
    this.pipe = pipe;
    this.renderer = pipe.renderer;
    this.scene = pipe.scene;
    this.camera = pipe.camera;
    this.lib = library;
    this.collider = collider;
    this.opts = { ...STREAM_DEFAULTS, ...opts };
    this.manifest = null;
    this.sectors = [];
    this.always = [];
    this.queue = [];
    this.jobs = new Map();
    this.jobSeq = 0;
    this._tracked = new Set();     // every chunk mesh, for the per-frame distance rules
    this._cullDirty = true;
    this.tasks = [];
    this.taskMs = {};          // per step label: count, max and total ms (hitch hunting)
    this.waiters = new Set();
    this.holds = new Set();
    this.enabled = true;
    this.started = false;
    this.lastFrame = 0;
    this.pos = { x: 0, y: 0 };
    this.ground = null;
    this.log = [];
    this.events = [];          // recent swaps for the overlay / tests
    this.workers = [];
    for (let i = 0; i < this.opts.workers; i++) {
      const w = new Worker(new URL('./chunk.worker.js', import.meta.url), { type: 'module' });
      w.busy = null;
      w.onmessage = (e) => {
        const t0 = performance.now();
        this._onMessage(w, e.data);
        const d = performance.now() - t0;
        const k = this.taskMs[e.data.type === 'done' ? 'message' : 'progress'] ||= { n: 0, max: 0, sum: 0 };
        k.n++; k.sum += d; if (d > k.max) k.max = d;
      };
      w.onerror = (e) => console.error('chunk worker error', e.message || e);
      this.workers.push(w);
    }
    // pump driver when rAF is not running (hidden page, or before the main loop starts)
    this._mc = new MessageChannel();
    this._spinning = false;
    this._mc.port1.onmessage = () => {
      this._spinning = false;
      if (performance.now() - this.lastFrame < 250) return;     // the frame loop pumps
      this.update(this.pos.x, this.pos.y);
      this.pump(30);
      if (this.tasks.length) this.kick();
    };
    this._timer = setInterval(() => { if (this.tasks.length || this.waiters.size) this.kick(); }, 500);
    // warm-up: a 1x1 render with a trivial material uploads vertex/index buffers
    this._warmRT = new THREE.WebGLRenderTarget(1, 1, { depthBuffer: false });
    this._warmScene = new THREE.Scene();
    this._warmScene.overrideMaterial = new THREE.MeshBasicMaterial();
    this._warmCam = new THREE.PerspectiveCamera();
    this._warmCam.layers.enableAll();
  }

  // ---------------------------------------------------------------- manifest
  // url: sectors.json (null = the single legacy city.glb). Returns the normalised manifest.
  async open(url, legacyUrl = '/city.glb') {
    const base = new URL(url || legacyUrl, location.href);
    if (!url) {
      this.manifest = { url: base.href, legacy: true, materials: null, always: [base.href], ground: [base.href], groundCutoff: 3, sectors: [] };
      return this.manifest;
    }
    const r = await fetch(base.href, { cache: 'no-store' });
    if (!r.ok) throw new Error(`${url}: HTTP ${r.status}`);
    const j = await r.json();                 // the dev server answers index.html for missing files
    if (!j || !Array.isArray(j.sectors)) throw new Error(`${url}: not a sector manifest`);
    // every build stamps the manifest; the stamp goes on each GLB URL so a rebuilt sector is never
    // served from the browser cache next to a fresh base (mismatched ground and buildings)
    const stamp = j.build ? `?b=${j.build}` : '';
    const abs = (p) => (p ? new URL(p, base).href + stamp : null);
    const always = (j.always || []).map(abs);
    let ground = j.ground ? [].concat(j.ground).map(abs) : always.filter((u) => /ground/i.test(u.split('/').pop()));
    const st = j.stream || {};
    if (st.r_in) this.opts.rIn = +st.r_in;
    if (st.r_out) this.opts.rOut = +st.r_out;
    this.manifest = {
      url: base.href, legacy: false, version: j.version, materials: abs(j.materials), always, ground, groundCutoff: Infinity,
      sectors: j.sectors.map((s) => ({ id: s.id, name: s.name || s.id, bounds: s.bounds, hiUrl: abs(s.hi), loUrl: abs(s.lo), trisHi: s.tris_hi || 0, trisLo: s.tris_lo || 0 })),
    };
    return this.manifest;
  }

  // ---------------------------------------------------------------- start
  // palette, then always + lo + the hi sectors around (x, y); resolves when all are resident
  async start(x, y) {
    const m = this.manifest;
    this.pos = { x, y };
    const t0 = performance.now();
    if (m.materials) {
      this.paletteProgress = { loaded: 0, total: 0 };
      const buf = await fetchWithProgress(m.materials, this.paletteProgress);
      await this.lib.addGLB(buf, m.materials.replace(/[^/]*$/, ''), null, { pinned: true, source: 'palette' });
      if (this.opts.compact && this.opts.mergeFlat) this.lib.buildFlat();
    }
    const tPalette = performance.now();
    const initial = [];
    for (const url of m.always) {
      const c = new Chunk('always', url);
      if (m.ground.includes(url) && !this.always.some((a) => a.height)) c.height = { cutoff: m.groundCutoff, cell: 1, maxRes: 2048 };
      this.always.push(c);
      this._request(c, -2e4);
      initial.push(c.done);
    }
    for (const s of m.sectors) {
      // bounds: the manifest's, grown to what the sector's chunks turn out to hold (_activate)
      const sec = { ...s, plan: s.bounds, bounds: [...s.bounds], seen: false, hi: null, lo: null, err: null, retryAt: 0, pinned: false, dist: Infinity, swaps: 0 };
      this.sectors.push(sec);
      if (s.loUrl) {
        sec.lo = new Chunk('lo', s.loUrl, sec);
        this._request(sec.lo, -1.5e4);
        initial.push(sec.lo.done);
      }
    }
    this.update(x, y);
    await Promise.all(initial);
    // without the base (the ground carries every street surface) there is nothing to walk on
    const lost = this.always.filter((c) => c.state !== 'active');
    if (lost.length) throw new Error(`base not loaded: ${lost.map((c) => `${c.url.split('/').pop()} (${c.error})`).join(', ')}`);
    const tBase = performance.now();
    await this.ensure(x, y, this.opts.rIn);
    if (!this.ground) this._setGround(null);
    this.started = true;
    this.timing = { palette: Math.round(tPalette - t0), base: Math.round(tBase - tPalette), hi: Math.round(performance.now() - tBase), total: Math.round(performance.now() - t0) };
    return this.timing;
  }

  // download progress of the start-up set, 0..1
  startProgress() {
    let got = 0, tot = 0;
    const add = (c) => {
      if (!c) return;
      const t = c.total || (c.state === 'active' ? c.loaded || 1 : 0);
      tot += t || 1e6;
      got += c.state === 'active' ? t || 1e6 : c.loaded || 0;
    };
    this.always.forEach(add);
    for (const s of this.sectors) { add(s.lo); if (s.hi) add(s.hi); }
    if (this.paletteProgress) { tot += this.paletteProgress.total || 1e6; got += this.paletteProgress.loaded; }
    return tot ? got / tot : 0;
  }

  // ---------------------------------------------------------------- per frame
  frame(x, y) {
    this.lastFrame = performance.now();
    this.update(x, y);
    this.pump(this.holds.size || this.waiters.size ? 12 : this.opts.budget);
  }

  update(x, y) {
    this.pos.x = x; this.pos.y = y;
    const now = performance.now();
    const { rIn, rOut } = this.opts;
    for (const s of this.sectors) {
      s.dist = distRect(x, y, s.bounds);
      const state = this.state(s);
      let want = s.pinned;
      s.held = false;
      for (const h of this.holds) if (distRect(h.x, h.y, s.bounds) <= h.r) want = s.held = true;
      if (!want && this.enabled) want = s.dist <= rIn || (state !== 'lo' && state !== 'error' && s.dist <= rOut);
      if (!want && !this.enabled) want = state !== 'lo' && state !== 'error';    // frozen
      if (want) {
        if (state === 'lo' || (state === 'error' && now > s.retryAt)) this._loadHi(s);
      } else if (s.hi) this._unloadHi(s);
    }
    // what a held player waits for goes first, then by distance
    for (const c of this.queue) if (c.kind === 'hi') c.priority = c.sector.dist - (c.sector.held ? 1e4 : 0);
    this._dispatch();
    this._checkWaiters();
  }

  state(s) {
    if (!s.hi) return s.err ? 'error' : 'lo';
    return { queued: 'queued', fetch: 'loading', build: 'building', active: 'hi' }[s.hi.state] || 'lo';
  }

  // ---------------------------------------------------------------- waiting
  // resolves when every sector within r of (x, y) is resident in full detail (or failed);
  // the sectors are kept wanted until then. An abort (signal: AbortSignal, e.g. a newer
  // teleport) lets go of them at once and resolves with false.
  ensure(x, y, r = this.opts.rHold, signal = null) {
    if (signal?.aborted) return Promise.resolve(false);
    const h = { x, y, r };
    const drop = () => this.holds.delete(h);
    this.holds.add(h);
    signal?.addEventListener('abort', drop, { once: true });
    return this.waitFor(() => this.sectors.every((s) => distRect(x, y, s.bounds) > r || ['hi', 'error'].includes(this.state(s))), signal)
      .finally(() => { drop(); signal?.removeEventListener('abort', drop); });
  }

  pending(x, y, r = this.opts.rHold) {
    return this.sectors.filter((s) => distRect(x, y, s.bounds) <= r && this.state(s) !== 'hi').map((s) => s.id);
  }

  // sectors whose geometry may reach (x, y) although their bounds do not come close: inside a
  // sector's plan bounds whatever is built belongs to that sector, but outside every plan (beyond
  // the walls) the build gives geometry to the nearest sector, up to ~80 m past its bounds
  // (stairs). Until a sector's full detail has been in once, that reach is unknown: the ones
  // within rIn of here
  unsure(x, y) {
    if (this.sectors.some((s) => distRect(x, y, s.plan) === 0)) return [];
    return this.sectors.filter((s) => !s.seen && distRect(x, y, s.bounds) <= this.opts.rIn).map((s) => s.id);
  }

  // resolves with true once pred() holds, or with false when signal aborts first
  waitFor(pred, signal = null) {
    if (pred()) return Promise.resolve(true);
    if (signal?.aborted) return Promise.resolve(false);
    return new Promise((resolve) => {
      const w = { pred, resolve: () => { signal?.removeEventListener('abort', w.abort); resolve(true); } };
      w.abort = () => { this.waiters.delete(w); resolve(false); };
      this.waiters.add(w);
      signal?.addEventListener('abort', w.abort, { once: true });
      this.update(this.pos.x, this.pos.y);
      this.kick();
    });
  }

  _checkWaiters() {
    for (const w of this.waiters) if (w.pred()) { this.waiters.delete(w); w.resolve(); }
  }

  // pin sectors in full detail regardless of distance (ids: array, 'all', or null to unpin)
  force(ids) {
    const set = ids === 'all' ? null : new Set(ids || []);
    for (const s of this.sectors) s.pinned = ids === 'all' ? true : set.has(s.id);
    this.update(this.pos.x, this.pos.y);
    const pinned = this.sectors.filter((s) => s.pinned);
    return this.waitFor(() => pinned.every((s) => ['hi', 'error'].includes(this.state(s)))).then(() => pinned.map((s) => s.id));
  }

  // ---------------------------------------------------------------- jobs
  // queue a chunk; callers dispatch once they have queued everything (lowest priority first)
  _request(c, priority) {
    c.state = 'queued';
    c.priority = priority;
    this.queue.push(c);
  }

  _dispatch() {
    for (const w of this.workers) {
      if (w.busy || !this.queue.length) continue;
      let bi = 0;
      for (let i = 1; i < this.queue.length; i++) if (this.queue[i].priority < this.queue[bi].priority) bi = i;
      const c = this.queue.splice(bi, 1)[0];
      c.state = 'fetch';
      c.tFetch = performance.now();
      const id = ++this.jobSeq;
      this.jobs.set(id, c);
      w.busy = c;
      const o = this.opts;
      w.postMessage({
        type: 'job', id, url: c.url,
        opts: {
          ...this._split(c), compact: o.compact, known: this._known(),
          height: c.height, allMaterials: this.manifest.legacy, flat: this.lib.flatTable,
          bake: (c.kind === 'lo' && o.bakeLo) || (c.kind === 'always' && o.farLod) ? this.lib.bakeTable : null,
          bakeAll: c.kind === 'lo' && o.bakeLo,
          shadowProxy: o.shadowProxy && !this.manifest.legacy && c.kind !== 'lo', noProxy: this._noProxy(),
          tinySize: this.manifest.legacy ? 0 : o.tinySize,
        },
      });
    }
  }

  // render-cell split per chunk kind: sectors always per cell (the LOD swap needs it; the lo
  // also keeps a whole copy), the base coarser; the single legacy city.glb as it always was
  _split(c) {
    const o = this.opts;
    if (this.manifest.legacy) return { cell: o.cell, minTris: o.minTris };
    // (the ground is practically one material: a far copy would not save draws, only memory)
    if (c.kind === 'always') return o.farLod && this.lib.bakeTable && (!c.height || o.farGround) ? { cell: o.cellBase, minTris: 0, far: true } : { cell: o.cellBase, minTris: o.minTris };
    return { cell: o.cell, minTris: o.lod ? 0 : o.minTris, whole: c.kind === 'lo' };
  }

  // material names a worker may leave out of its material extract: only the palette's (pinned
  // for the session). A name that some resident chunk registered from its own GLB can be
  // disposed before this job's result arrives (that chunk unloads), so the job brings its own.
  _known() {
    const out = [];
    for (const e of this.lib.entries.values()) if (e.pinned) out.push(e.name);
    return out;
  }

  // materials whose geometry must keep casting itself (alpha-tested cut-outs) or not at all
  _noProxy() {
    if (!this.__noProxy) {
      this.__noProxy = [];
      for (const e of this.lib.entries.values()) if (e.flags && (e.flags.cutout || !e.flags.castShadow || e.mat?.transparent)) this.__noProxy.push(e.name);
    }
    return this.__noProxy;
  }

  _onMessage(w, msg) {
    const c = this.jobs.get(msg.id);
    if (!c) return;
    if (msg.type === 'progress') {
      c.loaded = msg.loaded; c.total = msg.total;
      c.progress = msg.total ? msg.loaded / msg.total : 0;
      return;
    }
    this.jobs.delete(msg.id);
    w.busy = null;
    this._dispatch();
    if (msg.type === 'error') this._fail(c, msg.message);
    else this._finalize(c, msg.result).catch((e) => this._fail(c, e && e.stack || String(e)));
    this.kick();
  }

  _fail(c, message) {
    console.warn(`chunk ${c.key} failed:`, message);
    c.error = String(message).split('\n')[0];
    this.log.push({ t: Math.round(performance.now()), key: c.key, error: c.error });
    this._dispose(c);
    // the base and the LODs stay resident for the whole session: try again a few times (the build
    // may be rewriting the file); whoever waits on c.done keeps waiting meanwhile
    if (c.kind !== 'hi' && !this.destroyed && (c.tries = (c.tries || 0) + 1) <= this.opts.retries) {
      c.state = 'retry';
      c.loaded = c.total = 0;
      setTimeout(() => { if (!this.destroyed) { this._request(c, c.priority); this._dispatch(); } }, 1000 * 2 ** c.tries);
      return;
    }
    c.state = 'failed';
    c._done(false);
    const s = c.sector;
    if (c.kind === 'hi' && s && s.hi === c) {
      s.hi = null;
      s.err = String(message).split('\n')[0];
      s.retryAt = performance.now() + 15000;
    }
    this._checkWaiters();
  }

  // ---------------------------------------------------------------- main-thread pipeline
  async _finalize(c, res) {
    if (c.cancelled) return this._drop(c);
    c.state = 'build';
    c.stats = res.stats;
    c.tWorker = performance.now();
    // materials: the palette has everything; a name it lacks takes this GLB's own definition.
    // Hold a reference before any await, so no other chunk's unload disposes one meanwhile.
    c.matNames = res.usedMaterials.filter((n) => this.lib.has(n));
    this.lib.acquire(c.matNames);
    c.acquired = true;
    if (res.materials) {
      const names = Object.keys(res.materials.index);
      const fresh = names.filter((n) => !this.lib.has(n));     // the rest is held above already
      if (fresh.length && !this.manifest.legacy) console.warn(`${c.key}: material(s) not in the palette, using the GLB's own placeholder: ${fresh.join(', ')}`);
      await this.lib.addGLB(res.materials.glb, c.url.replace(/[^/]*$/, ''), names, { source: c.url });
    }
    for (const n of res.usedMaterials) {
      if (c.matNames.includes(n)) continue;
      if (!this.lib.has(n)) this.lib.addDefault(n);
      this.lib.acquire([n]);
      c.matNames.push(n);
    }
    await Promise.all(res.usedMaterials.map((n) => this.lib.get(n).ready));
    if (c.cancelled) return this._drop(c);
    // textures of materials new to the GPU, one per step
    while (this.started && this.lib.uploads.length) {
      await this.step(() => { const t = this.lib.uploads.shift(); if (t) this.renderer.initTexture(t); }, 'texture');
    }
    // mesh creation is spread over frames too (a big sector has thousands of pieces)
    const it = this._build(c, res);
    let r;
    do {
      r = await this.step(() => it.next(), 'build');
      if (c.cancelled) return this._drop(c);
    } while (!r.done);
    const batches = r.value;
    if (this.started) {
      for (const b of batches) {
        await this.step(() => { if (!c.cancelled) this._warm(b); }, 'upload');
        if (c.cancelled) return this._drop(c);
      }
      const fresh = c.matNames.filter((n) => !this.lib.get(n)?.compiled);
      if (fresh.length) {
        if (performance.now() - this.lastFrame < 250) await this.renderer.compileAsync(c.group, this.camera, this.scene);
        else this.renderer.compile(c.group, this.camera, this.scene);
        for (const n of fresh) { const e = this.lib.get(n); if (e) e.compiled = true; }
        if (c.cancelled) return this._drop(c);
      }
    }
    await this.step(() => this._activate(c), 'activate');
  }

  // meshes + collision from the worker's arrays; returns upload batches. Meshes are indexed by
  // render cell (c.cells), for the per-cell LOD swap inside a resident sector; a lo chunk also
  // keeps its unsplit meshes (c.whole) for when the whole sector is far.
  * _build(c, res) {
    const group = new THREE.Group();
    group.name = c.key;
    group.matrixAutoUpdate = false;
    c.group = group;                // set now: a cancel mid-build disposes what exists
    const batches = [];
    let batch = [], bytes = 0;
    c.cells = new Map();
    c.spanning = [];
    c.whole = [];
    const batching = this.started && c.kind === 'hi';
    let made = 0;
    const add = (g, e, p) => {
      made++;
      const ms = this._mesh(g, e, p);
      for (const m of ms) group.add(m);
      if (batching) {
        batch.push(ms[ms.length - 1]);
        bytes += p.bytes;
        if (bytes >= this.opts.uploadBytes) { batches.push(batch); batch = []; bytes = 0; }
      }
      return ms;
    };
    const proxied = res.shadow && res.shadow.length ? new Set(this._noProxy()) : null;
    const { flatTable, bakeTable } = this.lib;
    for (const g of res.groups) {
      const e = this.lib.get(g.name);
      // a base chunk's far copy only has what draws flat: merged flat materials and textured ones
      // with a baked palette slot. What it lacks (cut-outs such as foliage and grilles, a texture
      // the bake could not read) stays drawn at any distance instead of swapping with its cell,
      // and casts its own shadow (the cell's proxy swaps out with it). Props (nocol) and draw_dist
      // pieces are left out of the far copy on purpose and swap out with their cell: beyond rFar
      // they are past their own draw distance (rProps and the build's draw_dist stay within it)
      const farCopy = (!!flatTable && g.name.startsWith('__flat')) || !!(bakeTable && bakeTable[g.name]);
      const keep = !!(res.far && res.far.length) && (e.flags.cutout || (!farCopy && !g.nocol && !g.drawDist));
      for (const p of g.pieces) {
        const ms = add(g, e, p);
        if (proxied && !keep && !g.nocol && !g.drawDist && !proxied.has(g.name)) for (const m of ms) m.userData.oc.cast = false, m.castShadow = false;
        if (p.cell && !keep) {
          const key = p.cell[0] + ',' + p.cell[1];
          let rec = c.cells.get(key);
          if (!rec) c.cells.set(key, (rec = { meshes: [], box: [Infinity, Infinity, -Infinity, -Infinity] }));
          rec.meshes.push(...ms);
          const b = p.box;
          rec.box[0] = Math.min(rec.box[0], b[0]); rec.box[1] = Math.min(rec.box[1], b[2]);
          rec.box[2] = Math.max(rec.box[2], b[3]); rec.box[3] = Math.max(rec.box[3], b[5]);
        } else c.spanning.push(...ms);
        if (!g.whole) c.whole.push(...ms);          // a single piece is its own whole
        if (made >= 60 && this.started) { made = 0; yield; }
      }
      for (const p of g.whole || []) c.whole.push(...add(g, e, p));
    }
    // shadow-only casters, one per cell, switched with the cell's full-detail meshes
    for (const p of res.shadow || []) {
      const geom = new THREE.BufferGeometry();
      geom.setAttribute('position', new THREE.BufferAttribute(p.pos, 3));
      geom.setIndex(new THREE.BufferAttribute(p.idx, 1));
      const b = p.box, sp = p.sphere;
      geom.boundingBox = new THREE.Box3(new THREE.Vector3(b[0], b[1], b[2]), new THREE.Vector3(b[3], b[4], b[5]));
      geom.boundingSphere = new THREE.Sphere(new THREE.Vector3(sp[0], sp[1], sp[2]), sp[3]);
      if (this.opts.freeArrays) { geom.attributes.position.onUpload(freeArray); geom.index.onUpload(freeArray); }
      const m = new THREE.Mesh(geom, this._shadowMat ||= new THREE.MeshBasicMaterial({ name: 'shadow-proxy', side: THREE.DoubleSide, colorWrite: false }));
      m.name = 'shadow proxy';
      m.matrixAutoUpdate = false;
      m.castShadow = true;
      m.receiveShadow = false;
      m.layers.set(LAYER_SHADOW);
      m.userData.oc = { shadowOnly: true, cast: true };
      if (!this.manifest.legacy) this._tracked.add(m);
      group.add(m);
      if (++made >= 60 && this.started) { made = 0; yield; }
      if (batching) {
        batch.push(m);
        bytes += p.pos.byteLength + p.idx.byteLength;
        if (bytes >= this.opts.uploadBytes) { batches.push(batch); batch = []; bytes = 0; }
      }
      const key = p.cell[0] + ',' + p.cell[1];
      let rec = c.cells.get(key);
      if (!rec) c.cells.set(key, (rec = { meshes: [], box: [b[0], b[2], b[3], b[5]] }));
      rec.meshes.push(m);
    }
    // always-resident chunks: baked flat copy per cell for beyond rFar
    c.farCells = null;
    if (res.far && res.far.length) {
      c.farCells = new Map();
      for (const g of res.far) {
        const e = this.lib.get(g.name);
        for (const p of g.pieces) {
          const ms = add(g, e, p);
          for (const m of ms) { m.visible = false; m.userData.oc.far = true; }
          const key = p.cell[0] + ',' + p.cell[1];
          let rec = c.farCells.get(key);
          if (!rec) c.farCells.set(key, (rec = { meshes: [], box: [Infinity, Infinity, -Infinity, -Infinity] }));
          rec.meshes.push(...ms);
          const b = p.box;
          rec.box[0] = Math.min(rec.box[0], b[0]); rec.box[1] = Math.min(rec.box[1], b[2]);
          rec.box[2] = Math.max(rec.box[2], b[3]); rec.box[3] = Math.max(rec.box[3], b[5]);
        }
      }
      c.farUnion = cellUnion(c, { cells: c.farCells });
    }
    if (batch.length) batches.push(batch);
    c.gpuBytes = res.stats.gpuBytes;
    if (res.collision) {
      const col = res.collision;
      const g = new THREE.BufferGeometry();
      g.setAttribute('position', new THREE.BufferAttribute(col.pos, 3));
      const b = col.box;
      g.boundingBox = new THREE.Box3(new THREE.Vector3(b[0], b[1], b[2]), new THREE.Vector3(b[3], b[4], b[5]));
      c.bvh = MeshBVH.deserialize(col.bvh, g, { setIndex: true });
      c.colBox = g.boundingBox;
      c.colBytes = col.pos.byteLength + (col.bvh.index ? col.bvh.index.byteLength : 0) + col.bvh.roots.reduce((a, r) => a + r.byteLength, 0);
    }
    if (res.height) c.heightField = res.height;
    c.box = res.box;
    return batches;
  }

  // [depth twin,] mesh for one piece
  _mesh(g, e, p) {
    const f = e.flags;
    const geom = new THREE.BufferGeometry();
    const compactN = p.nrm instanceof Int8Array, compactC = p.col instanceof Uint8Array;
    geom.setAttribute('position', new THREE.BufferAttribute(p.pos, 3));
    geom.setAttribute('normal', new THREE.BufferAttribute(p.nrm, compactN ? 4 : 3, compactN));
    geom.setAttribute('uv', new THREE.BufferAttribute(p.uv, 2));
    geom.setAttribute('color', new THREE.BufferAttribute(p.col, compactC ? 4 : 3, compactC));
    geom.setIndex(new THREE.BufferAttribute(p.idx, 1));
    const b = p.box, s = p.sphere;
    geom.boundingBox = new THREE.Box3(new THREE.Vector3(b[0], b[1], b[2]), new THREE.Vector3(b[3], b[4], b[5]));
    geom.boundingSphere = new THREE.Sphere(new THREE.Vector3(s[0], s[1], s[2]), s[3]);
    if (this.opts.freeArrays) {
      for (const a of Object.values(geom.attributes)) a.onUpload(freeArray);
      geom.index.onUpload(freeArray);
    }
    const mesh = new THREE.Mesh(geom, e.mat);
    mesh.name = g.name + (g.nocol ? ' (nocol)' : '');
    mesh.castShadow = f.castShadow;
    mesh.receiveShadow = true;
    mesh.matrixAutoUpdate = false;
    if (!f.ao || g.nocol) mesh.layers.set(LAYER_NO_AO);
    // distance rules applied per frame (_distanceCull)
    const track = !this.manifest.legacy;   // the single legacy city renders exactly as it always did
    mesh.userData.oc = { ao: f.ao && !g.nocol, prop: g.nocol, tiny: !!g.tiny, drawDist: g.drawDist || 0, cast: f.castShadow };
    if (track) this._tracked.add(mesh);
    if (!e.depth) return [mesh];
    const twin = new THREE.Mesh(geom, e.depth);
    twin.name = mesh.name + ' (z)';
    twin.matrixAutoUpdate = false;
    twin.layers.set(LAYER_NO_AO);
    twin.renderOrder = RENDER_ORDER.cutoutDepth;
    mesh.renderOrder = RENDER_ORDER.cutout;
    twin.userData.oc = { ao: false, prop: g.nocol, tiny: !!g.tiny, drawDist: g.drawDist || 0, cast: false };
    if (track) this._tracked.add(twin);
    return [twin, mesh];
  }

  // ---------------------------------------------------------------- per-cell LOD
  // Inside a sector whose full detail is resident, render cells farther than rCell from the
  // camera show the sector's massing LOD for that cell instead (hysteresis 15 m). With no hi
  // shown, the LOD is drawn whole (a few draw calls per sector).
  lod() {
    const p = this.camera.position;
    for (const s of this.sectors) this._lod(s, p.x, p.z, false);
    for (const c of this.always) if (c.farUnion && c.state === 'active') swapCells(c.farUnion, p.x, p.z, this.opts.rFar, false);
    this._distanceCull(p);
  }

  // Distance rules per piece (bounding sphere), re-evaluated when the camera moved a metre or
  // a chunk came in: the AO prepass only gets geometry within rAO (GTAO's ~1 m radius is
  // sub-pixel beyond; those pixels read as unoccluded); small props (nocol: furniture, roof
  // clutter, cables, signs, decals) are not drawn beyond rProps and cast shadows only within
  // rPropShadow; nothing farther than rCast casts a shadow (the shadow range is 170 m).
  _distanceCull(p) {
    if (!this._cullDirty && this._cullAt && p.distanceToSquared(this._cullAt) < 1) return;
    this._cullDirty = false;
    (this._cullAt ||= new THREE.Vector3()).copy(p);
    const { rAO, rProps, rPropShadow, rCast, rTiny, rTinyShadow } = this.opts;
    const AO = 1, NO_AO = 1 << LAYER_NO_AO, FAR = 1 << LAYER_FAR;
    for (const m of this._tracked) {
      const u = m.userData.oc, bs = m.geometry.boundingSphere;
      const d = bs.center.distanceTo(p) - bs.radius;
      if (u.shadowOnly) { m.castShadow = d < rCast; continue; }
      if ((u.prop && d > (u.tiny ? rTiny : rProps)) || (u.drawDist && d > u.drawDist)) { m.layers.mask = FAR; m.castShadow = false; continue; }
      m.layers.mask = u.ao && d < rAO ? AO : NO_AO;
      m.castShadow = u.cast && d < (u.tiny ? rTinyShadow : u.prop ? rPropShadow : rCast);
    }
  }

  _lod(s, x, z, force) {
    const lo = s.lo && s.lo.state === 'active' ? s.lo : null;
    const hi = s.hi && s.hi.state === 'active' ? s.hi : null;
    if (!hi) {
      if (lo && s.lodMode !== 'whole') {
        lo.group.visible = true;
        for (const r of lo.cells.values()) for (const m of r.meshes) m.visible = false;
        for (const m of lo.spanning) m.visible = false;
        for (const m of lo.whole) m.visible = true;
        s.lodMode = 'whole';
      }
      return;
    }
    if (!lo || !this.opts.lod) {
      if (s.lodMode !== 'hi') {
        hi.group.traverse((o) => { if (o.isMesh) o.visible = true; });
        if (lo) lo.group.visible = false;
        s.lodMode = 'hi';
      }
      return;
    }
    if (s.lodMode !== 'cells' || !s.cellUnion) {
      lo.group.visible = true;
      for (const m of lo.whole) m.visible = false;
      for (const m of lo.spanning) m.visible = false;
      s.cellUnion = cellUnion(hi, lo);
      s.lodMode = 'cells';
      force = true;
    }
    s.nearCells = swapCells(s.cellUnion, x, z, this.opts.rCell, force);
  }

  // upload a batch of meshes' buffers: render them once into a 1x1 target with a basic material
  _warm(meshes) {
    const r = this.renderer, sc = this._warmScene;
    const parent = meshes[0].parent;
    for (const m of meshes) { m.frustumCulled = false; sc.add(m); }
    const prev = r.getRenderTarget();
    r.setRenderTarget(this._warmRT);
    r.render(sc, this._warmCam);
    r.setRenderTarget(prev);
    for (const m of meshes) { m.frustumCulled = true; parent.add(m); }
  }

  _activate(c) {
    if (c.cancelled) return this._drop(c);
    const s = c.sector;
    c.group.updateMatrixWorld(true);
    this.scene.add(c.group);
    if (c.kind === 'always') {
      this.collider.set(c.key, c.bvh, c.colBox);
      if (c.heightField) this._setGround(c.heightField);
    } else if (c.kind === 'lo') {
      const hiOn = s.hi && s.hi.state === 'active';
      if (!hiOn) this.collider.set('sec:' + s.id, c.bvh, c.colBox);
    } else {
      this.collider.set('sec:' + s.id, c.bvh || (s.lo && s.lo.bvh), c.bvh ? c.colBox : s.lo && s.lo.colBox);
      s.swaps++;
      s.seen = true;             // its bounds (grown below) now cover everything it holds
      this.events.push({ t: Math.round(performance.now()), id: s.id, in: true, ms: Math.round(performance.now() - c.t0) });
      if (this.events.length > 50) this.events.shift();
    }
    c.state = 'active';
    this._cullDirty = true;
    if (s && c.box && c.box[0] <= c.box[3]) {
      // the manifest's bounds come from the plan; the build may give a sector geometry beyond
      // them (stairs outside the walls go to the nearest sector): streaming, holds and pending()
      // measure to what the sector actually holds from now on (three (x, z) = (east, -north))
      const b = s.bounds, x = c.box;
      b[0] = Math.min(b[0], x[0]); b[1] = Math.min(b[1], -x[5]); b[2] = Math.max(b[2], x[3]); b[3] = Math.max(b[3], -x[2]);
    }
    if (s) {                     // the swap happens now, before this frame renders
      s.lodMode = null;
      s.cellUnion = null;
      this._lod(s, this.camera.position.x, this.camera.position.z, true);
    }
    c.ms = { worker: c.stats.ms, main: Math.round(performance.now() - c.tWorker), total: Math.round(performance.now() - c.t0) };
    c._done(true);
    this._checkWaiters();
  }

  _loadHi(s) {
    if (!s.hiUrl) { s.err = 'no hi file'; s.retryAt = Infinity; return; }
    s.err = null;
    s.hi = new Chunk('hi', s.hiUrl, s);
    this._request(s.hi, s.dist);
  }

  _unloadHi(s) {
    const c = s.hi;
    s.hi = null;
    if (c.state === 'queued') {
      this.queue.splice(this.queue.indexOf(c), 1);
      c.state = 'dropped';
      c._done(false);
      return;
    }
    if (c.state !== 'active') { c.cancelled = true; return; }   // the pipeline drops it
    s.lodMode = null;
    s.cellUnion = null;
    this._lod(s, this.camera.position.x, this.camera.position.z, true);   // lo drawn whole again
    if (s.lo && s.lo.bvh) this.collider.set('sec:' + s.id, s.lo.bvh, s.lo.colBox);
    else this.collider.delete('sec:' + s.id);
    this.events.push({ t: Math.round(performance.now()), id: s.id, in: false });
    this._dispose(c);
    c.state = 'dropped';
  }

  _drop(c) {
    this._dispose(c);
    c.state = 'dropped';
    c._done(false);
    this._checkWaiters();
  }

  // stop the workers and let go of every chunk (start() failed and the caller opens another
  // city with a new Streamer); the library's materials are the caller's to clear
  destroy() {
    this.destroyed = true;
    for (const w of this.workers) w.terminate();
    this.workers = [];
    clearInterval(this._timer);
    this._mc.port1.onmessage = null;
    this._mc.port1.close();
    for (const c of [...this.always, ...this.sectors.flatMap((s) => [s.lo, s.hi])]) {
      if (!c) continue;
      c.cancelled = true;
      this._dispose(c);
      this.collider.delete(c.kind === 'always' ? c.key : 'sec:' + c.sector.id);
    }
    this.queue = [];
    this.jobs.clear();
    this.tasks = [];
    this.waiters.clear();
    this.holds.clear();
    this._tracked.clear();
    this._warmRT.dispose();
  }

  _dispose(c) {
    if (c.group) {
      if (c.group.parent) c.group.parent.remove(c.group);
      const seen = new Set();
      c.group.traverse((o) => {
        this._tracked.delete(o);
        if (o.geometry && !seen.has(o.geometry)) { seen.add(o.geometry); o.geometry.dispose(); }
      });
      c.group = null;
    }
    if (c.acquired) { this.lib.release(c.matNames); c.acquired = false; }
    c.bvh = null;
  }

  _setGround(hf) {
    const old = U.ocGround.value;
    if (!hf) {
      const tex = new THREE.DataTexture(new Uint16Array([0]), 1, 1, THREE.RedFormat, THREE.HalfFloatType);
      tex.needsUpdate = true;
      U.ocGround.value = tex;
      U.ocGroundXf.value.set(0, 0, 1, 1);
      this.ground = { tex, W: 1, H: 1, minX: 0, minZ: 0, cell: 1, at: () => 0, ms: { total: 0 } };
    } else {
      const { h, half, W, H, minX, minZ, cell } = hf;
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
      this.ground = { tex, W, H, minX, minZ, cell, at, ms: hf.ms };
    }
    if (old && old !== this.ground.tex && old.isDataTexture && old.image.width > 1) old.dispose();
  }

  // compile every registry material's program up front (with the chunk vertex layout), so no
  // sector that streams in later needs a shader compile
  compilePalette() {
    const c = this.opts.compact;
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(9), 3));
    g.setAttribute('normal', c ? new THREE.BufferAttribute(new Int8Array(12), 4, true) : new THREE.BufferAttribute(new Float32Array(9), 3));
    g.setAttribute('uv', new THREE.BufferAttribute(new Float32Array(6), 2));
    g.setAttribute('color', c ? new THREE.BufferAttribute(new Uint8Array(12), 4, true) : new THREE.BufferAttribute(new Float32Array(9), 3));
    g.setIndex([0, 1, 2]);
    const grp = new THREE.Group();
    for (const e of this.lib.entries.values()) {
      if (!e.mat) continue;
      grp.add(new THREE.Mesh(g, e.mat));
      if (e.depth) grp.add(new THREE.Mesh(g, e.depth));
    }
    this.renderer.compile(grp, this.camera, this.scene);
    for (const e of this.lib.entries.values()) e.compiled = true;
    g.dispose();
  }

  // ---------------------------------------------------------------- task pump
  step(fn, label = 'step') {
    return new Promise((resolve, reject) => {
      this.tasks.push({ fn, resolve, reject, label });
      this.kick();
    });
  }

  pump(budget) {
    const t0 = performance.now();
    let n = 0;
    while (this.tasks.length) {
      if (n && performance.now() - t0 > budget) break;
      const t = this.tasks.shift();
      n++;
      const ts = performance.now();
      try { t.resolve(t.fn()); } catch (e) { t.reject(e); }
      const d = performance.now() - ts;
      const k = this.taskMs[t.label] ||= { n: 0, max: 0, sum: 0 };
      k.n++; k.sum += d; if (d > k.max) k.max = d;
    }
    this.lastPumpMs = performance.now() - t0;
    if (this.lastPumpMs > (this.maxPumpMs || 0)) this.maxPumpMs = this.lastPumpMs;
    return n;
  }

  kick() {
    if (this._spinning || performance.now() - this.lastFrame < 250) return;
    this._spinning = true;
    this._mc.port2.postMessage(0);
  }

  // ---------------------------------------------------------------- introspection
  list() {
    return this.sectors.map((s) => ({
      id: s.id, name: s.name, state: this.state(s), dist: Math.round(s.dist), pinned: s.pinned, bounds: s.bounds,
      tris: s.hi?.stats?.tris ?? s.trisHi, gpuMB: s.hi?.state === 'active' ? +(s.hi.gpuBytes / 1048576).toFixed(1) : 0,
      progress: s.hi && s.hi.state === 'fetch' ? +s.hi.progress.toFixed(2) : undefined,
      ms: s.hi?.ms || undefined, swaps: s.swaps, error: s.err || undefined,
    }));
  }

  memory() {
    let gpu = 0, col = 0, chunks = 0;
    const add = (c) => { if (c && c.state === 'active') { gpu += c.gpuBytes; col += c.colBytes; chunks++; } };
    this.always.forEach(add);
    for (const s of this.sectors) { add(s.lo); add(s.hi); }
    return { chunks, geometryMB: +(gpu / 1048576).toFixed(1), collisionMB: +(col / 1048576).toFixed(1), ...this.lib.stats(), renderer: { ...this.renderer.info.memory } };
  }

  // two lines for the F3 overlay
  summary() {
    if (!this.manifest) return '';
    const mem = this.memory();
    const short = (id) => id.replace(/_.*/, '');
    if (!this.sectors.length) {
      return `city ${this.manifest.legacy ? '(single city.glb)' : ''}  geometry ${mem.geometryMB.toFixed(0)} MB  collision ${mem.collisionMB.toFixed(0)} MB\n` +
        `textures ${mem.textures} (${mem.texMB.toFixed(0)} MB)  materials ${mem.materials}`;
    }
    const hi = [], busy = [], err = [];
    for (const s of this.sectors) {
      const st = this.state(s);
      if (st === 'hi') hi.push(short(s.id));
      else if (st === 'loading') busy.push(s.hi.progress >= 1 ? `${short(s.id)} merge` : `${short(s.id)} ${Math.round(100 * s.hi.progress)}%`);
      else if (st === 'building') busy.push(`${short(s.id)} build`);
      else if (st === 'queued') busy.push(`${short(s.id)} …`);
      else if (st === 'error') err.push(short(s.id));
    }
    return `sectors hi ${hi.length}/${this.sectors.length} [${hi.join(' ')}]` + (busy.length ? `  loading ${busy.join(', ')}` : '') +
      (err.length ? `  failed ${err.join(' ')}` : '') + (this.enabled ? '' : '  (frozen)') + '\n' +
      `geometry ${mem.geometryMB.toFixed(0)} MB  collision ${mem.collisionMB.toFixed(0)} MB  textures ${mem.textures} (${mem.texMB.toFixed(0)} MB)`;
  }
}

async function fetchWithProgress(url, prog) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`${url}: HTTP ${r.status}`);
  prog.total = +r.headers.get('content-length') || 0;
  if (!r.body) { const b = await r.arrayBuffer(); prog.loaded = prog.total = b.byteLength; return b; }
  const reader = r.body.getReader();
  const parts = [];
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    parts.push(value);
    prog.loaded += value.length;
  }
  const out = new Uint8Array(prog.loaded);
  let o = 0;
  for (const p of parts) { out.set(p, o); o += p.length; }
  prog.total = prog.loaded;
  const head = new TextDecoder().decode(out.subarray(0, 4));
  if (head !== 'glTF') throw new Error(`${url}: not a GLB`);
  return out.buffer;
}
