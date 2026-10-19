import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { Pipeline, LIGHT } from './render.js';
import { U as SHARED_UNIFORMS } from './materials.js';
import { buildWorld, buildGround } from './world.js';
import { GpuTimer, DynRes, PerfOverlay } from './perf.js';
import { Player } from './player.js';
import { Hud } from './hud.js';

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

const tick = () => new Promise((r) => setTimeout(r, 0));

async function load() {
  const [gltf, plan, photos, cams] = await Promise.all([
    new GLTFLoader().loadAsync('/city.glb', (e) => {
      if (e.total) loading.textContent = `Loading city… ${Math.round((100 * e.loaded) / e.total)}%`;
    }),
    fetch('/plan.json').then((r) => r.json()),
    fetch('/photos.json').then((r) => r.json()),
    loadCams(),
  ]);
  loading.textContent = 'Preparing city…';
  await tick();
  const t0 = performance.now();
  const world = buildWorld(gltf, {
    anisotropy: Math.min(8, renderer.capabilities.getMaxAnisotropy()),
    ...(q.has('chunk') ? { chunk: +q.get('chunk') || 1e9 } : {}),
    ...(q.has('chunkmin') ? { chunkMinTris: +q.get('chunkmin') } : {}),
  });
  scene.add(world.city);
  world.city.traverse((o) => {
    const m = o.material;
    if (o.isMesh && m?.isMeshStandardMaterial && (m.metalness >= 0.3 || m.roughness < 0.35)) pipe.addReflective(m);
  });
  const t1 = performance.now();
  const ground = buildGround(world.bvh, world.bounds, 1);
  const t2 = performance.now();
  // compile every program up front (main pass, AO prepass, shadow depth) to avoid hitches
  renderer.compile(scene, camera);
  loading.textContent = '';
  const timing = { merge: Math.round(t1 - t0), ground: ground.ms, compile: Math.round(performance.now() - t2) };
  return { ...world, ground, plan, photos, cams, timing };
}

const W = await load();
const { bvh, plan, photos, ground } = W;
let evalCams = W.cams;
const player = new Player(camera, bvh);
hud.init(plan, photos);

// start position: ?x=&y=&h=&p= (local metres / compass heading / pitch) or the spec spawn
if (q.has('x')) player.teleport(+q.get('x'), +q.get('y'), +(q.get('h') || 0), +(q.get('p') || 0));
else player.teleport(plan.spawn.p[0], plan.spawn.p[1], plan.spawn.heading);

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

function useCam(pose) {
  const x = +pose.x, y = +pose.y;
  const heading = +(pose.heading ?? 0), pitch = +(pose.pitch ?? 0);
  player.teleport(x, y, heading, pitch);
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
  useCam(pose);
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
  hud.update(player);
  gpuTimer.begin();
  const drawn = renderOnce();
  gpuTimer.end();
  const gpu = gpuTimer.poll();
  if (drawn) {
    lastStats = stats();
    overlay.frame(now, frameMs, lastStats);
    dynres.update(now, frameMs, gpu);
  }
}
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
  teleport: (x, y, h = 0, p = 0) => { releaseCam(); player.teleport(x, y, h, p); renderOnce(); },
  state: () => ({ ...player.plan(), heading: player.heading(), onGround: player.onGround }),
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
  ground,
  world: { stats: W.stats, timing: W.timing, bounds: W.bounds },
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
  // bench at the standard viewpoints with AO on and off: {view: {ao, noao, calls, tris}}
  benchViews: (n = 20, views = VIEWS) => {
    const save = { pos: player.pos.clone(), yaw: player.yaw, pitch: player.pitch, ao: pipe.useAO, cam: camPose };
    const out = {};
    for (const [k, v] of Object.entries(views)) {
      camPose = null;
      player.teleport(...v);
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

if (q.has('cam')) await setCam(q.get('cam'));
renderOnce();
window.game.ready = true;
