# Rendering, GPU backends, and WebXR

WebGL, WebGPU, render-target, buffer, shadow, compute, and XR behavior.

## CanvasTarget (r181)

`WebGPURenderer` introduces `CanvasTarget` as a canvas-backed target type.

## CCDIKSolver blending (r174)

`CCDIKSolver` now supports `blendFactor`, allowing IK corrections to be applied partially instead of always at full strength.

## Clustered WebGPU lighting (r185)

The `WebGPURenderer` addon adds Forward+ clustered-lighting shading.

## Corrected renderer blending (r178)

Blending formulas were corrected across all renderers. Scenes that relied on the previous formulas can produce different blended output after upgrading.

## Depth textures in WebGLOutput (r184)

`WebGLOutput` now adds a `DepthTexture` to the scene render target.

## Dynamic WebGPU lights (r184)

The WebGPU addon renderer introduces dynamic lights.

## Dynamic WebGPU shadow-map types (r181)

The WebGPU renderer now permits `shadowMap.type` to be switched dynamically instead of treating the selected type as fixed.

## Expanded WebGPU texture and lighting support (r185)

`WebGPURenderer` can render to texture arrays, supports all BPTC formats, and adds a `lighting.enabled` control.

## Float16Array renderer support (r178)

Renderers gain initial support for `Float16Array`, allowing half-precision array data to enter supported rendering paths.

## GPUTexture-backed external textures (r180)

`WebGPURenderer` can now use an `ExternalTexture` with a `GPUTexture`.

## HDR in WebGPURenderer (r180)

`WebGPURenderer` adds HDR support in r180.

## Instanced meshes in render bundles (r185)

Renderer render bundles now fully support `InstancedMesh`.

## Manual WebGPU mipmaps (r180)

`WebGPURenderer` now supports manually supplied mipmaps for both regular and cube textures.

## MRT pixel readback (r177)

`WebGLRenderer.readRenderTargetPixels()` now supports multiple render targets, allowing pixel readback from MRT rendering.

## MRT render bundles (r181)

WebGPU render bundles now work with multiple render targets.

## MSAA with MRT on the WebGL backend (r178)

The WebGL backend used by `WebGPURenderer` now supports combining MSAA with multiple render targets.

## Renderer initialization return value (r174)

`Renderer.init()` now returns the renderer itself, so asynchronous initialization can be assigned or chained.

```js
const readyRenderer = await renderer.init();
```

## Renderer output buffer types (r173)

The renderer introduces `colorBufferType`, and the WebGPU backend adds an `.outputType` backend parameter. These provide explicit control over output-buffer typing.

## Renderer texture and color support (r184)

The renderers add `EXT_texture_norm16` formats, while `WebGLRenderer` adds packed-normal-map support and uses the working color space for render targets.

## Reverse depth buffering in WebGL (r175)

`WebGLRenderer` now correctly supports `reverseDepthBuffer: true`; applications no longer need to treat that configuration as broken.

## Rotated environment maps in WebGPU (r174)

`WebGPURenderer` now honors environment-map rotation, bringing rotated environment lighting and backgrounds to the WebGPU path.

## Shadow rendering changes (r182)

`WebGLRenderer` modernizes its shadow-mapping path, while `WebGPURenderer` adds PCF filtering based on Vogel-disk sampling and interleaved gradient noise. Existing shadow output can therefore change after upgrading.

## SVGRenderer depth and clipping (r182)

`SVGRenderer` adds depth sorting for sprites and SVG objects, along with near- and far-plane clipping support.

## Transparent WebGPU render bundles (r175)

`WebGPURenderer` render bundles now support transparent objects.

## Truly non-blocking WebGPU compilation (r184)

`WebGPURenderer.compileAsync()` is now genuinely non-blocking; code can rely on the returned asynchronous work not blocking the calling thread.

## Two-dimensional array textures in MRT (r179)

`WebGLRenderer` now supports using 2D array textures with multiple render targets.

## WebGL output buffers and effects (r182)

`WebGLRenderer` adds `outputBufferType` and `setEffects()`, providing explicit output-buffer typing and an effects setup entry point.

## WebGPU compatibility mode (r176)

`WebGPURenderer` introduces `compatibilityMode`, providing an explicit compatibility rendering mode.

## WebGPU compatibility negotiation (r183)

`WebGPURenderer` now requests compatibility mode and upgrades to core mode where available. Antialiasing is disabled when compatibility mode remains active.

## WebGPU Inspector (r181)

`WebGPURenderer` introduces `Inspector` for renderer inspection and debugging workflows.

## WebGPU MRT blending (r183)

`WebGPURenderer` now supports a separate blend configuration for each multiple-render-target attachment.

## WebGPU MRT output nodes (r175)

`WebGPURenderer` now honors `material.outputNode` when MRT is used, so MRT rendering no longer ignores the material's custom output.

## WebGPU output render targets (r174)

`WebGPURenderer` adds `setOutputRenderTarget()` for explicitly selecting the target used for renderer output.

## WebGPU precision control (r176)

`WebGPURenderer` now exposes `renderer.highPrecision` for selecting its high-precision path.

## WebGPU premultiplied-alpha handling (r177)

The WebGPU backend now honors `Texture.premultiplyAlpha`; applications no longer need to treat that flag as ineffective on the WebGPU path.

## WebGPU render-target initialization (r183)

`WebGPURenderer` adds `initRenderTarget()` for explicit render-target initialization and exports `CubeRenderTarget`.

## WebGPU shadow-map arrays and multiview (r176)

`WebGPURenderer` adds shadow-map-array and multiview support, making both capabilities available on the WebGPU path.

## WebGPU stencil references (r174)

The WebGPU backend now supports `setStencilReference()`, so stencil-reference rendering no longer requires the WebGL backend.

## WebGPU storage textures and index buffers (r178)

`WebGPURenderer` adds `Storage3DTexture` and `StorageArrayTexture`, and permits a storage buffer to back an index attribute.

## WebGPU storage textures and partial readback (r184)

`WebGPURenderer` supports unfilterable float32 `StorageTexture`s and introduces `ReadbackBuffer`; `getArrayBufferAsync()` also gains partial-readback support.

## WebGPU volumetric lighting (r174)

`WebGPURenderer` gains volumetric-lighting support in r174.

## WebGPU WebXR output handling (r174)

WebXR rendering through `WebGPURenderer` now applies tone mapping and output color-space handling.

## WebGPU XR rendering (r173)

`WebGPURenderer` gains an `XRManager` with XR layers and MSAA support, together with the new `XRRenderTarget` render-target type.

## WebGPUBackend drawing-buffer signature (r179)

The obsolete argument to `WebGPUBackend.getDrawingBufferSize()` was removed. Direct callers must use the reduced signature.

## WebXR controller grip updates (r184)

`WebXRController` adds a grip update event when grip updates are enabled.

## WebXR raw camera access (r179)

`WebXRManager` adds a Raw Camera Access module, making raw XR camera access available through the manager.

## XR render-target resizing restriction (r175)

Render targets can no longer be resized while rendering in XR; defer resize operations until XR rendering has ended.

## Zero-count WebGPU draws (r176)

`WebGPURenderer` now skips a draw call when `object.count` is `0`, so a zero count reliably suppresses rendering.
