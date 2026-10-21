// Frame pipeline (no EffectComposer):
//   1. AO prepass at half resolution: view normals + depth of the opaque city (alpha cut-outs,
//      decals and props on LAYER_NO_AO are skipped), no shadows, no sky
//   2. GTAO + Poisson denoise at half resolution on that G-buffer (three's GTAOPass internals);
//      the denoise writes AO in .r and linear view depth in .g for the bilateral upsample
//   3. main pass straight into the canvas: native 4x MSAA, tone mapping in the shaders, AO read
//      by every city material and applied to indirect light, sky drawn last behind everything
// Shadows: SunLight with two cascades fitted to the view, snapped in light space (sunshadow.js).
import * as THREE from 'three';
import { Sky } from 'three/examples/jsm/objects/Sky.js';
import { SunLight } from 'three/examples/jsm/lights/SunLight.js';
import { GTAOPass } from 'three/examples/jsm/postprocessing/GTAOPass.js';
import { StableSunShadow, patchSunShadowChunk } from './sunshadow.js';
import { U } from './materials.js';
import { LAYER_NO_AO, LAYER_SHADOW, RENDER_ORDER } from './world.js';

patchSunShadowChunk();

// Warm Jerusalem afternoon: sun in the WSW, low and golden.
// three: x = east, z = -north; the spherical azimuth (from +z towards +x) is 180 - compass.
export const LIGHT = {
  sunCompass: 250, sunElev: 27,
  sunColor: 0xffcf96, sunIntensity: 4.8,
  // the hemisphere light stands for the warm bounce from sunlit stone (the ground and the
  // facades across the square); the cool sky fill comes from an SH light probe of the same sky
  // as the dome. Together they keep the shade a cool, slightly warm-tinged grey.
  hemiSky: 0x786a5a, hemiGround: 0xb6a58a, hemiIntensity: 0.55,
  envIntensity: 0.19,  // sky probe (and metal reflections)
  exposure: 1.7,      // AgX: highlights roll off to cream instead of clipping to white/yellow
  haze: 1 / 4000,     // extinction per metre: a hint of haze on the far buildings
  skyScale: 0.25,     // sky radiance -> scene units (dome and haze colour), so sunlit limestone
                      // ends up brighter than the horizon sky, as in reality
  sky: { turbidity: 4.2, rayleigh: 1.25, mieCoefficient: 0.0042, mieDirectionalG: 0.8,
    cloudCoverage: 0.18, cloudDensity: 0.32, cloudElevation: 0.55 },
};

// Phones and tablets (coarse pointer) get a lighter profile: no MSAA or AO, lower resolution, a smaller
// shadow map and sky cube (?mobile=1 / ?mobile=0 force it either way, for testing on a desktop)
const QS = new URLSearchParams(location.search);
export const MOBILE = QS.has('mobile') ? QS.get('mobile') !== '0' : matchMedia('(pointer: coarse)').matches;

export class Pipeline {
  constructor(canvas) {
    this.canvas = canvas;
    const r = (this.renderer = new THREE.WebGLRenderer({
      canvas, antialias: !MOBILE, preserveDrawingBuffer: !MOBILE, powerPreference: 'high-performance',
    }));
    // render-to-float support: many phone GPUs have neither (rendering into such a target fails
    // silently and the frame never draws); ?nofloat=1 / ?nohalf=1 simulate their absence
    const gl = r.getContext();
    const float = !QS.has('nofloat') && !QS.has('nohalf') && !!gl.getExtension('EXT_color_buffer_float');
    const half = float || (!QS.has('nohalf') && !!gl.getExtension('EXT_color_buffer_half_float'));
    this.caps = { float, half, mobile: MOBILE };
    this.maxPR = Math.min(window.devicePixelRatio || 1, MOBILE ? 1.25 : 1.5);
    this.minPR = 0.6;
    this.pixelRatio = this.maxPR;
    r.setPixelRatio(this.pixelRatio);
    r.toneMapping = THREE.AgXToneMapping;
    r.toneMappingExposure = LIGHT.exposure;
    r.shadowMap.enabled = true;
    r.shadowMap.type = THREE.PCFShadowMap;
    r.shadowMap.autoUpdate = false;     // rendered once per frame, in the main pass only
    r.info.autoReset = false;
    // shadow-only casters (one merged depth mesh per render cell, see stream.js) live on their own
    // layer: three filters shadow casters by the view camera's layers, so enable it just there
    const sm = r.shadowMap, smRender = sm.render.bind(sm);
    sm.render = (lights, scene, camera) => {
      const mask = camera.layers.mask;
      camera.layers.enable(LAYER_SHADOW);
      smRender(lights, scene, camera);
      camera.layers.mask = mask;
    };

    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(70, 1, 0.2, 1200);
    this.camera.layers.enable(LAYER_NO_AO);
    this.useAO = !MOBILE;
    this.aoScale = 0.5;

    this._setupLights();
    this._setupSky();
    this._setupAO();
  }

