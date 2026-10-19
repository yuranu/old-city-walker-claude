// Frame times of the running dev server in a headless Chrome on a chosen GPU, driven over the
// DevTools protocol (no extra packages). DRI_PRIME=1 selects the discrete GPU (the Arc).
//
//   node game/scripts/gpu_bench.mjs [--gpu arc|igpu] [--size 1024x768] [--query "pr=1"]
//                                   [--glide 60] [--url http://127.0.0.1:5173/]
//
// Prints JSON: start-up timing, per-view frame ms (devtest.benchViews: best of 3, AO on/off), and
// with --glide N a real-time run of N seconds along devtest.ROUTE (frame intervals, swaps, the
// main-thread streaming work per step type). Needs the dev server (npm --prefix game run dev).
// Note: numbers on a busy or hot machine (Blender builds, thermal throttling) vary by 2-4x.
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const arg = (k, d) => { const i = process.argv.indexOf('--' + k); return i > 0 ? process.argv[i + 1] : d; };
const gpu = arg('gpu', 'arc');
const [w, h] = arg('size', '1024x768').split('x').map(Number);
const base = arg('url', 'http://127.0.0.1:5173/');
const query = arg('query', 'pr=1');
const glide = +arg('glide', 0);
const port = 9300 + Math.floor(Math.random() * 500);
const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'ocw-chrome-'));
const env = { ...process.env };
if (gpu === 'arc' || gpu === 'dgpu') env.DRI_PRIME = '1'; else delete env.DRI_PRIME;

const chrome = spawn(process.env.CHROME || 'google-chrome-stable', [
  '--headless=new', `--remote-debugging-port=${port}`, `--user-data-dir=${dir}`, `--window-size=${w},${h}`,
  '--ignore-gpu-blocklist', '--enable-gpu', '--use-angle=gl', '--no-first-run', '--no-default-browser-check',
  '--disable-background-timer-throttling', '--disable-renderer-backgrounding', 'about:blank',
], { env, stdio: ['ignore', 'ignore', 'pipe'] });
let errLog = '';
chrome.stderr.on('data', (d) => { errLog += d; });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function json(p) {
  for (let i = 0; i < 100; i++) {
    try { const r = await fetch(`http://127.0.0.1:${port}${p}`); if (r.ok) return await r.json(); } catch { /* starting */ }
    await sleep(100);
  }
  throw new Error('chrome did not start: ' + errLog.slice(-500));
}

let ws, seq = 0;
const pending = new Map();
const send = (method, params = {}) => new Promise((res, rej) => {
  const id = ++seq;
  pending.set(id, { res, rej });
  ws.send(JSON.stringify({ id, method, params }));
});

const script = `(async () => {
  await new Promise((r) => { const t0 = performance.now(); const i = setInterval(() => { if ((window.game && window.game.ready) || performance.now() - t0 > 120000) { clearInterval(i); r(); } }, 200); });
  if (!window.game || !window.game.ready) return { error: 'game not ready', loading: document.getElementById('loading')?.textContent };
  const dt = (await import('/src/devtest.js')).default;
  game.clean(true);
  const out = { gpu: game.gpu, timing: game.world.timing, manifest: game.world.manifest, legacy: game.world.legacy };
  out.bench = await dt.benchViews();
  if (${glide} > 0) { await game.setCam(null); out.glide = await dt.glide({ secs: ${glide} }); }
  out.memory = game.memory();
  return out;
})()`;

try {
  const page = (await json('/json/list')).find((t) => t.type === 'page');
  ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((r) => (ws.onopen = r));
  ws.onmessage = (e) => {
    const m = JSON.parse(e.data);
    if (m.id && pending.has(m.id)) { const p = pending.get(m.id); pending.delete(m.id); m.error ? p.rej(new Error(m.error.message)) : p.res(m.result); }
    if (m.method === 'Runtime.exceptionThrown') console.error('[page]', m.params.exceptionDetails.exception?.description?.slice(0, 400));
  };
  await send('Runtime.enable');
  await send('Emulation.setDeviceMetricsOverride', { width: w, height: h, deviceScaleFactor: 1, mobile: false });
  await send('Page.navigate', { url: `${base}?${query}&dynres=0` });
  const r = await send('Runtime.evaluate', { expression: script, awaitPromise: true, returnByValue: true, timeout: 900000 });
  if (r.exceptionDetails) console.log('EXCEPTION', r.exceptionDetails.exception?.description || JSON.stringify(r.exceptionDetails));
  else console.log(JSON.stringify(r.result.value, null, 1));
} finally {
  try { ws && ws.close(); } catch { /* closed */ }
  chrome.kill('SIGTERM');
  setTimeout(() => fs.rmSync(dir, { recursive: true, force: true }), 500);
}
