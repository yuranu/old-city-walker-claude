// Two-cascade sun shadow (three's SunLight/SunLightShadow) with two changes:
//  - a configurable split between the near and the far cascade (three uses lambda 0.5, which
//    puts the split at ~40 m: too coarse for a walker), and
//  - per-cascade biases: `normalBias` and `bias` are given in shadow-map TEXELS and scaled by
//    each cascade's texel size, so the far cascade (4-5x coarser) gets no acne and the near
//    one no peter-panning. The texel size travels to the shader in the unused .w of the
//    cascade data vec4, via a small patch of the sun shadow chunk.
// Cascades are fitted with bounding spheres and snapped to whole texels in light space, so they
// do not shimmer when the camera moves or turns.
import * as THREE from 'three';
import { SunLightShadow } from 'three/examples/jsm/lights/SunLightShadow.js';

const CASCADES = 2;          // fixed by three's SUN_LIGHT_CASCADES
const FADE = 0.12;           // fraction of a cascade that blends into the next one

const _orient = new THREE.Matrix4();
const _viewToLight = new THREE.Matrix4();
const _dir = new THREE.Vector3();
const _up = new THREE.Vector3();
const _center = new THREE.Vector3();
const _near = [0, 1, 2, 3].map(() => new THREE.Vector3());
const _far = [0, 1, 2, 3].map(() => new THREE.Vector3());
const _corners = [0, 1, 2, 3, 4, 5, 6, 7].map(() => new THREE.Vector3());

export class StableSunShadow extends SunLightShadow {
  constructor() {
    super();
    this.split = 22;          // metres from the eye where the far cascade takes over
    this.texelBias = -0.25;   // depth bias in texels (towards the light), see patchSunShadowChunk
  }

  updateMatrices(light, viewCamera) {
    if (viewCamera === undefined) return;
    const insetX = Math.min(0.25, (Math.ceil(this.radius) + 1) / this.mapSize.x);
    const insetY = Math.min(0.25, (Math.ceil(this.radius) + 1) / this.mapSize.y);
    for (let i = 0; i < CASCADES; i++) this._viewports[i].set(i + insetX, insetY, 1 - 2 * insetX, 1 - 2 * insetY);
    const resX = this.mapSize.x * (1 - 2 * insetX), resY = this.mapSize.y * (1 - 2 * insetY);
    const res = Math.min(resX, resY);

    const camera = this.camera;
    const cNear = viewCamera.near;
    const cFar = Math.max(cNear + 1e-6, Math.min(camera.far, viewCamera.far));
    const splits = this._cascadeSplits;
    splits[0] = cNear;
    splits[1] = THREE.MathUtils.clamp(this.split, cNear + 1, cFar - 1);
    splits[2] = cFar;

    _dir.setFromMatrixPosition(light.matrixWorld).negate().normalize();
    _up.set(0, 1, 0);
    if (Math.abs(_up.dot(_dir)) > 0.99) _up.set(0, 0, 1);
    _orient.lookAt(_center.set(0, 0, 0), _dir, _up);
    _viewToLight.copy(_orient).transpose().multiply(viewCamera.matrixWorld);

    const zNear = viewCamera.reversedDepth ? 1 : -1;
    let maxZ = -Infinity;
    for (let i = 0; i < 4; i++) {
      const x = i === 0 || i === 1 ? 1 : -1, y = i === 0 || i === 3 ? 1 : -1;
      const n = _near[i].set(x, y, zNear).applyMatrix4(viewCamera.projectionMatrixInverse);
      const f = _far[i];
      if (viewCamera.isPerspectiveCamera) f.copy(n).multiplyScalar(cFar / cNear);
      else f.set(n.x, n.y, -cFar);
      n.applyMatrix4(_viewToLight);
      f.applyMatrix4(_viewToLight);
      maxZ = Math.max(maxZ, n.z, f.z);
    }
    // casters up to one shadow range towards the sun still land in the map
    maxZ += Math.min(cFar, 120);
    const sNear = camera.near;

    for (let i = 0; i < CASCADES; i++) {
      const near = i === 0 ? splits[0] : this._cascadeData[i - 1].z;
      const far = splits[i + 1];
      const fade = far - FADE * (far - splits[i]);
      const a0 = (near - cNear) / (cFar - cNear), a1 = (far - cNear) / (cFar - cNear);
      _center.set(0, 0, 0);
      for (let j = 0; j < 4; j++) {
        _corners[j * 2].lerpVectors(_near[j], _far[j], a0);
        _corners[j * 2 + 1].lerpVectors(_near[j], _far[j], a1);
        _center.add(_corners[j * 2]).add(_corners[j * 2 + 1]);
      }
      _center.multiplyScalar(1 / 8);
      let r2 = 0, minZ = Infinity;
      for (let j = 0; j < 8; j++) {
        r2 = Math.max(r2, _corners[j].distanceToSquared(_center));
        minZ = Math.min(minZ, _corners[j].z);
      }
      // the radius only depends on fov/aspect/splits: quantise it so tiny float noise cannot
      // change the texel size from frame to frame
      let radius = Math.ceil(Math.sqrt(r2) * 4) / 4;
      radius /= 1 - 1 / res;
      const tx = (2 * radius) / resX, ty = (2 * radius) / resY;
      _center.x = Math.round(_center.x / tx) * tx;
      _center.y = Math.round(_center.y / ty) * ty;
      // (begin, end, fade start, texel size in metres) consumed by the patched chunk
      this._cascadeData[i].set(i === 0 ? -1e10 : near, far, fade, Math.max(tx, ty));
      _center.z = maxZ + sNear;
      _center.applyMatrix4(_orient);
      const cam = this._cameras[i];
      cam.position.copy(_center);
      cam.quaternion.setFromRotationMatrix(_orient);
      cam.left = -radius; cam.right = radius; cam.top = radius; cam.bottom = -radius;
      cam.near = sNear;
      cam.far = maxZ - minZ + 2 * sNear;
      cam.coordinateSystem = camera.coordinateSystem;
      cam._reversedDepth = camera.reversedDepth;
      cam.updateProjectionMatrix();
      cam.updateMatrixWorld();
      this._updateMatrix(cam, this._matrices[i], this._frustums[i], this._viewports[i]);
    }
    // depth bias: texels -> NDC depth of each cascade differs; use the near cascade's mapping
    // and let the per-cascade normal offset do the rest
    const c0 = this._cameras[0];
    this.bias = (this.texelBias * this._cascadeData[0].w) / (c0.far - c0.near);
  }
}

// Scale the sun's normal bias by each cascade's texel size (cascade.w). Without the patch the
// chunk applies the same world-space offset to both cascades.
export function patchSunShadowChunk() {
  const key = 'shadowmap_pars_fragment';
  let src = THREE.ShaderChunk[key];
  const a = 'vec4 shadowWorldPosition = vec4( vSunShadowWorldPosition.xyz + vSunShadowWorldNormal * sunLightShadow.shadowNormalBias, 1.0 );';
  const b = 'vec4 cascade = sunShadowCascade[ cascadeOffset + i ];';
  if (!src.includes(a) || !src.includes(b)) {
    console.warn('sun shadow chunk changed; per-cascade bias not applied');
    return false;
  }
  src = src.replace(a, '');
  src = src.replace(b, b + '\n\t\t\t\tvec4 shadowWorldPosition = vec4( vSunShadowWorldPosition.xyz + vSunShadowWorldNormal * ( sunLightShadow.shadowNormalBias * cascade.w ), 1.0 );');
  THREE.ShaderChunk[key] = src;
  return true;
}
