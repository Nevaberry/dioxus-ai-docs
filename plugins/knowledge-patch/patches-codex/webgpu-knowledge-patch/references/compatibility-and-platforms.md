# Compatibility mode and platform availability

## Compatibility-mode negotiation

### Request syntax

Request compatibility defaulting with `featureLevel: "compatibility"`
(`chrome-133`). `"core"` is the default and the only other allowed request
value:

```js
const adapter = await navigator.gpu.requestAdapter({
  featureLevel: "compatibility",
});
```

The early `compatibilityMode` request option was replaced. The initially
exposed adapter `featureLevel` superseded `isCompatibilityMode`, but both
adapter attributes were subsequently removed.

### Determine restrictions from device features

The current experimental negotiation returns a compatibility-defaulting
adapter when possible and otherwise a core-defaulting adapter
(`chrome-136`). Core-defaulting adapters automatically enable
`"core-features-and-limits"`. Compatibility-defaulting adapters may expose
that feature for explicit request, lifting compatibility restrictions under
the unsafe WebGPU flag.

```js
const requiredFeatures =
  adapter.features.has("core-features-and-limits")
    ? ["core-features-and-limits"]
    : [];
const device = await adapter.requestDevice({ requiredFeatures });

const restricted =
  !device.features.has("core-features-and-limits");
```

Do not inspect the removed `GPUAdapter.featureLevel` or
`GPUAdapter.isCompatibilityMode` fields. Determine effective restrictions
from the created device.

### Vertex storage-buffer limit

Compatibility adapters expose `maxStorageBuffersInVertexStage`, which may be
zero on hardware unable to use storage buffers in vertex shaders
(`chrome-146-guides`). Choose a binding-free vertex path when it is zero:

```js
if (adapter.limits.maxStorageBuffersInVertexStage === 0) {
  useVertexPathWithoutStorageBuffers();
}
```

## Browser enablement and rollout

### Flag and trial history

The initial standardized request still required
`chrome://flags/#enable-unsafe-webgpu` (`chrome-133`). On Android, that single
flag later enabled every capability required by experimental compatibility
mode and allowed an OpenGL ES backend on devices without Vulkan
(`chrome-135`).

Compatibility mode could be delivered to visitors through an origin trial
scheduled through Chrome 145 (`chrome-139`). Local testing used
`chrome://flags/#enable-experimental-web-platform-features`; outside the
trial or flag it remained disabled by default.

### Android OpenGL ES path

Compatibility mode is available on Android hardware backed by OpenGL ES 3.1
(`chrome-146`). The request syntax and feature negotiation remain the same as
the earlier experimental path. This extends WebGPU to hardware without a
modern Vulkan-class API.

## Resource limits

Dawn may expose `maxStorageBuffersPerShaderStage` up to 16 and
`maxSampledTexturesPerShaderStage` up to 48 (`chrome-146`). Check the adapter
before requesting a higher tier:

```js
if (
  adapter.limits.maxStorageBuffersPerShaderStage >= 16 &&
  adapter.limits.maxSampledTexturesPerShaderStage >= 48
) {
  const device = await adapter.requestDevice({
    requiredLimits: {
      maxStorageBuffersPerShaderStage: 16,
      maxSampledTexturesPerShaderStage: 48,
    },
  });
}
```

## Linux rollout

Initial Linux availability targeted Intel Gen12 and newer GPUs, using Vulkan
for WebGPU while the rest of Chromium continued using OpenGL
(`chrome-144`). AMD and NVIDIA were not part of that initial path.

The Linux rollout later included modern NVIDIA drivers dated 2024-05 on
Wayland (`chrome-147-148`).

## Android APIs and validation

The first alpha Kotlin WebGPU bindings are available in Jetpack under
`androidx.webgpu` (`chrome-144`).

Dawn validates SPIR-V by default on Android (`chrome-146`). Native
applications must supply well-formed modules; malformed input is rejected
before reaching and potentially destabilizing the driver.

## Apple deployment floor

Dawn requires macOS 11 or iOS 14 and supports Metal 2.3 or newer
(`chrome-134`). Raise deployment targets and build environments that still
target older Apple platforms.

## WebXR integration

Experimental WebGPU integration with WebXR is available for developer testing
on Windows and Android (`chrome-135`). Treat it as an experimental platform
path rather than assuming general WebXR availability.

## Worker-only synchronous mapping

The experimental worker-only `GPUBuffer.mapSync()` maps with the same mode as
`mapAsync()` (`chrome-145`). It appears only when Chrome is launched with
`--enable-features=WebGPUMapSyncOnWorkers`; feature-detect and retain the
asynchronous path:

```js
if ("mapSync" in GPUBuffer.prototype) {
  buffer.mapSync(GPUMapMode.READ);
} else {
  await buffer.mapAsync(GPUMapMode.READ);
}
```
