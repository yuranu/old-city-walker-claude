export const meta = {
  name: 'qa-sv-critic',
  description: 'Reference critic: REAL (Street View) | MODEL pairs per place or region, each finding independently verified',
  phases: [
    { title: 'Critique', detail: 'one critic per batch of places, comparing every pair with reality' },
    { title: 'Verify', detail: 'independent skeptic per batch, checking each finding on its pair image' },
  ],
}
// args: { root: "<abs repo>", batches: [["austrian_hospice", ...], ...] } (or places: [...], one batch each)
// Pairs: <root>/build/qa/svcmp/<place>/pairs/*.jpg (left REAL, right MODEL, same spot / heading / field of view,
// headings aligned by skyline matching; build with pipeline/qa/sv_ref.py + sv_compare.py).
const FIND = { type: 'object', properties: {
  useless: { type: 'array', items: { type: 'string' } },
  findings: { type: 'array', items: { type: 'object', properties: {
    place: { type: 'string' }, pair: { type: 'string' }, severity: { type: 'string', enum: ['high', 'medium', 'low'] },
    kind: { type: 'string', enum: ['missing', 'invented', 'massing', 'openings', 'ground', 'roof', 'broken', 'material', 'other'] },
    real: { type: 'string' }, model: { type: 'string' }, where: { type: 'string' } },
    required: ['place', 'pair', 'severity', 'kind', 'real', 'model', 'where'] } } },
  required: ['useless', 'findings'] }
const VERDICTS = { type: 'object', properties: { verdicts: { type: 'array', items: { type: 'object', properties: {
  index: { type: 'integer' }, real: { type: 'boolean' }, why: { type: 'string' }, fix_hint: { type: 'string' } },
  required: ['index', 'real', 'why', 'fix_hint'] } } }, required: ['verdicts'] }

const RULES = `Each image is REAL (Google Street View, left half) | MODEL (the game, right half) from the same position, compass heading and field of view; the headings were aligned by matching skylines, positions can still be 1-3 m off.
Ignore: people, cars, signs, cables, shop goods, awnings, lighting, weather, texture resolution, colour grading.
Report STRUCTURAL differences a visitor would notice: buildings/walls/compound walls missing or invented, wrong heights or storey counts, wrong massing or roofline, missing or blind openings (gates, doors, arches, portals), wrong ground (stairs, ramps, levels, a road shown as a plaza), wrong roof or dome shape, broken or floating geometry, strongly wrong material (rubble vs ashlar, stone colour far off).
A pair is useless (list it, report nothing from it) when the two halves clearly do not show the same scene: the MODEL camera is inside a wall or building, or REAL is indoors / in a tunnel while MODEL is outdoors.`

// places go in batches (args.batches: [[place, ...], ...]); one verifier per batch checks all its findings
const batches = args.batches || args.places.map((p) => [p])
const results = await pipeline(batches,
  (ps) => agent(`You compare a 3D recreation of Jerusalem's Old City with reality at these places: ${ps.join(', ')}.
For each place open every image in ${args.root}/build/qa/svcmp/<place>/pairs/ with the Read tool (list the directory first).
${RULES}
For each finding give: place, pair (file name without .jpg), severity (high = this recognisable place looks wrong; medium = noticeable; low = minor), kind, what REAL shows, what MODEL shows, where in the frame. Be concrete and short; at most 10 findings a place, the most important first.`,
    { label: `critic:${ps[0]}+${ps.length - 1}`, phase: 'Critique', schema: FIND }),
  (r) => {
    if (!r) return null
    const fs = r.findings.filter((f) => f.severity !== 'low')
    if (!fs.length) return { useless: r.useless, findings: [] }
    return agent(`You verify claimed differences between reality and a 3D recreation of Jerusalem's Old City. ${RULES}
For each claim below open its pair image ${args.root}/build/qa/svcmp/<place>/pairs/<pair>.jpg with the Read tool and decide: is it correct and structural (not an artefact of the 1-3 m position error, people/cars or lighting)? Default to real=false if unsure. If real, hint the fix in generator terms (e.g. "OSM wall missing", "gate opening too narrow", "building height too low", "infill building in a courtyard", "terrain flat where the street slopes").
Return one verdict per claim, in the same order, with its index.
${fs.map((f, i) => `${i}. [${f.place}/${f.pair}] (${f.kind}, ${f.severity}) at ${f.where}: REAL ${f.real}; MODEL ${f.model}`).join('\n')}`,
      { label: `verify:${fs[0].place}`, phase: 'Verify', schema: VERDICTS })
      .then((v) => ({ useless: r.useless, findings: fs.map((f, i) => ({ ...f, verdict: (v.verdicts || []).find((x) => x.index === i) }))
        .filter((f) => f.verdict && f.verdict.real) }))
  },
)
return results.filter(Boolean)
