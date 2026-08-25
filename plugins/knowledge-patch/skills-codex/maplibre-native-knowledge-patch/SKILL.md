---
name: maplibre-native-knowledge-patch
description: MapLibre Native
version: null
license: MIT
metadata:
  author: Nevaberry
---


# MapLibre Native Knowledge Patch

Use this skill for MapLibre Native core, Android, iOS and Darwin, Node,
Qt, desktop rendering, native style behavior, and cross-platform migration
work. Start by identifying the target SDK or binding and its pinned release;
Android, iOS, Node, and Qt advance independently.

Trust the project's manifests, source, and tests when they differ from this
guidance. Do not infer Native API parity from a style that also renders in
MapLibre GL JS.

## Reference index

| Reference | Topics |
| --- | --- |
| [Android](references/android.md) | artifacts, renderer choice, sources, expressions, snapshots, feature state, annotations, and offline storage |
| [Architecture and rendering](references/architecture-and-rendering.md) | repository boundaries, actors, tiles, drawables, shaders, render passes, and backend support |
| [iOS and Darwin](references/ios-and-darwin.md) | distribution, style APIs, sources, custom layers, camera, snapshots, networking, observers, and offline packs |
| [Linux build and testing](references/linux-build-and-testing.md) | OpenGL development builds, headless image rendering, and render fixtures |
| [Node and Qt](references/node-and-qt.md) | Node runtimes, render and request APIs, logging, Qt targets, QML, deployment, and Android ABIs |
| [Styles and interoperability](references/styles-and-interoperability.md) | style support checks, fonts, expressions, runtime mutation, and GL JS boundaries |

## Resolve the platform first

1. Read the dependency manifest and identify Android, iOS/Darwin, Node, or
   Qt plus its exact version.
2. Check the renderer backend and whether the dependency is a published
   artifact or a source build.
3. Check every style feature against the target Native platform; style JSON
   validity alone is insufficient.
4. For rendering bugs, locate the boundary involved: resource loading, tile
   preparation, drawable construction, backend upload, or frame execution.
5. For offline bugs, distinguish explicit regions from the ambient cache.

## Breaking changes and migration gates

### Android renderer artifacts

The standard Android 13 artifact uses Vulkan. Applications that must remain
on OpenGL ES should use `org.maplibre.gl:android-sdk-opengl`. Vulkan surface
snapshots arrive in 13.3 and Vulkan custom layers in 13.4, so audit either
feature before moving an older application to the default artifact.

Android 13.5 adds a `multiBackend` Gradle flavor that can select OpenGL or
Vulkan at runtime. This is a deliberate exception to the usual build-time
backend selection rule.

### Android minimum SDK

Android 12 raises `minSdk` from 21 to 23. Update the application manifest and
dependency assumptions before upgrading.

### Node runtime and renderer

Node 6.1 requires Node.js 18 or newer and removes the legacy Linux and Windows
renderer in favor of the drawable renderer. The stable Node 6.4.1 line
supports Node.js 20, 22, and 24; do not assume Node.js 26 support from a
stable package.

### Synchronous Android GeoJSON updates

Android 13 removes the short-lived individual synchronous setters. Configure
new sources with:

```kotlin
GeoJsonOptions().withSynchronousUpdate(true)
```

Then use the normal GeoJSON update API. Android 13.5 can change this behavior
on an existing source with `setOverrideSynchronousUpdate`.

### Native style compatibility

A version 8 style that works elsewhere can still use unsupported Native root
properties, sources, layer properties, or expressions. Check the separate
Android and iOS support entries and their minimum versions feature by feature.
Native pitch is limited to 0–60 degrees, and root `centerAltitude`, `roll`,
and global state are unsupported on both platforms.

## Renderer and threading quick reference

- A platform Map View owns viewport and configuration state but does not draw
  by itself.
- Map observers report configuration and lifecycle changes. Rendering
  observers report frame events, which can propagate to map observers.
- Immutable actor messages cross threads. A worker pool prepares tiles while
  one render loop draws available state.
- iOS renders on the UI thread. Android uses a `GLSurfaceView` render thread
  and batches UI changes for it.
- Each tile worker processes only one message at a time, although successive
  messages can run on different threads.
- `RenderSource::update` computes the viewport tile cover. The render
  orchestrator builds an ordered tree but does not draw it.
- Tile parsing coalesces intermediate updates, discovers glyph and image
  dependencies, performs symbol layout, and emits geometry and collision
  metadata only when dependencies are ready.
- Prepared buckets become backend resources through Builders. Builders emit
  Drawables; backend subclasses own upload, binding, drawing, frame updates,
  and teardown.

## Backend selection

| Backend | Stable targets and constraints |
| --- | --- |
| OpenGL ES 3 | Android, Linux, Windows, Linux/Windows Node, and Qt 3; Qt 3 supports only OpenGL |
| Vulkan | Android and Linux; macOS source builds can route through MoltenVK |
| Metal | Default and recommended on iOS; used by macOS Node rendering |
| WebGPU | Experimental |

