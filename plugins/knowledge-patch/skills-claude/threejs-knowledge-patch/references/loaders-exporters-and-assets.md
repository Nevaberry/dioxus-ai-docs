# Loaders, Exporters, and Asset Pipelines

Use this reference when loading, exporting, serializing, transcoding, or packaging external assets and interchange formats.

## AnimationClip metadata in glTF workflows

**Batch:** `r180`

`AnimationClip` adds `userData`, and `GLTFLoader` and `GLTFExporter` now honor it. Custom animation metadata can therefore survive glTF import and export instead of requiring a separate mapping.

## Async loading and export migrations

**Batch:** `migration-guide-r173-r185`

`DRACOExporter.parse()` was replaced by `parseAsync()`, while `FileLoader.load()` and `ImageBitmapLoader.load()` no longer return a value and require their `onLoad` callbacks. `KTX2Loader.detectSupportAsync()` is deprecated; initialize the renderer with `await renderer.init()` and then call `detectSupport()`.

## Blender MaterialX imports

**Batch:** `r179`

`MaterialXNodes` import support now aligns with Blender's MaterialX exporter, improving compatibility with materials exported from Blender.

## Blob cache behavior

**Batch:** `r183`

`Cache` no longer caches `Blob` values. Applications that relied on repeated Blob loads being served from the three.js cache must provide their own caching layer.

## Collada polygon and joint instances

**Batch:** `r184`

`ColladaLoader` now supports the `polygons` primitive and `instance_joint`.

## ColladaLoader capabilities

**Batch:** `r183`

`ColladaLoader` was split into modular components, improves animation support, and now applies falloff angles to spot lights.

## Decoder and transcoder URL defaults

**Batch:** `r185`

`DRACOLoader` and `KTX2Loader` now use relative file URLs by default. `DRACOLoader.setDecoderConfig()` is deprecated, and decoder URLs for glTF use are now exported.

## Expanded EXR decoding

**Batch:** `r184`

`EXRLoader` adds YCbCr, B44/B44A, multipart, and deep-scanline support.

## Expanded KTX2 formats and mipmap generation

**Batch:** `r180`

`KTX2Loader` adds `VK_FORMAT_ASTC_6x6_SFLOAT_BLOCK_EXT`, RGB9E5, R11G11B10, BC4, BC5, and PVRTC1 RGBA support. It also supports `generateMipmaps = true`; renderer support is included for R11G11B10, BC4, and BC5.

## Expanded USD composition and loading

**Batch:** `r184`

`USDComposer` adds camera and light parsing. `USDLoader` adds Cube, Sphere, Cylinder, Cone, and Capsule primitives, MaterialX `UsdPreviewSurface` materials, and `metersPerUnit` handling.

## Expanded USD loading

**Batch:** `r183`

`USDLoader` now handles USDC and unified `.usd` input and is refactored around `USDComposer` with animation support. It also adds OpenPBR Surface materials, polygon holes, external textures, and broader material, UV, transform, skinning, variant, and display-opacity support.

## EXR output formats and lossy DCT channels

**Batch:** `r179`

`EXRLoader` adds an output-format API and lossy DCT channel decoding. Loaded EXR data now uses the linear-sRGB color space.

## FBX custom texture handlers and WebP

**Batch:** `r177`

`FBXLoader` now uses `getHandler()` for custom texture loaders and recognizes the WebP MIME type.

## FontLoader text direction

**Batch:** `r181`

`FontLoader` adds text-direction support for directional text workflows.

## GCodeLoader extrusion modes

**Batch:** `r183`

`GCodeLoader` now supports the `M82` and `M83` commands.

## glTF material and compression extensions

**Batch:** `r183`

`GLTFLoader` adds support for `KHR_meshopt_compression` and exposes `getMaterialExtension()` for material-extension handling.

## GLTFLoader image-format detection removal

**Batch:** `r176`

