# Dawn native APIs, builds, and Emscripten

## C and C++ API migrations

### Descriptor and enum changes

`WGPUProgrammableStageDescriptor` was renamed to `WGPUComputeState`
(`chrome-133`).

The C++ `wgpu::VertexStepMode::VertexBufferNotUsed` value was removed
(`chrome-133`). Represent an unused vertex-buffer layout with an undefined
step mode and no attributes:

```cpp
wgpu::VertexBufferLayout unused{
    .stepMode = wgpu::VertexStepMode::Undefined,
    .attributeCount = 0,
};
```

### Unified limits

`WGPURequiredLimits` and `WGPUSupportedLimits` were flattened into
`WGPULimits` (`chrome-135`). Native callers must migrate away from both
wrapper structures.

### Texel-copy type names

Use the renamed C structures (`chrome-135`):

| Old | Current |
| --- | --- |
| `WGPUImageCopyBuffer` | `WGPUTexelCopyBufferInfo` |
| `WGPUImageCopyTexture` | `WGPUTexelCopyTextureInfo` |
| `WGPUTextureDataLayout` | `WGPUTexelCopyBufferLayout` |

### Binding-layout defaults

Binding-layout fields set to `Undefined` receive concrete defaults
(`chrome-134`):

| Field type | Default |
| --- | --- |
| `BufferBindingType` | `Uniform` |
| `SamplerBindingType` | `Filtering` |
| `TextureSampleType` | `Float` |
| `StorageTextureAccess` | `WriteOnly` |

Code that depended on an undefined field staying unspecified must set an
explicit value.

## WGSL feature queries and conversion

The C++ `wgpu::Instance::GetWGSLLanguageFeatures()` replaces
`EnumerateWGSLLanguageFeatures()` (`chrome-134`).

The C function `wgpuInstanceGetWGSLLanguageFeatures()` returns no value rather
than `WGPUStatus`, because the query cannot fail (`chrome-140`). Remove status
assignments and checks.

Tint's SPIR-V frontend supports 16-bit floating-point values when converting
SPIR-V to WGSL (`chrome-141`).

## Callback and presentation behavior

### Callback statuses

The callback status `InstanceDropped` was renamed to `CallbackCancelled`
(`chrome-136`). Cancellation of a callback does not mean background work,
such as pipeline compilation, has stopped.

`wgpu::PopErrorScopeStatus::EmptyStack` was renamed to
`wgpu::PopErrorScopeStatus::Error` (`chrome-136`). Its callback also receives
an explanatory error message.

`WGPUQueueWorkDoneCallback` receives an additional `message` argument beside
its status (`chrome-139`). Update native callback signatures.

### Surface presentation

`wgpuSurfacePresent()` returns a `WGPUStatus` error when the surface has no
current texture (`chrome-140`). Handle the result rather than assuming the
present succeeds.

Configuring a `wgpu::Surface` with `wgpu::PresentMode::Undefined` invokes
present-mode defaulting (`chrome-142`). Leave it undefined when implementation
selection is desired.

## Device and instance configuration

`wgpu::InstanceFeatureName::MultipleDevicesPerAdapter` permits multiple Dawn
devices to be created from one adapter (`chrome-140`). This is the native
opt-in corresponding to a lifecycle that otherwise consumes adapters.

The `dump_shaders_on_failure` device toggle dumps shaders only after failure
and currently applies only to D3 backends (`chrome-140`).

Dawn's Vulkan-only `wgpu::FeatureName::AdapterPropertiesDRM` enables queries
for Linux DRM adapter information (`chrome-147-148`).

## Headers and builds

The standardized core API in `webgpu.h` is stable (`chrome-141`), but
implementation extensions are not covered by that stability guarantee.
Compile with the header supplied by the exact Dawn, Emdawnwebgpu, or other
implementation being linked.

Default CMake builds set `DAWN_BUILD_MONOLITHIC_LIBRARY` to `STATIC` and
produce `libwebgpu*` files (`chrome-142`). Set the variable to `OFF` to retain
the earlier non-monolithic behavior.

### Prebuilt artifacts

Dawn publishes GitHub Actions artifacts with Android static libraries, an
Apple `.XCFramework`, and required headers (`chrome-141`).

Nightly Dawn and Emdawnwebgpu binaries are also published through
`google/dawn` GitHub releases (`chrome-145`). They are best-effort, unsigned
builds without a project guarantee; account for this in production or
automated installation policies.

## Tracing and diagnostics

Set `DAWN_TRACE_FILE_BASE` when running a Dawn program to record API usage in
a `.gputrace` file for Xcode's Metal Debugger (`chrome-135`).

## Emdawnwebgpu migration and builds

`emdawnwebgpu` is Dawn's maintained implementation of the standardized
`webgpu.h` over the browser API (`chrome-137`). Emscripten's built-in
`USE_WEBGPU` bindings are unmaintained, substantially outdated, and planned
for removal. New browser-targeted C/C++ work should use Emdawnwebgpu.

Dawn GLFW supports Emscripten in CMake builds, allowing one Dawn GLFW
application structure to target browsers through Emdawnwebgpu
(`chrome-138`).

Dawn package releases include a remote `emdawnwebgpu` port, with a snapshot
available in Emscripten 4.0.10 and newer (`chrome-138`):

```sh
emcc --use-port=emdawnwebgpu ...
```

When linked with `-sSHARED_MEMORY`, Emdawnwebgpu compiles its own
`webgpu.cpp` with the same flag (`chrome-139`). This keeps the port
implementation consistent with the application's memory model.

Emdawnwebgpu supports `wgpu::ExternalTexture`, but JavaScript must import the
underlying object (`chrome-145`). C and C++ cannot construct a browser
external texture directly; bridge an `HTMLVideoElement`, `VideoFrame`, or
similar object through JavaScript.
