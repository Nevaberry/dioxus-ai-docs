# Web, rendering, and graphics

## Web renderers and image elements

- The HTML renderer is removed in 3.29.0. CanvasKit and skwasm both remain
  Skia-backed; Impeller is not available on web (`rendering-and-web`).
- `Image.network` no longer silently falls back to an HTML `<img>` after a CORS
  failure. Choose disabled (default), fallback-on-failure, or preferred behavior
  explicitly with `webHtmlElementStrategy` (3.29.0).
- When WebGL is unavailable, the runtime can fall back to CanvasKit rather than
  failing the original renderer path (3.38.0).
- Rounded superellipses initially fell back to rounded rectangles off mobile
  (`3.32-guide`); web gained real rounded-superellipse rendering in 3.35.0.

## WebAssembly deployment and compatibility

- A Wasm app can run under ordinary response headers but remains single-threaded.
  Cross-origin isolation headers are required for multithreading (3.29.0).
- JavaScript builds perform a Wasm dry run and emit compatibility warnings. Use
  `--no-wasm-dry-run` to suppress it or `--wasm-dry-run` explicitly
  (`3.35-guide`).
- Wasm requires Flutter 3.24+ and web initialization from Flutter 3.22+. Preserve
  customizations, replace an older `web/` directory with the current template, and
  run `flutter create . --platforms web` (`rendering-and-web`).
- App or dependency use of `dart:html` or `package:js` prevents Wasm compilation;
  migrate to `dart:js_interop` and `package:web`.
- A `--wasm` build also emits a JavaScript fallback for browsers without WasmGC.
  Detect the chosen path with
  `const bool.fromEnvironment('dart.tool.dart2wasm')` (`rendering-and-web`).
- Chrome extensions force Wasm single-threaded regardless of normal hosting
  configuration (3.41.0). For regular development servers,
  `flutter run --cross-origin-isolation` serves the required isolation headers.

## Stateful hot reload

- In `3.32-guide`, Chrome hot reload required
  `--web-experimental-hot-reload`; `r` reloaded and `R` restarted.
- `3.35-guide` enabled it by default on Chrome, with temporary
  `--no-web-experimental-hot-reload` opt-out; web-server was not yet supported.
- `3.38-guide` enabled hot reload by default for
  `flutter run -d web-server`, including multiple connected browsers.
- Remove deprecated `--web-hot-reload` from commands (`3.44-guide`). Use the
  current default workflow and retain the `--no-web-experimental-hot-reload` form
  only where the applicable SDK still documents it.

## Development and build configuration

- Project-root `web_dev_config.yaml` shares host, port, TLS certificates, headers,
  and path proxies for same-origin development (`3.38-guide`). Explicit command-
  line HTTPS and header options take precedence (3.41.0).
- `flutter run --base-href /app/` mirrors a production subpath during development
  (`3.44-guide`).
- Rename custom bootstrap option `entryPointBaseUrl` to `entrypointBaseUrl`
  (3.35.0).
- `flutter build web --web-define=NAME=value` injects template values (3.41.0).
  `--static-assets-url` selects a separate static-asset base (3.38.0).
- `--no-minify` controls JavaScript and Wasm minification; both use the same
  default selection (3.35.0).
- The generated service worker is self-cleaning and `--pwa-strategy` is deprecated
  (3.41.0). Do not build new release scripts around the old strategy switch.

## Filters and backdrop rendering

- Put compatible `BackdropFilter.grouped` widgets under one `BackdropGroup` to
  share backdrop work. `ImageFilter.shader(fragmentShader)` applies a fragment
  shader to child content and also works with backdrop filtering, unlike
  `AnimatedSampler` from `package:flutter_shaders` (3.29.0).
- `ColorFilter.saturation` replaces hand-written saturation matrices, while
  `ImageFilterConfig` configures iOS-style blur (3.41.0).
- `ImageFilter.blur` automatically chooses `tileMode` when omitted; pass a mode when
  edge sampling must stay fixed (`breaking-change-guides`). Remove the former
  `bounded` argument from `ImageFilterConfig.blur` (3.44.0).

## Shader textures and bindings

- `decodeImageFromPixelsSync` creates a shader texture in the same frame.
  `Picture.toImageSync(targetFormat: ...)` supports float formats through 128 bits
  before sampler attachment (`3.41-guide`).
- Impeller and web shaders bind float, vector, and image sampler uniforms by name.
  `FragmentShader.setImageSampler` accepts `FilterQuality` (3.41.0).
- Flutter tooling supports shader flavors and asset transformers (3.44.0). Listing
  one shader as both shader and normal asset is an error (3.41.0).

## Color and image precision

- Flutter GPU creation failures throw exceptions (3.32.0); catch them at resource
  creation boundaries.
- macOS supports Display P3. Float32 images preserve float32 through
  `Image.toByteData()`, and web `Color.lerp` interpolates across differing color
  spaces (3.44.0).
- `FontLoader.addFont` processes fonts in call order, making dynamic registration
  deterministic (3.38.0).

## Web accessibility and selection

- Web honors `prefers-reduced-motion` and reports form validation through
  `aria-description` (`3.44-guide`). It also respects forced colors when
  `ThemeData(useSystemColors: true)` and user text-spacing overrides.
- `SelectableRegion` forwards constraints unchanged and multiline copy preserves
  line breaks (`3.44-guide`). Test these behaviors on CanvasKit and skwasm.
