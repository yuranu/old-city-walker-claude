// Material setup by name (contract with blender/materials.py) and the shader injections shared by
// every city material:
//  - screen-space AO from the half-res GTAO buffer, joint-bilateral upsampled and applied to the
//    indirect light (plus a little of the direct light), so sunlit walls do not get dark halos
//  - haze: distance fog towards the sky's own horizon colour in that direction (a 1D LUT baked
//    from the sky), applied before tone mapping so distant stone melts into the sky
// and, for the stone materials only:
//  - low-frequency world-space macro variation of the albedo (brightness and a warm/cool drift)
//    that breaks up texture tiling, from a small tiling 3D noise texture
//  - ground grime: walls darken and brown towards their foot, fading out by ~1.2 m above the
//    local ground, read from a height texture raycast from the collision BVH at load
import * as THREE from 'three';

export const STONE = new Set(['ashlar', 'rubble', 'fort', 'dressed', 'paving', 'setts', 'herodian']);
const CUTOUT = new Set(['cut', 'signs']);
const DECAL = new Set(['decal']);

// uniforms shared by reference with every injected program
export const U = {
  ocAO: { value: null },
  ocAOParams: { value: new THREE.Vector4(0.5, 0.5, 0, 0.3) },   // xy full->AO px scale, z intensity, w direct share
  ocFogLUT: { value: null },
  ocHaze: { value: new THREE.Vector4(1 / 1400, 1, 0, 0) },       // x: extinction per metre, y: sky scale
  ocNoise: { value: null },
  ocMacro: { value: new THREE.Vector4(0.08, 0.035, 1 / 9.0, 1 / 37.0) }, // brightness amp, hue amp, freq A, freq B
  ocGround: { value: null },
  ocGroundXf: { value: new THREE.Vector4(0, 0, 1, 1) },          // minX, minZ, 1/sizeX, 1/sizeZ
  ocGrime: { value: new THREE.Vector4(0.74, 0.67, 0.58, 1.0) },  // albedo multiplier at the very foot, strength
  ocGrimeH: { value: 1.2 },
  ocPalette: { value: null },                                    // merged flat materials (see setupFlat)
};

const white = new THREE.DataTexture(new Uint8Array([255, 255, 255, 255]), 1, 1);
white.needsUpdate = true;
U.ocAO.value = white;
U.ocFogLUT.value = white;

// tiling 3D value noise, blurred so trilinear filtering gives a smooth field; channels are
// independent: r brightness, g hue, b grime-edge jitter
export function makeNoise3D(N = 32, seed = 7) {
  let s = seed >>> 0;
  const rnd = () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296);
  const n3 = N * N * N;
  const ch = [0, 1, 2].map(() => {
    let a = new Float32Array(n3);
    for (let i = 0; i < n3; i++) a[i] = rnd();
    // 3 separable box blurs (radius 1, wrapping) ~ gaussian
    const b = new Float32Array(n3);
    const idx = (x, y, z) => ((z + N) % N) * N * N + ((y + N) % N) * N + ((x + N) % N);
    for (let pass = 0; pass < 3; pass++) {
      for (const [dx, dy, dz] of [[1, 0, 0], [0, 1, 0], [0, 0, 1]]) {
        for (let z = 0; z < N; z++) for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) {
          b[idx(x, y, z)] = (a[idx(x - dx, y - dy, z - dz)] + a[idx(x, y, z)] + a[idx(x + dx, y + dy, z + dz)]) / 3;
        }
        a.set(b);
      }
    }
    // normalise to mean 0.5, +-2 sigma -> [0, 1]
    let m = 0, v = 0;
    for (let i = 0; i < n3; i++) m += a[i];
    m /= n3;
    for (let i = 0; i < n3; i++) v += (a[i] - m) ** 2;
    const sd = Math.sqrt(v / n3) || 1;
    for (let i = 0; i < n3; i++) a[i] = THREE.MathUtils.clamp(0.5 + (a[i] - m) / (4 * sd), 0, 1);
    return a;
  });
  const data = new Uint8Array(n3 * 4);
  for (let i = 0; i < n3; i++) {
    data[i * 4] = ch[0][i] * 255;
    data[i * 4 + 1] = ch[1][i] * 255;
    data[i * 4 + 2] = ch[2][i] * 255;
    data[i * 4 + 3] = 255;
  }
  const t = new THREE.Data3DTexture(data, N, N, N);
  t.format = THREE.RGBAFormat;
  t.type = THREE.UnsignedByteType;
  t.minFilter = t.magFilter = THREE.LinearFilter;
  t.wrapS = t.wrapT = t.wrapR = THREE.RepeatWrapping;
  t.unpackAlignment = 1;
  t.needsUpdate = true;
  return t;
}
U.ocNoise.value = makeNoise3D();