  _setupLights() {
    const L = LIGHT;
    this.sunDir = new THREE.Vector3().setFromSphericalCoords(
      1, THREE.MathUtils.degToRad(90 - L.sunElev), THREE.MathUtils.degToRad(180 - L.sunCompass));
    const sun = (this.sun = new SunLight(L.sunColor, L.sunIntensity));
    sun.position.copy(this.sunDir).multiplyScalar(100);
    sun.castShadow = true;
    sun.shadow = new StableSunShadow();
    sun.shadow.mapSize.set(MOBILE ? 1024 : 2048, MOBILE ? 1024 : 2048);
    sun.shadow.camera.near = 0.5;
    sun.shadow.camera.far = 170;          // shadow distance
    sun.shadow.split = 24;
    sun.shadow.normalBias = 0.9;          // texels (scaled per cascade)
    sun.shadow.texelBias = -0.35;         // texels towards the light
    sun.shadow.radius = 1.4;
    this.scene.add(sun);
    this.hemi = new THREE.HemisphereLight(L.hemiSky, L.hemiGround, L.hemiIntensity);
    this.scene.add(this.hemi);
    this.skyProbe = new THREE.LightProbe();
    this.scene.add(this.skyProbe);
    this.metals = [];           // materials that get the PMREM sky as envMap (see bakeSky)
  }

  // metals and glossy materials keep real sky reflections
  addReflective(m) {
    if (this.metals.includes(m)) return;
    this.metals.push(m);
    m.envMap = this.envRT ? this.envRT.texture : null;
    m.envMapIntensity = LIGHT.envIntensity;
    m.needsUpdate = true;
  }

  removeReflective(m) {
    const i = this.metals.indexOf(m);
    if (i >= 0) this.metals.splice(i, 1);
  }

  setEnvIntensity(v) {
    LIGHT.envIntensity = v;
    this.skyProbe.intensity = v;
    for (const m of this.metals) m.envMapIntensity = v;
  }

