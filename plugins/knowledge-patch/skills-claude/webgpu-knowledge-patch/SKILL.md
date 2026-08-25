---
name: webgpu-knowledge-patch
description: WebGPU / WGSL
version: Chrome 150
license: MIT
metadata:
  author: Nevaberry
---


# WebGPU and WGSL Compatibility

Use this skill for browser WebGPU, WGSL, Dawn, or Emdawnwebgpu applications. Apply the
feature-detection and validation rules here before relying on optional
capabilities.

## Reference index

| Reference | Topics |
| --- | --- |
| [adapters-and-compatibility.md](references/adapters-and-compatibility.md) | Adapter selection, compatibility mode, features, limits, device lifetime |
| [wgsl-and-shaders.md](references/wgsl-and-shaders.md) | WGSL validation, extensions, subgroups, built-ins, sampling, immediate data |
| [resources-and-rendering.md](references/resources-and-rendering.md) | Buffers, textures, views, formats, copies, render state, transient attachments |
| [native-dawn-and-emscripten.md](references/native-dawn-and-emscripten.md) | Dawn C/C++, callbacks, builds, tracing, Emscripten, SPIR-V |
| [platforms-and-integration.md](references/platforms-and-integration.md) | Linux, Android, Apple, WebXR, canvases, hardware reporting |

## Working method

1. Identify the browser and Dawn or Emdawnwebgpu version actually deployed.
2. Detect optional adapter features and WGSL language extensions independently.
3. Request every needed device feature and non-default limit explicitly.
4. Keep shader declarations synchronized with the JavaScript or native checks.
5. Treat validation changes and API removals as migration work, not runtime
   fallbacks.
6. Use the exact implementation header and library together for native builds.

## Breaking changes and removals

### An adapter is normally single-use

A successful `GPUAdapter.requestDevice()` consumes that adapter. A later
request rejects rather than returning a device already lost at creation.
Request one device, cache it, and share it:

```js
const adapter = await navigator.gpu.requestAdapter();
if (!adapter) throw new Error("WebGPU unavailable");
const device = await adapter.requestDevice();
```

Dawn native code can opt into multiple devices with the instance feature
`MultipleDevicesPerAdapter`; browser code should not assume that behavior.

### Explicit WGSL alignment cannot weaken required alignment

An `@align(n)` value must meet the type's required alignment in every struct.
This is invalid:

```wgsl
struct Invalid {
  @align(4) value: vec4<f32>,
}
```

Remove the undersized annotation or choose a valid larger alignment.

### Read-only `bgra8unorm` storage is gone

Do not use `"bgra8unorm"` for a read-only storage texture. It remains a
write-only storage format. Select another readable format when shader reads
are required.

### `mappedAtCreation` can throw synchronously

When `mappedAtCreation` is `true`, a buffer size not divisible by four throws
`RangeError`. Do not expect a validation error to be reported asynchronously.

### Compatibility mode is feature-based

Request a compatibility-defaulting adapter with:

```js
const adapter = await navigator.gpu.requestAdapter({
  featureLevel: "compatibility",
});
```

Do not read removed `GPUAdapter.featureLevel` or `isCompatibilityMode`
attributes. Inspect and request `"core-features-and-limits"` when available;
if the created device lacks it, compatibility restrictions remain active.
See the adapter reference for flag, origin-trial, Android, and limit details.

### Fallback status moved

`GPUAdapter.isFallbackAdapter` is removed. Use:

```js
const fallback = adapter.info.isFallbackAdapter;
```

Libraries that only receive a device can use `device.adapterInfo`.

### Dawn native migrations

Audit native code for renamed limit and texel-copy structures, callback
statuses and signatures, the `WGPUComputeState` name, the void WGSL feature
query, and `wgpuSurfacePresent()` error handling. The native reference contains
the exact replacements.

## High-value features

### Immediate data without a bind group

Feature-detect the WGSL language extension, declare it in the shader, and use
the shipped pass method `setImmediates()`:

```js
if (!navigator.gpu.wgslLanguageFeatures.has("immediate_address_space")) {
  throw new Error("Immediate data unavailable");
}

const module = device.createShaderModule({ code: `
  requires immediate_address_space;
  var<immediate> color: vec4f;

  @fragment
  fn fragmentMain() -> @location(0) vec4f {
    return color;
  }
` });

pass.setPipeline(pipeline);
pass.setImmediates(0, new Float32Array([1, 0, 0, 1]));
pass.draw(3);
```