const VERT_PARS = /* glsl */`
varying vec3 vOcWorld;
#ifdef OC_STONE
varying vec3 vOcNormal;
#endif
`;
const VERT_MAIN = /* glsl */`
vOcWorld = ( modelMatrix * vec4( transformed, 1.0 ) ).xyz;
#ifdef OC_STONE
vOcNormal = normalize( mat3( modelMatrix ) * objectNormal );
#endif
`;

const FRAG_PARS = /* glsl */`
varying vec3 vOcWorld;
uniform sampler2D ocAO;
uniform vec4 ocAOParams;
uniform sampler2D ocFogLUT;
uniform vec4 ocHaze;
// joint-bilateral upsample of the half-res AO: weights the 4 nearest low-res texels by their
// bilinear weight and by how close their view depth (stored in .g) is to this fragment's
float ocSSAO( float zf ) {
  vec2 p = gl_FragCoord.xy * ocAOParams.xy - 0.5;
  vec2 f = fract( p );
  ivec2 i0 = ivec2( floor( p ) );
  ivec2 mx = textureSize( ocAO, 0 ) - 1;
  vec2 s00 = texelFetch( ocAO, clamp( i0, ivec2( 0 ), mx ), 0 ).rg;
  vec2 s10 = texelFetch( ocAO, clamp( i0 + ivec2( 1, 0 ), ivec2( 0 ), mx ), 0 ).rg;
  vec2 s01 = texelFetch( ocAO, clamp( i0 + ivec2( 0, 1 ), ivec2( 0 ), mx ), 0 ).rg;
  vec2 s11 = texelFetch( ocAO, clamp( i0 + ivec2( 1, 1 ), ivec2( 0 ), mx ), 0 ).rg;
  vec4 wb = vec4( ( 1.0 - f.x ) * ( 1.0 - f.y ), f.x * ( 1.0 - f.y ), ( 1.0 - f.x ) * f.y, f.x * f.y );
  vec4 dz = abs( vec4( s00.y, s10.y, s01.y, s11.y ) - zf ) / ( 0.03 * zf + 0.05 );
  vec4 w = wb * max( 1.0 - dz, 0.0 );
  float tw = w.x + w.y + w.z + w.w;
  return tw > 1e-3 ? dot( w, vec4( s00.x, s10.x, s01.x, s11.x ) ) / tw : 1.0;
}
#ifdef OC_FLAT
uniform highp sampler2D ocPalette;
#endif
#ifdef OC_STONE
varying vec3 vOcNormal;
uniform highp sampler3D ocNoise;
uniform vec4 ocMacro;
uniform sampler2D ocGround;
uniform vec4 ocGroundXf;
uniform vec4 ocGrime;
uniform float ocGrimeH;
#endif
`;

