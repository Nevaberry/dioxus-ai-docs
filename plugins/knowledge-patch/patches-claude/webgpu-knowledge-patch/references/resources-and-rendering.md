# Resources, textures, copies, and rendering

## Vertex input and pipeline layouts

### Additional vertex formats

Vertex attributes accept `"unorm8x4-bgra"` plus the scalar formats `"uint8"`,
`"sint8"`, `"unorm8"`, `"snorm8"`, `"uint16"`, `"sint16"`, `"unorm16"`,
`"snorm16"`, and `"float16"` (`chrome-133`). The BGRA format avoids
rearranging encoded colors; scalar formats avoid fetching an unused second
component.

### Sparse bind-group indices

`GPUDevice.createPipelineLayout()` accepts `null` entries in
`bindGroupLayouts` (`chrome-135`). A null slot is ignored while preserving
later bind-group indices:

```js
const layout = device.createPipelineLayout({
  bindGroupLayouts: [globalsLayout, null, verticesLayout],
});
```

## Buffers and binding resources

### Direct buffer resources

Pass a `GPUBuffer` directly as a bind-group resource when its default offset
and size are desired (`chrome-138`):

```js
const bindGroup = device.createBindGroup({
  layout: pipeline.getBindGroupLayout(0),
  entries: [{ binding: 0, resource: buffer }],
});
```

This is equivalent to a `GPUBufferBinding` containing only `buffer`. Use
`{ buffer, offset, size }` when a range must be explicit.

### Whole-buffer copies

The two-argument overload of `copyBufferToBuffer()` copies an entire buffer,
using zero for both offsets and inferring the size (`chrome-137`):

```js
encoder.copyBufferToBuffer(sourceBuffer, destinationBuffer);
```

Use the longer overload for partial copies.

### `mappedAtCreation` size validation

Creating a buffer with `mappedAtCreation: true` and a size that is not a
multiple of four throws `RangeError` (`chrome-138`):

```js
device.createBuffer({
  mappedAtCreation: true,
  size: 42,
  usage: GPUBufferUsage.STORAGE,
}); // Throws RangeError.
```

This is a synchronous JavaScript argument error, not a `GPUValidationError`.

### Experimental synchronous worker mapping

The worker-only `GPUBuffer.mapSync()` experiment uses the same mode as
`mapAsync()` and requires launching Chrome with
`--enable-features=WebGPUMapSyncOnWorkers` (`chrome-145`). Feature-detect it
and retain the asynchronous path:

```js
if ("mapSync" in GPUBuffer.prototype) {
  buffer.mapSync(GPUMapMode.READ);
} else {
  await buffer.mapAsync(GPUMapMode.READ);
}
```

## External images and external textures

### VideoFrame dimensions

Importing a `VideoFrame` as `GPUExternalTexture` uses `displayWidth` and
`displayHeight` as its apparent size, not the visible size (`chrome-133`).
Dimension-dependent `textureLoad()` code should therefore use the display
dimensions.

### Image orientation in copies

`GPUQueue.copyExternalImageToTexture()` honors non-default orientation,
including images with orientation metadata and `ImageBitmap` objects created
with `imageOrientation: "from-image"` (`chrome-133`). Do not apply the old
manual compensation.

### Texture views in external-texture bindings

A 2D `GPUTextureView` covering one subresource can satisfy a
`GPUExternalTexture` bind-group binding (`chrome-137`). This allows imported
frames and intermediate textures to share a `texture_external` shader,
pipeline, and layout:

```js
const bindGroup = device.createBindGroup({
  layout: pipeline.getBindGroupLayout(0),
  entries: [{
    binding: 0,
    resource: intermediateTexture.createView(),
  }],
});
```

## Texture formats and capabilities

### Float filterability is not blendability

A filterable float texture is not automatically blendable (`chrome-134`).
Blending into 32-bit float textures requires a device created with the
`"float32-blendable"` feature.

### Sliced 3D compression

Compressed BC and ASTC formats can be used for 3D textures with optional
sliced-3D support (`chrome-139`). Request the base feature and matching 3D
feature together:

```js
if (!adapter.features.has("texture-compression-bc-sliced-3d")) {
  throw new Error("Sliced 3D BC unavailable");
}
const device = await adapter.requestDevice({
  requiredFeatures: [
    "texture-compression-bc",
    "texture-compression-bc-sliced-3d",
  ],
});
```

For ASTC, use `"texture-compression-astc"` and
`"texture-compression-astc-sliced-3d"`.

### Tiered format features

`"texture-formats-tier1"` adds `"r16unorm"`, `"r16snorm"`, `"rg16unorm"`,
`"rg16snorm"`, `"rgba16unorm"`, and `"rgba16snorm"` with render-attachment,
blending, multisampling, and read-only or write-only storage access
(`chrome-142`). It also adds render-attachment, blending, multisampling, and
resolve support to `"r8snorm"`, `"rg8snorm"`, and `"rgba8snorm"`.

`"texture-formats-tier2"` enables read-write storage for supported formats and
automatically enables tier 1:

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

### Texture component swizzle

With `"texture-component-swizzle"`, a texture view's four-character `swizzle`
maps output red, green, blue, and alpha to `"r"`, `"g"`, `"b"`, `"a"`, `"0"`,
or `"1"` (`chrome-143`). Request the device feature before specifying the
mapping:

```js
const device = await adapter.requestDevice({
  requiredFeatures: ["texture-component-swizzle"],
});
const opaqueGrayscale = texture.createView({ swizzle: "rrr1" });
```

### `bgra8unorm` storage access

Read-only storage access for `"bgra8unorm"` was deprecated as non-portable
(`chrome-140`) and then removed (`chrome-143`). Use another readable format.
`"bgra8unorm"` remains intended for write-only storage access.

### Vulkan 3D texture clearing

Dawn no longer rejects clearing a 3D texture on Vulkan (`chrome-143`).
Backend-specific workarounds for that former validation failure can be
removed.

## Render state

### Viewports outside render-target bounds

`GPURenderPassEncoder.setViewport()` accepts a rectangle that extends beyond
the render target, including a negative origin (`chrome-135`):

```js
pass.setViewport(
  -8,
  -8,
  colorTexture.width + 16,
  colorTexture.height + 16,
  0,
  1,
);
```

This permits oversized geometry to keep its natural viewport.

### Transient attachments

`GPUTextureUsage.TRANSIENT_ATTACHMENT` marks render-pass-only storage that may
remain in tile memory or be reused between passes (`chrome-146-guides`).
Feature-detect the constant. A transient texture:

- has usage exactly `RENDER_ATTACHMENT | TRANSIENT_ATTACHMENT`;
- is 2D, with one mip level and one array layer;
- cannot be used in a canvas configuration;
- passes its usage constraints to its views;
- uses `"clear"` load operations and `"discard"` store operations for
  transient color, depth, and stencil aspects; and
- resolves only to a non-transient target.

```js
const transient = device.createTexture({
  size: [width, height],
  sampleCount: 4,
  format: "rgba8unorm",
  usage:
    GPUTextureUsage.RENDER_ATTACHMENT |
    GPUTextureUsage.TRANSIENT_ATTACHMENT,
});

const pass = encoder.beginRenderPass({
  colorAttachments: [{
    view: transient.createView(),
    resolveTarget: context.getCurrentTexture().createView(),
    clearValue: [0, 0, 0, 0],
    loadOp: "clear",
    storeOp: "discard",
  }],
});
```

A transient texture must also have an empty `viewFormats` list
(`chrome-149-150`). Any alternative view format fails validation.
