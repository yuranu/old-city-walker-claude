// Static deploy build: dist/ = vite build, minus files the game never loads, with every model
// meshopt-compressed and anything still over the host's per-file cap split into parts.
//
//   node scripts/deploy_build.mjs [--max-mib 24] [--jobs 2]
//
// * compression: gltfpack -cc (EXT_meshopt_compression, decoded in the loader worker, src/gltf.js) with
//   names, materials, extras and all vertex attributes kept (the streamer needs node names, material
//   names, nocol/draw_dist; UVs look unused to gltfpack because the textures live in materials.glb)
//   and no quantization (positions are world coordinates: quantizing them moved geometry visibly).
//   base/materials.glb is left alone (it is the texture palette, a handful of quads).
// * splitting: Cloudflare Pages refuses files over 25 MiB. A bigger file becomes name.part0..N-1 and its
//   manifest entry name#parts=N (src/fetchparts.js joins the parts).
import { execFile } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { promisify } from 'node:util';
import { fileURLToPath } from 'node:url';

const run = promisify(execFile);
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const DIST = path.join(ROOT, 'dist');
const arg = (k, d) => { const i = process.argv.indexOf('--' + k); return i > 0 ? process.argv[i + 1] : d; };
const MAX = Math.floor(+arg('max-mib', 24) * 1024 * 1024);
const JOBS = +arg('jobs', 2);
const DROP = ['city.glb', 'mock'];          // not loaded by the game in sector mode (legacy single model, test fixtures)
const mib = (n) => (n / 1048576).toFixed(1);

function walk(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((e) =>
    e.isDirectory() ? walk(path.join(dir, e.name)) : [path.join(dir, e.name)]);
}

async function pool(items, n, fn) {
  const q = items.slice();
  await Promise.all(Array.from({ length: n }, async () => { while (q.length) await fn(q.shift()); }));
}

const t0 = Date.now();
console.log('vite build ...');
await run(path.join(ROOT, 'node_modules/.bin/vite'), ['build', '--emptyOutDir'], { cwd: ROOT, maxBuffer: 1 << 26 });
for (const d of DROP) fs.rmSync(path.join(DIST, d), { recursive: true, force: true });

const glbs = walk(DIST).filter((f) => f.endsWith('.glb') && !f.endsWith('materials.glb'));
let before = 0, after = 0;
console.log(`compressing ${glbs.length} models ...`);
await pool(glbs, JOBS, async (f) => {
  const tmp = f + '.tmp.glb';
  const b = fs.statSync(f).size;
  await run(path.join(ROOT, 'node_modules/.bin/gltfpack'), ['-i', f, '-o', tmp, '-cc', '-kn', '-km', '-ke', '-kv', '-noq'],
    { maxBuffer: 1 << 26 });
  fs.renameSync(tmp, f);
  const a = fs.statSync(f).size;
  before += b; after += a;
  console.log(`  ${path.relative(DIST, f)}  ${mib(b)} -> ${mib(a)} MiB`);
});

const parts = {};                                             // relative path -> number of parts
for (const f of walk(DIST)) {
  const size = fs.statSync(f).size;
  if (size <= MAX) continue;
  const buf = fs.readFileSync(f);
  const n = Math.ceil(size / MAX);
  for (let k = 0; k < n; k++) fs.writeFileSync(`${f}.part${k}`, buf.subarray(k * MAX, Math.min(size, (k + 1) * MAX)));
  fs.rmSync(f);
  parts[path.relative(DIST, f).split(path.sep).join('/')] = n;
  console.log(`  split ${path.relative(DIST, f)} (${mib(size)} MiB) into ${n} parts`);
}

const manPath = path.join(DIST, 'sectors.json');
const man = JSON.parse(fs.readFileSync(manPath, 'utf8'));
const ref = (p) => (p && parts[p] ? `${p}#parts=${parts[p]}` : p);
man.materials = ref(man.materials);
man.always = (man.always || []).map(ref);
if (man.ground) man.ground = [].concat(man.ground).map(ref);
for (const s of man.sectors) { s.hi = ref(s.hi); s.lo = ref(s.lo); }
fs.writeFileSync(manPath, JSON.stringify(man, null, 1));
const unsplit = Object.keys(parts).filter((p) => !JSON.stringify(man).includes(`${p}#parts=`));
if (unsplit.length) throw new Error(`split files the manifest does not reference: ${unsplit.join(', ')}`);

const files = walk(DIST);
const total = files.reduce((s, f) => s + fs.statSync(f).size, 0);
const biggest = Math.max(...files.map((f) => fs.statSync(f).size));
console.log(`models ${mib(before)} -> ${mib(after)} MiB; dist ${files.length} files, ${mib(total)} MiB, ` +
  `largest ${mib(biggest)} MiB; ${Object.keys(parts).length} split; ${((Date.now() - t0) / 1000).toFixed(0)} s`);
if (files.length > 20000 || biggest > 25 * 1048576) throw new Error('over the Cloudflare Pages limits');