Automatic layouts infer `immediateSize`. Explicit layouts set it themselves,
bounded by `device.limits.maxImmediateSize`. Offsets and copied byte counts are
four-byte aligned, and active non-padding slots must be initialized for each
draw or dispatch. Render bundles reset the surrounding pass's immediate state.

### Transient render attachments

Use `GPUTextureUsage.TRANSIENT_ATTACHMENT` only for a render-pass-only 2D
texture with one mip and one layer:

```js
const transient = device.createTexture({
  size: [width, height],
  sampleCount: 4,
  format: "rgba8unorm",
  usage:
    GPUTextureUsage.RENDER_ATTACHMENT |
    GPUTextureUsage.TRANSIENT_ATTACHMENT,
});
```

The usage must be exactly those two flags. Transient aspects use `"clear"`
loads and `"discard"` stores; resolve targets are non-transient. Canvas
configurations cannot use the flag, views retain the parent's usage, and
`viewFormats` must be empty.

### Opt-in texture capabilities

Request optional texture features before creating dependent resources:

- `"texture-formats-tier1"` adds normalized 16-bit formats and broader render,
  blend, multisample, and storage capabilities.
- `"texture-formats-tier2"` adds supported read-write storage and implies
  tier 1.
- `"texture-component-swizzle"` enables view mappings such as `"rrr1"`.
- Sliced 3D BC or ASTC compression requires both the base compression feature
  and its matching `*-sliced-3d` feature.
- `"float32-blendable"` is required to blend into 32-bit float textures;
  filterability alone does not imply blendability.

### Flexible bindings and copies

A `GPUBuffer` may be passed directly as a bind-group resource when the default
offset and size are desired. Use `{ buffer, offset, size }` for a subrange.
`copyBufferToBuffer(source, destination)` copies the whole buffer with zero
offsets. A 2D single-subresource texture view can satisfy an external-texture
binding, allowing one `texture_external` pipeline for imported frames and
intermediate textures.

### WGSL extensions need two kinds of checks

WGSL language support and adapter device features are separate:

```js
if (!navigator.gpu.wgslLanguageFeatures.has("subgroup_id")) {
  throw new Error("WGSL extension unavailable");
}
if (!adapter.features.has("subgroups")) {
  throw new Error("Device feature unavailable");
}
const device = await adapter.requestDevice({
  requiredFeatures: ["subgroups"],
});
```

Then use the WGSL gate or declaration required by that capability. This
applies to subgroup identity, standard uniform-buffer layout, subgroup
uniformity, primitive indices, linear indexing, texture/sampler local
bindings, and immediate data. The WGSL reference gives the exact spellings.

## Limit and feature request pattern

Probe before requesting an optional feature or elevated limit:

```js
const requiredFeatures = [];
if (adapter.features.has("texture-formats-tier2")) {
  requiredFeatures.push("texture-formats-tier2");
}

const requiredLimits = {};
if (adapter.limits.maxStorageBuffersPerShaderStage >= 16) {
  requiredLimits.maxStorageBuffersPerShaderStage = 16;
}

const device = await adapter.requestDevice({
  requiredFeatures,
  requiredLimits,
});
```

An unknown `requiredLimits` property may be forwarded with an `undefined`
value, so a possibly removed limit need not be prefiltered. Never request a
numeric limit above the adapter's reported value.

## Native implementation checklist

- Treat core `webgpu.h` as stable, but keep implementation extensions paired
  with the exact Dawn or Emdawnwebgpu header and library.
- Prefer the maintained `emdawnwebgpu` port over Emscripten's obsolete built-in
  WebGPU bindings.
- Raise Apple deployment targets to macOS 11 or iOS 14 and Metal 2.3 or newer.
- Expect Dawn Android builds to validate SPIR-V by default.
- Decide explicitly whether default static monolithic Dawn output is suitable.
- Treat nightly binaries as unsigned, best-effort artifacts.

## Validation checklist

- Verify every optional feature with `adapter.features.has(...)`.
- Verify every WGSL extension with `navigator.gpu.wgslLanguageFeatures`.
- Confirm requested limits against `adapter.limits`.
- Recompile shaders affected by alignment, uniformity, or extension gates.
- Exercise compatibility devices separately from core-defaulting devices.
- Test render-bundle immediate-state resets and transient attachment rules.
- Handle synchronous JavaScript exceptions and native callback/status changes.
