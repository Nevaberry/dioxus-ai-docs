# Addons, Controls, Post-Processing, and Editor

Use this reference for controls, effects, post-processing, browser-facing addons, physics helpers, inspection tools, and editor behavior.

## Additional HTMLMesh input types

**Batch:** `r179`

`HTMLMesh` now supports email and password inputs in addition to its previously supported form controls.

## AnaglyphEffect migration

**Batch:** `r183`

`AnaglyphEffect.screenDistance` was renamed to `planeDistance`, and the effect now uses `frameCorners()` for physically correct stereo framing.

## ArcballControls touch-action restoration

**Batch:** `r184`

When controls release their element, `ArcballControls` now resets `touch-action` to an empty string rather than forcing `auto`.

## BatchedMesh selection

**Batch:** `r181`

`SelectionBox` now supports selecting `BatchedMesh` content.

## BitonicSort addon

**Batch:** `r181`

A new `BitonicSort` addon provides bitonic sorting through the three.js addon surface.

## Configurable TransformControls gizmos

**Batch:** `r178`

`TransformControls` gizmo colors are now configurable instead of fixed.

## Controls connection target

**Batch:** `r175`

`Controls.connect()` now requires an element. Lifecycle code that reconnects controls must pass the target element explicitly.

```js
controls.connect(renderer.domElement);
```

## Custom tone mapping in OutputPass

**Batch:** `r173`

`OutputPass` now supports `THREE.CustomToneMapping`, allowing a custom tone-mapping mode in that post-processing pass.

## Depth-of-field and temporal-AA node replacements

**Batch:** `migration-guide-r173-r185`

`DepthOfFieldNode` received a new implementation and API in r180, so setups using its former surface must be rebuilt. In r179, `TRAAPassNode` became `TRAANode` and likewise requires the new setup rather than a direct constructor rename.

## Editor background texture color spaces

**Batch:** `r175`

The editor adds color-space options for background textures, allowing their color-space interpretation to be configured.

## Editor rendering defaults

**Batch:** `r183`

The editor now uses Neutral tone mapping by default and supports `WebGPURenderer` projects.

## Expanded TRAANode inputs and camera support

**Batch:** `r184`

`TRAANode` adds a velocity-node source and supports reversed or logarithmic depth buffers and orthographic cameras.

## EXR files in the editor

**Batch:** `r179`

The three.js editor can now load EXR files.

## FirstPersonControls movement changes

**Batch:** `r185`

`FirstPersonControls` adds damping, separates movement sources, and adds E/Q key controls.

## Forced Reflector updates

**Batch:** `r174`

The `Reflector` addon adds `forceUpdate`, allowing an application to request an otherwise skipped reflection refresh.

```js
reflector.forceUpdate = true;
```

## FSR1 and temporal upsampling

**Batch:** `r184`

The addons add an `FSR1Node` port for `WebGPURenderer` and `TAAUNode` for temporal antialiasing with upsampling.

## GTAO and SSR output migrations

**Batch:** `migration-guide-r173-r185`

The revised `GTAONode` produces darker, wider ambient occlusion, so existing scenes may need lower `radius` and `scale` values. `SSRNode` now has a revised API and optional denoiser, and its reflections should be composited additively instead of with `blendColor()`.

## GTAO temporal filtering

**Batch:** `r181`

`GTAONode` gains basic temporal-filtering support.

## HTMLMesh VR inputs

**Batch:** `r177`

`HTMLMesh` now supports text and number input controls in VR.

## HTMLTexture

**Batch:** `r184`

r184 adds `HTMLTexture`, providing a first-party texture type for HTML-backed content.

## HTMLTexture browser API support

**Batch:** `r185`

`HTMLTexture` now supports the new WICG HTML-in-Canvas API signatures.

## Inspector workflow additions

**Batch:** `r184`

Inspector adds a Memory tab, forced-WebGL mode, a command-recording Timeline with export, stack-trace capture, TSL graph addons, and extension support.

## Interleaved Gradient Noise relocation

**Batch:** `r181`

Interleaved Gradient Noise moved from TSL into `PostProcessingUtils`; update imports that use the utility directly.

## LUT and pass constructor updates

**Batch:** `migration-guide-r173-r185`

`LUTImageLoader` now accepts only a loading manager; replace its removed `flipVertical` argument with `loader.flip = true`. The redundant width and height inputs were removed from the `SMAAPass` and `HalftonePass` constructors.

## Multiple PostProcessing instances

