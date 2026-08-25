# Browser API, pipeline, and pass behavior

## Adapter and device lifecycle

### Required limits may be undefined

An unknown `requiredLimits` property may have an `undefined` value
(`chrome-133`). This permits forwarding a possibly unavailable adapter limit:

```js
const device = await adapter.requestDevice({
  requiredLimits: { someLimit: adapter.limits.someLimit },
});
```

Calling `requestDevice()` with neither `requiredFeatures` nor
`requiredLimits` requests the adapter's default capabilities
(`chrome-136`).

### Fallback status lives on adapter info

`GPUAdapterInfo.isFallbackAdapter` describes an adapter that trades
performance for compatibility, predictability, or privacy (`chrome-136`).
It is available as `adapter.info.isFallbackAdapter` and through
`device.adapterInfo`. The value was initially always `false` because no
fallback adapter shipped at that point.

The older `GPUAdapter.isFallbackAdapter` was deprecated in `chrome-138` and
removed in `chrome-140`. Do not branch on the adapter-level property.

### A successful device request consumes the adapter

After one successful browser `GPUAdapter.requestDevice()`, another call on
the same adapter rejects (`chrome-140`). The former behavior returned a
device already lost at creation.

```js
const first = await adapter.requestDevice();
await adapter.requestDevice(); // Rejects.
```

Request another adapter for another browser device. Native Dawn has a
separate opt-in for multiple devices per adapter.

### Architecture identifiers

`GPUAdapterInfo.architecture` recognizes the exact lowercase values
`"blackwell"` for recent NVIDIA GPUs and `"rdna4"` for recent AMD GPUs
(`chrome-138`). Telemetry parsers and allowlists should accept both.

### Experimental power-preference reporting

With `chrome://flags/#enable-webgpu-developer-features` enabled, the
non-standard `GPUAdapterInfo.powerPreference` reports `"low-power"` or
`"high-performance"` when supported (`chrome-137`). It reflects the
preference used to request the adapter:

```js
if (device.adapterInfo.powerPreference === "high-performance") {
  enableEnhancedGraphics();
}
```

Feature-detect this experimental information rather than making it a required
adapter-info field.

## Buffer creation, binding, and copies

### Whole-buffer copies

`GPUCommandEncoder.copyBufferToBuffer()` has a two-argument overload that
copies the entire source to the destination with both offsets set to zero
(`chrome-137`):

```js
encoder.copyBufferToBuffer(sourceBuffer, destinationBuffer);
```

### Direct buffer resources

A `GPUBuffer` may be passed directly as a bind-group resource when the
default offset and size are desired (`chrome-138`):

```js
device.createBindGroup({
  layout,
  entries: [{ binding: 0, resource: buffer }],
});
```

This is equivalent to `{ buffer }`. Use `{ buffer, offset, size }` when the
range must be explicit.

### `mappedAtCreation` throws a range error

Creating a buffer with `mappedAtCreation: true` and a size not divisible by
four throws `RangeError` rather than producing a `GPUValidationError`
(`chrome-138`).

```js
device.createBuffer({
  size: 42,
  usage: GPUBufferUsage.STORAGE,
  mappedAtCreation: true,
}); // RangeError
```

## Pipeline layouts and rendering

### Sparse bind-group layout indices

`GPUDevice.createPipelineLayout()` accepts `null` entries in
`bindGroupLayouts` (`chrome-135`). A null slot is ignored while preserving
later bind-group indices:

```js
const layout = device.createPipelineLayout({
  bindGroupLayouts: [globalsLayout, null, verticesLayout],
});
```

### Viewports may exceed the target

`GPURenderPassEncoder.setViewport()` accepts a viewport that extends beyond
the render target, including a negative origin (`chrome-135`). Oversized UI
or clipped geometry can use its natural viewport without pre-clamping.

### Additional vertex formats

Vertex attributes accept `"unorm8x4-bgra"` and the scalar formats `"uint8"`,
`"sint8"`, `"unorm8"`, `"snorm8"`, `"uint16"`, `"sint16"`, `"unorm16"`,
`"snorm16"`, and `"float16"` (`chrome-133`). BGRA avoids rearranging packed
colors; scalar formats avoid fetching an unused second component.

## Immediate data

Immediate data supplies small immutable shader inputs without a bind group
(`chrome-149-150-guide`). Declare one module-scope `var<immediate>` per entry
point at most. Its type must be concrete, constructible, host-shareable, and
contain no arrays. All shader stages share one range.

The shipped form requires the `"immediate_address_space"` WGSL language
extension and this declaration (`chrome-149-150`):

```wgsl
requires immediate_address_space;
var<immediate> values: vec4<f32>;
```

Detect the extension with `navigator.gpu.wgslLanguageFeatures`. No adapter
feature is required.

### Layout and limit

An explicit `GPUPipelineLayoutDescriptor.immediateSize` must cover the shader
variable and may not exceed `device.limits.maxImmediateSize`, whose default
is 64 bytes. An automatic pipeline layout infers the required size.
Struct padding counts toward `immediateSize`, although padding slots need not
be written. Pipeline layouts share immediate values only when their
`immediateSize` values match.

### Pass API

The shipped pass-encoder method is `setImmediates()`, replacing the earlier
guide's `setImmediateData()` spelling:

```js
pass.setPipeline(pipeline);
pass.setImmediates(0, new Float32Array([1, 0, 0, 1]));
pass.dispatchWorkgroups(1);
```

The range offset and copied byte count must be aligned to four bytes.
`dataOffset` and `size` count elements for typed arrays and bytes for other
data, matching `writeBuffer()` semantics.

At every draw or dispatch, all non-padding slots statically used by active
shader stages must have been set since encoder start. Render bundles snapshot
immediate values during bundle encoding. Executing bundles clears the render
pass's immediate-slot state before and after each bundle, so subsequent pass
draws must set the values again.

## Transient render attachments

`GPUTextureUsage.TRANSIENT_ATTACHMENT` marks storage that can remain in tile
memory or be reused between passes (`chrome-146-guides`). Feature-detect the
constant before use.

Creation constraints:

- Usage is exactly `RENDER_ATTACHMENT | TRANSIENT_ATTACHMENT`.
- The texture is 2D with one mip level and one array layer.
- Canvas configurations cannot use the flag.
- Texture views retain their parent's usage.
- `viewFormats` must be empty; alternative formats fail validation
  (`chrome-149-150`).

Transient color, depth, and stencil aspects require `"clear"` load operations
and `"discard"` store operations. A resolve target must be non-transient.

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

## Built-in canvas actions

The browser context menu for a WebGPU canvas includes **Save Image As…** and
**Copy Image** (`chrome-136`). This is native browser behavior and needs no
application code.
