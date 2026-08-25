# Textures, formats, and external images

## Texture-format capability tiers

### Tier 1

The optional `"texture-formats-tier1"` feature adds these formats
(`chrome-142`):

- `"r16unorm"` and `"r16snorm"`
- `"rg16unorm"` and `"rg16snorm"`
- `"rgba16unorm"` and `"rgba16snorm"`

They gain render-attachment, blending, multisampling, and read-only or
write-only storage access. Tier 1 also adds render-attachment, blending,
multisampling, and resolve support to `"r8snorm"`, `"rg8snorm"`, and
`"rgba8snorm"`.

### Tier 2

`"texture-formats-tier2"` enables read-write storage access for supported
formats and automatically enables tier 1 (`chrome-142`). Prefer tier 2 when
available and fall back to tier 1:

```js
const feature = adapter.features.has("texture-formats-tier2")
  ? "texture-formats-tier2"
  : adapter.features.has("texture-formats-tier1")
    ? "texture-formats-tier1"
    : null;

const device = await adapter.requestDevice({
  requiredFeatures: feature ? [feature] : [],
});
```

### Native feature migration

The removed Dawn `wgpu::FeatureName::R8UnormStorage` is superseded by
`wgpu::FeatureName::TextureFormatTier1` (`chrome-145`).
`wgpu::FeatureName::Snorm16TextureFormats` was also removed; most of its
capabilities are covered by `wgpu::FeatureName::TextureFormatsTier1`, but
resolve support is not an exact replacement. Audit any resolve dependency.

## Blending and storage access

### Float filterability does not imply blendability

A filterable floating-point texture is not automatically blendable
(`chrome-134`). Blending to 32-bit float textures requires a device created
with `"float32-blendable"`.

### Read-only `bgra8unorm` storage is gone

Read-only storage use of `"bgra8unorm"` was deprecated because the
specification disallows the non-portable combination (`chrome-140`) and then
removed (`chrome-143`). Use a portable readable format. `"bgra8unorm"`
remains intended for write-only storage access.

## Sliced 3D compression

Compressed BC and ASTC formats can be used for 3D textures when their
sliced-3D features are exposed (`chrome-139`). Request both the base and
companion feature:

```js
const device = await adapter.requestDevice({
  requiredFeatures: [
    "texture-compression-bc",
    "texture-compression-bc-sliced-3d",
  ],
});
```

For ASTC, request `"texture-compression-astc"` and
`"texture-compression-astc-sliced-3d"`.

## Component swizzles

The optional `"texture-component-swizzle"` feature enables a four-character
`GPUTextureView` `swizzle` (`chrome-143`). Each output component can select
`"r"`, `"g"`, `"b"`, `"a"`, `"0"`, or `"1"`. Request the feature before
creating a mapped view:

```js
if (!adapter.features.has("texture-component-swizzle")) {
  throw new Error("Texture swizzle unavailable");
}
const device = await adapter.requestDevice({
  requiredFeatures: ["texture-component-swizzle"],
});
const grayscaleView = texture.createView({ swizzle: "rrr1" });
```

## External textures

### Display dimensions

Importing a `VideoFrame` as a `GPUExternalTexture` uses `displayWidth` and
`displayHeight` as the apparent size rather than its visible size
(`chrome-133`). Dimension-dependent `textureLoad()` access therefore follows
the displayed frame dimensions.

### Texture views as external bindings

A two-dimensional, single-subresource `GPUTextureView` can satisfy a
`GPUExternalTexture` bind-group binding (`chrome-137`). A video pipeline can
use one `texture_external` shader and layout for both imported frames and
intermediate textures:

```js
const bindGroup = device.createBindGroup({
  layout: pipeline.getBindGroupLayout(0),
  entries: [{
    binding: 0,
    resource: intermediateTexture.createView(),
  }],
});
```

### Emdawnwebgpu import boundary

Emdawnwebgpu supports `wgpu::ExternalTexture`, but the object must be imported
from JavaScript (`chrome-145`). C or C++ cannot construct it directly because
the import requires an `HTMLVideoElement`, `VideoFrame`, or another JavaScript
object. Use a bridge such as `EM_ASM`.

## External-image copies

`GPUQueue.copyExternalImageToTexture()` honors non-default source orientation
(`chrome-133`). This includes an `ImageBitmap` created with
`imageOrientation: "from-image"` and images carrying non-default orientation.
Do not add the compensation that older behavior required.

## Backend clearing behavior

Dawn no longer reports a validation error when clearing a 3D texture on
Vulkan (`chrome-143`). Backend-specific workarounds for the former failure can
be removed.
