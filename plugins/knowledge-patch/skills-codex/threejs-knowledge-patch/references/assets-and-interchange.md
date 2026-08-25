# Assets, loaders, exporters, and interchange

Texture and model loading, serialization, exporters, cache behavior, and editor interchange.

## AnimationClip metadata in glTF workflows (r180)

`AnimationClip` adds `userData`, and `GLTFLoader` and `GLTFExporter` now honor it. Custom animation metadata can therefore survive glTF import and export instead of requiring a separate mapping.

## Blender MaterialX imports (r179)

`MaterialXNodes` import support now aligns with Blender's MaterialX exporter, improving compatibility with materials exported from Blender.

## Blob cache behavior (r183)

`Cache` no longer caches `Blob` values. Applications that relied on repeated Blob loads being served from the three.js cache must provide their own caching layer.

## Box3 and Sphere JSON serialization (r177)

`Box3` and `Sphere` now provide `toJSON()` and `fromJSON()` methods, so these bounds primitives can be serialized and restored without application-defined adapters.

## CanvasTarget cache disposal (r184)

Cached `CanvasTarget` entries can now be disposed individually instead of requiring cache-wide cleanup.

## ColladaLoader capabilities (r183)

`ColladaLoader` was split into modular components, improves animation support, and now applies falloff angles to spot lights.

## Editor background texture color spaces (r175)

The editor adds color-space options for background textures, allowing their color-space interpretation to be configured.

## Editor rendering defaults (r183)

The editor now uses Neutral tone mapping by default and supports `WebGPURenderer` projects.

## Expanded EXR decoding (r184)

`EXRLoader` adds YCbCr, B44/B44A, multipart, and deep-scanline support.

## Expanded KTX2 formats and mipmap generation (r180)

`KTX2Loader` adds `VK_FORMAT_ASTC_6x6_SFLOAT_BLOCK_EXT`, RGB9E5, R11G11B10, BC4, BC5, and PVRTC1 RGBA support. It also supports `generateMipmaps = true`; renderer support is included for R11G11B10, BC4, and BC5.

## Expanded USD composition and loading (r184)

`USDComposer` adds camera and light parsing. `USDLoader` adds Cube, Sphere, Cylinder, Cone, and Capsule primitives, MaterialX `UsdPreviewSurface` materials, and `metersPerUnit` handling.

## Expanded USD loading (r183)

`USDLoader` now handles USDC and unified `.usd` input and is refactored around `USDComposer` with animation support. It also adds OpenPBR Surface materials, polygon holes, external textures, and broader material, UV, transform, skinning, variant, and display-opacity support.

## EXR files in the editor (r179)

The three.js editor can now load EXR files.

## EXR output formats and lossy DCT channels (r179)

`EXRLoader` adds an output-format API and lossy DCT channel decoding. Loaded EXR data now uses the linear-sRGB color space.

## FBX custom texture handlers and WebP (r177)

`FBXLoader` now uses `getHandler()` for custom texture loaders and recognizes the WebP MIME type.

## FontLoader text direction (r181)

`FontLoader` adds text-direction support for directional text workflows.

## GCodeLoader extrusion modes (r183)

`GCodeLoader` now supports the `M82` and `M83` commands.

## glTF material and compression extensions (r183)

`GLTFLoader` adds support for `KHR_meshopt_compression` and exposes `getMaterialExtension()` for material-extension handling.

## KTX2 request headers (r181)

`KTX2Loader` now honors headers configured with `setRequestHeader()`.

## KTX2 sRGB formats (r177)

`KTX2Loader` adds support for ETC2, BCn, and ASTC 4x4 sRGB textures.

## Loader cancellation (r179)

`Loader` now exposes `abort()`, providing a common cancellation entry point for loader operations.

## Loader-specific cache keys (r178)

Loader cache keys are now unique per loader type. Loading the same resource key through different loader classes no longer aliases the same cached entry.

## Material JSON deserialization (r185)

`MaterialLoader` adds `registerMaterial()`, and `Material` adds `fromJSON()`. Material implementations can now be registered with the loader and deserialized through the material API.

## Material map serialization (r180)

`Material.toJSON()` now includes map properties that were previously omitted. Serialized material output can gain additional texture-map fields after upgrading.

## MTL displacement maps (r174)

`MTLLoader` now supports displacement maps declared by MTL assets.

## Multi-scene glTF animations (r185)

`GLTFExporter` now supports animations associated with multiple scenes.

## New DevTools and editor text geometry (r184)

r184 adds new DevTools, and the editor can now add `TextGeometry`.

## Object and scene serialization version (r177)

The Object/Scene serialization format version was increased. Consumers that validate, cache, or route serialized assets by format version must account for the r177 format.

## Package and addon assets no longer bundled (r185)

The npm package no longer includes `examples/fonts`. `DRACOExporter` encoders and the libraries used by `LottieLoader` and `TTFLoader` also move from bundled copies to CDN delivery, so code that resolved those assets from the installed package must adjust.

## PCD binary parsing (r177)

`PCDLoader` can parse headers without `TextDecoder` and now parses binary data according to each field's data type.

## PLY attribute fidelity (r185)

`PLYLoader` now uses declared PLY data types when creating buffer attributes. `PLYExporter` preserves buffer-attribute data types and supports custom attributes.

## PNG output from ImageUtils (r173)

`ImageUtils.getDataURL()` now always uses the `image/png` MIME type. Consumers must no longer assume that the returned data URL preserves another source image format.

## Rounded-box serialization and physics (r179)

`RoundedBoxGeometry` now exposes its type and parameters and implements `toJSON()`. The `RapierPhysics` addon also adds support for this geometry.

## Selectable ImageUtils output type (r175)

`ImageUtils.getDataURL()` now accepts an optional `type` argument, allowing callers to select an encoded data-URL type instead of being limited to PNG output.

```js
const url = THREE.ImageUtils.getDataURL(image, 'image/jpeg');
```

## USD animation and export expansion (r185)

`USDLoader` now preserves USDA animation-timing metadata. `USDZExporter` adds animation and multi-material support, basic normal-scale support, and a `mimeType` setting through `Texture.userData`.

## USDZ export visibility and hierarchy (r179)

`USDZExporter` adds the `onlyVisible` option and now exports scene hierarchy and object names.

## VideoFrameTexture (r173)

`VideoFrameTexture` is a new texture class for the WebCodecs API. Instances expose `isVideoFrameTexture` for type detection.

## VOXLoader format and API changes (r182)

`VOXLoader` now accepts version 200 files, supports scene graphs, and uses greedy meshing. The former `VOXMesh` and `VOXData3DTexture` classes were replaced with functions, so code that instantiated those classes must update its construction pattern.

## WebGPU-aligned Draco data (r181)

`DRACOLoader` now aligns decoded data for use with WebGPU.

## WebP glTF export and 16-bit KTX2 textures (r184)

`GLTFExporter` supports `EXT_texture_webp`, and `KTX2Loader` supports 16-bit unsigned-normalized RGBA formats.
