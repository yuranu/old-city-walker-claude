// Touch controls (phones, tablets): a thumb joystick bottom left moves (Player.stick, analog; pushed
// to the rim it runs), dragging anywhere else looks around, and buttons on the right do what the
// keys do on a desktop: fly, up and down while flying, the map, the nearest photo.
const CSS = `
#touch { position: absolute; inset: 0; pointer-events: none; z-index: 5; }
#touch .stick { position: absolute; left: 22px; bottom: 26px; width: 128px; height: 128px; border-radius: 50%;
  background: rgba(20,18,14,0.28); border: 2px solid rgba(255,255,255,0.35); pointer-events: auto; touch-action: none; }
#touch .knob { position: absolute; left: 39px; top: 39px; width: 50px; height: 50px; border-radius: 50%;
  background: rgba(255,255,255,0.55); }
#touch .btns { position: absolute; right: 14px; bottom: 26px; display: flex; flex-direction: column; gap: 10px; }
#touch button { pointer-events: auto; touch-action: none; width: 58px; height: 58px; border-radius: 50%; border: 0;
  background: rgba(20,18,14,0.5); color: #fff; font: 600 13px system-ui, sans-serif; }
#touch button.on { background: rgba(200,150,60,0.75); }
#touch button.updown { display: none; }
#touch.flying button.updown { display: block; }
`;

export class TouchControls {
  constructor(canvas, player, hud, { onLook, onFly } = {}) {
    this.player = player;
    const style = document.createElement('style');
    style.textContent = CSS;
    document.head.appendChild(style);
    const root = (this.root = document.createElement('div'));
    root.id = 'touch';
    root.innerHTML = `<div class="stick"><div class="knob"></div></div>
      <div class="btns">
        <button data-k="up" class="updown">▲</button><button data-k="down" class="updown">▼</button>
        <button data-k="fly">Fly</button><button data-k="map">Map</button><button data-k="photo">Photo</button>
      </div>`;
    document.body.appendChild(root);
    this._stick(root.querySelector('.stick'), root.querySelector('.knob'));
    this._look(canvas, onLook);
    const flyBtn = root.querySelector('[data-k=fly]');
    const hold = (btn, code) => {
      btn.addEventListener('pointerdown', (e) => { e.preventDefault(); player.keys.add(code); });
      for (const ev of ['pointerup', 'pointercancel', 'pointerleave']) btn.addEventListener(ev, () => player.keys.delete(code));
    };
    hold(root.querySelector('[data-k=up]'), 'Space');
    hold(root.querySelector('[data-k=down]'), 'KeyC');
    flyBtn.addEventListener('click', () => {
      const on = onFly ? onFly() : player.toggleFly();
      flyBtn.classList.toggle('on', on);
      root.classList.toggle('flying', on);
    });
    root.querySelector('[data-k=map]').addEventListener('click', () => hud.toggleBig(player));
    root.querySelector('[data-k=photo]').addEventListener('click', () => hud.togglePhoto(player));
  }

  _stick(base, knob) {
    const R = 52;                           // knob travel (px)
    let id = null, cx = 0, cy = 0;
    const set = (dx, dy) => {
      const d = Math.hypot(dx, dy), k = d > R ? R / d : 1;
      dx *= k; dy *= k;
      knob.style.transform = `translate(${dx}px, ${dy}px)`;
      this.player.stick.x = dx / R;
      this.player.stick.y = -dy / R;
    };
    base.addEventListener('pointerdown', (e) => {
      e.preventDefault();
      id = e.pointerId;
      try { base.setPointerCapture(id); } catch { /* synthetic or already released pointer */ }
      const r = base.getBoundingClientRect();
      cx = r.left + r.width / 2; cy = r.top + r.height / 2;
      set(e.clientX - cx, e.clientY - cy);
    });
    base.addEventListener('pointermove', (e) => { if (e.pointerId === id) set(e.clientX - cx, e.clientY - cy); });
    const end = (e) => { if (e.pointerId === id) { id = null; set(0, 0); } };
    base.addEventListener('pointerup', end);
    base.addEventListener('pointercancel', end);
  }

  _look(canvas, onLook) {
    canvas.style.touchAction = 'none';
    const last = new Map();
    canvas.addEventListener('pointerdown', (e) => {
      if (e.pointerType === 'mouse') return;
      last.set(e.pointerId, [e.clientX, e.clientY]);
      try { canvas.setPointerCapture(e.pointerId); } catch { /* synthetic or already released pointer */ }
    });
    canvas.addEventListener('pointermove', (e) => {
      const p = last.get(e.pointerId);
      if (!p) return;
      const dx = e.clientX - p[0], dy = e.clientY - p[1];
      last.set(e.pointerId, [e.clientX, e.clientY]);
      if (onLook) onLook();
      this.player.look(dx * 1.8, dy * 1.8);   // (a thumb covers fewer pixels than a mouse)
    });
    const end = (e) => last.delete(e.pointerId);
    canvas.addEventListener('pointerup', end);
    canvas.addEventListener('pointercancel', end);
  }
}
