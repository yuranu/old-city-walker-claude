import * as THREE from 'three';
import { Pipeline, LIGHT } from './render.js';
import { U as SHARED_UNIFORMS } from './materials.js';
import { GpuTimer, DynRes, PerfOverlay } from './perf.js';
import { Player } from './player.js';
import { Hud } from './hud.js';
import { Library } from './library.js';
import { Collider } from './collider.js';
import { Streamer } from './stream.js';

const q = new URLSearchParams(location.search);
const canvas = document.getElementById('view');
const pipe = new Pipeline(canvas);
const { renderer, scene, camera, sun } = pipe;
const DEFAULT_FOV = 70;
if (q.get('ao') === '0') pipe.useAO = false;
if (q.has('pr')) { pipe.pixelRatio = THREE.MathUtils.clamp(+q.get('pr') || 1, 0.25, 3); }

const hud = new Hud();
const loading = document.getElementById('loading');
const perfEl = document.getElementById('perf');
const overlay = new PerfOverlay(perfEl);
const gpuTimer = new GpuTimer(renderer.getContext());
// which GPU the browser gave us (integrated vs discrete / PRIME offload) - shown on the start
// screen and in the F3 panel
const GPU = gpuInfo(renderer.getContext());
console.info('GPU:', GPU.raw);
document.getElementById('gpu').textContent = `GPU: ${GPU.name}${GPU.kind ? ` (${GPU.kind})` : ''}`;
overlay.gpu = GPU;
const dynres = new DynRes(pipe);
// fixed resolution for reproducible screenshots, or when a pixel ratio was asked for
if (q.get('dynres') === '0' || q.has('pr') || q.has('cam') || q.get('clean') === '1') dynres.enabled = false;

function gpuInfo(gl) {
  const ext = gl.getExtension('WEBGL_debug_renderer_info');
  const raw = String(ext ? gl.getParameter(ext.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER));
  const name = raw.replace(/^ANGLE \((.*)\)$/, '$1').replace(/, (OpenGL|Direct3D|Vulkan|Metal).*$/i, '')
    .replace(/\((R|TM)\)/gi, '').replace(/\s+/g, ' ').trim();
  const kind = /\b(Arc|NVIDIA|GeForce|RTX|GTX|Quadro|Radeon RX|Radeon Pro)\b/i.test(raw) ? 'discrete'
    : /\b(Iris|UHD|HD Graphics|Radeon Graphics|Vega|Apple M\d|Mali|Adreno)\b/i.test(raw) ? 'integrated'
      : /SwiftShader|llvmpipe|Software/i.test(raw) ? 'software' : '';
  return { raw, name, kind };
}

function setClean(on) {
  document.body.classList.toggle('clean', !!on);
}
if (q.get('clean') === '1') setClean(true);
if (q.get('perf') === '1') overlay.toggle(true);

async function loadCams() {
  try {
    const r = await fetch('/eval_cams.json', { cache: 'no-store' });
    if (!r.ok) return {};
    const j = await r.json();          // the dev server answers index.html for missing files
    return (j && j.cams) || {};
  } catch {
    return {};
  }
}

