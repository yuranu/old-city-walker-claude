// Union of the resident collision BVHs (one per chunk: ground, walls, context, and per sector
// either its full-detail or its massing LOD). Queries skip parts whose bounds miss.
import * as THREE from 'three';

const _box = new THREE.Box3();

export class Collider {
  constructor() {
    this.parts = new Map();     // key -> { bvh, box }
    this.version = 0;
  }

  set(key, bvh, box = null) {
    if (!bvh) { this.delete(key); return; }
    if (!box) box = bvh.geometry.boundingBox || bvh.getBoundingBox(new THREE.Box3());
    this.parts.set(key, { bvh, box });
    this.version++;
  }

  delete(key) {
    if (this.parts.delete(key)) this.version++;
  }

  get(key) { return this.parts.get(key)?.bvh || null; }

  // callbacks as for MeshBVH.shapecast; box: the query bounds (world)
  shapecast(box, callbacks) {
    for (const p of this.parts.values()) if (p.box.intersectsBox(box)) p.bvh.shapecast(callbacks);
  }

  // every hit along the ray, unsorted
  raycast(ray, side = THREE.DoubleSide) {
    const out = [];
    for (const p of this.parts.values()) {
      if (!ray.intersectsBox(p.box)) continue;
      for (const h of p.bvh.raycast(ray, side)) out.push(h);
    }
    return out;
  }

  bounds(target = new THREE.Box3()) {
    target.makeEmpty();
    for (const p of this.parts.values()) target.union(_box.copy(p.box));
    return target;
  }

  tris() {
    let n = 0;
    for (const p of this.parts.values()) n += p.bvh.geometry.index ? p.bvh.geometry.index.count / 3 : 0;
    return n;
  }
}
