# Web, rendering, and graphics

## Contents

- [Web hot reload](#web-hot-reload)
- [Shared development configuration](#shared-development-configuration)
- [WebAssembly](#webassembly)
- [Web renderers](#web-renderers)
- [Web build and run options](#web-build-and-run-options)
- [Impeller and Flutter GPU](#impeller-and-flutter-gpu)
- [Backdrop and image filters](#backdrop-and-image-filters)
- [Shader textures and bindings](#shader-textures-and-bindings)
- [Image formats and color spaces](#image-formats-and-color-spaces)
- [Rounded superellipses](#rounded-superellipses)
- [Diagnostics](#diagnostics)

## Web hot reload

Stateful web hot reload is enabled by default. Its evolution matters when cleaning old
launch configurations:

- The initial experiment required `--web-experimental-hot-reload` (`3.32-guide`).
- It then became the default for Chrome; `--no-web-experimental-hot-reload` remained a
  temporary opt-out, while the `web-server` device was not yet supported
  (`3.35-guide`).
- The `web-server` device gained default hot reload, including with several browsers
  connected to the application URL (`3.38-guide`).
- Remove the deprecated `--web-hot-reload` spelling. In an attached terminal, `r`
  reloads and `R` performs a hot restart.

## Shared development configuration

Put team-wide host, port, certificate, header, and path-proxy settings in project-root
`web_dev_config.yaml`. Path proxies provide consistent same-origin development
endpoints. Explicit command-line HTTPS and header settings take precedence.

Use `flutter run --base-href /app/` when a development run must use the same non-root
base path as production (`3.44-guide`).

## WebAssembly

### Hosting and threading

A WebAssembly build runs with ordinary HTTP headers, but without cross-origin
isolation it is single-threaded (`3.29.0`). Serve the required isolation headers when
multithreading is required, or let Flutter serve them during a run:

```sh
flutter run --cross-origin-isolation
```

Chrome extensions always run Flutter Wasm single-threaded, regardless of the normal
hosting setup (`3.41.0`).

### Project and interop prerequisites

The Wasm target requires Flutter 3.24 or later and the Flutter 3.22-or-later web
initialization. Preserve customizations, clear an outdated `web/` directory, and
regenerate it when the project predates the compatible template:

```sh
flutter create . --platforms web
```

Application or dependency code that retains `dart:html` or `package:js` cannot
compile to Wasm. Dart also deprecates `dart:indexed_db`, `dart:js`, `dart:js_util`,
`dart:web_audio`, and `dart:web_gl` (`dart-3.7.0`). Migrate JavaScript interop to
`dart:js_interop` and browser APIs to `package:web`.
The legacy libraries were scheduled for removal at the end of 2025.

### Fallback detection

`--wasm` emits a JavaScript fallback for browsers without WasmGC. Check the
compile-time environment value when behavior depends on the selected path:

```dart
const isRunningWithWasm = bool.fromEnvironment('dart.tool.dart2wasm');
```

Every JavaScript web build performs a dry-run Wasm compilation and reports
compatibility warnings. Use `--no-wasm-dry-run` to suppress it or `--wasm-dry-run` to
request it explicitly.

## Web renderers

The HTML renderer is removed. CanvasKit and skwasm both remain Skia-backed; Impeller
is not available on the web. When WebGL is unavailable, the runtime can use its
CanvasKit fallback rather than failing on the original renderer path (`3.38.0`).

`Image.network` does not automatically switch to an HTML `<img>` after a CORS error.
Choose `webHtmlElementStrategy` explicitly to disable HTML-element fallback (the
default), allow it only after failure, or prefer it.

## Web build and run options

- `flutter build web --static-assets-url` selects a separate base URL for static
  assets.
- `flutter build web --web-define=NAME=value` injects web template variables.
- `--no-minify` disables minification; Wasm and JavaScript builds honor the same
  selection and default (`3.35.0`).
- The custom bootstrap option is `entrypointBaseUrl`, not the deprecated
  `entryPointBaseUrl`.
- The generated service worker cleans itself up. `--pwa-strategy` is deprecated; do
  not base build automation on its former behavior.
- Chrome launches no longer add `--no-sandbox` automatically.

## Impeller and Flutter GPU

Impeller is mandatory on iOS, defaults on supported Android devices, remains opt-in
on macOS, and is unavailable on web. Platform backend details are in the Android and
Apple references.

The experimental Flutter GPU API is disabled by default. Enable it for a run with:

```sh
flutter run --enable-flutter-gpu
```

macOS embedders can set `FLTEnableFlutterGPU`. Resource-creation failures throw, so
catch exceptions rather than expecting an error return.

## Backdrop and image filters

Place compatible filters under one `BackdropGroup` and use
`BackdropFilter.grouped` to share backdrop work:

```dart
final blur = ImageFilter.blur(sigmaX: 12, sigmaY: 12);
return BackdropGroup(
  child: Stack(
    children: [
      BackdropFilter.grouped(filter: blur, child: firstPane),
      BackdropFilter.grouped(filter: blur, child: secondPane),
    ],
  ),
);
```

`ImageFilter.shader(fragmentShader)` filters child content and can also be used by a
backdrop filter, unlike `AnimatedSampler` from `package:flutter_shaders`.

`ColorFilter.saturation` replaces hand-written saturation matrices. `ImageFilterConfig`
configures iOS-style blur behavior, but callers of `ImageFilterConfig.blur` must remove
the former `bounded` argument.

```dart
ColorFiltered(
  colorFilter: const ColorFilter.saturation(0.5),
  child: image,
)
```

When `ImageFilter.blur` omits `tileMode`, Flutter selects it automatically. Supply an
explicit mode when edge sampling must be stable:

```dart
ImageFilter.blur(
  sigmaX: 8,
  sigmaY: 8,
  tileMode: TileMode.clamp,
)
```

## Shader textures and bindings

`decodeImageFromPixelsSync` creates a shader texture usable in the same frame.
Textures support float formats up to 128 bits; select a target format when converting
a picture synchronously (`3.41-guide`):

```dart
final image = recorder.endRecording().toImageSync(
  128,
  128,
  targetFormat: ui.TargetPixelFormat.rFloat32,
);
shader.setImageSampler(0, image);
```

Impeller and the web renderer can bind float, vector, and image-sampler uniforms by
name. `FragmentShader.setImageSampler` accepts `FilterQuality` for per-binding
sampling. Flutter tooling supports shader flavors and asset transformers; declaring
one shader as both a shader and a normal asset is an error.

Flutter no longer bundles SkSL data or the iOS SkSL build target. Remove capture and
warm-up bundle steps from build pipelines.

## Image formats and color spaces

- macOS rendering supports Display P3.
- Float32 images retain float32 output through `Image.toByteData()`.
- Web `Color.lerp` accepts colors from different color spaces (`3.44.0`).
- `FontLoader.addFont` processes fonts in call order, making multi-font registration
  deterministic.

## Rounded superellipses

Use `RoundedSuperellipseBorder`, `ClipRSuperellipse`,
`Canvas.drawRSuperellipse`, `Canvas.clipRSuperellipse`, and
`Path.addRSuperellipse` for continuous corners. They initially rendered natively only
on iOS and Android and fell back to rounded rectangles elsewhere; the web renderer
later implemented the actual superellipse (`3.35.0`). `CupertinoAlertDialog` and
`CupertinoActionSheet` use the shape.

## Diagnostics

Set `debugPaintTextLayoutBoxes = true` in debug builds to show the otherwise invisible
line and glyph boxes used by text layout.