// ------------------------------------------------------------------ city: sectors or legacy
// ?sectors=<dir or .json> picks a manifest (e.g. ?sectors=mock), ?sectors=0 the single city.glb;
// by default /sectors.json when it is complete (palette present), else city.glb.
// ?rin= ?rout= ?rhold= stream radii (m), ?rcell= per-cell LOD radius, ?lod=0 no per-cell LOD,
// ?workers=, ?compact=0, ?chunk= ?chunkmin= render cells
const streamOpts = {};
for (const [k, o] of [['rin', 'rIn'], ['rout', 'rOut'], ['rhold', 'rHold'], ['rcell', 'rCell'], ['rao', 'rAO'], ['rprops', 'rProps'],
  ['rps', 'rPropShadow'], ['rcast', 'rCast'], ['rfar', 'rFar'], ['tiny', 'tinySize'], ['rtiny', 'rTiny'], ['rts', 'rTinyShadow'], ['cellbase', 'cellBase'], ['workers', 'workers'], ['chunkmin', 'minTris'], ['budget', 'budget']]) {
  if (q.has(k)) streamOpts[o] = +q.get(k);
}
if (q.has('chunk')) streamOpts.cell = +q.get('chunk') || 1e9;
if (q.get('compact') === '0') streamOpts.compact = false;
if (q.get('lod') === '0') streamOpts.lod = false;
if (q.get('flat') === '0') streamOpts.mergeFlat = false;
if (q.get('bake') === '0') streamOpts.bakeLo = false;
// integrated GPUs: full detail within 100 m instead of 140 (-14% triangles, -50 draw calls)
if (!q.has('rcell') && GPU.kind === 'integrated') streamOpts.rCell = 100;
if (q.get('far') === '0') streamOpts.farLod = false;
if (q.has('farground')) streamOpts.farGround = q.get('farground') !== '0';
if (q.get('sproxy') === '0') streamOpts.shadowProxy = false;
const library = new Library(pipe, Math.min(8, renderer.capabilities.getMaxAnisotropy()));
if (q.get('twins') === '0') library.twins = false;
const collider = new Collider();
const streamer = new Streamer({ pipe, library, collider, opts: streamOpts });

async function exists(url) {
  try {
    const r = await fetch(url, { method: 'HEAD', cache: 'no-store' });
    return r.ok && !/text\/html/.test(r.headers.get('content-type') || '');
  } catch {
    return false;
  }
}

async function openCity() {
  const p = q.get('sectors');
  if (p === '0' || p === 'legacy') return streamer.open(null);
  const url = p ? (p.endsWith('.json') ? p : `/${p.replace(/^\/|\/$/g, '')}/sectors.json`) : '/sectors.json';
  try {
    const m = await streamer.open(url);
    // the build writes the manifest sector by sector: until the palette and the always-resident
    // base are in it, the single city.glb is the playable city
    const incomplete = !m.always.length ? 'no always-resident base (ground, walls)'
      : m.materials && !(await exists(m.materials)) ? `palette ${m.materials} missing` : null;
    if (!p && incomplete) {
      console.warn(`${url}: ${incomplete}, falling back to city.glb (force it with ?sectors=${url.replace(/^\//, '')})`);
      return streamer.open(null);
    }
    return m;
  } catch (e) {
    if (p) throw e;
    console.info('no sector manifest, using city.glb:', e.message);
    return streamer.open(null);
  }
}

async function load() {
  const t0 = performance.now();
  const [manifest, plan, photos, cams] = await Promise.all([
    openCity(),
    fetch('/plan.json').then((r) => r.json()),
    fetch('/photos.json').then((r) => r.json()),
    loadCams(),
  ]);
  // where the player starts decides which sectors load before the loading screen goes
  let start = { x: plan.spawn.p[0], y: plan.spawn.p[1] };
  if (q.has('x')) start = { x: +q.get('x'), y: +q.get('y') };
  else if (q.has('cam') && cams[q.get('cam')]) start = { x: +cams[q.get('cam')].x, y: +cams[q.get('cam')].y };
  const prog = setInterval(() => {
    loading.textContent = `Loading city… ${Math.round(100 * streamer.startProgress())}%`;
  }, 100);
  let timing;
  try {
    timing = await streamer.start(start.x, start.y);
  } finally {
    clearInterval(prog);
  }
  loading.textContent = 'Preparing city…';
  const t1 = performance.now();
  // compile every program up front (palette with the chunk vertex layout, then the scene: main
  // pass, AO prepass, shadow depth) and upload the atlases, to avoid hitches later
  streamer.compilePalette();
  renderer.compile(scene, camera);
  for (const t of library.uploads) renderer.initTexture(t);
  library.uploads.length = 0;
  warmAll();
  loading.textContent = '';
  timing = { ...timing, compile: Math.round(performance.now() - t1), all: Math.round(performance.now() - t0) };
  return { manifest, plan, photos, cams, timing, start };
}

