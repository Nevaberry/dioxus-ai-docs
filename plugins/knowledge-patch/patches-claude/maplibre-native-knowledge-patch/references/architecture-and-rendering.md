# Architecture and rendering

Use this reference for core ownership, threading, tile preparation, drawable
construction, backend support, Linux source builds, and render-fixture tests.

## Repository and product boundaries (`core-architecture`)

The C++ core lives under `include/mbgl` and `src/mbgl`. Android reaches it
through JNI, iOS through the shared Objective-C++ Darwin layer, and Node ships
it as `@maplibre/maplibre-gl-native`. Part of the Qt binding is maintained in
the separate `maplibre-native-qt` repository.

Android, iOS, Node, and Qt release independently. There is no single public
C++ core version that identifies all four platform releases.

CMake covers platform builds. Bazel is also used for iOS and several core
desktop targets. A build selects the renderer backend and compiles it together
with the platform wrapper; they are not independently interchangeable runtime
components.

## Map views, observers, and render handoff

### View and observer responsibilities (`core-architecture`)

A platform Map View owns viewport and map configuration but has no rendering
capability itself. Map observers receive configuration and lifecycle changes,
including style, camera, idle, and render start/completion events. Rendering
observers receive frame-level events, which can propagate to map observers.

### Android-to-core handoff (`render-pipeline`)

The Android Java Map View initializes the device renderer and a JNI-backed
native Map View peer. That peer wraps the generic Map component. The native
`MapRenderer` actor carries platform rendering events to the core renderer.

`Transform` stores the combined global camera and viewport state; it does not
represent one transformation operation. Observer notifications let the
renderer derive rotation, pitch, projection, resize, and camera transforms.

## Threading and tile workers

### Actor and render threading (`core-architecture`)

Core rendering work crosses threads as immutable actor messages, including
callable messages delivered through typed mailboxes. A worker pool prepares
tiles while one render loop draws the currently available state. iOS runs that
loop on the UI thread. Android uses a separate `GLSurfaceView` `GLThread` and
batches UI changes for it. Each platform supplies the core concurrency
primitives.

### Worker type contracts (`core-architecture`)

Geometry, raster, and elevation tile workers do not share a worker base class.
Their matching tile types instead derive from the common `Tile` base. A worker
is an actor accepting its matching tile type. Its messages may execute on any
thread, but only one thread may process a given worker instance at a time.

### Geometry work coalescing (`render-pipeline`)

Work is queued per unique geometry tile. Updates received during parsing or
layout are folded into the newest combined state for the next pass rather than
replaying every intermediate camera state.

Parsing discovers required glyphs and images. Dependency arrivals can move a
worker through `NeedsSymbolLayout` or `NeedsParse`. Finalization waits for both
parsing and symbol dependencies before emitting geometry, resource references,
and collision metadata.

## Tile cover and render-tree construction (`render-pipeline`)

For a tile source, `RenderSource::update` builds the tile pyramid selected by
the viewport's tile cover. The render orchestrator then creates an ordered
render tree from render layers, render sources, and atlas-backed items; it does
not draw that tree itself. Dirty tile or style state is updated while unchanged
tiles remain reusable.

The preparation path loads style resources, TileJSON, tiles, glyphs, and
sprites through the file source and cache, then parses and lays out source data
layer by layer on workers. Prepared buckets become drawables and are uploaded
through backend-specific resource builders. Descriptions that end at OpenGL
buffers predate this abstraction: OpenGL ES, Metal, and Vulkan consume the same
higher-level prepared tile state.

## Glyph atlas (`core-architecture`)

Glyphs are delivered as 24-pixel signed-distance-field bitmaps in a texture
atlas packed in a protobuf container. Pixels inside an outline use values
`192`–`255`; outside pixels use `0`–`191`. The GPU can resize and rotate glyphs
and render halos from the shared atlas.

## Drawables and backend builders (`render-pipeline`)