Android source builds provide `opengl` and `vulkan` Gradle flavors, while the
checkout's broad-compatibility flavor is OpenGL. Do not confuse that source
build default with the standard published Android 13 artifact, which uses
Vulkan. iOS selects Metal in its CMake or Bazel configuration.

## Sources, tiles, and offline data

### PMTiles and MLT

PMTiles is available across the Android, iOS, and Node lines described in the
platform references. iOS uses `pmtiles://`; its PMTiles metadata is treated
as XYZ from 6.14. Android PMTiles can participate in ambient caching from
13.3.

Android 12.1 and iOS 6.20 parse MLT vector tiles. Android 13.4 additionally
supports FastPFOR-encoded MLT tiles, and Android 13.5 adds binary
`CustomVectorSource` data delivery.

### Explicit regions versus ambient cache

Android explicit offline regions retain opaque application metadata and have
asynchronous lifecycle operations. Pausing a region stops fetching without
making downloaded resources unavailable.

The ambient cache is populated by normal rendering and has separate size,
revalidation, eviction, and prewarming controls. Clearing it retains resources
still required by explicit regions.

## Expressions and style mutation

`get` returns a generic value. Add a type assertion when a consuming
expression needs a concrete type:

```json
["string", ["get", "feature_property"]]
```

`to-*` operators are coercions and can provide fallbacks:

```json
["to-number", ["get", "feature_property"], 0]
```

Android and iOS builders feed the same core expression evaluator. Android
13.5 adds `split` and `join`, Unicode-aware string handling, and alpha-bearing
HSL parsing.

Mutate a style only after it has loaded. Android exposes typed operations on
`Style`; iOS uses `MLNStyle`, `MLNSource`, and `MLNStyleLayer`. Native typed
property names often differ from their style JSON names.

## Android feature and rendering checks

- Camera roll and Color-Relief layers begin in Android 13. Recheck
  Color-Relief and hillshade stacking on early Vulkan 13 releases.
- Android 13.1 changes pitched-map icon offsets by disabling icon scaling
  when offsets are active; visually regress affected styles.
- Android 13.4 adds feature state and rounded fill extrusions.
- Android 13.5 repaints symbol paint properties when their feature state
  changes and adds location-indicator bearing placement lower in the image
  stack.
- Prefer the separate Annotation Plugin for new markers, polylines, and
  polygons; the core annotation hierarchy is deprecated.

## iOS and Darwin checks

- Import the Swift package as `MapLibre` from the distribution repository;
  report issues in the main source repository.
- iOS style attributes use Foundation expressions and predicates, Cocoa
  values, and platform-specific property names.
- Canvas and video sources are unsupported on iOS; vector, raster,
  raster-DEM, GeoJSON, and image sources have typed classes.
- Darwin plugin layers are Metal-only. Subclass `MLNPluginLayer`, register the
  class, and declare capabilities before the style parser sees the layer.
- When importing an offline database, call `reloadPacks` before reading
  `MLNOfflineStorage.sharedOfflineStorage.packs`.
- Style JSON loading in 6.22 cancels a pending style request.
- Custom layers can use `nearClippedProjectionMatrix` from 6.28.

## Node and Qt checks

Node `Map.render` returns an asynchronous raw four-channel buffer. Calling
`release()` inside its callback is safe, but permanently disables later
renders. A constructor `request` hook must handle every resource and custom
URL scheme; successful responses contain uncompressed bytes. Subscribe to the
module's `message` event for native style and resource diagnostics.

Qt 3 uses the `QMapLibre` namespace and separate Core, Location, and Widgets
components. QML applications import `MapLibre 3.0` and must deploy both the
geoservices and QML plugin trees. For Android multi-ABI builds, resolve the
ABI-specific package beneath `QMapLibre_Android_DIR`.

## Linux rendering workflow

Use the `linux-opengl` preset on Ubuntu 22.04 or later after cloning
submodules. The preset defaults to Wayland and requires EGL development
headers. Run `mbgl-render` under `xvfb-run -a` on hosts without an X display.

Render fixtures compare output with `expected.png`, retain `actual.png` and
`diff.png`, and produce an HTML summary. Use the fixture runner's `--filter`
option to isolate one rendering case.

## Investigation discipline

- Reproduce against the exact platform release and renderer backend.
- Reduce style failures to one root property, source, layer, or expression.
- Compare OpenGL, Vulkan, or Metal only when both configurations are actually
  supported by the target artifact.
- Observe resource requests and renderer events before assuming a tile or
  shader failure.
- For visual regressions, save backend, viewport, style, expected image,
  actual image, and diff image together.
- Treat application integration as platform-specific even when styles,
  shaders, assets, and fixtures are shared.
