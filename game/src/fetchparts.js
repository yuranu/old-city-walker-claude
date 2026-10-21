// Files the deploy step split (static hosts cap the size of one file, Cloudflare Pages at 25 MiB) are
// referenced as "name.glb#parts=N" and served as name.glb.part0 .. name.glb.part{N-1}; the fragment
// never reaches the server. fetchJoined fetches the parts in parallel and joins them; an unsplit URL
// is one plain fetch. onProgress(loaded, total) as the bytes arrive.

export function partUrls(url) {
  const u = new URL(url, self.location.href);
  const m = /(?:^|&)parts=(\d+)/.exec(u.hash.slice(1));
  u.hash = '';
  if (!m || +m[1] < 2) return [u.href];
  const out = [];
  for (let k = 0; k < +m[1]; k++) {
    const p = new URL(u.href);
    p.pathname += `.part${k}`;
    out.push(p.href);
  }
  return out;
}

export async function fetchJoined(url, onProgress) {
  const urls = partUrls(url);
  const rs = await Promise.all(urls.map((u) => fetch(u)));
  for (let k = 0; k < rs.length; k++) if (!rs[k].ok) throw new Error(`${urls[k]}: HTTP ${rs[k].status}`);
  const total = rs.reduce((s, r) => s + (+r.headers.get('content-length') || 0), 0);
  const chunks = [];
  let got = 0, last = 0;
  for (const r of rs) {                       // read in order (they download in parallel meanwhile)
    if (!r.body) { const b = new Uint8Array(await r.arrayBuffer()); chunks.push(b); got += b.length; continue; }
    const reader = r.body.getReader();
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      chunks.push(value);
      got += value.length;
      const now = performance.now();
      if (onProgress && now - last > 80) { last = now; onProgress(got, total); }
    }
  }
  if (onProgress) onProgress(got, total || got);
  if (chunks.length === 1 && chunks[0].byteOffset === 0 && chunks[0].byteLength === chunks[0].buffer.byteLength) return chunks[0].buffer;
  const out = new Uint8Array(got);
  let o = 0;
  for (const c of chunks) { out.set(c, o); o += c.length; }
  return out.buffer;
}
