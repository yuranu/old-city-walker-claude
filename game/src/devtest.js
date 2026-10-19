// Dev-only test helpers for the streaming engine (not imported by the game). In the console or
// from automation:  await import('/src/devtest.js')  then  await devtest.benchViews()  etc.
// Everything drives frames itself (game.simFrame or rAF), so walk() works in hidden tabs.
const yieldTask = () => new Promise((r) => { const ch = new MessageChannel(); ch.port1.onmessage = () => r(); ch.port2.postMessage(0); });

// views for frame-time comparisons: inside the walls, and from the walls looking across
export const VIEWS = {
  david_street: 'david_street',                                                   // souq, inside
  souq_east: { x: 300, y: 8, heading: 90, pitch: 0, fov: 70 },                     // David St east end
  wall_north: { x: -2, y: 40, z_ground: 12.5, z_eye: 1.6, heading: 95, pitch: -6, fov: 70 },   // rampart N of the gate
  citadel_tower: { x: 60, y: -15, z_ground: 26, z_eye: 1.6, heading: 75, pitch: -8, fov: 70 }, // over the whole city
};

// Jaffa Gate -> David St -> Christian Quarter St -> Aqabat el-Khanqa -> Khan ez-Zeit -> Damascus Gate
// (OSM centre lines, local plan metres)
export const ROUTE = [[12.4, -2.5], [25.4, -7.5], [47.8, -0.2], [58.4, 3.7], [69.5, 7.2], [82, 8.4], [94.5, 4.2], [96.7, 2.8],
  [106.4, 9.1], [115.4, 9.3], [135.9, 8.7], [159, 8.2], [175.6, 9.4], [175.3, 14.2], [174.6, 19.3], [173, 54.2], [170.5, 99.5],
  [169.3, 117.6], [167.8, 132.9], [166.8, 148.4], [165.2, 181.5], [160.3, 220.7], [159.4, 261.5], [189.7, 266.5], [206.8, 269.6],
  [262.7, 279.3], [285.1, 283.1], [299, 287.2], [317.2, 292.1], [313.8, 299.7], [312.7, 328.4], [311.3, 348.3], [309.4, 397.7],
  [307.4, 402.8], [305.9, 443.7], [303.8, 469.7], [303.7, 492.6], [308.3, 496.2], [262, 560]];

const quant = (arr) => {
  const f = [...arr].sort((a, b) => a - b);
  const q = (p) => +f[Math.min(f.length - 1, Math.floor(f.length * p))].toFixed(1);
  return { n: f.length, p50: q(0.5), p95: q(0.95), p99: q(0.99), max: +f[f.length - 1].toFixed(1), over34: f.filter((x) => x > 34).length };
};

// bench each view (AO on and off), best of `reps` runs of n frames
export async function benchViews(views = VIEWS, { n = 30, reps = 3 } = {}) {
  const game = window.game;
  const out = {};
  for (const [k, v] of Object.entries(views)) {
    await game.setCam(v);
    game.bench(5);
    const ao = [], noao = [];
    for (let i = 0; i < reps; i++) {
      game.setAO(true); ao.push(game.bench(n));
      game.setAO(false); noao.push(game.bench(n));
    }
    game.setAO(true);
    const p = game.perf();
    out[k] = { ao: +Math.min(...ao).toFixed(2), noao: +Math.min(...noao).toFixed(2), calls: p.calls, tris: p.tris,
      hi: game.sectors().filter((s) => s.state === 'hi').map((s) => s.id.slice(0, 3)).join(' ') };
  }
  return { gpu: game.gpu.name, size: [game.renderer.domElement.width, game.renderer.domElement.height], views: out };
}

