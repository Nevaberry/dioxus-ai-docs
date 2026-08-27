---
name: maplibre-native-knowledge-patch
description: MapLibre Native
version: null
license: MIT
metadata:
  author: Nevaberry
---


# MapLibre Native Compatibility Guide

Use this skill when changing MapLibre Native applications, styles, renderers,
offline storage, platform bindings, or source builds. First identify the target
product and its pinned release: Android, iOS/Darwin, Node, and Qt advance on
independent release lines and do not share one public core version.

## Reference index

| Reference | Topics |
| --- | --- |
| [Android](references/android.md) | SDK migrations, renderer artifacts, sources, offline storage, camera, and style behavior |
| [iOS and Darwin](references/ios.md) | Distribution, sources, networking, camera, snapshots, observers, offline packs, and Metal layers |
| [Architecture and rendering](references/architecture-and-rendering.md) | Core ownership, actors, tile preparation, drawables, backends, Linux builds, and render tests |
| [Desktop bindings](references/desktop-bindings.md) | Node rendering and resource hooks; Qt libraries, QML, deployment, and Android ABIs |
| [Style and interoperability](references/style-and-interop.md) | Style-spec differences, expressions, typed mutation, and Native/GL JS boundaries |

## Working rules

1. Read the platform dependency declaration before recommending an API or
   renderer. Do not infer Android support from iOS, Node, Qt, or the shared
   style specification.
2. Distinguish packaged artifact defaults from source-build defaults. An
   Android Maven coordinate, a Gradle source-build flavor, and a runtime
   backend choice are separate decisions.
3. Check Native Android and Native iOS support tables property by property.
   Valid version 8 style JSON does not imply complete feature parity.
4. Wait for the style-load callback before mutating typed sources, layers,
   images, light, or transitions.
5. Treat platform wrappers and the renderer as one build-time composition.
   Shared style assets and fixtures do not create shared runtime APIs.

## Breaking changes and migrations

### Android minimum SDK

Android 12.0 raises `minSdk` from 21 to 23. Set the application to at least 23
before upgrading.

### Android renderer artifacts

Android 13.0 makes `org.maplibre.gl:android-sdk` the Vulkan artifact. Keep
OpenGL ES explicitly with:

```kotlin
implementation("org.maplibre.gl:android-sdk-opengl:13.4.0")
```

Vulkan surface snapshots require 13.3 or later and Vulkan custom layers
require 13.4 or later. Android 13.5 adds the `multiBackend` Gradle flavor for
runtime OpenGL/Vulkan selection. For a source checkout, `opengl` and `vulkan`
remain build flavors and the broad-compatibility default is OpenGL.

### Android synchronous GeoJSON

Android 12.3 introduced synchronous GeoJSON setters, but Android 13.0 removed
the individual setters. Configure new sources and then use the ordinary update
API:

```kotlin
GeoJsonOptions().withSynchronousUpdate(true)
```

For a source already attached to a style, Android 13.5 adds
`setOverrideSynchronousUpdate`.

### Node runtime and renderer

Node.js 16 is unsupported from the Node 6.1 package line; the packaging path
requires Node.js 18 or newer. The stable 6.4.1 binding explicitly supports
Node.js 20, 22, and 24. Do not assume Node.js 26 support from the stable line.
Linux and Windows use the drawable renderer; the legacy renderer is gone.

### Deprecated Android annotations

The core `Annotation` family (`Marker`, `Polyline`, `Polygon`, their option
types, and `IconFactory`) has been deprecated since 7.0.0. Use the separate
MapLibre Annotation Plugin for new overlay work.

### Style and request behavior to recheck

- Android 13.1 stops scaling icons when offsets are used on pitched maps;
  visually retest affected symbol styles.
- iOS 6.22 cancels an in-flight style request when style JSON is loaded.
- A native-library load failure throws from Android 12.1 onward instead of
  failing silently.
- When adopting the iOS 6.14 dynamic texture atlas, verify glyph loading in
  existing styles.

## Renderer selection

| Target | Practical choice |
| --- | --- |
| Android packaged SDK | Vulkan through `android-sdk`; OpenGL ES through `android-sdk-opengl`; `multiBackend` when runtime switching is required |
| Android source build | `opengl` or `vulkan` Gradle flavor, setting the matching CMake option |
| iOS | Metal is stable, recommended, and selected by the CMake or Bazel configuration |
| Linux | OpenGL ES 3 and Vulkan are stable; WebGPU remains experimental |
| Windows | OpenGL ES 3 is stable |
| Node | Drawable renderer on Linux/Windows; Metal on macOS |
| Qt 3 | OpenGL is the only stable backend; `QSG_RHI_BACKEND=opengl` can force it |

Do not treat the shader-registry and named-render-pass design as proof that a
platform SDK publicly exposes every operation. Consult the architecture
reference before changing renderer internals.

