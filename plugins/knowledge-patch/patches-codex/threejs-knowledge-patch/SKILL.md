---
name: threejs-knowledge-patch
description: three.js
version: "r185"
license: MIT
metadata:
  author: Nevaberry
---


# three.js Knowledge Patch

Use this skill when working on a three.js application, addon, node graph, asset
pipeline, renderer integration, or upgrade. Inspect the project's `three`
dependency before applying release-specific advice. Prefer the installed
package, application code, and tests when they disagree with compatibility
guidance.

## Reference index

| Reference | Topics |
| --- | --- |
| [migrations-and-deprecations.md](references/migrations-and-deprecations.md) | Removed and deprecated APIs, renames, upgrade-sensitive behavior |
| [rendering-and-webxr.md](references/rendering-and-webxr.md) | WebGL, WebGPU, buffers, render targets, shadows, compute, WebXR |
| [tsl-and-node-graphs.md](references/tsl-and-node-graphs.md) | TSL, node materials, shader graphs, storage nodes, transpilation |
| [assets-and-interchange.md](references/assets-and-interchange.md) | Loaders, exporters, formats, serialization, cache and editor interchange |
| [scene-animation-and-geometry.md](references/scene-animation-and-geometry.md) | Scene graph, animation, materials, lighting, geometry, math, physics |
| [addons-postprocessing-and-controls.md](references/addons-postprocessing-and-controls.md) | Passes, effects, controls, HTML surfaces, inspectors and utilities |

## Start with migration hazards

### Removed modules and assets

- Replace removed `PeppersGhostEffect`, `RGBMLoader`, `MeshPostProcessingMaterial`,
  `TiledLighting`, scriptable-node APIs, and obsolete VOX classes before
  upgrading.
- Replace `WebGLCubeRenderTarget` with `CubeRenderTarget` when using
  `WebGPURenderer`.
- Use `USDLoader` instead of deprecated `USDZLoader`; avoid new uses of
  `MeshGouraudMaterial`, `LottieLoader`, `VTKLoader`, and `LWOLoader`.
- Do not resolve `examples/fonts`, DRACO exporter encoders, or Lottie/TTF
  libraries from the installed package; these assets are no longer bundled.
- Audit all previously deprecated APIs before an r178 upgrade because that
  release removed deprecated code broadly.

### High-impact renames

| Old | Current |
| --- | --- |
| `NodeBuilder.monitor` | `NodeBuilder.observer` |
| `varying()` | `toVarying()` |
| `vertexStage()` | `toVertexStage()` |
| `RGBELoader` | `HDRLoader` |
| `label()` | `setName()` |
| `DFGApprox` | `DFGLUT` |
| `Line2NodeMaterial.useColor` | `Line2NodeMaterial.vertexColors` |
| `AnaglyphEffect.screenDistance` | `AnaglyphEffect.planeDistance` |
| `directionToFaceDirection` | `negateOnBackSide` |
| `PI2` | `TWO_PI` |
| `reverseDepthBuffer` | `reversedDepthBuffer` |

Also replace `directionToColor()` with `packNormalToRGB()` and
`colorToDirection()` with `unpackRGBToNormal()`. For WebGL shader directions,
choose `transformNormalByInverseViewMatrix()` for normals and
`transformDirectionByInverseViewMatrix()` for directions.

### Async lifecycle changes

- Pass an element to `Controls.connect(element)`.
- Await `renderer.init()` before renderer-dependent loader detection or GPU
  work; initialization returns the renderer.
- Use `DRACOExporter.parseAsync()` in place of `parse()`.
- Treat `FileLoader.load()` and `ImageBitmapLoader.load()` as callback-driven;
  they no longer return a value.
- Do not build new code on deprecated `renderAsync()` or `computeAsync()`;
  `waitForGPU()` is gone.
- `WebGPURenderer.compileAsync()` is genuinely non-blocking.
- Use `Loader.abort()` as the common cancellation entry point.

### State and default changes

- `SpriteNodeMaterial.transparent` defaults to `true`; set it explicitly when
  opaque behavior is required.
- Camera scale no longer contributes to the view matrix.
- `SpriteNodeMaterial.sizeAttenuation` only affects perspective cameras.
- `Cache` does not retain `Blob` values.
- Loader cache keys are isolated by loader type.
- When `matrixAutoUpdate` is disabled and `.matrix` changes directly, set
  `matrixWorldNeedsUpdate = true` before `updateWorldMatrix()`.
- Raw WebGL pixel-store mutations must go through
  `renderer.state.pixelStorei()` to keep cached renderer state synchronized.
- Background and environment-map rotations now follow object rotation
  conventions; remove compensating rotations written for the old convention.
- `FBXLoader` converts +Z-up assets to +Y-up automatically.

## Renderer quick reference

### Output and render-target control

- Output typing appears as renderer `colorBufferType`, WebGL
  `outputBufferType`, and WebGPU backend `outputType`. On the WebGPU path,
  `getOutputBufferType()` replaces `getColorBufferType()`.
- Use `WebGPURenderer.setOutputRenderTarget()` to choose the renderer output
  target explicitly.
- Use `initRenderTarget()` when a WebGPU target must be initialized before its
  first render.
- `RenderTarget.clone()` creates independent texture resources, and
  `RenderTarget.copy()` preserves multiview state.
- Do not resize render targets during an XR render.

### WebGPU capabilities

- Compatibility mode can be requested explicitly; automatic negotiation
  upgrades to core mode where possible and disables antialiasing if
  compatibility mode remains active.
