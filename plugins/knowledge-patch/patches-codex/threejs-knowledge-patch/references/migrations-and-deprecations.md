# Migrations and deprecations

Removed, renamed, deprecated, and behavior-sensitive APIs, including focused upgrade guidance.

## Addon module migrations (migration guide)

`USDZLoader` is deprecated in favor of `USDLoader`. `ParametricGeometries` became `ParametricFunctions`, and its former inner geometry classes were removed because the module now exports only parametric functions.

## AnimationClip parsing deprecation (r175)

`AnimationClip.parseAnimation()` is deprecated in r175; migrate callers away before it is removed.

## Async loading and export migrations (migration guide)

`DRACOExporter.parse()` was replaced by `parseAsync()`, while `FileLoader.load()` and `ImageBitmapLoader.load()` no longer return a value and require their `onLoad` callbacks. `KTX2Loader.detectSupportAsync()` is deprecated; initialize the renderer with `await renderer.init()` and then call `detectSupport()`.

## Clock deprecation (r183)

The core `Clock` module is deprecated. New and migrated timing code should use `Timer` instead.

## ColorManagement method renames (migration guide)

`ColorManagement.fromWorkingColorSpace()` became `workingToColorSpace()`, and `toWorkingColorSpace()` became `colorSpaceToWorking()`.

## Deprecated code removal (r178)

r178 removes previously deprecated code, so remaining uses of deprecated APIs must be migrated before upgrading.

## Depth-of-field and temporal-AA node replacements (migration guide)

`DepthOfFieldNode` received a new implementation and API in r180, so setups using its former surface must be rebuilt. In r179, `TRAAPassNode` became `TRAANode` and likewise requires the new setup rather than a direct constructor rename.

## Direction helper migrations (migration guide)

TSL renamed `directionToColor()` to `packNormalToRGB()` and `colorToDirection()` to `unpackRGBToNormal()`. WebGL shader code should replace deprecated `inverseTransformDirection()` with `transformNormalByInverseViewMatrix()` for normals or `transformDirectionByInverseViewMatrix()` for directions.

## GLTFLoader image-format detection removal (r176)

`GLTFLoader` no longer performs WebP or AVIF support detection. Applications targeting environments that may not support those formats must handle compatibility before loading such assets.

## GTAO and SSR output migrations (migration guide)

The revised `GTAONode` produces darker, wider ambient occlusion, so existing scenes may need lower `radius` and `scale` values. `SSRNode` now has a revised API and optional denoiser, and its reflections should be composited additively instead of with `blendColor()`.

## HemisphereLightNode normal rename (r177)

`HemisphereLightNode` changed `normalView` to `normalWorld`; custom node code using the former name must migrate.

## Independent RenderTarget clones (migration guide)

`RenderTarget.clone()` now performs a full structural clone without sharing texture resources with the original target.

## Legacy luminance formats removed (r176)

`LuminanceFormat` and `LuminanceAlphaFormat` were removed. Textures that still select either legacy format must migrate to a supported format before upgrading.

## LightProbe deserialization removal (r182)

`LightProbe.fromJSON()` was removed. Direct callers must migrate away from that method when upgrading to r182.

## Line2NodeMaterial line-width removal (r179)

The unused `Line2NodeMaterial.lineWidth` property was removed. Code that still sets or reads that property must stop relying on it when upgrading.

## Line2NodeMaterial vertex-color rename (r183)

`Line2NodeMaterial.useColor` was renamed to `Line2NodeMaterial.vertexColors`; update direct property access when upgrading.

## LottieLoader deprecation (r176)

`LottieLoader` is deprecated; migrate to using the underlying library inline.

## LUT and pass constructor updates (migration guide)

`LUTImageLoader` now accepts only a loading manager; replace its removed `flipVertical` argument with `loader.flip = true`. The redundant width and height inputs were removed from the `SMAAPass` and `HalftonePass` constructors.

## Manual world-matrix invalidation (migration guide)

`Object3D.updateWorldMatrix()` now honors `matrixWorldNeedsUpdate`; when `matrixAutoUpdate` is disabled and code changes `.matrix` directly, it must set `.matrixWorldNeedsUpdate = true` before requesting the world-matrix update.

## Matrix3 transform deprecations (r185)

`Matrix3.scale()`, `Matrix3.rotate()`, and `Matrix3.translate()` are deprecated. Direct callers must migrate away from these methods.

## MeshGouraudMaterial deprecation (r173)

The `MeshGouraudMaterial` addon is deprecated in r173 and should not be selected for new code.

## NodeBuilder observer rename (r173)

`NodeBuilder.monitor` was renamed to `NodeBuilder.observer`; update direct property access when migrating to r173.

## PeppersGhostEffect removal (r177)

The `PeppersGhostEffect` addon was removed in r177; applications importing it must replace or vendor the effect before upgrading.

## PointsNodeMaterial replaces InstancedPointsNodeMaterial (r173)

`PointsNodeMaterial` now replaces `InstancedPointsNodeMaterial`. Code using the older material should migrate its imports and construction to `PointsNodeMaterial`.

## Raw WebGL pixel-store state (migration guide)

