# Addons, post-processing, controls, and tools

Effects, passes, controls, HTML surfaces, inspectors, helpers, and other developer-facing addons.

## Additional HTMLMesh input types (r179)

`HTMLMesh` now supports email and password inputs in addition to its previously supported form controls.

## AnaglyphEffect migration (r183)

`AnaglyphEffect.screenDistance` was renamed to `planeDistance`, and the effect now uses `frameCorners()` for physically correct stereo framing.

## ArcballControls touch-action restoration (r184)

When controls release their element, `ArcballControls` now resets `touch-action` to an empty string rather than forcing `auto`.

## BitonicSort addon (r181)

A new `BitonicSort` addon provides bitonic sorting through the three.js addon surface.

## Configurable TransformControls gizmos (r178)

`TransformControls` gizmo colors are now configurable instead of fixed.

## Controls connection target (r175)

`Controls.connect()` now requires an element. Lifecycle code that reconnects controls must pass the target element explicitly.

```js
controls.connect(renderer.domElement);
```

## Custom tone mapping in OutputPass (r173)

`OutputPass` now supports `THREE.CustomToneMapping`, allowing a custom tone-mapping mode in that post-processing pass.

## Expanded TRAANode inputs and camera support (r184)

`TRAANode` adds a velocity-node source and supports reversed or logarithmic depth buffers and orthographic cameras.

## FirstPersonControls movement changes (r185)

`FirstPersonControls` adds damping, separates movement sources, and adds E/Q key controls.

## Forced Reflector updates (r174)

The `Reflector` addon adds `forceUpdate`, allowing an application to request an otherwise skipped reflection refresh.

```js
reflector.forceUpdate = true;
```

## FSR1 and temporal upsampling (r184)

The addons add an `FSR1Node` port for `WebGPURenderer` and `TAAUNode` for temporal antialiasing with upsampling.

## GTAO temporal filtering (r181)

`GTAONode` gains basic temporal-filtering support.

## HTMLMesh VR inputs (r177)

`HTMLMesh` now supports text and number input controls in VR.

## HTMLTexture (r184)

r184 adds `HTMLTexture`, providing a first-party texture type for HTML-backed content.

## HTMLTexture browser API support (r185)

`HTMLTexture` now supports the new WICG HTML-in-Canvas API signatures.

## Inspector workflow additions (r184)

Inspector adds a Memory tab, forced-WebGL mode, a command-recording Timeline with export, stack-trace capture, TSL graph addons, and extension support.

## Multiple PostProcessing instances (r173)

`PostProcessing` now supports more than one instance, allowing multiple post-processing pipelines to coexist.

## OffscreenCanvas ViewHelper (r181)

`ViewHelper` now supports `OffscreenCanvas`.

## OrbitControls public operations (r183)

`OrbitControls` now exposes its pan, rotate, and dolly methods and adds a `cursorStyle` property.

## PassNode asynchronous compilation and render bounds (r179)

`PassNode` adds `compileAsync()` together with viewport and scissor APIs, allowing a pass to be compiled asynchronously and constrained to explicit render bounds.

## ProgressiveLightMap normals requirement (r181)

`ProgressiveLightMap` now requires normals. Geometry used with it must provide normal data when upgrading to r181.

## Reflector antialiasing samples (r180)

The reflector node adds an AA-samples parameter, allowing its multisampling level to be configured.

## Screen-space lighting nodes (r181)

The addons add `SSGINode` for screen-space global illumination and `SSSNode` for screen-space shadows.

## SSR resolution and quality controls (r180)

`SSRPass` adds `resolutionScale`, while `SSRNode` gains a quality setting and uses blurred mipmaps so reflections honor roughness.

```js
ssrPass.resolutionScale = 0.5;
```

## TransformControls viewport and gizmo control (r185)

`TransformControls` adds viewport support and lets applications control the visibility of rotation gizmos.

## TubePainter end caps (r181)

`TubePainter` now generates caps as part of its improved geometry output.

## ViewHelper placement (r183)

`ViewHelper` adds a `location` property for positioning the helper.
