# Architecture and Rendering

Use this reference to trace ownership, threading, tile preparation, drawable
construction, renderer backends, and release boundaries.

## Repository and release boundaries

The C++ core lives in `include/mbgl` and `src/mbgl`. Android reaches it
through JNI. iOS shares an Objective-C++ Darwin layer. Node publishes it as
`@maplibre/maplibre-gl-native`. Part of the Qt binding lives in the separate
`maplibre-native-qt` repository.

Android, iOS, Node, and Qt have independent release streams. No single public
C++ core version identifies all platform releases, so always diagnose against
the platform package and version actually in use.

Android and iOS follow semantic versioning but have no fixed cadence or LTS
line. To backport a fix, request an older-series branch and submit the code
plus changelog update to a branch such as `android-10.x.x`. A release is
attempted after merge; workflow changes needed by that release may require a
separate backport.

## Build-time platform composition

CMake drives platform builds. Bazel is also used for iOS and several core
desktop targets. Normally the backend is selected at build time, and the
platform wrapper and core renderer are compiled together rather than loaded
as independently interchangeable runtime parts. Android's `multiBackend`
flavor is the explicit runtime-selection exception.

## Views, observers, and threads

### Map View responsibilities

A platform Map View owns the viewport and map configuration but has no drawing
capability by itself. Map observers cover style, camera, idle, and render
start/completion lifecycle events. Rendering observers cover frame-level
events, and rendering events can propagate to map observers.

### Actor and render threading

Core work crosses threads as immutable actor messages, including callable
messages delivered through typed mailboxes. A worker pool prepares tiles while
one render loop draws the currently available state. iOS runs this loop on the
UI thread. Android uses a separate `GLSurfaceView` `GLThread` and batches UI
changes for it. Each platform supplies the concurrency primitives used by the
core.

### Android handoff

The Java Map View initializes the device renderer and a JNI-backed native Map
View peer. That peer wraps the generic Map component. A native `MapRenderer`
actor forwards platform rendering events to the core renderer. `Transform`
stores combined global camera and viewport state rather than one operation;
observer notifications allow the renderer to derive rotation, pitch,
projection, resize, and camera transforms.

## Tile worker contracts

Geometry, raster, and elevation workers do not inherit from a common worker
base. Their tile types inherit from `Tile`, and each worker actor accepts its
matching tile type. Its messages may execute on any thread, but only one
thread may process a particular worker instance at a time.

## Tile cover and render tree

For a tile source, `RenderSource::update` computes the tile pyramid selected
by the viewport's tile cover. The render orchestrator creates an ordered tree
of render layers, render sources, and atlas-backed items without drawing it.
Unchanged tiles remain reusable; dirty tile or style state is updated.

## Geometry work coalescing

Work is queued per unique geometry tile. Updates that arrive during parsing or
layout are folded into the newest combined state for the next pass rather than
replaying every intermediate camera state.

Parsing discovers glyph and image dependencies. Dependency arrivals can move
a worker through `NeedsSymbolLayout` or `NeedsParse`. Finalization waits for
parsing and symbol dependencies, then emits geometry, resource references,
and collision metadata.

## Resource preparation

The preparation path loads style resources, TileJSON, tiles, glyphs, and
sprites through the file source and cache. Workers parse and lay out source
data layer by layer. Prepared buckets become Drawables and are uploaded with
backend-specific resource builders.

Descriptions that stop at OpenGL buffers predate this abstraction. OpenGL ES,
Metal, and Vulkan all consume the same higher-level prepared tile state.

## Glyph atlas

Glyphs are 24-pixel signed-distance-field bitmaps packed in a texture atlas
inside a protobuf container. Interior pixels use values `192`–`255`; exterior
pixels use `0`–`191`. The shared atlas lets the GPU resize and rotate glyphs
and render halos.

## Drawable and Builder boundary

Layers supply shader selection, attribute arrays, uniforms or uniform
structs, and geometry to a backend-specific Builder. The Builder emits
Drawables. Shared Drawable state handles cross-backend transitions and tile
tracking. Backend subclasses own upload and binding, direct or indirect
drawing, per-frame updates, and resource teardown.

## Shader registry contract

The modular renderer uses a generic shader representation and a thread-safe
registry keyed by well-known names. The design supports:

- shader source or precompiled references;
- named uniforms or uniform structs;
- calculation shaders; and
- adding or replacing a shader before a layer requests it.

These are architecture requirements. They do not imply that every operation
is exposed through every platform's public API.

## Render passes and offscreen targets

The modular design uses named, ordered passes whose outputs can feed later
passes; empty passes are omitted. Offscreen targets specify size and bit
depth, allow geometry to choose a target, and can be queried or snapshotted.
Snapshot callbacks run after drawing completes, avoiding a forced render-flow
stall on non-OpenGL backends.

## Backend support matrix

| Backend | Stable support |
| --- | --- |
| OpenGL ES 3 | Android, Linux, Windows, Linux/Windows Node, and Qt 3 |
| Vulkan | Android and Linux; a macOS CMake path uses MoltenVK |
| Metal | Default and recommended on iOS; used by macOS Node since Node 6.0 |
| WebGPU | Experimental |

Stable Qt 3 supports OpenGL only.

## Source-build selectors

Android source builds expose `opengl` and `vulkan` Gradle flavors, setting
`MLN_WITH_OPENGL=ON` and `MLN_WITH_VULKAN=ON` respectively. The checkout's
broad-compatibility default is OpenGL. This differs from the standard
published Android 13 artifact, whose default renderer is Vulkan. iOS selects
Metal through CMake or Bazel configuration.
