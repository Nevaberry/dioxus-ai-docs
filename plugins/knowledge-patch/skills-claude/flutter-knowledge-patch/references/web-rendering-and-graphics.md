# Web, rendering, and graphics

## Web renderer migrations

The HTML renderer is removed (3.29.0). Web apps must use the remaining renderer
paths. CanvasKit and skwasm are both Skia-backed; Impeller is not available on web
(rendering-and-web).

When WebGL is unavailable, the runtime can fall back to CanvasKit rather than fail
on the original path (3.38.0). Test fallback behavior on the browser/device classes
the product supports.

`Image.network` no longer switches automatically to an HTML `<img>` after a CORS
error. Choose whether HTML-element fallback is disabled (the default), allowed on
failure, or preferred with `webHtmlElementStrategy` (3.29.0).

## WebAssembly

### Bootstrap and interop requirements (rendering-and-web)

Wasm requires Flutter 3.24 or later and web initialization from Flutter 3.22 or
later. Preserve custom web bootstrap changes, regenerate an old `web/` directory
from the current template, then reapply intentional customizations:

```sh
flutter create . --platforms web
```

Application or dependency code that still uses `dart:html` or `package:js` cannot
compile to Wasm. Dart 3.7 also deprecated `dart:indexed_db`, `dart:js`,
`dart:js_util`, `dart:web_audio`, and `dart:web_gl`; migrate browser APIs to
`package:web` and interop to `dart:js_interop` (dart-3.7.0).

### Fallback and path detection

A `--wasm` run/build emits a JavaScript fallback for browsers without WasmGC. Use
the compile-time environment to distinguish the selected path when behavior must
differ:

```dart
const isRunningWithWasm = bool.fromEnvironment('dart.tool.dart2wasm');
```

### Threading and headers

Wasm can run with ordinary response headers but is then single-threaded. Multithread
execution requires cross-origin isolation headers (3.29.0).

`flutter run --cross-origin-isolation` serves the required headers (3.41.0).
Chrome extensions are forced to single-threaded Wasm regardless of the setup used
by normally hosted pages.

### Compatibility dry run

Every JavaScript web build performs a dry-run Wasm compile and reports compatibility
warnings (3.35-guide). Disable it with `--no-wasm-dry-run` or request it explicitly
with `--wasm-dry-run`. Treat warnings as dependency migration work, not renderer
noise.

## Hot reload and development server

Web hot reload progressed through several command contracts:

- 3.32-guide: opt in with `--web-experimental-hot-reload`; `r` reloads and `R`
  restarts.
- 3.35-guide: stateful reload is the default on Chrome, with
  `--no-web-experimental-hot-reload` as a temporary opt-out; the web-server device
  was not yet supported.
- 3.38-guide: the web-server device reloads by default and supports multiple
  connected browsers when run with `flutter run -d web-server`.
- 3.44-guide: the deprecated `--web-hot-reload` option is removed from current
  workflows.

Remove stale enablement flags and use the options exposed by the selected SDK.

## Shared web development configuration (3.38-guide)

Put host, port, certificate, and header settings in project-root
`web_dev_config.yaml`. It can also define path-based proxies to another server,
giving the team consistent same-origin development endpoints.

Explicit command-line HTTPS and header options override the file (3.41.0).
`flutter run --base-href /app/` makes development use a production-like non-root
base path (3.44-guide).

Custom bootstrap configuration must spell `entrypointBaseUrl`, not the old
`entryPointBaseUrl` (3.35.0).

`flutter build web --web-define=NAME=value` injects web-template variables
(3.41.0), and `--static-assets-url` selects a separate asset base
(3.38.0).

## Service workers and output controls

The generated service worker is self-cleaning and `--pwa-strategy` is deprecated;
remove build logic that depends on that option (3.41.0).

Web compilation accepts `--no-minify`. Wasm honors the same minification choice and
default as JavaScript (3.35.0).

Chrome-device launches no longer add `--no-sandbox` automatically (3.41.0); supply
only the browser flags required by the actual environment.

