# Platforms and integration

## Browser integrations

### WebXR testing

Experimental WebGPU integration with WebXR is available for developer testing
on Windows and Android (`chrome-135`). Treat the integration as experimental
and keep a non-WebGPU XR path where deployment requirements demand it.

### Canvas image export

The browser context menu for a WebGPU canvas includes **Save Image As…** and
**Copy Image** (`chrome-136`). This behavior is built in and requires no
application code.

## Platform support

### Linux rollout

The initial Linux rollout covered Intel Gen12 and newer GPUs, using Vulkan for
WebGPU while the rest of Chromium continued to use OpenGL (`chrome-144`). AMD
and Nvidia were not part of that initial enablement.

Modern NVIDIA drivers dated 2024-05 gained WebGPU support on Wayland in the
later Linux rollout (`chrome-147-148`). Keep backend, GPU generation, driver,
and display-server checks in deployment diagnostics.

### Android bindings and compatibility

The first alpha Android Kotlin bindings are available in Jetpack under
`androidx.webgpu` (`chrome-144`).

Android compatibility mode can run on OpenGL ES 3.1 hardware that lacks a
modern Vulkan-class API (`chrome-146`). Adapter request and device feature
semantics match the compatibility path described in the adapter reference.

### Apple deployment floor

Dawn requires macOS 11 or iOS 14 and supports Metal 2.3 or newer
(`chrome-134`). Raise both build settings and deployment targets that still
name older Apple platform versions.

## Adapter and hardware reporting

`GPUAdapterInfo.architecture` recognizes the exact lowercase strings
`"blackwell"` for recent Nvidia GPUs and `"rdna4"` for recent AMD GPUs
(`chrome-138`). Logging, metrics schemas, and architecture allowlists must
accept these values.
