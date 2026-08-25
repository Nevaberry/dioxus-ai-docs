# Renderers, GPU Backends, and XR

Use this reference for WebGLRenderer, WebGPURenderer, backend capabilities, render targets, GPU resources, WebXR, and renderer state.

## Built-in renderer contexts

**Batch:** `r182`

TSL adds a global renderer-context node together with `builtinShadowContext()` and `builtinAOContext()` for accessing built-in shadow and ambient-occlusion contexts.

## CanvasTarget

**Batch:** `r181`

`WebGPURenderer` introduces `CanvasTarget` as a canvas-backed target type.

## CanvasTarget cache disposal

**Batch:** `r184`

Cached `CanvasTarget` entries can now be disposed individually instead of requiring cache-wide cleanup.

## Clustered WebGPU lighting

**Batch:** `r185`

The `WebGPURenderer` addon adds Forward+ clustered-lighting shading.

## Corrected renderer blending

**Batch:** `r178`

Blending formulas were corrected across all renderers. Scenes that relied on the previous formulas can produce different blended output after upgrading.

## Depth textures in WebGLOutput

**Batch:** `r184`

`WebGLOutput` now adds a `DepthTexture` to the scene render target.

## Dynamic WebGPU lights

**Batch:** `r184`

The WebGPU addon renderer introduces dynamic lights.

## Dynamic WebGPU shadow-map types

**Batch:** `r181`

The WebGPU renderer now permits `shadowMap.type` to be switched dynamically instead of treating the selected type as fixed.

## Dynamically sized ArrayCamera

**Batch:** `r173`

`WebGPURenderer` now permits dynamic resizing of an `ArrayCamera` camera array, so the array no longer has to remain fixed after setup.

## Expanded WebGPU texture and lighting support

**Batch:** `r185`

`WebGPURenderer` can render to texture arrays, supports all BPTC formats, and adds a `lighting.enabled` control.

## Float16Array renderer support

**Batch:** `r178`

Renderers gain initial support for `Float16Array`, allowing half-precision array data to enter supported rendering paths.

## GPUTexture-backed external textures

**Batch:** `r180`

`WebGPURenderer` can now use an `ExternalTexture` with a `GPUTexture`.

## HDR in WebGPURenderer

**Batch:** `r180`

`WebGPURenderer` adds HDR support in r180.

## Independent RenderTarget clones

**Batch:** `migration-guide-r173-r185`

`RenderTarget.clone()` now performs a full structural clone without sharing texture resources with the original target.
## Indirect compute dispatch

**Batch:** `r181`

`WebGPURenderer` adds `dispatchWorkgroupsIndirect`, enabling compute workgroup counts to come from an indirect GPU buffer.

## Instanced meshes in render bundles

**Batch:** `r185`

Renderer render bundles now fully support `InstancedMesh`.

## Manual WebGPU mipmaps

**Batch:** `r180`

`WebGPURenderer` now supports manually supplied mipmaps for both regular and cube textures.

## MRT pixel readback

**Batch:** `r177`

`WebGLRenderer.readRenderTargetPixels()` now supports multiple render targets, allowing pixel readback from MRT rendering.

## MRT render bundles

**Batch:** `r181`

WebGPU render bundles now work with multiple render targets.

## MSAA with MRT on the WebGL backend

**Batch:** `r178`

The WebGL backend used by `WebGPURenderer` now supports combining MSAA with multiple render targets.

## Raw WebGL pixel-store state

**Batch:** `migration-guide-r173-r185`

Code that changes pixel-storage values through the raw WebGL 2 context must now call `renderer.state.pixelStorei()` so renderer state remains synchronized.

## Renderer compatibility replacements

**Batch:** `migration-guide-r173-r185`

`MeshPostProcessingMaterial` was removed, and `WebGLCubeRenderTarget` can no longer be used with `WebGPURenderer`; use `CubeRenderTarget` there. With `WebGLRenderer`, deprecated `PCFSoftShadowMap` should be replaced by `PCFShadowMap`, which now produces soft shadows too.

## Renderer initialization return value

**Batch:** `r174`

`Renderer.init()` now returns the renderer itself, so asynchronous initialization can be assigned or chained.

```js
const readyRenderer = await renderer.init();
```

## Renderer output buffer types

**Batch:** `r173`

The renderer introduces `colorBufferType`, and the WebGPU backend adds an `.outputType` backend parameter. These provide explicit control over output-buffer typing.

## Renderer texture and color support

**Batch:** `r184`

The renderers add `EXT_texture_norm16` formats, while `WebGLRenderer` adds packed-normal-map support and uses the working color space for render targets.

## Reverse depth buffering in WebGL

**Batch:** `r175`

`WebGLRenderer` now correctly supports `reverseDepthBuffer: true`; applications no longer need to treat that configuration as broken.

## Reversed- and logarithmic-depth identifiers

**Batch:** `migration-guide-r173-r185`

`WebGLRenderer` renamed the `reverseDepthBuffer` constructor parameter to `reversedDepthBuffer`. Custom shaders must also replace `USE_REVERSEDEPTHBUF` with `USE_REVERSED_DEPTH_BUFFER` and `USE_LOGDEPTHBUF` with `USE_LOGARITHMIC_DEPTH_BUFFER`.

## Reversed-depth additions

**Batch:** `r183`

Core adds the `ReversedDepthFuncs` dictionary, viewport-depth view-Z functions support reversed depth, and `WebGPURenderer` gains basic reversed-depth-buffer support.

## Rotated environment maps in WebGPU

**Batch:** `r174`

`WebGPURenderer` now honors environment-map rotation, bringing rotated environment lighting and backgrounds to the WebGPU path.

## StorageTexture manual mipmaps