**Batch:** `r173`

`PostProcessing` now supports more than one instance, allowing multiple post-processing pipelines to coexist.

## New DevTools and editor text geometry

**Batch:** `r184`

r184 adds new DevTools, and the editor can now add `TextGeometry`.

## New geometry addons

**Batch:** `r185`

r185 adds the `LoftGeometry` addon and `TileCreasedNormalsPlugin`.

## New TSL coordinate, fog, and post-processing helpers

**Batch:** `r183`

TSL adds `clipSpace`, `exponentialHeightFogFactor()`, and the `retroPass` post-processing helper.

## OffscreenCanvas ViewHelper

**Batch:** `r181`

`ViewHelper` now supports `OffscreenCanvas`.

## OrbitControls public operations

**Batch:** `r183`

`OrbitControls` now exposes its pan, rotate, and dolly methods and adds a `cursorStyle` property.

## PassNode asynchronous compilation and render bounds

**Batch:** `r179`

`PassNode` adds `compileAsync()` together with viewport and scissor APIs, allowing a pass to be compiled asynchronously and constrained to explicit render bounds.

## PeppersGhostEffect removal

**Batch:** `r177`

The `PeppersGhostEffect` addon was removed in r177; applications importing it must replace or vendor the effect before upgrading.

## Perspective volume rendering

**Batch:** `r185`

`VolumeShader` now supports perspective cameras.

## Physics addon changes

**Batch:** `r182`

`AmmoPhysics` adds restitution support, `Octree` adds a `Box3` interface, and the physics helpers now report errors when `getShape()` is used with unsupported geometry types.

## ProgressiveLightMap normals requirement

**Batch:** `r181`

`ProgressiveLightMap` now requires normals. Geometry used with it must provide normal data when upgrading to r181.

## Rapier heightfields

**Batch:** `r176`

The `RapierPhysics` addon adds heightfield support.

## Raw pointer-lock movement

**Batch:** `r175`

`PointerLockControls.lock()` gains an `unadjustedMovement` option, allowing callers to request unadjusted pointer motion.

## Reflector antialiasing samples

**Batch:** `r180`

The reflector node adds an AA-samples parameter, allowing its multisampling level to be configured.

## Removed and deprecated addons

**Batch:** `r185`

The `TiledLighting` addon was removed, and `LWOLoader` is deprecated. Applications importing the former need a replacement, while new code should avoid the latter.

## Removed post-processing settings and nodes

**Batch:** `migration-guide-r173-r185`

`SSAAPassNode.clearColor` and `.clearAlpha` were removed, so clear colors must be configured on the renderer. `AnamorphicNode` was also removed; use `BloomNode` instead.

## Rendering addon additions

**Batch:** `r183`

`HalftoneShader` adds a diamond shape, `Sky`/`SkyMesh` add procedural clouds while dropping the legacy gamma-correction curve, and the WebGPU addons add `GodraysNode`.

## Resolution-scale API migrations

**Batch:** `migration-guide-r173-r185`

`PassNode.setResolution()` and `.getResolution()` became `setResolutionScale()` and `getResolutionScale()`, and `WaterMesh.resolution` became `.resolutionScale`. The `resolution` properties of `ReflectorNode`, `AnamorphicNode`, and `GaussianBlurNode` likewise became scalar `resolutionScale` values rather than `Vector2` values.

## Rounded-box serialization and physics

**Batch:** `r179`

`RoundedBoxGeometry` now exposes its type and parameters and implements `toJSON()`. The `RapierPhysics` addon also adds support for this geometry.

## Screen-space lighting nodes

**Batch:** `r181`

The addons add `SSGINode` for screen-space global illumination and `SSSNode` for screen-space shadows.

## SSR resolution and quality controls

**Batch:** `r180`

`SSRPass` adds `resolutionScale`, while `SSRNode` gains a quality setting and uses blurred mipmaps so reflections honor roughness.

```js
ssrPass.resolutionScale = 0.5;
```

## TransformControls viewport and gizmo control

**Batch:** `r185`

`TransformControls` adds viewport support and lets applications control the visibility of rotation gizmos.

## TubePainter end caps

**Batch:** `r181`

`TubePainter` now generates caps as part of its improved geometry output.

## ViewHelper placement

**Batch:** `r183`

`ViewHelper` adds a `location` property for positioning the helper.

## WebGPU Inspector

**Batch:** `r181`

`WebGPURenderer` introduces `Inspector` for renderer inspection and debugging workflows.

