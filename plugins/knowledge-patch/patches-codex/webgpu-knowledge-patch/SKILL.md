---
name: webgpu-knowledge-patch
description: WebGPU / WGSL
version: "Chrome 150"
license: MIT
metadata:
  author: Nevaberry
---


# WebGPU and WGSL Compatibility

Load this skill when changing browser WebGPU code, WGSL shaders, Dawn native
code, or Emscripten WebGPU builds. Use it to select current API spellings,
feature gates, limits, validation rules, and platform paths.

## Working method

1. Identify whether the code runs through the browser API, native Dawn, or
   Emdawnwebgpu.
2. Feature-detect optional adapter features and WGSL language extensions
   separately; one does not imply the other.
3. Request every device feature and non-default limit before creating
   dependent resources or pipelines.
4. Keep fallback paths for compatibility devices and optional shader
   extensions.
5. Treat validation behavior as part of the API contract, especially for
   mapped buffers, transient textures, immediate data, and storage formats.
6. Prefer the implementation's matching `webgpu.h` when compiling native
   extensions even though the core C API is stable.
7. Verify assumptions against the application's manifests, code, runtime
   feature sets, and tests.

## Reference index

| Reference | Topics |
| --- | --- |
| [references/browser-api-and-passes.md](references/browser-api-and-passes.md) | Adapters, devices, limits, buffers, pipeline layouts, passes, immediate data, transient attachments |
| [references/wgsl-and-shaders.md](references/wgsl-and-shaders.md) | WGSL validation, subgroup operations, language extensions, built-ins, sampling, uniform layout |
| [references/textures-and-external-images.md](references/textures-and-external-images.md) | Texture formats, compression, storage access, swizzles, external textures, image copies |
| [references/compatibility-and-platforms.md](references/compatibility-and-platforms.md) | Compatibility mode, WebXR, browser rollout, Android, Linux, worker-only experiments |
| [references/dawn-native-and-emscripten.md](references/dawn-native-and-emscripten.md) | Dawn C/C++ migrations, callbacks, surfaces, builds, tracing, Tint, Emdawnwebgpu |

## Breaking-change checklist

### Use the shipped immediate-data spelling

Declare the language requirement and call `setImmediates()`. Do not copy the
earlier guide spelling `setImmediateData()`.

```wgsl
requires immediate_address_space;
var<immediate> color: vec4f;
```

```js
pass.setPipeline(pipeline);
pass.setImmediates(0, new Float32Array([1, 0, 0, 1]));
pass.draw(3);
```

Feature-detect `immediate_address_space` through
`navigator.gpu.wgslLanguageFeatures`. An automatic pipeline layout infers the
range; an explicit layout supplies `immediateSize`. Every used non-padding
slot must be initialized for the active stages before a draw or dispatch.

### Create one device per adapter

A successful `requestDevice()` consumes a browser adapter. Reusing it rejects:

```js
const adapter = await navigator.gpu.requestAdapter();
if (!adapter) throw new Error("WebGPU unavailable");
const device = await adapter.requestDevice();
```

Request a fresh adapter for another device. Native Dawn can opt into
`MultipleDevicesPerAdapter` at instance creation when multiple devices are
required.

### Check compatibility on the device

Request compatibility defaulting with:

```js
const adapter = await navigator.gpu.requestAdapter({
  featureLevel: "compatibility",
});
```

Do not read the removed adapter `featureLevel` or `isCompatibilityMode`
attributes. The presence of `"core-features-and-limits"` on the created
device determines whether core restrictions were lifted. Check
`maxStorageBuffersInVertexStage`; zero requires a vertex path without storage
buffers.

### Read fallback status from adapter info

`GPUAdapter.isFallbackAdapter` is gone. Use:

```js
if (adapter.info.isFallbackAdapter) {
  chooseConservativeDefaults();
}
```

Libraries that receive only a device can read `device.adapterInfo`.

### Remove read-only `bgra8unorm` storage use

Read-only storage access for `"bgra8unorm"` is no longer accepted. Use a
portable readable format or keep this format write-only.

### Expect synchronous descriptor errors

`createBuffer({ mappedAtCreation: true })` throws `RangeError` when `size` is
not a multiple of four. Catch it as a JavaScript argument/range error rather
than waiting for a `GPUValidationError`.

## Feature and limit negotiation

