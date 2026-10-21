// First-person capsule controller against the resident collision (a Collider: the union of the
// chunks' MeshBVHs; after the three-mesh-bvh character-movement example). World frame: three.js,
// Y up; local plan frame: x east, y north => three (x, z) = (east, -north).
import * as THREE from 'three';

const RADIUS = 0.35;
const SEGMENT = 1.0;          // top sphere centre -> bottom sphere centre
const EYE = 0.3;              // eye above the top sphere centre (eye at 1.65 m)
const GRAVITY = -24;

export class Player {
  constructor(camera, world) {
    this.camera = camera;
    this.world = world;           // Collider
    this.held = false;            // frozen in place (waiting for the sectors around a teleport)
    this.spawn = [-22, 2, 104];   // respawn after falling out of the world (x, y, heading)
    this.onFall = null;           // replaces the plain respawn teleport (main: one that waits for sectors)
    this._killY = -40;
    this._killVersion = -1;
    this.pos = new THREE.Vector3();        // top sphere centre
    this.vel = new THREE.Vector3();
    this.yaw = 0;
    this.pitch = 0;
    this.onGround = false;
    this.flying = false;          // fly mode: no gravity, no collision, move where you look
    this.keys = new Set();
    this.stick = { x: 0, y: 0 };  // touch joystick: x right, y forward, each -1..1 (touch.js)
    this._seg = new THREE.Line3();
    this._box = new THREE.Box3();
    this._wb = new THREE.Box3();
    this._a = new THREE.Vector3();
    this._b = new THREE.Vector3();
    this._d = new THREE.Vector3();
  }

  // place feet at local plan (x east, y north) on the ground below
  teleport(x, y, headingDeg = null, pitchDeg = 0) {
    // stand on the lowest upward-facing surface with headroom (street level, not a canopy or roof)
    const down = new THREE.Vector3(0, -1, 0);
    const top = Math.max(80, this.world.bounds(this._wb).max.y + 1);
    const hits = this.world.raycast(new THREE.Ray(new THREE.Vector3(x, top, -y), down), THREE.DoubleSide)
      .sort((a, b) => a.point.y - b.point.y);
    let groundY = hits.length ? hits[hits.length - 1].point.y : 0;
    for (let i = 0; i < hits.length; i++) {
      const h = hits[i];
      if (!h.face || h.face.normal.y < 0.5) continue;
      const above = i + 1 < hits.length ? hits[i + 1].point.y : Infinity;
      if (above - h.point.y >= 2.0) { groundY = h.point.y; break; }
    }
    this.groundY = groundY;
    this.pos.set(x, groundY + RADIUS + SEGMENT + 0.05, -y);
    this.vel.set(0, 0, 0);
    if (headingDeg !== null) this.yaw = -THREE.MathUtils.degToRad(headingDeg);
    this.pitch = THREE.MathUtils.degToRad(pitchDeg);
    this.updateCamera();
  }

  // heading in compass degrees (0 = north, 90 = east)
  heading() {
    return (THREE.MathUtils.radToDeg(-this.yaw) % 360 + 360) % 360;
  }

  plan() {
    return { x: this.pos.x, y: -this.pos.z, z: this.pos.y - RADIUS - SEGMENT };
  }

  look(dx, dy) {
    this.yaw -= dx * 0.0022;
    this.pitch = THREE.MathUtils.clamp(this.pitch - dy * 0.0022, -1.45, 1.45);
  }

  // below the lowest resident geometry: fell out of the world (the terrain spans tens of metres)
  killY() {
    if (this._killVersion !== this.world.version) {
      const b = this.world.bounds(this._wb);
      this._killY = b.isEmpty() ? -40 : b.min.y - 30;
      this._killVersion = this.world.version;
    }
    return this._killY;
  }

  // F: fly mode on/off; turning it off lands on the street below
  toggleFly() {
    this.flying = !this.flying;
    this.vel.set(0, 0, 0);
    if (!this.flying) {
      const { x, y } = this.plan();
      this.teleport(x, y, this.heading(), THREE.MathUtils.radToDeg(this.pitch));
    }
    return this.flying;
  }