// glide the camera along a polyline at running speed in the real rAF loop (collision off, feet on
// the ground height field): frame intervals, swaps, and the streaming work per step type
export async function glide({ route = ROUTE, secs = 60, speed = 6.5 } = {}) {
  const game = window.game, P = game.player, S = game.streamer, G = game.ground;
  const path = route.concat(route.slice(0, -1).reverse());
  const seg = []; let L = 0;
  for (let i = 1; i < path.length; i++) { const d = Math.hypot(path[i][0] - path[i - 1][0], path[i][1] - path[i - 1][1]); seg.push([L, d]); L += d; }
  const at = (s) => {
    s %= L;
    let i = seg.findIndex(([a, d]) => s <= a + d); if (i < 0) i = seg.length - 1;
    const [a, d] = seg[i], t = d ? (s - a) / d : 0, p = path[i], q = path[i + 1];
    return [p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t, Math.atan2(q[0] - p[0], q[1] - p[1])];
  };
  await game.teleport(path[0][0], path[0][1]);
  S.taskMs = {};
  P.held = true;
  const frames = [], ev0 = S.events.length;
  let s = 0, last = performance.now(), running = true;
  const loop = () => {
    if (!running) return;
    const now = performance.now(), dt = now - last;
    frames.push([dt, now]); last = now;
    s += (speed * Math.min(dt, 50)) / 1000;
    const [x, y, h] = at(s);
    P.pos.set(x, G.at(x, -y) + 1.4, -y); P.yaw = -h; P.pitch = 0;
    requestAnimationFrame(loop);
  };
  requestAnimationFrame(loop);
  await new Promise((r) => setTimeout(r, secs * 1000));
  running = false; P.held = false;
  const evs = S.events.slice(ev0);
  const nearSwap = frames.filter(([, t]) => evs.some((e) => t >= e.t - 50 && t <= e.t + 500)).map((x) => x[0]);
  return {
    metres: Math.round(s), frames: quant(frames.slice(5).map((x) => x[0])), nearSwapMax: nearSwap.length ? +Math.max(...nearSwap).toFixed(1) : null,
    swaps: evs.map((e) => `${e.id}${e.in ? '+' : '-'}`).join(' '),
    steps: Object.fromEntries(Object.entries(S.taskMs).map(([k, v]) => [k, { n: v.n, maxMs: +v.max.toFixed(1) }])),
  };
}

// walk with keys held through game.simFrame (works in hidden tabs); checks tunnelling: the
// knee-height segment between consecutive positions must not cross collision
export async function walk(secs, codes = ['KeyW'], { steer = null } = {}) {
  const game = window.game, T = game.THREE, P = game.player, S = game.streamer;
  const prev = P.pos.clone(), gaps = [], tunnels = [];
  const ev0 = S.events.length;
  let last = performance.now(), falls = 0;
  for (let i = 0; i < Math.round(secs * 60); i++) {
    if (steer) steer(P, i);
    const st = game.simFrame(1 / 60, codes);
    await yieldTask();
    const now = performance.now(); gaps.push(now - last); last = now;
    const a = prev.clone(), b = P.pos.clone(); a.y -= 0.9; b.y -= 0.9;
    const d = b.clone().sub(a), len = d.length();
    if (len > 1e-3 && !st.held) {
      const hits = game.collider.raycast(new T.Ray(a, d.clone().normalize()), T.DoubleSide).filter((h) => h.distance < len - 1e-3);
      if (hits.length) tunnels.push({ i, at: [+a.x.toFixed(2), +(-a.z).toFixed(2)] });
    }
    if (P.pos.y < prev.y - 3) falls++;
    prev.copy(P.pos);
  }
  return { gaps: quant(gaps), end: game.state(), falls, tunnels: tunnels.length, firstTunnels: tunnels.slice(0, 5),
    swaps: S.events.slice(ev0).map((e) => `${e.id}${e.in ? '+' : '-'}`).join(' ') };
}

// heading towards waypoints in turn
export function steerer(pts) {
  let k = 0;
  return (P) => {
    const x = P.pos.x, y = -P.pos.z;
    while (k < pts.length - 1 && Math.hypot(pts[k][0] - x, pts[k][1] - y) < 5) k++;
    P.yaw = -Math.atan2(pts[k][0] - x, pts[k][1] - y);
  };
}

window.devtest = { VIEWS, ROUTE, benchViews, glide, walk, steerer };
export default window.devtest;
