// GPU frame timing (EXT_disjoint_timer_query_webgl2 when available), dynamic resolution and the
// F3 performance overlay.
export class GpuTimer {
  constructor(gl) {
    this.gl = gl;
    this.ext = gl.getExtension('EXT_disjoint_timer_query_webgl2');
    this.pending = [];
    this.active = null;
    this.last = null;      // ms of the most recent finished frame
  }

  begin() {
    if (!this.ext || this.active || this.pending.length > 3) return;
    const q = this.gl.createQuery();
    this.gl.beginQuery(this.ext.TIME_ELAPSED_EXT, q);
    this.active = q;
  }

  end() {
    if (!this.active) return;
    this.gl.endQuery(this.ext.TIME_ELAPSED_EXT);
    this.pending.push(this.active);
    this.active = null;
  }

  // returns the newest available result (ms) or null
  poll() {
    if (!this.ext) return null;
    const gl = this.gl;
    const disjoint = gl.getParameter(this.ext.GPU_DISJOINT_EXT);
    let got = null;
    while (this.pending.length) {
      const q = this.pending[0];
      if (!gl.getQueryParameter(q, gl.QUERY_RESULT_AVAILABLE)) break;
      const ns = gl.getQueryParameter(q, gl.QUERY_RESULT);
      this.pending.shift();
      gl.deleteQuery(q);
      if (!disjoint) got = ns / 1e6;
    }
    if (got !== null) this.last = got;
    return got;
  }
}

// Keeps frames near the 16.7 ms budget by changing the renderer pixel ratio between minPR and
// maxPR. Driven by GPU time when timer queries exist (target ~13 ms leaves room for the
// compositor and CPU), otherwise by the rAF interval with an upward probe every few seconds.
export class DynRes {
  constructor(pipe) {
    this.pipe = pipe;
    this.enabled = true;
    this.targetGpu = 13;
    this.win = [];
    this.lastEval = 0;
    this.lastChange = 0;
    this.probeFailUntil = 0;
    this.probing = false;
  }

  set(pr) {
    const p = this.pipe;
    pr = Math.round(Math.min(p.maxPR, Math.max(p.minPR, pr)) * 20) / 20;
    if (Math.abs(pr - p.pixelRatio) < 0.01) return false;
    p.pixelRatio = pr;
    this.win.length = 0;
    return true;
  }

  update(now, dt, gpu) {
    if (!this.enabled) return;
    this.win.push({ dt, gpu });
    if (this.win.length > 90) this.win.shift();
    if (now - this.lastEval < 500 || this.win.length < 20) return;
    this.lastEval = now;
    const n = this.win.length;
    const gpus = this.win.filter((s) => s.gpu != null).map((s) => s.gpu);
    const p = this.pipe;
    const pr = p.pixelRatio;
    if (gpus.length >= n / 2) {
      gpus.sort((a, b) => a - b);
      const g = gpus[Math.floor(gpus.length * 0.75)];     // 75th percentile
      if (g > this.targetGpu * 1.1) {
        if (this.set(pr * Math.max(0.8, Math.sqrt(this.targetGpu / g)))) this.lastChange = now;
      } else if (g < this.targetGpu * 0.72 && now - this.lastChange > 1500) {
        if (this.set(pr * Math.min(1.15, Math.sqrt(this.targetGpu / g)))) this.lastChange = now;
      }
      return;
    }
    // no timer queries: rAF interval (vsync-capped, so probe upwards carefully)
    const dts = this.win.map((s) => s.dt).sort((a, b) => a - b);
    const d = dts[Math.floor(n / 2)];
    if (d > 19.5) {
      if (this.probing) this.probeFailUntil = now + 15000;
      this.probing = false;
      if (this.set(pr * Math.max(0.8, Math.sqrt(16.7 / d)))) this.lastChange = now;
    } else if (d < 17.6 && now - this.lastChange > 4000 && now > this.probeFailUntil && pr < p.maxPR) {
      this.probing = true;
      if (this.set(pr + 0.05)) this.lastChange = now;
    } else if (now - this.lastChange > 3000) {
      this.probing = false;
    }
  }
}

export class PerfOverlay {
  constructor(el) {
    this.el = el;
    this.visible = false;
    this.fps = 0;
    this.dt = 16.7;
    this.last = 0;
    this.extra = null;     // () => extra text lines (sector streaming), built only on refresh
    this.worst = 0;        // worst frame (ms) since the last refresh
  }

  toggle(on = !this.visible) {
    this.visible = on;
    this.el.style.display = on ? 'block' : 'none';
    this.last = 0;
  }

  // dt = null: refresh the text without feeding the frame-time average (step(), toggle)
  frame(now, dt, stats) {
    if (dt != null) { this.dt += (dt - this.dt) * 0.1; this.worst = Math.max(this.worst, dt); }
    if (!this.visible || now - this.last < 250) return;
    this.last = now;
    const s = stats;
    const extra = this.extra ? this.extra() : '';
    this.el.textContent =
      `${(1000 / this.dt).toFixed(0)} fps  ${this.dt.toFixed(1)} ms  worst ${this.worst.toFixed(0)} ms` +
      (s.gpu != null ? `  gpu ${s.gpu.toFixed(1)} ms` : '') + '\n' +
      `pixel ratio ${s.pr.toFixed(2)}${s.dyn ? ' (auto)' : ''}  ${s.w}×${s.h}\n` +
      `draw calls ${s.calls}  triangles ${(s.tris / 1000).toFixed(0)}k\n` +
      `AO ${s.ao ? 'on' : 'off'} (O)  shadows 2×${s.shadow}` +
      (extra ? '\n' + extra : '') +
      (this.gpu ? `\n${this.gpu.name}${this.gpu.kind ? ` (${this.gpu.kind})` : ''}` : '');
    this.worst = 0;
  }
}
