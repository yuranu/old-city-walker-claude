// Visible failure report: a blank canvas tells nobody anything, least of all on a phone without a
// console. Uncaught errors, rejected promises, WebGL context loss and failed render targets (via
// reportError) show in a panel with the browser and GPU, so a screenshot is enough to diagnose.
const lines = [];
let panel = null;

function show() {
  if (!panel) {
    panel = document.createElement('div');
    panel.id = 'errors';
    panel.style.cssText = 'position:absolute;left:8px;right:8px;top:8px;z-index:100;max-height:60vh;overflow:auto;' +
      'background:rgba(90,10,10,0.88);color:#fff;font:12px/1.4 ui-monospace,Menlo,monospace;padding:10px 12px;' +
      'border-radius:8px;white-space:pre-wrap;pointer-events:auto';
    panel.addEventListener('click', () => { panel.style.display = 'none'; });
    document.body.appendChild(panel);
  }
  panel.style.display = 'block';
  panel.textContent = 'Something went wrong (tap to hide)\n\n' + lines.join('\n\n') + '\n\n' + env();
}

let gpu = '';
export function setGpuInfo(s) { gpu = s; }

function env() {
  return `${navigator.userAgent}\nscreen ${screen.width}x${screen.height} @${devicePixelRatio}${gpu ? '\nGPU ' + gpu : ''}`;
}

export function reportError(msg) {
  const s = String(msg).slice(0, 1200);
  if (lines.includes(s) || lines.length > 8) return;
  lines.push(s);
  console.error(s);
  show();
}

addEventListener('error', (e) => reportError(`${e.message}\n  at ${e.filename || '?'}:${e.lineno || 0}` +
  (e.error && e.error.stack ? '\n' + String(e.error.stack).split('\n').slice(0, 4).join('\n') : '')));
addEventListener('unhandledrejection', (e) => {
  const r = e.reason;
  reportError('Unhandled: ' + (r && r.stack ? String(r.stack).split('\n').slice(0, 5).join('\n') : String(r)));
});

export function watchContext(canvas) {
  canvas.addEventListener('webglcontextlost', (e) => {
    e.preventDefault();
    reportError('WebGL context lost (the GPU ran out of memory or reset). Reload the page; the mobile profile streams less.');
  });
}
