# Native Dawn and Emdawnwebgpu

## C and C++ API migrations

### Types and enum values

`WGPUProgrammableStageDescriptor` was renamed to `WGPUComputeState`
(`chrome-133`). The C++ value
`wgpu::VertexStepMode::VertexBufferNotUsed` was removed; express an unused
vertex buffer with an undefined step mode and no attributes:

```cpp
wgpu::VertexBufferLayout unused{
    .stepMode = wgpu::VertexStepMode::Undefined,
    .attributeCount = 0,
};
```

The limit wrappers `WGPURequiredLimits` and `WGPUSupportedLimits` were
flattened into `WGPULimits` (`chrome-135`). The texel-copy structures were
renamed in the same API:

| Old name | Current name |
| --- | --- |
| `WGPUImageCopyBuffer` | `WGPUTexelCopyBufferInfo` |
| `WGPUImageCopyTexture` | `WGPUTexelCopyTextureInfo` |
| `WGPUTextureDataLayout` | `WGPUTexelCopyBufferLayout` |

### Binding-layout defaults

Binding-layout fields set to `Undefined` receive concrete defaults
(`chrome-134`):

| Field category | Default |
| --- | --- |
| Buffer | `BufferBindingType::Uniform` |
| Sampler | `SamplerBindingType::Filtering` |
| Sampled texture | `TextureSampleType::Float` |
| Storage texture | `StorageTextureAccess::WriteOnly` |

Set fields explicitly when a different interpretation is required.

### WGSL language-feature queries

`wgpu::Instance::GetWGSLLanguageFeatures()` replaces
`EnumerateWGSLLanguageFeatures()` in C++ (`chrome-134`).
`wgpuInstanceGetWGSLLanguageFeatures()` no longer returns `WGPUStatus`; the
query cannot fail, so remove assignments and status checks (`chrome-140`).

### Callback changes

`InstanceDropped` was renamed to `CallbackCancelled` (`chrome-136`).
Cancellation of the callback does not mean background work such as pipeline
compilation stopped.

`wgpu::PopErrorScopeStatus::EmptyStack` became
`wgpu::PopErrorScopeStatus::Error`, and the callback receives an explanatory
message (`chrome-136`).

`WGPUQueueWorkDoneCallback` gained a `message` argument in addition to its
status (`chrome-139`). Update callback function signatures and any adapters
that forward them.

### Surface behavior

`wgpuSurfacePresent()` returns a `WGPUStatus` error when no current surface
texture exists (`chrome-140`). Handle the result.

Configuring `wgpu::Surface` with `wgpu::PresentMode::Undefined` correctly
invokes present-mode defaulting (`chrome-142`); callers may leave it undefined
instead of selecting a mode.

### Multiple devices

Enable `wgpu::InstanceFeatureName::MultipleDevicesPerAdapter` when a native
application needs more than one device from the same adapter (`chrome-140`).
Without it, a successful device request consumes the adapter.

## Headers, libraries, and artifacts

### Stable core header

The standardized core API in `webgpu.h` is stable (`chrome-141`), but that
stability does not cover implementation extensions. Use the header supplied
by the exact Dawn, Emdawnwebgpu, or other implementation being linked.

### Monolithic library default

`DAWN_BUILD_MONOLITHIC_LIBRARY` defaults to `STATIC`, so default CMake builds
produce `libwebgpu*` files (`chrome-142`). Set it to `OFF` to retain the old
non-monolithic behavior.

### Prebuilt and nightly artifacts

Dawn publishes GitHub Actions artifacts containing Android static libraries,
an Apple `.XCFramework`, and required headers (`chrome-141`). These are an
alternative to compiling from source.

Nightly Dawn and Emdawnwebgpu binaries are also published in the `google/dawn`
releases (`chrome-145`). They are best-effort, unsigned builds without a
project guarantee; account for provenance and stability before automated or
production installation.

## Debugging and shader input

### Metal trace capture

Set `DAWN_TRACE_FILE_BASE` when running a Dawn program to record API use in a
`.gputrace` file for Xcode's Metal Debugger (`chrome-135`).

### Failure-only shader dumps

The `dump_shaders_on_failure` device toggle emits shaders only on failure and
currently applies only to D3 backends (`chrome-140`).

### SPIR-V handling

Tint's SPIR-V frontend supports 16-bit floating-point values during
SPIR-V-to-WGSL conversion (`chrome-141`).

Dawn validates SPIR-V by default on Android (`chrome-146`). Supply well-formed
modules; malformed input is stopped before reaching and potentially
destabilizing the driver.

## Emdawnwebgpu

### Prefer the maintained browser implementation

`emdawnwebgpu` implements current standardized `webgpu.h` over the browser API
and is maintained by Dawn (`chrome-137`). Emscripten's built-in `USE_WEBGPU`
bindings are unmaintained, substantially outdated, and planned for removal.
Use Emdawnwebgpu for new work and migrate existing browser targets.

Package releases include the remote port, and Emscripten 4.0.10 or newer
contains a snapshot (`chrome-138`):

```sh
emcc --use-port=emdawnwebgpu ...
```

Dawn GLFW supports Emscripten in CMake builds, so the same application
structure can target the browser through Emdawnwebgpu (`chrome-138`).

### Shared-memory builds

When linked with `-sSHARED_MEMORY`, Emdawnwebgpu's `webgpu.cpp` is compiled
with the same flag (`chrome-139`). Keep the application's and port's
shared-memory configuration aligned.

### External textures

Emdawnwebgpu supports `wgpu::ExternalTexture` (`chrome-145`), but the texture
must be imported from JavaScript, for example through `EM_ASM`. C or C++ cannot
construct it directly because import requires a JavaScript object such as an
`HTMLVideoElement` or `VideoFrame`.

## Native feature changes

`wgpu::FeatureName::R8UnormStorage` was removed in favor of
`wgpu::FeatureName::TextureFormatTier1` (`chrome-145`).
`wgpu::FeatureName::Snorm16TextureFormats` was also removed;
`wgpu::FeatureName::TextureFormatsTier1` covers most of its capabilities but
is not an exact replacement when resolve support is required.

On Linux Vulkan, `wgpu::FeatureName::AdapterPropertiesDRM` enables querying
DRM adapter information (`chrome-147-148`).