Layers feed shader selection, attribute arrays, uniforms or uniform structs,
and geometry into a backend-specific Builder, which emits Drawables. Shared
Drawable state owns cross-backend concerns such as transitions and tile
tracking. Backend subclasses own upload and binding, direct or indirect draws,
per-frame updates, and resource teardown.

## Shader and render-pass design (`render-pipeline`)

The modular renderer design replaces opaque per-program handling with a
generic shader representation and a thread-safe registry keyed by well-known
names. Its contract supports:

- shader source or references to precompiled shaders;
- named uniforms or uniform structs;
- calculation shaders; and
- adding or replacing a shader before a layer requests it.

These are architectural requirements, not a promise that every platform's
public API exposes each operation.

The same design calls for named, ordered render passes whose outputs may feed
later passes; empty passes are omitted. Offscreen targets carry size and
bit-depth settings, allow geometry to choose targets, and support querying or
snapshotting. Snapshots use callbacks after drawing completes so a
non-OpenGL backend need not stall the render flow.

## Stable backend matrix (`rendering-platforms`)

| Backend | Stable targets and qualifications |
| --- | --- |
| OpenGL ES 3 | Android, Linux, Windows, Linux/Windows Node, and Qt 3; Qt 3 supports only OpenGL |
| Vulkan | Android and Linux; macOS has a CMake route through MoltenVK |
| Metal | Stable default and recommended backend on iOS; used by macOS Node since Node 6.0 |
| WebGPU | Experimental |

Android source builds expose `opengl` and `vulkan` Gradle flavors, setting
`MLN_WITH_OPENGL=ON` or `MLN_WITH_VULKAN=ON`. The checkout's
broad-compatibility default is OpenGL. iOS selects Metal in its CMake or Bazel
configuration.

## Linux OpenGL development build (`rendering-platforms`)

On Ubuntu 22.04 or later, clone submodules and use the `linux-opengl` preset.
It builds GLFW development tools and can emit static libraries for other C++
projects. The preset defaults to Wayland and therefore needs
`libegl1-mesa-dev`. `libsqlite3-dev` is optional because SQLite can be
vendored.

```bash
git clone --recurse-submodules -j8 https://github.com/maplibre/maplibre-native.git
cd maplibre-native
apt install build-essential clang cmake ccache ninja-build pkg-config
apt install libcurl4-openssl-dev libglfw3-dev libuv1-dev libpng-dev libicu-dev libjpeg-turbo8-dev libwebp-dev xvfb libegl1-mesa-dev
cmake --preset linux-opengl
cmake --build build-linux-opengl --target mbgl-render
```

## Linux image rendering (`rendering-platforms`)

`mbgl-render` accepts a style URL or file and writes a PNG. In a local style,
address an MBTiles database with an absolute
`mbtiles:///path/to/data.mbtiles` source URL.

```bash
./build-linux-opengl/bin/mbgl-render --style style.json --output out.png
```

On a remote or containerized host without an X display, install `xvfb` and
`xauth`, then use a virtual display:

```bash
xvfb-run -a ./build-linux-opengl/bin/mbgl-render --style style.json --output out.png
```

## Linux render-fixture runner (`rendering-platforms`)

The runner compares each fixture's rendered PNG with `expected.png`, leaves
`actual.png` and `diff.png` beside it, and writes an HTML summary next to the
manifest. Run the full manifest or narrow it with `--filter`:

```bash
./build-linux-opengl/mbgl-render-test-runner --manifestPath metrics/linux-clang8-release-style.json
./build-linux-opengl/mbgl-render-test-runner --manifestPath metrics/linux-clang8-release-style.json --filter "render-tests/fill-visibility/visible"
```

## Release and backport policy (`core-architecture`)

Android and iOS use semantic versioning but have no fixed release cadence or
LTS releases. For an older-series backport, request the branch, then submit the
fix and changelog update to a branch named `platform-x.x.x`, for example
`android-10.x.x`. A release is attempted after merge. Release-workflow changes
may themselves need backporting for the older branch to publish successfully.
