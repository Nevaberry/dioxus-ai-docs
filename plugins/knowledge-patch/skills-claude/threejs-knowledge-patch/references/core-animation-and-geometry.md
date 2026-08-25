# Core, Animation, and Geometry

Use this reference for core math and scene behavior, animation, serialization, geometry, object state, and general API changes.

## Addon module migrations

**Batch:** `migration-guide-r173-r185`

`USDZLoader` is deprecated in favor of `USDLoader`. `ParametricGeometries` became `ParametricFunctions`, and its former inner geometry classes were removed because the module now exports only parametric functions.

## AnimationAction creation and reversal behavior

**Batch:** `r184`

Creating an `AnimationAction` now preserves interpolant settings, and reversing `timeScale` no longer causes a jump.

## AnimationClip parsing deprecation

**Batch:** `r175`

`AnimationClip.parseAnimation()` is deprecated in r175; migrate callers away before it is removed.

## AnimationClipCreator default name

**Batch:** `r175`

`AnimationClipCreator` now uses an empty string as the default clip name when no name is supplied.

## Automatic ExtrudeGeometry shape cleanup

**Batch:** `r175`

`ExtrudeGeometry` now cleans shape data automatically before extrusion, changing how unclean input contours are handled.

## BatchedMesh opacity and wireframes

**Batch:** `r183`

`BatchedMesh` now supports per-instance opacity and wireframe materials.

## BatchedMesh optimization updates

**Batch:** `r182`

`BatchedMesh.optimize()` now updates its index and attributes correctly. Applications that worked around stale geometry data after optimization should recheck those workarounds.

## BezierInterpolant

**Batch:** `r183`

r183 adds `BezierInterpolant` as an animation interpolant for Bézier-interpolated values.

## Box3 and Sphere JSON serialization

**Batch:** `r177`

`Box3` and `Sphere` now provide `toJSON()` and `fromJSON()` methods, so these bounds primitives can be serialized and restored without application-defined adapters.

## Camera scale no longer affects the view matrix

**Batch:** `r183`

Camera scale is now excluded from the view matrix, so scaling a camera no longer scales its view transform.

## CapsuleGeometry height and segmentation

**Batch:** `r176`

`CapsuleGeometry` renames its `length` parameter to `height` and adds a `heightSegments` parameter, allowing separate control over tessellation along the capsule's height.

## Clamped plane-line intersections

**Batch:** `r184`

`Plane.intersectLine()` adds `clampToLine`, allowing callers to request a result clamped to the supplied line.

## Clock deprecation

**Batch:** `r183`

The core `Clock` module is deprecated. New and migrated timing code should use `Timer` instead.

## Closed Catmull-Rom extrusion paths

**Batch:** `r182`

`ExtrudeGeometry` now honors `CatmullRomCurve3.closed`. Extrusions along a closed Catmull-Rom path can therefore produce different geometry after upgrading.

## Corrected copy semantics

**Batch:** `r184`

`Object3D.copy()` now preserves `pivot`, and `RenderTarget.copy()` preserves multiview state.

## Deprecated code removal

**Batch:** `r178`

r178 removes previously deprecated code, so remaining uses of deprecated APIs must be migrated before upgrading.

## Direction-aware bone transforms

**Batch:** `r184`

`SkinnedMesh.applyBoneTransform()` can now take a `Vector4`, supporting both direction and position transformations.

## Float light-probe generation

**Batch:** `r179`

`LightProbeGenerator.fromCubeRenderTarget()` now supports render targets using `FloatType`.

## Indirect drawing offset

**Batch:** `r182`

`BufferGeometry` adds an `indirectOffset` parameter for indirect drawing, allowing geometry to select an offset within indirect draw data.

## Instance velocity

**Batch:** `r183`

`InstanceNode` now supports velocity data for instanced rendering workflows.

## Legacy luminance formats removed

**Batch:** `r176`

`LuminanceFormat` and `LuminanceAlphaFormat` were removed. Textures that still select either legacy format must migrate to a supported format before upgrading.

## LightProbe deserialization removal

**Batch:** `r182`

`LightProbe.fromJSON()` was removed. Direct callers must migrate away from that method when upgrading to r182.

## Line-segment distance queries

**Batch:** `r179`

`Line3` adds a method for computing the closest squared distance between two line segments, so applications no longer need a separate implementation for that query.

## Manual world-matrix invalidation

**Batch:** `migration-guide-r173-r185`

`Object3D.updateWorldMatrix()` now honors `matrixWorldNeedsUpdate`; when `matrixAutoUpdate` is disabled and code changes `.matrix` directly, it must set `.matrixWorldNeedsUpdate = true` before requesting the world-matrix update.

## Matrix3 transform deprecations

**Batch:** `r185`

`Matrix3.scale()`, `Matrix3.rotate()`, and `Matrix3.translate()` are deprecated. Direct callers must migrate away from these methods.

## Object and scene serialization version

**Batch:** `r177`

The Object/Scene serialization format version was increased. Consumers that validate, cache, or route serialized assets by format version must account for the r177 format.

## Object3D static and pivot data

**Batch:** `r183`

`Object3D.static` is now preserved by `copy()` and JSON serialization. `Object3D` also gains `pivot`, with support in exporters and in glTF import and export.

## Quaternion slerp extrapolation

**Batch:** `r183`

Quaternion slerp methods now extrapolate when the interpolation factor lies outside the usual `[0, 1]` interval.

## Rotation and axis convention changes

**Batch:** `migration-guide-r173-r185`

Background and environment-map rotation now follows the same rotation convention as 3D objects. `FBXLoader` also converts +Z-up content to +Y-up automatically, so application-level corrective rotations should be removed.

## SVG shape creation migration

**Batch:** `migration-guide-r173-r185`

`SVGLoader.createShapes()` is deprecated; convert an SVG shape path with `shapePath.toShapes()` instead.

## Timer connection lifecycle

**Batch:** `r174`

`Timer` adds `connect()` and `disconnect()` so applications can explicitly manage its document connection and visibility-event lifecycle.

```js
timer.connect(document);
timer.disconnect();
```

## Timer moved into core

**Batch:** `r179`

`Timer` moved into the core library in r179. Imports that used its former addon location must be updated to the core export.

## TorusGeometry angular controls

**Batch:** `r183`

`TorusGeometry` adds `thetaStart` and `thetaLength` controls for selecting the generated angular span.

