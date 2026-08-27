# Adapters, compatibility, features, and limits

## Requesting limits safely

### Forward an unavailable limit as `undefined`

An unknown property in `requiredLimits` may have an `undefined` value
(`chrome-133`). This lets code forward a limit that may have disappeared or
may not be exposed without filtering the key first:

```js
const adapter = await navigator.gpu.requestAdapter();
const device = await adapter.requestDevice({
  requiredLimits: { someLimit: adapter.limits.someLimit },
});
```

For numeric requirements that are known, compare with `adapter.limits` before
requesting them. A request above the supported value still fails.

### Higher per-stage tiers

Dawn can expose `maxStorageBuffersPerShaderStage` up to 16 and
`maxSampledTexturesPerShaderStage` up to 48 (`chrome-146`). Request those
values only after checking both:

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

### Retired inter-stage component limit

`maxInterStageShaderComponents` was deprecated in favor of
`maxInterStageShaderVariables` and scheduled for removal (`chrome-133`).
Do not request or branch on the component limit.

## Compatibility mode

### Adapter request spelling

Request a compatibility-defaulting adapter with
`featureLevel: "compatibility"`; `"core"` is the default and only other
allowed request value (`chrome-133`):

```js
const adapter = await navigator.gpu.requestAdapter({
  featureLevel: "compatibility",
});
```

At introduction, the adapter exposed the selected level through
`featureLevel`, replacing the experimental `compatibilityMode` option and
`isCompatibilityMode` attribute. That adapter attribute was removed later.

### Determine restrictions from device features

The adapter-level experimental `featureLevel` and `isCompatibilityMode`
attributes were removed (`chrome-136`). The request can return a
compatibility-defaulting adapter when possible and otherwise a core-defaulting
adapter.

Core-defaulting adapters automatically enable `"core-features-and-limits"`.
A compatibility-defaulting adapter may expose that feature for explicit
request, lifting compatibility restrictions when the experimental browser
configuration permits it:

```js
const adapter = await navigator.gpu.requestAdapter({
  featureLevel: "compatibility",
});
if (!adapter) throw new Error("WebGPU unavailable");

const requiredFeatures = adapter.features.has("core-features-and-limits")
  ? ["core-features-and-limits"]
  : [];
const device = await adapter.requestDevice({ requiredFeatures });

if (!device.features.has("core-features-and-limits")) {
  useCompatibilityRestrictedPath();
}
```

Calling `requestDevice()` with neither `requiredFeatures` nor
`requiredLimits` asks for the adapter's default capabilities.

### Browser enablement history and Android

- The unsafe WebGPU flag was required for the early compatibility path
  (`chrome-133`).
- On Android, that single flag came to enable all capabilities needed by the
  experimental path, including an OpenGL ES backend on devices without Vulkan
  (`chrome-135`).
- An origin trial could expose compatibility mode to visitors, while local
  testing used the experimental web-platform-features flag; the trial was
  scheduled through Chrome 145 and the mode was otherwise disabled by default
  (`chrome-139`).
- Android OpenGL ES 3.1 hardware gained the compatibility path without changing
  the request or feature semantics (`chrome-146`).

These are deployment switches, not a substitute for runtime capability checks.

### Vertex-stage storage buffers

Compatibility adapters expose `maxStorageBuffersInVertexStage`, which may be
zero (`chrome-146-guides`). Choose a vertex path with no storage-buffer
bindings when needed:

```js
if (adapter.limits.maxStorageBuffersInVertexStage === 0) {
  useVertexPathWithoutStorageBuffers();
}
```

## Adapter and device lifetime

### One successful device per adapter

A successful `GPUAdapter.requestDevice()` consumes the adapter
(`chrome-140`). A second request now rejects:

```js
const adapter = await navigator.gpu.requestAdapter();
const device = await adapter.requestDevice();
await adapter.requestDevice(); // Rejects.
```

Native Dawn applications that really need more than one device can enable
`wgpu::InstanceFeatureName::MultipleDevicesPerAdapter` on the instance.

### Fallback status

`GPUAdapterInfo.isFallbackAdapter` describes an adapter chosen for
compatibility, predictability, or privacy rather than performance, and is also
available at `GPUDevice.adapterInfo` (`chrome-136`). At introduction, Chrome
did not ship fallback adapters and the value was always `false`.

The adapter-level `GPUAdapter.isFallbackAdapter` was deprecated
(`chrome-138`) and then removed (`chrome-140`). Use:

```js
const isFallback = adapter.info.isFallbackAdapter;
```

## Experimental adapter metadata

With the WebGPU developer-features flag enabled, the non-standard
`GPUAdapterInfo.powerPreference` can report `"low-power"` or
`"high-performance"` when supported (`chrome-137`). It reflects the preference
used for adapter selection:

```js
if (device.adapterInfo.powerPreference === "high-performance") {
  enableEnhancedGraphics();
}
```

Feature-detect non-standard metadata and do not require it for correctness.