**Batch:** `r181`

`WebGPURenderer` now permits manual mipmap creation with `StorageTexture`.

## SVGRenderer depth and clipping

**Batch:** `r182`

`SVGRenderer` adds depth sorting for sprites and SVG objects, along with near- and far-plane clipping support.

## Timestamp query spelling

**Batch:** `r173`

The WebGPU renderer property `timeStampQuerySet` was renamed to `timestampQuerySet`; integrations accessing it directly must use the corrected spelling.

## Transparent WebGPU render bundles

**Batch:** `r175`

`WebGPURenderer` render bundles now support transparent objects.

## Truly non-blocking WebGPU compilation

**Batch:** `r184`

`WebGPURenderer.compileAsync()` is now genuinely non-blocking; code can rely on the returned asynchronous work not blocking the calling thread.

## Two-dimensional array textures in MRT

**Batch:** `r179`

`WebGLRenderer` now supports using 2D array textures with multiple render targets.

## WebGL output buffers and effects

**Batch:** `r182`

`WebGLRenderer` adds `outputBufferType` and `setEffects()`, providing explicit output-buffer typing and an effects setup entry point.

## WebGPU async API deprecations

**Batch:** `r181`

`renderAsync()`, `computeAsync()`, and related asynchronous renderer methods are deprecated, and `waitForGPU()` was removed. Callers must stop relying on `waitForGPU()` and migrate away from the deprecated async entry points.

## WebGPU compatibility mode

**Batch:** `r176`

`WebGPURenderer` introduces `compatibilityMode`, providing an explicit compatibility rendering mode.

## WebGPU compatibility negotiation

**Batch:** `r183`

`WebGPURenderer` now requests compatibility mode and upgrades to core mode where available. Antialiasing is disabled when compatibility mode remains active.

## WebGPU MRT blending

**Batch:** `r183`

`WebGPURenderer` now supports a separate blend configuration for each multiple-render-target attachment.

## WebGPU MRT output nodes

**Batch:** `r175`

`WebGPURenderer` now honors `material.outputNode` when MRT is used, so MRT rendering no longer ignores the material's custom output.

## WebGPU output render targets

**Batch:** `r174`

`WebGPURenderer` adds `setOutputRenderTarget()` for explicitly selecting the target used for renderer output.

## WebGPU output-buffer API rename

**Batch:** `r182`

In the WebGPU renderer path, `getColorBufferType()` was renamed to `getOutputBufferType()`. `getPreferredCanvasFormat()` now uses `outputType` as its default when choosing the canvas format.

## WebGPU pipeline class renames

**Batch:** `r183`

The WebGPU renderer renamed `Nodes` to `NodeManager`, `RenderPipeline` to `RenderObjectPipeline`, and `PostProcessing` to `RenderPipeline`. Imports and direct construction must use the final names.

## WebGPU precision control

**Batch:** `r176`

`WebGPURenderer` now exposes `renderer.highPrecision` for selecting its high-precision path.

## WebGPU premultiplied-alpha backgrounds

**Batch:** `migration-guide-r173-r185`

The r185 premultiplied-alpha implementation can expose blending problems in `WebGPURenderer`; use an opaque `Scene.background` or opaque `renderer.setClearColor()` value unless the canvas must blend with the HTML background.

## WebGPU premultiplied-alpha handling

**Batch:** `r177`

The WebGPU backend now honors `Texture.premultiplyAlpha`; applications no longer need to treat that flag as ineffective on the WebGPU path.

## WebGPU render-target initialization

**Batch:** `r183`

`WebGPURenderer` adds `initRenderTarget()` for explicit render-target initialization and exports `CubeRenderTarget`.

## WebGPU shadow-map arrays and multiview

**Batch:** `r176`

`WebGPURenderer` adds shadow-map-array and multiview support, making both capabilities available on the WebGPU path.

## WebGPU stencil references

**Batch:** `r174`

The WebGPU backend now supports `setStencilReference()`, so stencil-reference rendering no longer requires the WebGL backend.

## WebGPU storage textures and index buffers

**Batch:** `r178`

`WebGPURenderer` adds `Storage3DTexture` and `StorageArrayTexture`, and permits a storage buffer to back an index attribute.

## WebGPU storage textures and partial readback

**Batch:** `r184`

`WebGPURenderer` supports unfilterable float32 `StorageTexture`s and introduces `ReadbackBuffer`; `getArrayBufferAsync()` also gains partial-readback support.

## WebGPU volumetric lighting

**Batch:** `r174`

`WebGPURenderer` gains volumetric-lighting support in r174.

## WebGPU WebXR output handling

**Batch:** `r174`

WebXR rendering through `WebGPURenderer` now applies tone mapping and output color-space handling.

## WebGPU XR rendering

**Batch:** `r173`

`WebGPURenderer` gains an `XRManager` with XR layers and MSAA support, together with the new `XRRenderTarget` render-target type.

## WebGPUBackend drawing-buffer signature

**Batch:** `r179`

The obsolete argument to `WebGPUBackend.getDrawingBufferSize()` was removed. Direct callers must use the reduced signature.

## WebXR controller grip updates

**Batch:** `r184`

`WebXRController` adds a grip update event when grip updates are enabled.

## WebXR raw camera access

**Batch:** `r179`

`WebXRManager` adds a Raw Camera Access module, making raw XR camera access available through the manager.

## XR render-target resizing restriction

**Batch:** `r175`

Render targets can no longer be resized while rendering in XR; defer resize operations until XR rendering has ended.

## Zero-count WebGPU draws

**Batch:** `r176`

`WebGPURenderer` now skips a draw call when `object.count` is `0`, so a zero count reliably suppresses rendering.