const FRAG_STONE = /* glsl */`
#ifdef OC_STONE
{
  vec4 nA = texture( ocNoise, vOcWorld * ocMacro.z );
  vec4 nB = texture( ocNoise, vOcWorld * ocMacro.w + vec3( 0.37, 0.11, 0.73 ) );
  float br = ( nA.r * 0.4 + nB.r * 0.6 ) * 2.0 - 1.0;
  float hue = nB.g * 2.0 - 1.0;
  diffuseColor.rgb *= ( 1.0 + br * ocMacro.x ) * ( 1.0 + hue * ocMacro.y * vec3( 1.0, 0.15, -1.1 ) );
  // ground grime on vertical faces; the ground height is read a little in front of the face so
  // walls see the street, not the roof behind them
  vec3 n = normalize( vOcNormal );
  float vert = 1.0 - smoothstep( 0.45, 0.8, abs( n.y ) );
  if ( vert > 0.0 ) {
    vec2 gp = vOcWorld.xz + n.xz * 0.9;
    float g = textureLod( ocGround, ( gp - ocGroundXf.xy ) * ocGroundXf.zw, 0.0 ).r;
    float h = ( vOcWorld.y - g ) / ocGrimeH + ( nA.b - 0.5 ) * 0.35;
    float k = vert * ( 1.0 - smoothstep( 0.0, 1.0, h ) ) * ocGrime.a;
    diffuseColor.rgb *= mix( vec3( 1.0 ), ocGrime.rgb, k );
  }
}
#endif
`;

// merged flat material: the vertex colour's alpha byte is a palette index; row 0 of the palette
// is the base colour, row 1 roughness / metalness, row 2 emissive
const FRAG_FLAT = /* glsl */`
#ifdef OC_FLAT
int ocIdx = int( vColor.a * 255.0 + 0.5 );
diffuseColor.rgb *= texelFetch( ocPalette, ivec2( ocIdx, 0 ), 0 ).rgb;
diffuseColor.a = opacity;
vec4 ocPal1 = texelFetch( ocPalette, ivec2( ocIdx, 1 ), 0 );
#endif
`;

const FRAG_AO = /* glsl */`
if ( ocAOParams.z > 0.0 ) {
  float ocA = mix( 1.0, ocSSAO( vViewPosition.z ), ocAOParams.z );
  reflectedLight.indirectDiffuse *= ocA;
  reflectedLight.indirectSpecular *= ocA;
  float ocD = mix( 1.0, ocA, ocAOParams.w );
  reflectedLight.directDiffuse *= ocD;
  reflectedLight.directSpecular *= ocD;
}
`;

const FRAG_HAZE = /* glsl */`
{
  vec3 v = vOcWorld - cameraPosition;
  float d = length( v );
  vec3 dir = v / max( d, 1e-4 );
  float az = atan( dir.x, - dir.z ) * 0.15915494 + 0.5;
  vec3 hc = texture2D( ocFogLUT, vec2( az, 0.5 ) ).rgb * ocHaze.y;
  float f = 1.0 - exp( - d * ocHaze.x );
  gl_FragColor.rgb = mix( gl_FragColor.rgb, hc, f );
}
`;

function inject(material, stone, flat = false) {
  material.onBeforeCompile = (shader) => {
    Object.assign(shader.uniforms, U);
    const pre = (stone ? '#define OC_STONE\n' : '') + (flat ? '#define OC_FLAT\n' : '');
    shader.vertexShader = pre + shader.vertexShader
      .replace('#include <common>', '#include <common>\n' + VERT_PARS)
      .replace('#include <project_vertex>', '#include <project_vertex>\n' + VERT_MAIN);
    shader.fragmentShader = pre + shader.fragmentShader
      .replace('#include <common>', '#include <common>\n' + FRAG_PARS)
      .replace('#include <color_fragment>', '#include <color_fragment>\n' + FRAG_STONE + FRAG_FLAT)
      .replace('#include <roughnessmap_fragment>', '#include <roughnessmap_fragment>\n#ifdef OC_FLAT\nroughnessFactor = ocPal1.r;\n#endif')
      .replace('#include <metalnessmap_fragment>', '#include <metalnessmap_fragment>\n#ifdef OC_FLAT\nmetalnessFactor = ocPal1.g;\n#endif')
      .replace('#include <emissivemap_fragment>', '#include <emissivemap_fragment>\n#ifdef OC_FLAT\ntotalEmissiveRadiance = texelFetch( ocPalette, ivec2( ocIdx, 2 ), 0 ).rgb;\n#endif')
      .replace('#include <aomap_fragment>', '#include <aomap_fragment>\n' + FRAG_AO)
      .replace('#include <opaque_fragment>', '#include <opaque_fragment>\n' + FRAG_HAZE);
  };
  material.customProgramCacheKey = () => (stone ? 'oc-stone-1' : flat ? 'oc-flat-1' : 'oc-base-1');
  material.needsUpdate = true;
}

