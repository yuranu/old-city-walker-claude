// HUD: place name + live lat/lon, north-up minimap, nearest geotagged reference photo,
// and a jump to the same spot in Google Maps Street View.
// The map is pre-rendered once (the whole walled city, ~3000 footprints) into an offscreen canvas;
// the minimap crops it every few frames and draws labels live. M opens the full map (pan, zoom,
// click to teleport).
const PPM = 1.6;                                   // offscreen map resolution, pixels per metre
const ZOOMS = [0.5, 0.8, 1.35, 2.2, 3.4];          // minimap scales, screen px per metre
const COL = { ground: '#e9e1d0', street: '#f6f1e6', steps: '#d9cdb5', ctx: '#cdbfa3', bld: '#a89170',
  bldEdge: '#6e5a40', landmark: '#9b6b4a', wall: '#5e4a31', citadel: '#b49b74' };

export class Hud {
  init(plan, photos) {
    this.plan = plan;
    this.photos = photos;
    const lat0 = plan.origin.lat;
    const phi = (lat0 * Math.PI) / 180;
    this.mLat = 111132.92 - 559.82 * Math.cos(2 * phi) + 1.175 * Math.cos(4 * phi);
    this.mLon = 111412.84 * Math.cos(phi) - 93.5 * Math.cos(3 * phi);
    this.place = document.getElementById('place');
    this.coords = document.getElementById('coords');
    this.map = document.getElementById('mapCanvas').getContext('2d');
    this.photoBox = document.getElementById('photo');
    this.photoImg = document.getElementById('photoImg');
    this.photoMeta = document.getElementById('photoMeta');
    this.photoIdx = 0;
    this.zoom = 2;
    this.streets = (plan.streets || []).filter((w) => w.name);
    this.named = plan.buildings.filter((b) => b.name).map((b) => ({ name: b.name, ring: b.ring, landmark: b.landmark }))
      .concat(plan.labels.map((l) => ({ name: l.name, p: l.p })));
    this.frame = 0;
    this.renderBase();
    this.big = { el: document.getElementById('bigmap'), cv: document.getElementById('bigCanvas'), open: false,
      cx: 300, cy: 150, s: 0.7 };
    this.onTeleport = null;
    if (this.big.el) this.bindBig();
  }

  // ---------------------------------------------------------------- offscreen city image
  renderBase() {
    let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
    for (const b of this.plan.buildings) for (const [x, y] of b.ring) {
      x0 = Math.min(x0, x); y0 = Math.min(y0, y); x1 = Math.max(x1, x); y1 = Math.max(y1, y);
    }
    this.bx = [x0 - 20, y0 - 20, x1 + 20, y1 + 20];
    const W = Math.ceil((this.bx[2] - this.bx[0]) * PPM), H = Math.ceil((this.bx[3] - this.bx[1]) * PPM);
    const cv = document.createElement('canvas');
    cv.width = W; cv.height = H;
    const g = cv.getContext('2d');
    const P = (p) => [(p[0] - this.bx[0]) * PPM, (this.bx[3] - p[1]) * PPM];
    const path = (pts, close) => {
      g.beginPath();
      pts.forEach((p, i) => { const [a, b] = P(p); i ? g.lineTo(a, b) : g.moveTo(a, b); });
      if (close) g.closePath();
    };
    g.fillStyle = COL.ground; g.fillRect(0, 0, W, H);
    g.lineCap = 'round'; g.lineJoin = 'round';
    for (const w of this.plan.streets || []) {                 // streets under the buildings
      path(w.pts, false);
      g.strokeStyle = w.steps ? COL.steps : COL.street; g.lineWidth = (w.steps ? 2.4 : 3.2) * PPM; g.stroke();
    }
    path(this.plan.citadel, true); g.fillStyle = COL.citadel; g.fill();
    for (const b of this.plan.buildings) {
      path(b.ring, true);
      g.fillStyle = b.landmark ? COL.landmark : (b.detailed ? COL.bld : COL.ctx); g.fill();
      if (b.detailed) { g.strokeStyle = COL.bldEdge; g.lineWidth = 0.6; g.stroke(); }
    }
    path(this.plan.gatehouse, true); g.fillStyle = COL.wall; g.fill();
    g.strokeStyle = COL.wall; g.lineWidth = 3 * PPM; g.lineCap = 'butt';
    for (const w of this.plan.walls) { path(w, false); g.stroke(); }
    this.base = cv;
  }