  // The physical sky is baked once into a cube map (it was the most expensive full-screen shader
  // per pixel: scattering + fbm clouds) and drawn after the opaque city with a depth test, so
  // only visible sky pixels are shaded. The same cube feeds the sky light probe, the metals' PMREM and the haze LUT.
  _setupSky() {
    const skyType = this.caps.half ? THREE.HalfFloatType : THREE.UnsignedByteType;     // (8 bit clips the sun's glow)
    this.skyCube = new THREE.WebGLCubeRenderTarget(MOBILE ? 512 : 1024, { type: skyType, generateMipmaps: false });
    this.fogLUT = new THREE.WebGLRenderTarget(64, 1, { type: skyType, depthBuffer: false });
    this.fogLUT.texture.wrapS = THREE.RepeatWrapping;
    this.fogLUT.texture.minFilter = this.fogLUT.texture.magFilter = THREE.LinearFilter;
    U.ocFogLUT.value = this.fogLUT.texture;
    U.ocHaze.value.set(LIGHT.haze, LIGHT.skyScale, 0, 0);

    // sky dome: rendered after the opaque city at depth 1.0 (before the alpha cut-outs)
    const dome = new THREE.Mesh(new THREE.BoxGeometry(2, 2, 2), new THREE.ShaderMaterial({
      name: 'SkyDome',
      uniforms: {
        tSky: { value: this.skyCube.texture },
        sunDir: { value: this.sunDir },
        sunDisc: { value: new THREE.Color(LIGHT.sunColor).multiplyScalar(40) },
        skyScale: U.ocHaze,
        qaKey: { value: 0 },     // QA: sky below the horizon drawn pure magenta (holes show as magenta)
      },
      vertexShader: /* glsl */`
        varying vec3 vDir;
        void main() {
          vDir = position;
          vec4 p = projectionMatrix * mat4( mat3( viewMatrix ) ) * vec4( position, 1.0 );
          gl_Position = p.xyww;
        }`,
      fragmentShader: /* glsl */`
        uniform samplerCube tSky;
        uniform vec3 sunDir;
        uniform vec3 sunDisc;
        uniform vec4 skyScale;
        uniform float qaKey;
        varying vec3 vDir;
        void main() {
          vec3 d = normalize( vDir );
          vec3 c = textureCube( tSky, d ).rgb * skyScale.y;
          float cs = dot( d, sunDir );
          c += sunDisc * smoothstep( 0.999985, 0.999992, cs );   // ~0.3 deg disc
          gl_FragColor = vec4( c, 1.0 );
          #include <tonemapping_fragment>
          #include <colorspace_fragment>
          if ( qaKey > 0.5 ) gl_FragColor = d.y < 0.0 ? vec4( 1.0, 0.0, 1.0, 1.0 ) : vec4( 0.0, 1.0, 1.0, 1.0 );
        }`,
      side: THREE.BackSide, depthWrite: false,
    }));
    dome.frustumCulled = false;
    dome.renderOrder = RENDER_ORDER.sky;
    dome.layers.set(LAYER_NO_AO);
    this.scene.add(dome);
    this.dome = dome;
    this.bakeSky();
  }