// one frame of everything resident, hidden LOD cells included and nothing culled, into a 1x1
// scissor: uploads every buffer and creates the vertex array objects of all three passes (main,
// shadow, AO), so the first look in any direction does not hitch
function warmAll() {
  const saved = [];
  scene.traverse((o) => { saved.push([o, o.visible, o.frustumCulled]); o.visible = true; o.frustumCulled = false; });
  renderer.setScissor(0, 0, 1, 1);
  renderer.setScissorTest(true);
  pipe.render();
  renderer.setScissorTest(false);
  for (const [o, v, f] of saved) { o.visible = v; o.frustumCulled = f; }
}

const W = await load();
const { plan, photos } = W;
let evalCams = W.cams;
const player = new Player(camera, collider);
player.spawn = [plan.spawn.p[0], plan.spawn.p[1], plan.spawn.heading];
player.onFall = () => { goTo(...player.spawn); };
hud.init(plan, photos);

// start position: ?x=&y=&h=&p= (local metres / compass heading / pitch) or the spec spawn
if (q.has('x')) player.teleport(+q.get('x'), +q.get('y'), +(q.get('h') || 0), +(q.get('p') || 0));
else player.teleport(plan.spawn.p[0], plan.spawn.p[1], plan.spawn.heading);

// teleport, holding the player in place until the sectors around the target are in full
// detail (the massing LOD collides meanwhile, so nothing can be walked through); the latest
// teleport wins
let tpToken = 0;
async function goTo(x, y, heading = null, pitch = 0, r = streamer.opts.rHold) {
  const tok = ++tpToken;
  player.teleport(x, y, heading, pitch);
  streamer.update(x, y);
  if (!streamer.pending(x, y, r).length) { player.held = false; return true; }
  player.held = true;
  await streamer.ensure(x, y, r);
  if (tok !== tpToken) return false;
  player.teleport(x, y, player.heading(), THREE.MathUtils.radToDeg(player.pitch));   // keeps any look-around
  player.held = false;
  return true;
}

// ------------------------------------------------------------------ evaluation cameras
// pose: {x, y (local, east/north), z_eye (eye above the ground under the camera), heading
// (compass deg), pitch (deg up), fov (vertical deg), optional roll (deg), shift_x/shift_y
// (lens shift as a fraction of the frame), z_ground (absolute ground height override)}
let camPose = null;
const baseUpdateProjection = camera.updateProjectionMatrix.bind(camera);
camera.updateProjectionMatrix = function () {
  baseUpdateProjection();
  if (camPose && (camPose.shift_x || camPose.shift_y)) {
    this.projectionMatrix.elements[8] += 2 * (+camPose.shift_x || 0);
    this.projectionMatrix.elements[9] += 2 * (+camPose.shift_y || 0);
    this.projectionMatrixInverse.copy(this.projectionMatrix).invert();
  }
};

function applyCam() {
  const c = camPose;
  camera.position.set(c._x, c._eye, c._z);
  camera.rotation.set(c._pitch, c._yaw, c._roll, 'YXZ');
  camera.updateMatrixWorld();
}

async function useCam(pose) {
  const x = +pose.x, y = +pose.y;
  const heading = +(pose.heading ?? 0), pitch = +(pose.pitch ?? 0);
  // a screenshot wants everything the normal streaming would show from here
  await goTo(x, y, heading, pitch, streamer.opts.rIn);
  // ground under the camera: where a player teleported here would stand (street level first)
  const g = pose.z_ground !== undefined ? +pose.z_ground : player.groundY;
  camPose = {
    ...pose, _x: x, _z: -y, _eye: g + +(pose.z_eye ?? 1.6),
    _yaw: -THREE.MathUtils.degToRad(heading), _pitch: THREE.MathUtils.degToRad(pitch),
    _roll: THREE.MathUtils.degToRad(+(pose.roll ?? 0)),
  };
  camera.fov = +(pose.fov ?? DEFAULT_FOV);
  camera.updateProjectionMatrix();
  applyCam();
}