  // world (x, y) -> canvas px for a view centred on (cx, cy) at scale s (px per metre), canvas size W x H
  static view(cx, cy, s, W, H) { return (p) => [W / 2 + (p[0] - cx) * s, H / 2 - (p[1] - cy) * s]; }

  drawView(g, W, H, cx, cy, s, opts = {}) {
    const sx = (cx - this.bx[0]) * PPM - (W / 2) * PPM / s, sy = (this.bx[3] - cy) * PPM - (H / 2) * PPM / s;
    g.fillStyle = COL.ground; g.fillRect(0, 0, W, H);
    g.imageSmoothingEnabled = true;
    g.drawImage(this.base, sx, sy, W * PPM / s, H * PPM / s, 0, 0, W, H);
    const P = Hud.view(cx, cy, s, W, H);
    const inView = (p, m = 0) => p[0] > -m && p[0] < W + m && p[1] > -m && p[1] < H + m;
    g.textAlign = 'center'; g.textBaseline = 'middle';
    const label = (txt, p, font, fill, halo = '#f5efe2') => {
      g.font = font; g.lineWidth = 3; g.strokeStyle = halo; g.strokeText(txt, p[0], p[1]); g.fillStyle = fill; g.fillText(txt, p[0], p[1]);
    };
    // street names along their longest segment (only at readable scales)
    if (s >= (opts.big ? 0.9 : 1.3)) {
      g.font = `${opts.big ? 11 : 9}px system-ui`;
      const done = new Set();
      for (const w of this.streets) {
        if (done.has(w.name)) continue;
        let best = null, bl = 0;
        for (let i = 0; i + 1 < w.pts.length; i++) {
          const l = Math.hypot(w.pts[i + 1][0] - w.pts[i][0], w.pts[i + 1][1] - w.pts[i][1]);
          if (l > bl) { bl = l; best = i; }
        }
        if (bl * s < w.name.length * (opts.big ? 6 : 5)) continue;
        const a = P(w.pts[best]), b = P(w.pts[best + 1]), m = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];
        if (!inView(m)) continue;
        let ang = Math.atan2(b[1] - a[1], b[0] - a[0]);
        if (ang > Math.PI / 2) ang -= Math.PI; else if (ang < -Math.PI / 2) ang += Math.PI;
        g.save(); g.translate(m[0], m[1]); g.rotate(ang);
        label(w.name, [0, 0], g.font, '#4a3a26');
        g.restore();
        done.add(w.name);
      }
    }
    if (opts.big || s < 1.6) {                                    // landmarks
      for (const n of this.named) {
        if (!n.landmark || !n.ring) continue;
        let x = 0, y = 0; n.ring.forEach((p) => { x += p[0]; y += p[1]; });
        const p = P([x / n.ring.length, y / n.ring.length]);
        if (inView(p)) label(n.name, p, `${opts.big ? 11 : 9}px system-ui`, '#5a2e14');
      }
    }
    for (const q of this.plan.gates || []) {
      const p = P(q.p);
      if (inView(p, 20)) label(q.name, p, `bold ${opts.big ? 12 : 10}px system-ui`, '#2f2416');
    }
    if (opts.big || s <= 0.8) {
      for (const q of this.plan.quarters || []) {
        const p = P(q.p);
        if (inView(p, 40)) label(q.name.toUpperCase(), p, `bold ${opts.big ? 15 : 10}px system-ui`, 'rgba(70,50,30,0.75)');
      }
    }
    return P;
  }

  arrow(g, x, y, heading, size = 1) {
    g.save(); g.translate(x, y); g.rotate((heading * Math.PI) / 180); g.scale(size, size);
    g.beginPath(); g.moveTo(0, -9); g.lineTo(6, 7); g.lineTo(0, 3); g.lineTo(-6, 7); g.closePath();
    g.fillStyle = '#d13b2a'; g.fill(); g.strokeStyle = '#fff'; g.lineWidth = 1.5; g.stroke();
    g.restore();
  }

  latlon(x, y) {
    return [this.plan.origin.lat + y / this.mLat, this.plan.origin.lon + x / this.mLon];
  }

  nearestPlace(x, y) {
    let street = null, sd = 1e9;                 // the street you are on, then the building, then the quarter
    for (const w of this.streets) {
      for (let i = 0; i + 1 < w.pts.length; i++) {
        const d = segDist(x, y, w.pts[i], w.pts[i + 1]);
        if (d < sd) { sd = d; street = w.name; }
      }
    }
    let best = null, bd = 1e9;
    for (const n of this.named) {
      let d;
      if (n.p) d = Math.hypot(n.p[0] - x, n.p[1] - y);
      else d = Math.min(...n.ring.map((p, i) => segDist(x, y, p, n.ring[(i + 1) % n.ring.length])));
      if (d < bd) { bd = d; best = n.name; }
    }
    let quarter = 'Outside the walls';
    for (const a of this.plan.areas || []) if (a.rings.some((r) => inRing(x, y, r))) { quarter = a.name; break; }
    const main = bd < 12 ? best : (sd < 7 ? street : (bd < 30 ? best : quarter));
    return main === quarter ? quarter : `${main} · ${quarter}`;
  }

  update(player) {
    if (this.frame++ % 6) return;
    const { x, y, z } = player.plan();
    const [lat, lon] = this.latlon(x, y);
    this.place.textContent = this.nearestPlace(x, y);
    this.coords.textContent = `${lat.toFixed(6)}, ${lon.toFixed(6)} · heading ${player.heading().toFixed(0)}° · ` +
      `${(z + 770.6).toFixed(0)} m asl`;
    this.drawMap(x, y, player.heading());
    if (this.big.open) this.drawBig(x, y, player.heading());
  }

  drawMap(px, py, heading) {
    const g = this.map, W = g.canvas.width, s = ZOOMS[this.zoom];
    this.drawView(g, W, W, px, py, s);
    g.fillStyle = '#2b6cb0';
    const P = Hud.view(px, py, s, W, W);
    for (const ph of this.photos) {
      const [a, b] = P([ph.x, ph.y]);
      if (a > 0 && a < W && b > 0 && b < W) g.fillRect(a - 1.5, b - 1.5, 3, 3);
    }
    this.arrow(g, W / 2, W / 2, heading);
    g.textAlign = 'left'; g.fillStyle = '#333'; g.font = '11px system-ui';
    g.fillText('N ↑', 6, 12); g.fillText(`${Math.round(60 / s)} m`, 6, W - 8);
    g.fillRect(40, W - 9, 60, 2);
  }

  flash(msg) {                                  // a short notice under the place name
    let el = document.getElementById('flash');
    if (!el) { el = document.createElement('div'); el.id = 'flash'; el.style.cssText = 'margin-top:6px;color:#ffd88a'; this.place.parentNode.appendChild(el); }
    el.textContent = msg;
    clearTimeout(this._flashT);
    this._flashT = setTimeout(() => { el.textContent = ''; }, 5000);
  }

  zoomMap(d) { this.zoom = Math.max(0, Math.min(ZOOMS.length - 1, this.zoom + d)); this.frame = 0; }

  // ---------------------------------------------------------------- full map (M)
  toggleBig(player) {
    const b = this.big;
    b.open = !b.open;
    b.el.style.display = b.open ? 'block' : 'none';
    if (b.open) {
      if (document.pointerLockElement) document.exitPointerLock();
      const { x, y } = player.plan();
      b.cx = x; b.cy = y; b.s = Math.max(b.s, 0.55);
      this.player = player;
      this.drawBig(x, y, player.heading());
    }
  }

  drawBig(px, py, heading) {
    const b = this.big, cv = b.cv;
    const W = cv.clientWidth, H = cv.clientHeight;
    if (cv.width !== W || cv.height !== H) { cv.width = W; cv.height = H; }
    const g = cv.getContext('2d');
    const P = this.drawView(g, W, H, b.cx, b.cy, b.s, { big: true });
    const [a, c] = P([px, py]);
    this.arrow(g, a, c, heading, 1.3);
    g.textAlign = 'left'; g.fillStyle = '#333'; g.font = '12px system-ui';
    g.fillText('N ↑   drag to pan · wheel to zoom · click to go there · M or Esc to close', 10, H - 12);
  }

  bindBig() {
    const b = this.big, cv = b.cv;
    let drag = null, moved = false;
    cv.addEventListener('mousedown', (e) => { drag = [e.clientX, e.clientY, b.cx, b.cy]; moved = false; });
    addEventListener('mousemove', (e) => {
      if (!drag) return;
      const dx = e.clientX - drag[0], dy = e.clientY - drag[1];
      if (Math.abs(dx) + Math.abs(dy) > 4) moved = true;
      b.cx = drag[2] - dx / b.s; b.cy = drag[3] + dy / b.s;
      if (this.player) { const { x, y } = this.player.plan(); this.drawBig(x, y, this.player.heading()); }
    });
    addEventListener('mouseup', (e) => {
      if (drag && !moved && e.target === cv) {               // a click: teleport there
        const r = cv.getBoundingClientRect();
        const x = b.cx + (e.clientX - r.left - r.width / 2) / b.s, y = b.cy - (e.clientY - r.top - r.height / 2) / b.s;
        if (this.onTeleport) this.onTeleport(x, y);
        this.toggleBig(this.player);
      }
      drag = null;
    });
    cv.addEventListener('wheel', (e) => {
      e.preventDefault();
      const r = cv.getBoundingClientRect();
      const mx = e.clientX - r.left - r.width / 2, my = e.clientY - r.top - r.height / 2;
      const wx = b.cx + mx / b.s, wy = b.cy - my / b.s;
      b.s = Math.max(0.3, Math.min(6, b.s * (e.deltaY < 0 ? 1.25 : 0.8)));
      b.cx = wx - mx / b.s; b.cy = wy + my / b.s;
      if (this.player) { const { x, y } = this.player.plan(); this.drawBig(x, y, this.player.heading()); }
    }, { passive: false });
  }

  photosByDistance(player) {
    const { x, y } = player.plan();
    return this.photos.map((p) => ({ p, d: Math.hypot(p.x - x, p.y - y) })).sort((a, b) => a.d - b.d);
  }

  showPhoto(player) {
    const list = this.photosByDistance(player);
    const { p, d } = list[this.photoIdx % Math.min(list.length, 12)];
    this.photoImg.src = '/' + p.file;
    this.photoMeta.innerHTML = `<b>${esc(p.title)}</b><br>${d.toFixed(0)} m from you · ${esc(p.date || '')}` +
      ` · ${esc(p.artist)} · ${esc(p.licence || '')}<br><a href="${p.page}" target="_blank" rel="noopener">Wikimedia Commons</a>` +
      ` · <kbd>N</kbd> next (${(this.photoIdx % 12) + 1}/12)`;
    this.photoBox.style.display = 'block';
  }

  togglePhoto(player) {
    if (this.photoBox.style.display === 'block') { this.photoBox.style.display = 'none'; return; }
    this.photoIdx = 0;
    this.showPhoto(player);
  }

  nextPhoto(player) {
    this.photoIdx++;
    this.showPhoto(player);
  }

  openGoogleMaps(player) {
    const { x, y } = player.plan();
    const [lat, lon] = this.latlon(x, y);
    const url = `https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=${lat.toFixed(6)},${lon.toFixed(6)}` +
      `&heading=${player.heading().toFixed(0)}&pitch=0&fov=90`;
    if (document.pointerLockElement) document.exitPointerLock();
    window.open(url, '_blank', 'noopener');
  }
}

function inRing(x, y, r) {
  let c = false;
  for (let i = 0, j = r.length - 1; i < r.length; j = i++) {
    if ((r[i][1] > y) !== (r[j][1] > y) && x < ((r[j][0] - r[i][0]) * (y - r[i][1])) / (r[j][1] - r[i][1]) + r[i][0]) c = !c;
  }
  return c;
}

function segDist(x, y, a, b) {
  const ax = b[0] - a[0], ay = b[1] - a[1];
  const t = Math.max(0, Math.min(1, ((x - a[0]) * ax + (y - a[1]) * ay) / (ax * ax + ay * ay || 1)));
  return Math.hypot(x - a[0] - t * ax, y - a[1] - t * ay);
}

function esc(s) {
  return String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}