`GLTFLoader` no longer performs WebP or AVIF support detection. Applications targeting environments that may not support those formats must handle compatibility before loading such assets.

## ISO gain-map metadata

**Batch:** `r183`

`UltraHDRLoader` now supports ISO 21496-1 gain-map metadata.

## KTX2 request headers

**Batch:** `r181`

`KTX2Loader` now honors headers configured with `setRequestHeader()`.

## KTX2 sRGB formats

**Batch:** `r177`

`KTX2Loader` adds support for ETC2, BCn, and ASTC 4x4 sRGB textures.

## Loader cancellation

**Batch:** `r179`

`Loader` now exposes `abort()`, providing a common cancellation entry point for loader operations.

## Loader-specific cache keys

**Batch:** `r178`

Loader cache keys are now unique per loader type. Loading the same resource key through different loader classes no longer aliases the same cached entry.

## LottieLoader deprecation

**Batch:** `r176`

`LottieLoader` is deprecated; migrate to using the underlying library inline.

## MTL displacement maps

**Batch:** `r174`

`MTLLoader` now supports displacement maps declared by MTL assets.

## Multi-scene glTF animations

**Batch:** `r185`

`GLTFExporter` now supports animations associated with multiple scenes.

## Package and addon assets no longer bundled

**Batch:** `r185`

The npm package no longer includes `examples/fonts`. `DRACOExporter` encoders and the libraries used by `LottieLoader` and `TTFLoader` also move from bundled copies to CDN delivery, so code that resolved those assets from the installed package must adjust.

## PCD binary parsing

**Batch:** `r177`

`PCDLoader` can parse headers without `TextDecoder` and now parses binary data according to each field's data type.

## PLY attribute fidelity

**Batch:** `r185`

`PLYLoader` now uses declared PLY data types when creating buffer attributes. `PLYExporter` preserves buffer-attribute data types and supports custom attributes.

## PNG output from ImageUtils

**Batch:** `r173`

`ImageUtils.getDataURL()` now always uses the `image/png` MIME type. Consumers must no longer assume that the returned data URL preserves another source image format.

## RGBELoader renamed to HDRLoader

**Batch:** `r180`

`RGBELoader` was renamed to `HDRLoader`; update addon imports and constructor names when migrating to r180.

## RGBMLoader removal

**Batch:** `r180`

`RGBMLoader` was removed. Applications that still import it must replace or vendor the loader before upgrading.

## Selectable ImageUtils output type

**Batch:** `r175`

`ImageUtils.getDataURL()` now accepts an optional `type` argument, allowing callers to select an encoded data-URL type instead of being limited to PNG output.

```js
const url = THREE.ImageUtils.getDataURL(image, 'image/jpeg');
```

## USD animation and export expansion

**Batch:** `r185`

`USDLoader` now preserves USDA animation-timing metadata. `USDZExporter` adds animation and multi-material support, basic normal-scale support, and a `mimeType` setting through `Texture.userData`.

## USDZ export visibility and hierarchy

**Batch:** `r179`

`USDZExporter` adds the `onlyVisible` option and now exports scene hierarchy and object names.

## VOXLoader format and API changes

**Batch:** `r182`

`VOXLoader` now accepts version 200 files, supports scene graphs, and uses greedy meshing. The former `VOXMesh` and `VOXData3DTexture` classes were replaced with functions, so code that instantiated those classes must update its construction pattern.

## VRML cameras

**Batch:** `r183`

`VRMLLoader` now imports cameras from VRML assets.

## VTKLoader deprecation

**Batch:** `r184`

`VTKLoader` is deprecated in r184; applications should plan to migrate away from it.

## WebGPU-aligned Draco data

**Batch:** `r181`

`DRACOLoader` now aligns decoded data for use with WebGPU.

## WebP glTF export and 16-bit KTX2 textures

**Batch:** `r184`

`GLTFExporter` supports `EXT_texture_webp`, and `KTX2Loader` supports 16-bit unsigned-normalized RGBA formats.