- Render bundles support transparent objects, MRT, and `InstancedMesh`.
- MRT supports per-attachment blending and material `outputNode`.
- Texture support includes 3D and array storage textures, texture-array render
  targets, BPTC formats, manual mipmaps, and `GPUTexture`-backed external
  textures.
- Use `ReadbackBuffer` or partial `getArrayBufferAsync()` reads for targeted
  GPU readback.
- `dispatchWorkgroupsIndirect` drives compute counts from an indirect buffer.
- The addon renderer provides dynamic lights and Forward+ clustered lighting.

### WebGL capabilities

- `reversedDepthBuffer` is the current constructor option.
- Shadows support alpha-to-coverage; `PCFShadowMap` now supplies soft shadows.
- MRT supports pixel readback, 2D array textures, and MSAA through the WebGL
  backend used by `WebGPURenderer`.
- `WebGLRenderer` offers `outputBufferType`, `setEffects()`, packed normal maps,
  and a `NodeMaterial` compatibility layer.

### WebXR

- `WebGPURenderer` has an XR manager with XR layers, MSAA, dynamic
  `ArrayCamera` sizing, tone mapping, and output color-space handling.
- Use `XRRenderTarget` for XR-specific target work.
- Raw camera access is available from `WebXRManager`.
- Grip updates can emit an event through `WebXRController`.

## TSL and node-graph quick reference

### Current construction patterns

- Use `toVarying()`, `toVertexStage()`, `setName()`, and assignment's automatic
  `toVar()` conversion.
- Use `positionGeometry` rather than `positionLocal` when `positionNode` needs
  pre-skinning or otherwise pre-transformed vertices.
- Use `premultiplyAlpha`; `premult` is the former name.
- Use `DFGLUT`; do not call removed `nodeObject()` for Node classes.
- TSL no longer defines `string` or `arrayBuffer`.

### Data and compute

- Graphs can use `mat2`, arrays, structs, atomics, boolean uniforms, matrix
  attributes, storage-backed instance attributes, and 3D storage textures.
- Texture operations include `load()`, `sample()`, offset access,
  `texture3DLoad()`, `texture3DLevel()`, `textureGather()`, and
  `textureGatherCompare()`.
- Compute work can use `computeKernel()`, subgroup reductions, indirect
  dispatch, global/local scopes, and frame or before-event hooks.
- Provide tangent attributes explicitly when the graph requires them; TSL no
  longer auto-generates tangents.

### Diagnostics and transpilation

- `debug()` callbacks receive `(builder, code)`; `DebugNode` callbacks receive
  raw data.
- `StackTrace` and stack `debug()` are available for diagnostics.
- The transpiler handles matrices, boolean vectors, varyings, texture
  operations, `discard`, `switch`, structs, bitcasts, simplified `Fn()`
  layouts, linking, and WGSL encoding.

## Assets and interchange quick reference

- `ImageUtils.getDataURL(image, type)` selects the encoded MIME type; without a
  type, do not assume the source image format is preserved.
- `DRACOLoader` and `KTX2Loader` use relative file URLs by default. Configure
  deployed decoder/transcoder paths deliberately.
- `GLTFLoader` no longer probes WebP or AVIF support; gate incompatible assets
  in the application.
- `KTX2Loader` covers additional ASTC, EAC, BCn, PVRTC, RGB9E5, R11G11B10,
  and 16-bit normalized formats and can generate mipmaps.
- `MaterialLoader.registerMaterial()` and `Material.fromJSON()` support custom
  material deserialization.
- `GLTFExporter` carries animation metadata, supports animations across
  multiple scenes, and can export WebP textures.
- `PLYLoader` and `PLYExporter` preserve declared attribute data types.
- `USDLoader` handles unified USD input, composition, animation, broader
  primitives and materials; `USDZExporter` supports hierarchy, animation, and
  multi-material output.

## Scene, material, and geometry quick reference

- `Material.allowOverride` controls override-material replacement and is
  preserved by `copy()`.
- `Object3D.static` and `pivot` survive copying and serialization.
- `Mesh` and `Sprite` expose `count`; `BatchedMesh` supports per-instance
  opacity and wireframes.
- Physically based output changed through corrected blending, GGX VNDF PMREM
  sampling, direct-light multi-scattering compensation, and energy-conservation
  fixes. Revalidate image baselines after upgrades.
- Geometry without normals is flat-shaded automatically, but
  `ProgressiveLightMap` still requires normals.
- `CapsuleGeometry` uses `height` and `heightSegments`; `TorusGeometry` adds
  `thetaStart` and `thetaLength`.
- Quaternion slerp extrapolates outside `[0, 1]`.
- Use `Timer` for new timing code instead of deprecated `Clock`.

## Working method

1. Read the installed `three` version and identify direct imports from
   `three/addons`, TSL, renderer internals, and copied example assets.
2. Search the migration reference for every imported symbol and directly
   accessed renderer or node property.
3. Read the topic reference for the subsystem being changed; many rendering
   changes alter output without causing an exception.
4. Update application code and asset URLs together when an addon, decoder, or
   packaged resource moved.
5. Exercise both WebGL and WebGPU paths when the application supports both.
6. Re-run image comparisons, animation tests, serializer fixtures, and XR or
   input smoke tests affected by the change.

When code depends on renderer internals, inspect the installed source before
choosing a property or class name. Internal renderer and node-pipeline surfaces
have changed more often than public scene APIs.