// returns { castShadow, ao, cutout } flags for meshes using this material
export function setupMaterial(m, anisotropy) {
  const name = (m.name || '').toLowerCase();
  if (!m.isMeshStandardMaterial) return { castShadow: true, ao: true, cutout: false };
  for (const key of ['map', 'normalMap', 'roughnessMap']) {
    if (m[key]) m[key].anisotropy = anisotropy;
  }
  let castShadow = true, ao = true, cutout = false;
  m.side = THREE.DoubleSide;     // the exporter marks everything double sided anyway
  m.shadowSide = null;
  if (CUTOUT.has(name)) {
    // grilles, railings, fan lights, foliage cards, signs: alpha test (alpha to coverage under
    // MSAA for soft edges); the shadow pass alpha-tests too (map + alphaTest on the material)
    m.transparent = false;
    m.depthWrite = true;
    m.alphaTest = 0.5;
    m.alphaToCoverage = true;
    m.blending = THREE.NormalBlending;
    ao = false;
    cutout = true;
  } else if (DECAL.has(name)) {
    m.transparent = true;
    m.depthWrite = false;
    m.alphaTest = 0.02;
    m.polygonOffset = true;
    m.polygonOffsetFactor = -2;
    m.polygonOffsetUnits = -4;
    castShadow = false;
    ao = false;
  } else if (m.transparent && m.map) {
    // unknown blended texture: treat as a cut-out
    m.transparent = false; m.depthWrite = true; m.alphaTest = 0.5; m.alphaToCoverage = true;
    ao = false;
    cutout = true;
  }
  if (name === 'void') { m.roughness = 1; m.metalness = 0; }      // darkness behind grilles
  if (name === 'glass_lamp') { m.emissive = new THREE.Color(0x2a2214); }
  inject(m, STONE.has(name));
  return { castShadow, ao, cutout };
}

// Untextured materials (plastic, lime, metals, wood...) differ only in factors, so they draw as
// one merged material each for "no sky reflection" and "sky reflection": the loader worker writes
// a palette index into every vertex (colour alpha) and the base colour, roughness, metalness and
// emissive come from this palette. Cuts a draw call per flat material per render cell and pass.
// entries: [{ mat }] in palette order (index = position); returns the palette texture.
export function makePalette(entries) {
  const n = Math.max(1, entries.length);
  const data = new Float32Array(n * 3 * 4);
  entries.forEach(({ mat: m }, i) => {
    data.set([m.color.r, m.color.g, m.color.b, 1], i * 4);
    data.set([m.roughness, m.metalness, 0, 1], (n + i) * 4);
    const e = m.emissive ? m.emissive.clone().multiplyScalar(m.emissiveIntensity ?? 1) : new THREE.Color(0);
    data.set([e.r, e.g, e.b, 1], (2 * n + i) * 4);
  });
  const t = new THREE.DataTexture(data, n, 3, THREE.RGBAFormat, THREE.FloatType);
  t.minFilter = t.magFilter = THREE.NearestFilter;
  t.needsUpdate = true;
  U.ocPalette.value = t;
  return t;
}

export function setupFlat(m) {
  m.side = THREE.DoubleSide;
  m.shadowSide = null;
  m.vertexColors = true;
  inject(m, false, true);
  return { castShadow: true, ao: true, cutout: false };
}
