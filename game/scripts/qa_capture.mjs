// QA capture: render a list of viewpoints in the real game (headless Chrome over the DevTools
// protocol, no extra packages) and save, per view: the normal frame, a frame from 1 cm away (z-fighting
// flips between textures, ordinary surfaces barely move) and a sky-keyed frame (magenta = sky seen
// below the horizon = a hole). AO is off so frames are deterministic.
//
//   node game/scripts/qa_capture.mjs --views build/qa/<run>/views.json --out build/qa/<run> [--gpu arc]
//
// views.json: [{id, x, y, z_eye, heading, pitch, fov}] in the local frame (z_eye above the ground found
// under the camera, like eval cams). Needs the dev server (npm --prefix game run dev).
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const arg = (k, d) => { const i = process.argv.indexOf('--' + k); return i > 0 ? process.argv[i + 1] : d; };
const views = JSON.parse(fs.readFileSync(arg('views'), 'utf8'));
const out = arg('out');
const [w, h] = arg('size', '960x640').split('x').map(Number);
const base = arg('url', 'http://127.0.0.1:5173/');
const gpu = arg('gpu', 'arc');
fs.mkdirSync(out, { recursive: true });
const port = 9800 + Math.floor(Math.random() * 150);
const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'ocw-qa-'));
const env = { ...process.env };
if (gpu === 'arc') env.DRI_PRIME = '1'; else delete env.DRI_PRIME;
const chrome = spawn(process.env.CHROME || 'google-chrome-stable', [
  '--headless=new', `--remote-debugging-port=${port}`, `--user-data-dir=${dir}`, `--window-size=${w},${h}`,
  '--ignore-gpu-blocklist', '--enable-gpu', '--use-angle=gl', '--no-first-run', '--no-default-browser-check',
  '--disable-background-timer-throttling', '--disable-renderer-backgrounding', 'about:blank',
], { env, stdio: ['ignore', 'ignore', 'pipe'] });
let errLog = '';
chrome.stderr.on('data', (d) => { errLog += d; });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function json(p) {
  for (let i = 0; i < 150; i++) {
    try { const r = await fetch(`http://127.0.0.1:${port}${p}`); if (r.ok) return await r.json(); } catch { /* starting */ }
    await sleep(100);
  }
  throw new Error('chrome did not start: ' + errLog.slice(-500));
}
let ws, seq = 0;
const pending = new Map();
const send = (method, params = {}) => new Promise((res, rej) => {
  const id = ++seq; pending.set(id, { res, rej }); ws.send(JSON.stringify({ id, method, params }));
});
async function evalJs(expr) {
  const r = await send('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true });
  if (r.exceptionDetails) throw new Error(JSON.stringify(r.exceptionDetails).slice(0, 400));
  return r.result.value;
}
async function shot(file) {
  const r = await send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync(file, Buffer.from(r.data, 'base64'));
}

try {
  const targets = await json('/json/list');
  const page = targets.find((t) => t.type === 'page');
  ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((r) => ws.addEventListener('open', r));
  ws.addEventListener('message', (e) => {
    const m = JSON.parse(e.data);
    if (m.id && pending.has(m.id)) { const p = pending.get(m.id); pending.delete(m.id); m.error ? p.rej(new Error(m.error.message)) : p.res(m.result); }
  });
  await send('Page.enable'); await send('Runtime.enable');
  await send('Emulation.setDeviceMetricsOverride', { width: w, height: h, deviceScaleFactor: 1, mobile: false });
  await send('Page.navigate', { url: `${base}?clean=1&dynres=0&pr=1` });
  const ready = await evalJs(`new Promise((r) => { const t0 = performance.now(); const i = setInterval(() => {
    if ((window.game && window.game.ready) || performance.now() - t0 > 180000) { clearInterval(i); r(!!(window.game && window.game.ready)); } }, 250); })`);
  if (!ready) throw new Error('game not ready');
  await evalJs('game.qaAO(false), true');
  const meta = [];
  for (const v of views) {
    const pose = { x: v.x, y: v.y, z_eye: v.z_eye ?? 1.7, heading: v.heading, pitch: v.pitch ?? 0, fov: v.fov ?? 75 };
    if (v.z_ground !== undefined) pose.z_ground = v.z_ground;
    const info = await evalJs(`(async () => { const r = await game.setCam(${JSON.stringify(pose)}); game.qaKey(false);
      return { place: document.getElementById('place')?.textContent || '', cam: r }; })()`);
    await sleep(60);
    await shot(path.join(out, `${v.id}_n.png`));
    // 1 cm sideways: ordinary geometry moves < 0.1 px, coplanar faces flip
    const side = { ...pose, x: pose.x + 0.01 * Math.cos(pose.heading * Math.PI / 180), y: pose.y - 0.01 * Math.sin(pose.heading * Math.PI / 180) };
    if (info.cam && info.cam.ground !== null && info.cam.ground !== undefined) side.z_ground = pose.z_ground = info.cam.ground;   // same eye height
    await evalJs(`game.setCam(${JSON.stringify(side)}).then(() => true)`);
    await sleep(40);
    await shot(path.join(out, `${v.id}_j.png`));
    await evalJs(`game.setCam(${JSON.stringify(pose)}).then(() => { game.qaKey(true); return true; })`);
    await sleep(40);
    await shot(path.join(out, `${v.id}_k.png`));
    await evalJs('game.qaKey(false), true');
    meta.push({ ...v, place: info.place, ground: info.cam ? info.cam.ground : null });
    process.stdout.write('.');
  }
  fs.writeFileSync(path.join(out, 'captured.json'), JSON.stringify(meta, null, 1));
  console.log(`\ncaptured ${meta.length} views -> ${out}`);
} catch (e) {
  console.error('QA capture failed:', e.message);
  process.exitCode = 1;
} finally {
  chrome.kill('SIGKILL');
  // the profile caches every GLB it loaded (~1 GB) and /tmp is RAM-backed: 13 GB of these piled up
  if (chrome.exitCode === null && chrome.signalCode === null) await new Promise((r) => chrome.once('exit', r));
  fs.rmSync(dir, { recursive: true, force: true });
}