  // (re)bake the sky cube, the PMREM environment and the haze LUT
  bakeSky(params = LIGHT.sky) {
    const r = this.renderer;
    const sky = new Sky();
    sky.scale.setScalar(1000);
    const u = sky.material.uniforms;
    for (const [k, v] of Object.entries(params)) if (u[k]) u[k].value = v;
    u.sunPosition.value.copy(this.sunDir);
    // no sun disc in the bake: the cube also lights the scene (PMREM), where a disc would leak
    // unshadowed sunlight into the shade; the dome draws its own disc
    u.showSunDisc.value = 0;
    const skyScene = new THREE.Scene();
    skyScene.add(sky);
    new THREE.CubeCamera(1, 2000, this.skyCube).update(r, skyScene);
    // PMREM: only metals get it as envMap (specular reflections); everything else gets its sky
    // fill from an SH light probe of the same sky, which costs no texture fetches (the PMREM
    // lookups were ~25-35% of the main pass)
    if (this.envRT) this.envRT.dispose();
    this.envRT = null;
    if (this.caps.half) {                   // (PMREM renders to half float: without it metals go without)
      const pmrem = new THREE.PMREMGenerator(r);
      this.envRT = pmrem.fromCubemap(this.skyCube.texture);
      pmrem.dispose();
    }
    sky.geometry.dispose(); sky.material.dispose();
    this.skyProbe.sh.copy(this._skySH());
    this.skyProbe.intensity = LIGHT.envIntensity;
    for (const m of this.metals) { m.envMap = this.envRT ? this.envRT.texture : null; m.envMapIntensity = LIGHT.envIntensity; }

    // haze LUT: sky radiance just above the horizon for 64 azimuths (world, from -z towards +x)
    const quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), new THREE.ShaderMaterial({
      uniforms: { tSky: { value: this.skyCube.texture } },
      vertexShader: 'varying vec2 vUv; void main() { vUv = uv; gl_Position = vec4( position.xy, 0.0, 1.0 ); }',
      fragmentShader: /* glsl */`
        uniform samplerCube tSky;
        varying vec2 vUv;
        void main() {
          float a = ( vUv.x - 0.5 ) * 6.2831853;
          vec3 c = vec3( 0.0 );
          // average a few elevations around 2-6 deg: the horizon band distant walls sit against
          for ( int k = 0; k < 4; k ++ ) {
            float e = radians( 1.5 + 1.5 * float( k ) );
            c += textureCube( tSky, vec3( sin( a ) * cos( e ), sin( e ), - cos( a ) * cos( e ) ) ).rgb;
          }
          gl_FragColor = vec4( c * 0.25, 1.0 );
        }`,
      depthTest: false, depthWrite: false,
    }));
    this._fullscreen(quad, this.fogLUT);
  }

  _fullscreen(quad, target) {
    const r = this.renderer;
    quad.frustumCulled = false;
    const sc = new THREE.Scene();
    sc.add(quad);
    const prev = r.getRenderTarget();
    r.setRenderTarget(target);
    r.render(sc, new THREE.Camera());
    r.setRenderTarget(prev);
    quad.geometry.dispose(); quad.material.dispose();
  }

  // project the baked sky (lat-long, 4x4 supersampled) onto 9 SH coefficients; below the
  // horizon the sky shader is meaningless, so the lower hemisphere repeats a dim horizon (the
  // warm ground bounce is the hemisphere light's job)
  _skySH() {
    const W = 64, H = 32;
    const F = this.caps.float;              // without float targets: 8 bit, radiance / 8 (sky values stay below 8)
    const rt = new THREE.WebGLRenderTarget(W, H, { type: F ? THREE.FloatType : THREE.UnsignedByteType, depthBuffer: false });
    const quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), new THREE.ShaderMaterial({
      uniforms: { tSky: { value: this.skyCube.texture } },
      vertexShader: 'varying vec2 vUv; void main() { vUv = uv; gl_Position = vec4( position.xy, 0.0, 1.0 ); }',
      fragmentShader: /* glsl */`
        uniform samplerCube tSky;
        varying vec2 vUv;
        void main() {
          vec3 c = vec3( 0.0 );
          vec2 px = vec2( 1.0 / 64.0, 1.0 / 32.0 );
          for ( int i = 0; i < 4; i ++ ) for ( int j = 0; j < 4; j ++ ) {
            vec2 uv = vUv + ( vec2( float( i ), float( j ) ) - 1.5 ) * 0.25 * px;
            float phi = ( uv.x - 0.5 ) * 6.2831853;
            float el = ( uv.y - 0.5 ) * 3.1415927;
            vec3 d = vec3( sin( phi ) * cos( el ), sin( el ), - cos( phi ) * cos( el ) );
            if ( d.y < 0.02 ) d = normalize( vec3( d.x, 0.02, d.z ) );
            vec3 s = textureCube( tSky, d ).rgb;
            c += el < 0.0 ? s * 0.35 : s;
          }
          gl_FragColor = vec4( c / 16.0 * SCALE, 1.0 );
        }`,
      defines: { SCALE: F ? '1.0' : '0.125' },
      depthTest: false, depthWrite: false,
    }));
    this._fullscreen(quad, rt);
    let px = new Float32Array(W * H * 4);
    if (F) this.renderer.readRenderTargetPixels(rt, 0, 0, W, H, px);
    else {
      const b = new Uint8Array(W * H * 4);
      this.renderer.readRenderTargetPixels(rt, 0, 0, W, H, b);
      px = Float32Array.from(b, (v) => (v / 255) * 8);
    }
    rt.dispose();
    const sh = new THREE.SphericalHarmonics3();
    const basis = new Array(9).fill(0);
    const dir = new THREE.Vector3();
    for (let y = 0; y < H; y++) {
      const el = ((y + 0.5) / H - 0.5) * Math.PI;
      const dOmega = (2 * Math.PI / W) * (Math.PI / H) * Math.cos(el);
      for (let x = 0; x < W; x++) {
        const phi = ((x + 0.5) / W - 0.5) * 2 * Math.PI;
        dir.set(Math.sin(phi) * Math.cos(el), Math.sin(el), -Math.cos(phi) * Math.cos(el));
        THREE.SphericalHarmonics3.getBasisAt(dir, basis);
        const i = (y * W + x) * 4;
        for (let k = 0; k < 9; k++) {
          const w = basis[k] * dOmega;
          sh.coefficients[k].x += px[i] * w;
          sh.coefficients[k].y += px[i + 1] * w;
          sh.coefficients[k].z += px[i + 2] * w;
        }
      }
    }
    return sh;
  }

  _setupAO() {
    // half-res G-buffer: packed view normal (rgb8) + depth texture
    const depth = new THREE.DepthTexture(4, 4, THREE.UnsignedIntType);
    this.pre = new THREE.WebGLRenderTarget(4, 4, {
      type: THREE.UnsignedByteType, minFilter: THREE.NearestFilter, magFilter: THREE.NearestFilter,
      depthTexture: depth, generateMipmaps: false,
    });
    this.normalMat = new THREE.MeshNormalMaterial({ side: THREE.DoubleSide });
    this.normalMat.blending = THREE.NoBlending;
    const gtao = (this.gtao = new GTAOPass(this.scene, this.camera, 4, 4));
    gtao.setGBuffer(depth, this.pre.texture);
    gtao.output = GTAOPass.OUTPUT.Off;
    gtao.updateGtaoMaterial({ radius: 1.1, distanceExponent: 1.6, thickness: 1.4, scale: 1.15, samples: 8, distanceFallOff: 1.0 });
    gtao.pdMaterial.defines.FRAGMENT_OUTPUT = 'vec4( denoised.r, - viewPos.z, 0.0, 1.0 )';
    gtao.updatePdMaterial({ lumaPhi: 10, depthPhi: 1.5, normalPhi: 4, radius: 5, radiusExponent: 1.5, rings: 2.5, samples: 10 });
    gtao.pdMaterial.needsUpdate = true;
    U.ocAO.value = gtao.pdRenderTarget.texture;
  }

  setAOEnabled(on) { this.useAO = on; }

  // the pane can start hidden (0x0) and resize without events: check every frame
  fit() {
    const w = this.canvas.clientWidth, h = this.canvas.clientHeight;
    if (!w || !h) return false;
    const r = this.renderer;
    if (r.getPixelRatio() !== this.pixelRatio) r.setPixelRatio(this.pixelRatio);
    const pr = this.pixelRatio;
    if (this.canvas.width !== Math.floor(w * pr) || this.canvas.height !== Math.floor(h * pr)) {
      r.setSize(w, h, false);
      this.camera.aspect = w / h;
      this.camera.updateProjectionMatrix();
    }
    const bw = this.canvas.width, bh = this.canvas.height;
    const aw = Math.max(1, Math.ceil(bw * this.aoScale)), ah = Math.max(1, Math.ceil(bh * this.aoScale));
    if (this.useAO && (this.pre.width !== aw || this.pre.height !== ah)) {     // (AO off: its targets stay tiny)
      this.pre.setSize(aw, ah);
      this.gtao.setSize(aw, ah);
    }
    U.ocAOParams.value.x = aw / bw;
    U.ocAOParams.value.y = ah / bh;
    return true;
  }

  render() {
    if (!this.fit()) return false;
    const r = this.renderer, scene = this.scene, camera = this.camera;
    camera.updateMatrixWorld();
    r.info.reset();
    if (this.useAO) {
      // 1. half-res normals + depth
      camera.layers.set(0);
      scene.overrideMaterial = this.normalMat;
      r.setRenderTarget(this.pre);
      r.setClearColor(0x7f7fff, 1);
      r.clear();
      r.render(scene, camera);
      scene.overrideMaterial = null;
      camera.layers.enable(LAYER_NO_AO);
      // 2. GTAO + denoise (output Off: only fills gtao.pdRenderTarget)
      this.gtao.render(r, null, null);
      U.ocAOParams.value.z = 1;
    } else {
      U.ocAOParams.value.z = 0;
    }
    // 3. main pass
    r.setRenderTarget(null);
    r.setClearColor(0x000000, 1);
    r.shadowMap.needsUpdate = true;
    r.render(scene, camera);
    return true;
  }
}