function releaseCam() {
  if (!camPose) return;
  camPose = null;
  camera.fov = DEFAULT_FOV;
  camera.updateProjectionMatrix();
  player.updateCamera();
}

async function setCam(c) {
  if (c === null || c === undefined || c === false) { releaseCam(); renderOnce(); return null; }
  let pose = typeof c === 'string' ? evalCams[c] : c;
  if (!pose && typeof c === 'string') {
    evalCams = await loadCams();
    pose = evalCams[c];
  }
  if (!pose) {
    console.warn(`setCam: no camera "${c}" in /eval_cams.json`);
    return null;
  }
  await useCam(pose);
  renderOnce();
  return { name: typeof c === 'string' ? c : undefined, ...pose };
}

// ------------------------------------------------------------------ input
const start = document.getElementById('start');
start.addEventListener('click', () => canvas.requestPointerLock());
document.addEventListener('pointerlockchange', () => {
  start.style.display = document.pointerLockElement === canvas ? 'none' : 'flex';
});
document.addEventListener('mousemove', (e) => {
  if (document.pointerLockElement === canvas) {
    if (camPose) releaseCam();
    player.look(e.movementX, e.movementY);
  }
});
addEventListener('keydown', (e) => {
  player.keys.add(e.code);
  if (e.code === 'KeyP') hud.togglePhoto(player);
  if (e.code === 'KeyN') hud.nextPhoto(player);
  if (e.code === 'KeyG') hud.openGoogleMaps(player);
  if (e.code === 'KeyO') pipe.useAO = !pipe.useAO;
  if (e.code === 'F3') { overlay.toggle(); overlay.frame(performance.now(), null, stats()); e.preventDefault(); }
  if (e.code === 'Space' || e.code === 'F3') e.preventDefault();
});
addEventListener('keyup', (e) => player.keys.delete(e.code));
addEventListener('blur', () => player.keys.clear());

// ------------------------------------------------------------------ frame
function renderOnce() {
  if (camPose) applyCam();
  streamer.lod();
  return pipe.render();
}

let lastStats = { gpu: null };
function stats() {
  const i = renderer.info.render;
  return {
    gpu: gpuTimer.last, pr: pipe.pixelRatio, dyn: dynres.enabled, w: canvas.width, h: canvas.height,
    calls: i.calls, tris: i.triangles, ao: pipe.useAO, shadow: sun.shadow.mapSize.x,
  };
}

const MOVE_KEYS = ['KeyW', 'KeyA', 'KeyS', 'KeyD', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'Space'];
const timer = new THREE.Timer();
let lastT = performance.now();
function frame(t) {
  requestAnimationFrame(frame);
  timer.update(t);
  const dt = Math.min(timer.getDelta(), 0.05);
  const now = performance.now();
  const frameMs = now - lastT;
  lastT = now;
  if (camPose && MOVE_KEYS.some((k) => player.keys.has(k))) releaseCam();
  if (!camPose) player.update(dt);
  const pp = player.plan();
  streamer.frame(pp.x, pp.y);
  hud.update(player);
  gpuTimer.begin();
  const drawn = renderOnce();
  gpuTimer.end();
  const gpu = gpuTimer.poll();
  if (drawn) {
    lastStats = stats();
    overlay.frame(now, frameMs, lastStats);
    dynres.update(now, frameMs, gpu);
    if (frameMs > 34 && now - startT > 3000) slowFrames.push({ t: Math.round(now), ms: +frameMs.toFixed(1), pump: +streamer.lastPumpMs.toFixed(1) });
    if (slowFrames.length > 200) slowFrames.shift();
  }
}
const startT = performance.now();
const slowFrames = [];
const longTasks = [];
try {
  new PerformanceObserver((l) => {
    for (const e of l.getEntries()) { longTasks.push({ t: Math.round(e.startTime), ms: Math.round(e.duration) }); if (longTasks.length > 200) longTasks.shift(); }
  }).observe({ type: 'longtask', buffered: false });
} catch { /* not supported */ }
overlay.extra = () => streamer.summary();
requestAnimationFrame(frame);

