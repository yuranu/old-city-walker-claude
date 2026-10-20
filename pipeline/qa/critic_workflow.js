export const meta = {
  name: 'qa-vision-critic',
  description: 'Vision critic over QA contact sheets for one level, each finding independently verified',
  phases: [
    { title: 'Critique', detail: 'one critic per batch of contact sheets' },
    { title: 'Verify', detail: 'independent skeptic per finding, on the full frame' },
  ],
}
// args: { level, run: "<abs run dir>", nbatches, per: 6 }  (sheets listed in <run>/sheets.json)
const RUBRIC = `Read /home/yuranu/projects/old-city-walker/data/qa/levels.md first: it defines the QA levels.`
const FIND = { type: 'object', properties: { findings: { type: 'array', items: { type: 'object', properties: {
  view: { type: 'string' }, kind: { type: 'string' }, severity: { type: 'string', enum: ['high', 'medium', 'low'] },
  what: { type: 'string' }, where_in_image: { type: 'string' } }, required: ['view', 'kind', 'severity', 'what', 'where_in_image'] } } },
  required: ['findings'] }
const VERDICT = { type: 'object', properties: { real: { type: 'boolean' }, why: { type: 'string' },
  cause_guess: { type: 'string' } }, required: ['real', 'why', 'cause_guess'] }

const level = args.level
const batches = Array.from({ length: args.nbatches }, (_, i) => i)
const results = await pipeline(batches,
  (i) => agent(`${RUBRIC}
You are a QA critic for a 3D recreation of Jerusalem's Old City (a three.js game). Look at each contact sheet image below with the Read tool. Each sheet holds 4 in-game frames labelled "N: <view id>" in yellow at the top-left of each quadrant.
Report every defect of LEVEL ${level} or lower according to levels.md, for each view where you see one. Be concrete: what is wrong and where in that frame (e.g. "lower left, the slab crossing the plaza"). Do not report things that are merely plain or low-detail unless the level asks for it. No defect -> no entry.
Your sheets: open ${args.run}/sheets.json and take entries ${i * args.per} to ${i * args.per + args.per - 1} (0-based; fewer if the list ends); each entry has "sheet" (image path) and "views" (the 4 view ids in order).`,
    { label: `critic:${i}`, phase: 'Critique', schema: FIND }),
  (r) => r ? parallel(r.findings.filter((f) => f.severity !== 'low').map((f) => () => agent(`${RUBRIC}
You verify one reported QA defect in a 3D recreation of Jerusalem's Old City. Open the full frame ${args.run}/${f.view}_n.png with the Read tool (also ${args.run}/${f.view}_k.png: the same frame with the sky keyed, magenta = sky seen below the horizon = a hole).
Claimed defect (level ${level}): ${f.what} — at: ${f.where_in_image}.
Is it real, i.e. would a player see this as a level-${level} problem? Default to real=false if you cannot see it clearly. Also guess the cause in generator terms (e.g. "retaining wall slab from flat edges", "stair treads overlapping", "ground triangulation spike", "building footprint across street", "prop floating", "missing texture").`,
      { label: `verify:${f.view}`, phase: 'Verify', schema: VERDICT }).then((v) => ({ ...f, verdict: v })))) : [],
)
return results.filter(Boolean).flat().filter((f) => f && f.verdict && f.verdict.real)
