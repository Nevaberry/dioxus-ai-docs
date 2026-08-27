---
name: threejs-knowledge-patch
description: three.js
version: "r185"
license: MIT
metadata:
  author: Nevaberry
---


# three.js Knowledge Patch

## When to load this skill

Load this skill when a task involves:

- upgrading a three.js application or addon;
- choosing between WebGLRenderer and WebGPURenderer APIs;
- migrating TSL, NodeMaterial, shader-node, or compute code;
- diagnosing changed lighting, blending, shadows, depth, or color output;
- updating loaders, exporters, decoder paths, or packaged assets;
- maintaining post-processing, controls, XR, physics, or editor integrations.

Start with the quick reference below for migration hazards. Open the matching
topic reference before editing code; the references retain API details,
behavior changes, defaults, and batch attribution.

## Reference index

| Reference | Topics |
| --- | --- |
| [Core, animation, and geometry](references/core-animation-and-geometry.md) | Object and scene behavior, animation, serialization, geometry, math, timing |
| [Materials, lighting, and textures](references/materials-lighting-and-textures.md) | Materials, PBR, lights, shadows, texture behavior, color and blending |
| [TSL and node APIs](references/tsl-and-node-apis.md) | TSL migrations, NodeMaterial, shader helpers, node events, compute and transpilation |
| [Renderers, GPU backends, and XR](references/renderers-gpu-and-xr.md) | WebGL, WebGPU, render targets, MRT, GPU resources, depth, WebXR |
| [Loaders, exporters, and assets](references/loaders-exporters-and-assets.md) | Asset formats, loading, export, serialization, codecs, package layout |
| [Addons, controls, and post-processing](references/addons-controls-and-post-processing.md) | Effects, controls, post-processing, browser addons, physics, inspector, editor |

## Breaking changes and removals

Audit these before attempting an upgrade:

- Replace `InstancedPointsNodeMaterial` with `PointsNodeMaterial`.
- Replace `RGBELoader` with `HDRLoader`; `RGBMLoader` is removed.
- Replace `Clock` with core `Timer`; update imports from the former addon path.
- Remove uses of `LightProbe.fromJSON()`.
- Replace legacy `LuminanceFormat` and `LuminanceAlphaFormat`.
- Replace `PeppersGhostEffect`, `AnamorphicNode`, and `TiledLighting`.
- Replace `MeshPostProcessingMaterial`.
- Stop using removed `Line2NodeMaterial.lineWidth`.
- Replace `Line2NodeMaterial.useColor` with `.vertexColors`.
- Replace the scriptable node and `ScriptableNodeResources`.
- Replace `VOXMesh` and `VOXData3DTexture` construction with their function APIs.
- Do not use `WebGLCubeRenderTarget` with `WebGPURenderer`; use
  `CubeRenderTarget`.
- Stop depending on `renderAsync()`, `computeAsync()`, or removed
  `waitForGPU()`.
- Stop expecting `FileLoader.load()` or `ImageBitmapLoader.load()` to return
  a value; use `onLoad`.
- Replace `DRACOExporter.parse()` with `parseAsync()`.
- Stop passing width and height to `SMAAPass` and `HalftonePass`.
- Stop passing `flipVertical` to `LUTImageLoader`; set `loader.flip = true`.
- Stop resolving example fonts, DRACO exporter encoders, or the LottieLoader
  and TTFLoader libraries from bundled package copies.

## Deprecations to remove from new code

- `AnimationClip.parseAnimation()`
- `MeshGouraudMaterial`
- `LottieLoader`
- `premultipliedGaussianBlur()`
- `SkyMesh.isSky`; use `isSkyMesh`
- `VTKLoader`
- `LWOLoader`
- `Matrix3.scale()`, `.rotate()`, and `.translate()`
- `DRACOLoader.setDecoderConfig()`
- `SVGLoader.createShapes()`; use `shapePath.toShapes()`
- `KTX2Loader.detectSupportAsync()`; initialize the renderer, then call
  `detectSupport()`
- `USDZLoader`; use `USDLoader`
- `PCFSoftShadowMap`; use `PCFShadowMap`

## Final API names

Use final names rather than intermediate or historical spellings.

| Replace | With |
| --- | --- |
| `NodeBuilder.monitor` | `NodeBuilder.observer` |
| `timeStampQuerySet` | `timestampQuerySet` |
| `varying()` | `toVarying()` |
| `vertexStage()` | `toVertexStage()` |
| `premult()` | `premultiplyAlpha()` |
| `label()` | `setName()` |
| `TriplanarTexturesNode` | `triplanarTextures()` |
| `EquirectUVNode` | `equirectUV()` |
| `MatcapUVNode` | `matcapUV` |
| `DFGApprox` | `DFGLUT` |
| `directionToFaceDirection` | `negateOnBackSide` |
| `PI2` | `TWO_PI` |
| `directionToColor()` | `packNormalToRGB()` |
| `colorToDirection()` | `unpackRGBToNormal()` |
| `HemisphereLightNode.normalView` | `normalWorld` |
| WebGPU `getColorBufferType()` | `getOutputBufferType()` |
| WebGPU `Nodes` | `NodeManager` |
| WebGPU `RenderPipeline` | `RenderObjectPipeline` |
| WebGPU `PostProcessing` | `RenderPipeline` |
| `AnaglyphEffect.screenDistance` | `planeDistance` |
| `PassNode.setResolution()` | `setResolutionScale()` |
| `PassNode.getResolution()` | `getResolutionScale()` |
| `WaterMesh.resolution` | `resolutionScale` |
| `reverseDepthBuffer` constructor option | `reversedDepthBuffer` |
| `USE_REVERSEDEPTHBUF` | `USE_REVERSED_DEPTH_BUFFER` |
| `USE_LOGDEPTHBUF` | `USE_LOGARITHMIC_DEPTH_BUFFER` |
| `ColorManagement.fromWorkingColorSpace()` | `workingToColorSpace()` |
| `ColorManagement.toWorkingColorSpace()` | `colorSpaceToWorking()` |
| `ParametricGeometries` | `ParametricFunctions` |