// ------------------------------------------------------------------ debug / automation hooks
const gl = renderer.getContext();
const px = new Uint8Array(4);
function sync() {
  renderer.setRenderTarget(null);
  gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px);
}
const VIEWS = {
  spawn: [-22, 2, 104, 0], square_west: [22, -2, 75, 0], square_east: [92, 2, 267, 0],
  david_street: [104, 8.5, 90, 0], citadel: [50, 5, 210, 5],
};

window.game = {
  // returns a promise that resolves once the sectors around the target are in (the player is
  // placed at once and held there until then)
  teleport: (x, y, h = 0, p = 0) => {
    releaseCam();
    const done = goTo(x, y, h, p).then(() => { renderOnce(); return window.game.state(); });
    renderOnce();
    return done;
  },
  state: () => ({ ...player.plan(), heading: player.heading(), onGround: player.onGround, held: player.held }),
  // deterministic simulation (works while the tab is hidden and rAF is paused)
  step: (seconds, codes = [], turnDegPerSec = 0) => {
    if (codes.length || turnDegPerSec) releaseCam();
    codes.forEach((c) => player.keys.add(c));
    const n = Math.round(seconds * 60);
    for (let i = 0; i < n; i++) {
      player.yaw -= THREE.MathUtils.degToRad(turnDegPerSec) / 60;
      player.update(1 / 60);
    }
    codes.forEach((c) => player.keys.delete(c));
    const pp = player.plan();
    streamer.update(pp.x, pp.y);
    streamer.kick();
    hud.frame = 0;
    hud.update(player);
    renderOnce();
    overlay.last = 0;
    overlay.frame(performance.now(), null, stats());
    return window.game.state();
  },
  hud,
  player,
  scene,
  sun,
  renderer,
  camera,
  pipeline: pipe,
  light: LIGHT,
  uniforms: SHARED_UNIFORMS,
  get ground() { return streamer.ground; },
  get world() { return { stats: worldStats(), timing: W.timing, bounds: collider.bounds(), manifest: W.manifest.url, legacy: W.manifest.legacy }; },
  // ---- sector streaming
  sectors: () => streamer.list(),
  // every sector in full detail (pinned until forceSectors(null)); resolves with timing + memory
  loadAll: async () => {
    const t0 = performance.now();
    await streamer.force('all');
    return { ms: Math.round(performance.now() - t0), ...streamer.memory() };
  },
  // pin a set of sectors in full detail (e.g. for screenshots); null unpins
  forceSectors: (ids) => streamer.force(ids),
  // resolves when every sector within r metres of (x, y) is in full detail
  ensure: (x, y, r) => streamer.ensure(x, y, r),
  streaming: (o = {}) => {
    if ('enabled' in o) streamer.enabled = !!o.enabled;
    for (const k of ['rIn', 'rOut', 'rHold', 'rCell', 'rAO', 'rProps', 'rPropShadow', 'rCast', 'rFar', 'rTiny', 'rTinyShadow', 'budget', 'uploadBytes']) if (k in o) streamer.opts[k] = +o[k];
    streamer._cullDirty = true;
    if ('lod' in o) streamer.opts.lod = !!o.lod;
    return { enabled: streamer.enabled, ...streamer.opts };
  },
  memory: () => streamer.memory(),
  streamLog: () => ({ events: streamer.events, errors: streamer.log, slowFrames, longTasks, maxPumpMs: streamer.maxPumpMs, taskMs: streamer.taskMs }),
  streamer,
  THREE,
  collider,
  library,
  setAO: (on) => { pipe.useAO = !!on; renderOnce(); },
  // ms per frame, measured synchronously (readPixels forces the GPU to finish), so it works
  // while the tab is hidden; renders n frames back to back at the current pixel ratio
  bench: (n = 20) => {
    renderOnce(); sync();
    const t0 = performance.now();
    for (let i = 0; i < n; i++) renderOnce();
    sync();
    return (performance.now() - t0) / n;
  },
  // bench at the standard viewpoints with AO on and off: {view: {ao, noao, calls, tris}};
  // async: waits at each view for the sectors the normal streaming would show there
  benchViews: async (n = 20, views = VIEWS) => {
    const save = { pos: player.pos.clone(), yaw: player.yaw, pitch: player.pitch, ao: pipe.useAO, cam: camPose };
    const out = {};
    for (const [k, v] of Object.entries(views)) {
      camPose = null;
      await goTo(v[0], v[1], v[2], v[3] || 0, streamer.opts.rIn);
      pipe.useAO = true; const ao = window.game.bench(n);
      const s = stats();
      pipe.useAO = false; const noao = window.game.bench(n);
      out[k] = { ao: +ao.toFixed(2), noao: +noao.toFixed(2), calls: s.calls, tris: s.tris };
    }
    player.pos.copy(save.pos); player.yaw = save.yaw; player.pitch = save.pitch; player.updateCamera();
    pipe.useAO = save.ao; camPose = save.cam;
    renderOnce();
    return { w: canvas.width, h: canvas.height, pr: pipe.pixelRatio, views: out };
  },
  perf: () => ({ ...stats(), fps: 1000 / overlay.dt, frameMs: overlay.dt }),
  // one full frame without rAF (works in hidden tabs): player step with the given keys held,
  // streaming update + pump, render, GPU sync. Returns ms (total) and pump (streaming work).
  simFrame: (dt = 1 / 60, codes = []) => {
    const t0 = performance.now();
    codes.forEach((c) => player.keys.add(c));
    if (codes.length) releaseCam();
    if (!camPose) player.update(dt);
    codes.forEach((c) => player.keys.delete(c));
    const pp = player.plan();
    streamer.frame(pp.x, pp.y);
    const t1 = performance.now();
    renderOnce();
    sync();
    return { ms: performance.now() - t0, pump: t1 - t0, x: pp.x, y: pp.y, z: pp.z, onGround: player.onGround, held: player.held };
  },
  gpu: GPU,
  dynres,
  showPerf: (on = true) => { overlay.toggle(on); overlay.frame(performance.now(), null, stats()); },
  setDynRes: (on) => { dynres.enabled = !!on; if (!on) { pipe.pixelRatio = pipe.maxPR; } renderOnce(); },
  setPixelRatio: (pr) => { dynres.enabled = false; pipe.pixelRatio = pr; renderOnce(); return pipe.pixelRatio; },
  // evaluation cameras from /eval_cams.json (or a pose object); null releases
  setCam,
  cams: () => evalCams,
  reloadCams: async () => (evalCams = await loadCams()),
  clean: (on = true) => { setClean(on); renderOnce(); },
  ready: false,
};

function worldStats() {
  let meshes = 0, tris = 0;
  scene.traverse((o) => {
    if (o.isMesh && o.visible && o.geometry.index && o.parent && o.parent.visible && o.parent.name.includes(':') && !/\(z\)$/.test(o.name)) {
      meshes++; tris += o.geometry.index.count / 3;
    }
  });
  return { meshes, tris, ...streamer.memory() };
}

if (q.has('cam')) await setCam(q.get('cam'));
renderOnce();
window.game.ready = true;
