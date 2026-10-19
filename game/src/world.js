// Render conventions shared by the chunk builder (stream.js) and the frame pipeline (render.js).
// Geometry itself is merged in the loader worker (chunk.worker.js + merge.js):
//  - static geometry is merged per (material name, nocol); large groups are split into spatial
//    cells so frustum culling (view, AO prepass, near shadow cascade) can skip them
//  - every merged geometry has position/normal/uv/color; a missing COLOR_0 becomes white (the
//    vertex colour multiplies the base colour)
//  - meshes under a node with extras {"nocol": 1} stay out of the collision BVH

export const LAYER_NO_AO = 1;     // meshes that are not drawn into the AO depth/normal prepass
export const LAYER_FAR = 2;       // beyond their draw distance: no pass renders this layer
export const LAYER_SHADOW = 3;    // shadow-only casters: seen by the shadow pass alone
// opaque draw order: city, then the sky dome (only where nothing was drawn), then the cut-out
// depth twins, then the cut-outs themselves (alpha-to-coverage edges then blend over the sky)
export const RENDER_ORDER = { sky: 1, cutoutDepth: 2, cutout: 3 };