## Impeller and Flutter GPU

Android devices without working Vulkan use Impeller OpenGLES rather than Skia, while
iOS removed Skia and the Impeller opt-out (3.29.0). Android later deprecated its
Impeller opt-out (3.38.0). Impeller on macOS remains opt-in through
`--enable-impeller` or `FLTEnableImpeller` (rendering-and-web).

The experimental Flutter GPU API is off by default. Enable it with
`flutter run --enable-flutter-gpu`; a macOS embedder can use
`FLTEnableFlutterGPU` (3.35.0). Resource-creation failures throw exceptions rather
than return the previous failure value, so experimental callers must catch them
(3.32.0).

## Filters and color

### Backdrop and shader filters (3.29.0)

Share compatible backdrop work by placing `BackdropFilter.grouped` widgets beneath
one `BackdropGroup`.

```dart
final blur = ImageFilter.blur(sigmaX: 12, sigmaY: 12);
return BackdropGroup(
  child: Stack(children: [
    BackdropFilter.grouped(filter: blur, child: firstPane),
    BackdropFilter.grouped(filter: blur, child: secondPane),
  ]),
);
```

`ImageFilter.shader(fragmentShader)` applies a custom shader to child content and,
unlike `AnimatedSampler` from `package:flutter_shaders`, can also be used by
backdrop filters.

When `ImageFilter.blur` omits `tileMode`, Flutter chooses it automatically. Supply
one when edge sampling must remain stable (breaking-change-guides). Remove the old
`bounded` argument from `ImageFilterConfig.blur` (3.44.0).

### Saturation, blur, and color spaces

`ColorFilter.saturation` changes saturation without a hand-written matrix, while
`ImageFilterConfig` configures iOS-style blur behavior (3.41.0).

On iOS, bounded backdrop blur prevents translucent content from bleeding color at
its edges (3.41-guide).

macOS supports Display P3, float32 images can preserve float output through
`Image.toByteData()`, and web `Color.lerp` can interpolate values from different
color spaces (3.44.0).

## Shaders and textures

`decodeImageFromPixelsSync` creates a shader texture in the same frame. Shader
textures support float formats up to 128 bits; select one with
`Picture.toImageSync(targetFormat: ...)` before binding it (3.41-guide).

```dart
final image = recorder.endRecording().toImageSync(
  128,
  128,
  targetFormat: ui.TargetPixelFormat.rFloat32,
);
shader.setImageSampler(0, image);
```

Impeller and web can bind float, vector, and image-sampler uniforms by name.
`FragmentShader.setImageSampler` accepts `FilterQuality` per sampler (3.41.0).

Shader assets support flavors and asset transformers (3.44.0). Do not list the same
shader as both shader and ordinary asset; that is a build error (3.41.0).

## Shapes and images

Rounded-superellipse APIs initially rendered natively only on iOS and Android and
fell back to rounded rectangles elsewhere (3.32-guide). Web gained a native
rounded-superellipse implementation in 3.35.0.

Dynamic fonts loaded through `FontLoader.addFont` are registered in call order,
making multi-font loading deterministic (3.38.0).

## Web accessibility and selection

Flutter web supports semantic locales, forced-color themes, user text-spacing
overrides, reduced motion, and immediate validation-error feedback
(3.32-guide, 3.35-guide, 3.41-guide, 3.44-guide).

`SelectableRegion` preserves its layout constraints and multiline copy preserves
line breaks on web and native targets (3.44-guide).

## Rendering verification

- Test JavaScript, WasmGC, and JavaScript fallback paths; validate cross-origin
  isolation and Chrome-extension single-thread behavior.
- Run Wasm dry runs and migrate every incompatible dependency.
- Exercise WebGL loss/fallback, CORS image policy, renderer selection, and browser
  accessibility preferences.
- Compare filter edges, shader bindings, sampler quality, float precision, wide
  gamut, and mixed-color-space interpolation per renderer.
- Verify hot reload through Chrome and web-server devices and test
  `web_dev_config.yaml` proxies, headers, TLS, and base paths.