Code that changes pixel-storage values through the raw WebGL 2 context must now call `renderer.state.pixelStorei()` so renderer state remains synchronized.

## Removed and deprecated addons (r185)

The `TiledLighting` addon was removed, and `LWOLoader` is deprecated. Applications importing the former need a replacement, while new code should avoid the latter.

## Removed post-processing settings and nodes (migration guide)

`SSAAPassNode.clearColor` and `.clearAlpha` were removed, so clear colors must be configured on the renderer. `AnamorphicNode` was also removed; use `BloomNode` instead.

## Renderer compatibility replacements (migration guide)

`MeshPostProcessingMaterial` was removed, and `WebGLCubeRenderTarget` can no longer be used with `WebGPURenderer`; use `CubeRenderTarget` there. With `WebGLRenderer`, deprecated `PCFSoftShadowMap` should be replaced by `PCFShadowMap`, which now produces soft shadows too.

## Resolution-scale API migrations (migration guide)

`PassNode.setResolution()` and `.getResolution()` became `setResolutionScale()` and `getResolutionScale()`, and `WaterMesh.resolution` became `.resolutionScale`. The `resolution` properties of `ReflectorNode`, `AnamorphicNode`, and `GaussianBlurNode` likewise became scalar `resolutionScale` values rather than `Vector2` values.

## Reversed- and logarithmic-depth identifiers (migration guide)

`WebGLRenderer` renamed the `reverseDepthBuffer` constructor parameter to `reversedDepthBuffer`. Custom shaders must also replace `USE_REVERSEDEPTHBUF` with `USE_REVERSED_DEPTH_BUFFER` and `USE_LOGDEPTHBUF` with `USE_LOGARITHMIC_DEPTH_BUFFER`.

## RGBELoader renamed to HDRLoader (r180)

`RGBELoader` was renamed to `HDRLoader`; update addon imports and constructor names when migrating to r180.

## RGBMLoader removal (r180)

`RGBMLoader` was removed. Applications that still import it must replace or vendor the loader before upgrading.

## RoomEnvironment lighting shift (migration guide)

`RoomEnvironment` changed its scene position, so PMREMs generated from it produce different lighting after the upgrade.

## Rotation and axis convention changes (migration guide)

Background and environment-map rotation now follows the same rotation convention as 3D objects. `FBXLoader` also converts +Z-up content to +Y-up automatically, so application-level corrective rotations should be removed.

## SVG shape creation migration (migration guide)

`SVGLoader.createShapes()` is deprecated; convert an SVG shape path with `shapePath.toShapes()` instead.

## Timer moved into core (r179)

`Timer` moved into the core library in r179. Imports that used its former addon location must be updated to the core export.

## TSL API migrations (r182)

`DFGApprox` was renamed to `DFGLUT`, and `nodeObject()` was removed for Node classes. Imports and node construction code using the former APIs must be updated.

## TSL constants and effect inputs (migration guide)

TSL renamed `PI2` to `TWO_PI`. `AfterImageNode.damp` is now a `Node<float>`, so `afterImage()` accepts a node constant or uniform instead of requiring a numeric value.

## TSL function migrations (r178)

`TriplanarTexturesNode` moves to `triplanarTextures()`, `EquirectUVNode` to `equirectUV()`, and `MatcapUVNode` to the `matcapUV` Fn constant. Affected `transformed*` names also lose that prefix.

## TSL geometry positions in vertex transforms (migration guide)

When assigning `material.positionNode`, `positionLocal` does not include internal transforms such as skinning. Use `positionGeometry` when the node needs vertices from the pre-transformed geometry.

## TSL method renames (r173)

TSL renamed `varying()` to `toVarying()` and `vertexStage()` to `toVertexStage()`; both old names must be replaced when upgrading.

## TSL removals and rename (r185)

TSL removes the `string` and `arrayBuffer` definitions, and renames `directionToFaceDirection` to `negateOnBackSide`. Imports and node code using those names must be updated.

## VTKLoader deprecation (r184)

`VTKLoader` is deprecated in r184; applications should plan to migrate away from it.

## WebGPU async API deprecations (r181)

`renderAsync()`, `computeAsync()`, and related asynchronous renderer methods are deprecated, and `waitForGPU()` was removed. Callers must stop relying on `waitForGPU()` and migrate away from the deprecated async entry points.

## WebGPU output-buffer API rename (r182)

In the WebGPU renderer path, `getColorBufferType()` was renamed to `getOutputBufferType()`. `getPreferredCanvasFormat()` now uses `outputType` as its default when choosing the canvas format.

## WebGPU pipeline class renames (r183)

The WebGPU renderer renamed `Nodes` to `NodeManager`, `RenderPipeline` to `RenderObjectPipeline`, and `PostProcessing` to `RenderPipeline`. Imports and direct construction must use the final names.

## WebGPU premultiplied-alpha backgrounds (migration guide)

The r185 premultiplied-alpha implementation can expose blending problems in `WebGPURenderer`; use an opaque `Scene.background` or opaque `renderer.setClearColor()` value unless the canvas must blend with the HTML background.