## Sources, tiles, and runtime state

### PMTiles and MLT

PMTiles is available in Android, iOS through `pmtiles://`, and Node. iOS 6.14
always treats PMTiles metadata as XYZ; Android 13.3 includes PMTiles resources
in the ambient cache. MLT parsing arrives in Android 12.1 and iOS 6.20, while
Android 13.4 also accepts FastPFOR-encoded MLT tiles.

### Feature state and custom vector data

Android 13.4 exposes per-feature state. Android 13.5 repaints symbol paint
properties that depend on changed feature state and adds `CustomVectorSource`
for binary vector-tile delivery. Complete vector-tile feature-state updates are
applied on the iOS 6.15 line.

### Camera and visual capabilities

Both mobile SDKs support camera roll on their newer lines. Frustum offsets can
omit screen edges. Color-relief layers and updated hillshade algorithms are
available on both; Android 13.0.1 fixes Vulkan color-relief and hillshade
layers becoming invisible above fill layers.

## Style and expressions

Native pitch is limited to 0–60 degrees. Root `centerAltitude`, `roll`, and
`state`/global-state are unsupported on Android and iOS. A `glyphs` URL works,
but omitting it for local fonts does not; root `font-faces` support begins in
Android 11.13.0 and iOS 6.18.0.

`get` returns the generic `value` type. Assert a concrete type when the
consumer requires one:

```json
["string", ["get", "feature_property"]]
```

Use a `to-*` coercion when conversion and a fallback are desired:

```json
["to-number", ["get", "feature_property"], 0]
```

Android and iOS builders feed the shared C++ expression evaluator. Check the
platform's typed names rather than mechanically converting style JSON keys.
Android 13.5 adds `split` and `join`, Unicode-correct string expressions, and
alpha-bearing HSL color parsing.

## Offline storage

Keep explicit offline regions separate from the ambient cache. Pausing an
explicit region does not make downloaded resources unavailable. Clearing the
ambient cache retains resources required by offline regions. Database packing,
resetting, and cache maintenance are asynchronous storage work and must stay
off the frame-rendering path.

On iOS, call `reloadPacks` after importing a database before reading
`MLNOfflineStorage.sharedOfflineStorage.packs`. Newer `MLNOfflinePack` objects
also expose the underlying region identifier.

## Node rendering checklist

- `Map.render` returns an asynchronous four-channel raw pixel buffer.
- Constructor `ratio` controls high-density scale.
- A custom `request` hook must handle every style resource and custom scheme;
  successful data must be uncompressed bytes.
- Listen to module `message` events for native style and resource failures.
- `release()` permanently disables rendering but is safe in the render
  callback because that callback retains its returned buffer.

## Qt deployment checklist

- Use `QMapLibre::Core`, `QMapLibre::Location`, or `QMapLibre::Widgets` CMake
  targets rather than legacy names.
- QML uses `import MapLibre 3.0`.
- Deploy both `plugins/geoservices` and `qml/MapLibre` for Location/QML apps.
- Include both `QMapLibre` and `QMapLibreWidgets` libraries for Widgets apps.
- For Android multi-ABI builds, resolve `QMapLibre_DIR` below the common
  `QMapLibre_Android_DIR` using `ANDROID_ABI`.

## Linux rendering workflow

Use the `linux-opengl` preset with cloned submodules. It builds the GLFW tools
and static libraries; current Wayland defaults also require
`libegl1-mesa-dev`. Render local styles with `mbgl-render`; use `xvfb-run -a`
on hosts without an X display. Render-fixture tests write actual and diff PNGs
plus an HTML summary and can be narrowed with `--filter`.

## Architecture guardrails

- A platform Map View owns configuration and viewport state, not rendering.
- Immutable actor messages cross threads; only one thread processes a worker
  instance at a time.
- The tile pyramid comes from viewport tile cover. Dirty state is refreshed
  while unchanged tiles remain reusable.
- Workers parse and lay out source data; backend builders upload prepared
  buckets and emit drawables.
- Shared drawable state owns cross-backend concerns. Backend subclasses own
  resource binding, drawing, per-frame updates, and teardown.
- Offscreen snapshots are callback-driven after drawing; do not force a
  synchronous GPU stall into backend-neutral code.

## Release and backport work

Android and iOS follow semantic versioning but have no fixed cadence or LTS
line. For an older-series fix, request the platform release branch, submit the
fix and changelog update to a branch such as `android-10.x.x`, and account for
release-workflow changes that may also need backporting.

## Final verification

Before shipping a change, verify the exact platform dependency, backend,
style-property support, thread or callback contract, resource URL schemes,
offline-store semantics, and visual render fixtures. When application behavior
or the checked-out source differs from this guide, prefer the manifest, code,
tests, and observed behavior for that concrete build.
