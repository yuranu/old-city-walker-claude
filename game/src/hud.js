// HUD: place name + live lat/lon, north-up minimap, nearest geotagged reference photo,
// and a jump to the same spot in Google Maps Street View.
export class Hud {
  init(plan, photos) {
    this.plan = plan;
    this.photos = photos;
    const lat0 = plan.origin.lat, lon0 = plan.origin.lon;
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
    this.named = plan.buildings.filter((b) => b.name).map((b) => ({ name: b.name, ring: b.ring }))
      .concat(plan.labels.map((l) => ({ name: l.name, p: l.p })));
    this.frame = 0;
  }

  latlon(x, y) {
    return [this.plan.origin.lat + y / this.mLat, this.plan.origin.lon + x / this.mLon];
  }

  nearestPlace(x, y) {
    let best = null, bd = 1e9;
    for (const n of this.named) {
      let d;
      if (n.p) d = Math.hypot(n.p[0] - x, n.p[1] - y);
      else d = Math.min(...n.ring.map((p, i) => segDist(x, y, p, n.ring[(i + 1) % n.ring.length])));
      if (d < bd) { bd = d; best = n.name; }
    }
    return bd < 30 ? best : 'Old City, Jerusalem';
  }

  update(player) {
    if (this.frame++ % 6) return;
    const { x, y, z } = player.plan();
    const [lat, lon] = this.latlon(x, y);
    this.place.textContent = this.nearestPlace(x, y);
    this.coords.textContent = `${lat.toFixed(6)}, ${lon.toFixed(6)} · heading ${player.heading().toFixed(0)}° · ` +
      `${(z + 776).toFixed(0)} m asl`;
    this.drawMap(x, y, player.heading());
  }

  drawMap(px, py, heading) {
    const g = this.map, W = 230, s = 1.35;
    const P = (p) => [W / 2 + (p[0] - px) * s, W / 2 - (p[1] - py) * s];
    g.fillStyle = '#e9e1d0';
    g.fillRect(0, 0, W, W);
    const poly = (ring, fill, stroke) => {
      g.beginPath();
      ring.forEach((p, i) => { const [a, b] = P(p); i ? g.lineTo(a, b) : g.moveTo(a, b); });
      g.closePath();
      g.fillStyle = fill; g.fill();
      if (stroke) { g.strokeStyle = stroke; g.stroke(); }
    };
    poly(this.plan.citadel, '#b49b74', '#7a6446');
    for (const b of this.plan.buildings) poly(b.ring, b.detailed ? '#a89170' : '#c9b99c', b.detailed ? '#6e5a40' : null);
    poly(this.plan.gatehouse, '#7a6446');
    g.strokeStyle = '#6b5233'; g.lineWidth = 4;
    for (const w of this.plan.walls) {
      g.beginPath();
      w.forEach((p, i) => { const [a, b] = P(p); i ? g.lineTo(a, b) : g.moveTo(a, b); });
      g.stroke();
    }
    g.lineWidth = 1;
    g.fillStyle = '#2b6cb0';
    for (const ph of this.photos) {
      const [a, b] = P([ph.x, ph.y]);
      if (a > 0 && a < W && b > 0 && b < W) g.fillRect(a - 1.5, b - 1.5, 3, 3);
    }
    // player arrow
    const r = (heading * Math.PI) / 180;
    g.save();
    g.translate(W / 2, W / 2);
    g.rotate(r);
    g.beginPath(); g.moveTo(0, -9); g.lineTo(6, 7); g.lineTo(0, 3); g.lineTo(-6, 7); g.closePath();
    g.fillStyle = '#d13b2a'; g.fill(); g.strokeStyle = '#fff'; g.stroke();
    g.restore();
    g.fillStyle = '#333'; g.font = '11px system-ui'; g.fillText('N ↑', 6, 14);
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

function segDist(x, y, a, b) {
  const ax = b[0] - a[0], ay = b[1] - a[1];
  const t = Math.max(0, Math.min(1, ((x - a[0]) * ax + (y - a[1]) * ay) / (ax * ax + ay * ay || 1)));
  return Math.hypot(x - a[0] - t * ax, y - a[1] - t * ay);
}

function esc(s) {
  return String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}