Never assume that format, subgroup, compression, or compatibility
capabilities travel together. Probe first and request exactly what is used:

```js
const adapter = await navigator.gpu.requestAdapter();
if (!adapter) throw new Error("WebGPU unavailable");

const requiredFeatures = [];
if (adapter.features.has("texture-formats-tier2")) {
  requiredFeatures.push("texture-formats-tier2");
} else if (adapter.features.has("texture-formats-tier1")) {
  requiredFeatures.push("texture-formats-tier1");
}

const device = await adapter.requestDevice({ requiredFeatures });
```

Tier 2 automatically enables tier 1. For sliced 3D compression, request both
the base compression feature and its `-sliced-3d` companion. Blending to
32-bit float textures requires `"float32-blendable"`.

Unknown `requiredLimits` entries may carry `undefined`, so forwarding an
optional adapter limit does not require filtering. For higher resource tiers,
check the supported value before requesting it. Calling `requestDevice()`
without required features or limits asks for the adapter defaults.

## WGSL language gates

WGSL language extensions are exposed by `navigator.gpu.wgslLanguageFeatures`.
Use the declaration required by each shader:

| Capability | Declaration | Additional device feature |
| --- | --- | --- |
| Subgroup operations | `enable subgroups;` | `"subgroups"` |
| Subgroup identity | `requires subgroup_id;` | `"subgroups"` |
| Subgroup-scoped uniformity | availability changes analysis | none beyond features used by the shader |
| Standard uniform layout | `requires uniform_buffer_standard_layout;` | none |
| Primitive index | `enable primitive_index;` | `"primitive-index"` |
| Linear compute indices | `requires linear_indexing;` | none |
| Immediate address space | `requires immediate_address_space;` | none |

For `f16` subgroup operations, request both `"shader-f16"` and `"subgroups"`.
Do not request removed Chromium experimental subgroup feature names.
Algorithms must tolerate subgroup widths between `subgroupMinSize` and
`subgroupMaxSize`, and identity-based code must not assume every subgroup is
full.

Explicit `@align` values may not be smaller than a member's required
alignment. Remove undersized annotations instead of relying on permissive
validation.

## Pass and resource shortcuts

- `copyBufferToBuffer(source, destination)` copies the whole buffer with zero
  offsets.
- A `GPUBuffer` can be a bind-group resource directly when default offset and
  size are wanted; use `{ buffer, offset, size }` for an explicit range.
- A `null` pipeline-layout slot preserves its bind-group index without an
  empty layout.
- A viewport may extend outside the render target and may have a negative
  origin.
- `textureSampleLevel()` accepts 1D textures for explicit-level sampling.
- A single-subresource 2D `GPUTextureView` may satisfy an external-texture
  binding.

## Transient attachment rules

Use `GPUTextureUsage.TRANSIENT_ATTACHMENT` only with
`RENDER_ATTACHMENT`. The texture must be 2D with one mip level and one array
layer, must have no alternative `viewFormats`, and cannot be a canvas texture.
Views retain the parent usage.

Transient color, depth, and stencil aspects require `loadOp: "clear"` and
`storeOp: "discard"`. Resolve into a non-transient target. Feature-detect the
usage constant before creating the texture.

## Native migration priorities

- Replace removed or renamed C structures and callback statuses before
  updating headers.
- Handle the `WGPUStatus` returned by `wgpuSurfacePresent()`.
- Remove status handling around `wgpuInstanceGetWGSLLanguageFeatures()`,
  which now returns no value.
- Update queue-work-done callbacks for their additional message argument.
- Account for the default static monolithic Dawn build if library layout
  matters.
- Use `wgpu::PresentMode::Undefined` when default present-mode selection is
  desired.
- Migrate browser-targeted C/C++ from Emscripten's old built-in bindings to
  the packaged `emdawnwebgpu` port.

See the native reference for exact type names, build flags, callback
semantics, binary caveats, and backend-specific behavior.

## Validation checklist

- Confirm every optional adapter feature before requesting it.
- Confirm every WGSL extension before compiling a shader that requires it.
- Check supported limits before requesting higher values.
- Reinitialize immediate slots after render-bundle execution.
- Keep transient resolve targets non-transient.
- Validate storage texture access against the selected format tier.
- Test both core and compatibility paths when compatibility is in scope.
- On native paths, compile against the same implementation headers that are
  linked.