The renderer shadow transmission switch is
`shadowMap.transmitted`; do not use the interim `color` or `colored` names.

## Renderer and backend migration

Initialize asynchronous renderers explicitly:

```js
const renderer = await new THREE.WebGPURenderer(parameters).init();
```

After initialization, use the synchronous renderer surface unless a specific
API is documented as asynchronous. `compileAsync()` is genuinely non-blocking.

For backend-sensitive code:

- `WebGPURenderer` can negotiate compatibility mode and upgrade to core mode.
- Antialiasing is disabled if compatibility mode remains active.
- Render targets cannot be resized during XR rendering.
- A zero `object.count` suppresses a WebGPU draw.
- Render bundles support transparent objects, MRT, and instanced meshes.
- MRT supports per-attachment blending and material output nodes.
- WebGL MRT supports pixel readback, 2D array textures, and MSAA through the
  WebGL backend used by WebGPURenderer.
- Use `initRenderTarget()` when explicit WebGPU target initialization is
  required.
- Use `renderer.state.pixelStorei()` for raw WebGL pixel-store changes.

For reversed depth, use the final constructor and shader identifiers in the
table above. Viewport-depth view-Z helpers and `ReversedDepthFuncs` also support
reversed depth.

For a premultiplied-alpha WebGPU canvas, use an opaque `Scene.background` or
opaque `renderer.setClearColor()` unless HTML-background compositing is
required.

## TSL and NodeMaterial migration

Apply these rules before debugging generated shader code:

- `assign()` performs `toVar()` automatically.
- Use `positionGeometry`, not `positionLocal`, when `material.positionNode`
  needs vertices before internal transforms such as skinning.
- Geometry must provide tangents when the node graph needs them; TSL no longer
  creates tangent attributes automatically.
- Geometry without normals is forced to flat shading.
- `DebugNode` callbacks receive raw data.
- The earlier `debug()` callback form changed to `( builder, code )`.
- `AfterImageNode.damp` is a `Node<float>`; pass a node constant or uniform.
- `SpriteNodeMaterial.transparent` defaults to `true`.
- `SpriteNodeMaterial.sizeAttenuation` applies only to perspective cameras.
- `NodeMaterial` honors `premultipliedAlpha`, supports `compute()`, and exposes
  masking controls.
- `bufferAttribute()` accepts `mat3` and `mat4`.
- `uniform()` accepts booleans.
- Texture nodes support `load()`, offsets, 3D reads, storage reads and writes,
  and gather operations.

Open the TSL reference for control-flow, event, layout, scope, bit operation,
transpiler, compute-kernel, and helper additions.

## Asset pipeline migration

- `ImageUtils.getDataURL()` accepts an optional output MIME type; without an
  override, do not assume it preserves the source format.
- Loader cache keys are loader-specific, and `Cache` no longer stores `Blob`
  values.
- `Loader.abort()` is the common cancellation entry point.
- `GLTFLoader` no longer detects WebP or AVIF support for the application.
- `DRACOLoader` and `KTX2Loader` use relative file URLs by default.
- Decoder URLs for glTF use are exported.
- `FBXLoader` converts +Z-up assets to +Y-up; remove duplicate corrective
  rotations.
- EXR output is linear-sRGB and supports expanded compression and multipart
  forms.
- `GLTFExporter` preserves animation metadata and supports animations spanning
  multiple scenes.
- `MaterialLoader.registerMaterial()` and `Material.fromJSON()` support custom
  material deserialization.
- `RenderTarget.clone()` creates independent texture resources.

## Visual-output changes to review

Create comparison renders when an upgrade touches:

- corrected blending formulas;
- GGX VNDF PMREM sampling;
- direct-light multi-scattering energy compensation;
- rough-reflection mixing and the WebGL DFG LUT;
- intermediate-metalness, iridescence, or sheen energy conservation;
- shadow filtering and alpha-to-coverage;
- environment or background rotation;
- `RoomEnvironment`-generated PMREMs;
- Neutral tone mapping in editor projects;
- GTAO radius and scale;
- additive SSR compositing and its optional denoiser;
- the rebuilt depth-of-field and temporal-AA nodes.

## Safe upgrade workflow

1. Search imports, constructors, direct property access, and shader defines for
   the removed and renamed surfaces above.
2. Open every reference matching the application’s renderer, node system,
   post-processing stack, and asset formats.
3. Update renderer initialization and loader callbacks before chasing runtime
   errors.
4. Rebuild TSL graphs around final helper names and position semantics.
5. Confirm required normals, tangents, update ranges, and storage-backed
   attributes on geometry.
6. Revalidate serialized assets, material copies, pivots, and render-target
   cloning.
7. Compare WebGL and WebGPU output where both backends are supported.
8. Capture visual regressions in blending, PBR, shadows, depth, post-processing,
   and color-space handling.