  // forward / sideways input from the keys, else the touch stick; m: speed factor (a stick part-way out
  // walks slower), run: Shift or the stick pushed to its rim
  _input() {
    const k = this.keys, s = this.stick;
    let fwd = (k.has('KeyW') || k.has('ArrowUp') ? 1 : 0) - (k.has('KeyS') || k.has('ArrowDown') ? 1 : 0);
    let side = (k.has('KeyD') ? 1 : 0) - (k.has('KeyA') ? 1 : 0);
    let m = 1, run = k.has('ShiftLeft') || k.has('ShiftRight');
    if (!fwd && !side) {
      const sm = Math.hypot(s.x, s.y);
      if (sm > 0.12) { fwd = s.y / sm; side = s.x / sm; m = Math.min(1, sm / 0.7); run = run || sm > 0.95; }
    }
    return { fwd, side, m, run };
  }

  fly(dt) {
    const k = this.keys;
    const { fwd: f0, side: s0, m, run } = this._input();
    const fwd = f0 * m, side = s0 * m;
    const up = (k.has('Space') || k.has('KeyE') ? 1 : 0) - (k.has('KeyC') || k.has('KeyQ') ? 1 : 0);
    if (k.has('ArrowLeft')) this.yaw += 1.8 * dt;
    if (k.has('ArrowRight')) this.yaw -= 1.8 * dt;
    const speed = run ? 45 : 12;
    const dir = this._d.set(0, 0, -1).applyEuler(new THREE.Euler(this.pitch, this.yaw, 0, 'YXZ'));
    const right = this._a.set(Math.cos(this.yaw), 0, -Math.sin(this.yaw));
    this.pos.addScaledVector(dir, fwd * speed * dt).addScaledVector(right, side * speed * dt);
    this.pos.y += up * speed * dt;
    this.updateCamera();
  }

  update(dt) {
    if (this.held) { this.vel.set(0, 0, 0); this.updateCamera(); return; }
    if (this.flying) { this.fly(dt); return; }
    const k = this.keys;
    const { fwd, side, m, run } = this._input();
    if (k.has('ArrowLeft')) this.yaw += 1.8 * dt;
    if (k.has('ArrowRight')) this.yaw -= 1.8 * dt;
    const speed = (run ? 6.5 : 2.8) * m;

    // horizontal move in the yaw frame (camera looks down -Z at yaw 0, i.e. north)
    const sin = Math.sin(this.yaw), cos = Math.cos(this.yaw);
    const mx = (-sin * fwd + cos * side), mz = (-cos * fwd - sin * side);
    const len = Math.hypot(mx, mz) || 1;
    this.vel.y += GRAVITY * dt;
    if (this.onGround && k.has('Space')) this.vel.y = 6.0;

    const steps = Math.max(1, Math.ceil(dt / (1 / 120)));   // substeps keep fast falls stable
    const h = dt / steps;
    for (let i = 0; i < steps; i++) {
      this.pos.x += (mx / len) * speed * h * (fwd || side ? 1 : 0);
      this.pos.z += (mz / len) * speed * h * (fwd || side ? 1 : 0);
      this.pos.addScaledVector(this.vel, h);
      this.collide(h);
    }
    if (this.pos.y < this.killY()) {
      if (this.onFall) this.onFall(); else this.teleport(...this.spawn);
    }
    this.updateCamera();
  }

  collide(dt) {
    const seg = this._seg, box = this._box;
    seg.start.copy(this.pos);
    seg.end.copy(this.pos).y -= SEGMENT;
    box.makeEmpty().expandByPoint(seg.start).expandByPoint(seg.end);
    box.min.addScalar(-RADIUS);
    box.max.addScalar(RADIUS);
    const a = this._a, b = this._b;
    this.world.shapecast(box, {
      intersectsBounds: (bb) => bb.intersectsBox(box),
      intersectsTriangle: (tri) => {
        const dist = tri.closestPointToSegment(seg, a, b);
        if (dist < RADIUS) {
          const depth = RADIUS - dist;
          const dir = b.sub(a).normalize();
          seg.start.addScaledVector(dir, depth);
          seg.end.addScaledVector(dir, depth);
        }
      },
    });
    const delta = this._d.subVectors(seg.start, this.pos);
    this.onGround = delta.y > Math.abs(dt * this.vel.y * 0.25);
    const off = Math.max(0, delta.length() - 1e-5);
    delta.normalize().multiplyScalar(off);
    this.pos.add(delta);
    if (this.onGround) this.vel.set(0, 0, 0);
    else if (off > 0) {
      delta.normalize();
      this.vel.addScaledVector(delta, -delta.dot(this.vel));
    }
  }

  updateCamera() {
    this.camera.position.set(this.pos.x, this.pos.y + EYE, this.pos.z);
    this.camera.rotation.set(this.pitch, this.yaw, 0, 'YXZ');
  }
}
