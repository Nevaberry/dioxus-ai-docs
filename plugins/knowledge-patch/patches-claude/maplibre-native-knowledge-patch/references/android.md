# Android

Use this reference for Android dependency upgrades, renderer choice, sources,
runtime style behavior, camera features, and offline storage.

## Dependencies and renderer selection

### SDK floor and load failures (`android-12.0.0`)

Android 12.0 raises the minimum supported SDK from 21 to 23. Set application
`minSdk` to at least 23 before upgrading. From 12.1, a failed
`System.loadLibrary` throws an exception instead of letting native library
loading fail silently; preserve and diagnose that exception.

### Vulkan-default artifact (`android-13.0.0`)

Starting in Android 13.0, `org.maplibre.gl:android-sdk` uses Vulkan. Depend on
`org.maplibre.gl:android-sdk-opengl` to remain on OpenGL ES:

```kotlin
implementation("org.maplibre.gl:android-sdk-opengl:13.4.0")
```

Vulkan surface snapshots arrive in 13.3 and Vulkan custom layers in 13.4. A
source build is a distinct choice: its `opengl` and `vulkan` Gradle flavors set
`MLN_WITH_OPENGL=ON` and `MLN_WITH_VULKAN=ON`, and its broad-compatibility
default is the OpenGL flavor.

### Runtime-switchable renderer (`android-13.5.0`)

The `multiBackend` Gradle flavor can switch between OpenGL and Vulkan at
runtime, deferring backend selection beyond the build. Do not confuse it with
the single-backend Maven artifacts or source-build flavors.

## Sources and tile formats

### PMTiles and ambient caching (`android-11.8.0`, `android-13.0.0`)

Android 11.8.0 adds PMTiles-backed map data. Starting in 13.3, PMTiles source
resources also participate in the ambient cache.

### MLT vector tiles (`android-12.0.0`, `android-13.0.0`)

Android 12.1 parses vector-tile sources in MLT format. Android 13.4 extends
that support to MLT tiles encoded with FastPFOR.

### Synchronous GeoJSON migration (`android-12.0.0`, `android-sdk`)

Android 12.3 introduced synchronous GeoJSON source updates for changes that
must be applied before execution continues. Android 13.0 then removed the
short-lived individual synchronous setter methods. Configure a new source and
use its normal update API:

```kotlin
GeoJsonOptions().withSynchronousUpdate(true)
```

### Existing-source synchronous override (`android-13.5.0`)

Use `setOverrideSynchronousUpdate` to change synchronous-update behavior for a
source that already exists. This extends the construction-time
`GeoJsonOptions.withSynchronousUpdate(true)` choice.

### Binary custom vector sources (`android-13.5.0`)

`CustomVectorSource` accepts vector-tile data delivered as binary data.

## Feature state and expressions

### Android feature state (`android-13.0.0`)

Android 13.4 exposes runtime per-feature state.

### Symbol repainting from feature state (`android-13.5.0`)

Changing feature state now repaints symbol paint properties that depend on
that state. Do not add manual symbol invalidation to compensate for the older
behavior.

### String and color expressions (`android-13.5.0`)

The expression engine implements `split` and `join`. String expressions now
operate on Unicode text and handle non-ASCII input correctly. The core color
parser also accepts HSL colors carrying an alpha component.

## Camera, snapshots, and location indicators

### Snapshot attribution and padding (`android-12.0.0`)

Android 12.0.1 lets snapshots hide attribution. Android 12.1 adds padding to
`MapSnapshotter`.

### Frustum offset (`android-12.0.0`)

Android 12.2 can set a frustum offset so the renderer omits screen edges. This
is a projection/rendering control, not ordinary view padding.

### Camera roll (`android-13.0.0`)

Android 13.0 adds camera roll. Keep it distinct from bearing and pitch when
serializing or restoring camera state.

### Location-indicator bearing placement (`android-13.5.0`)

Android can move the symbol location indicator's bearing down the image stack.
Use the option when the bearing artwork must render beneath other location
indicator images.

## Layer rendering behavior

### Color relief and hillshade (`android-13.0.0`)

Android 13.0 adds Color-Relief Layers and updates the hillshade algorithms.
Android 13.0.1 fixes color-relief and hillshade layers becoming invisible when
placed above fill layers on Vulkan, the default Android 13 backend.

### Pitched-map icon offsets (`android-13.0.0`)

Android 13.1 disables icon scaling when offsets are used on pitched maps.
Visually recheck styles that combine pitch and icon offsets.

### Rounded fill extrusions (`android-13.0.0`)

Android 13.4 adds a fill-extrusion style property for rounded corners on
extruded buildings.

## Annotations

### Legacy core annotations are deprecated (`android-sdk`)

The core `Annotation` hierarchy has been deprecated since 7.0.0. This includes
`Marker`, `Polyline`, `Polygon`, `MarkerOptions`, and `IconFactory`. Use the
separate MapLibre Annotation Plugin for new annotation and overlay work.

## Offline regions and cache

### Explicit regions (`android-sdk`)

`OfflineManager.getInstance(context)` manages persistent region definitions
with opaque application metadata. Operations are asynchronous and callbacks
arrive on the main thread. Attach a region observer for progress and errors.

`setDownloadState` pauses or resumes fetching without making downloaded
resources unavailable. `invalidate` revalidates resources, `updateMetadata`
replaces the opaque metadata, and `delete` makes region resources eligible for
eviction.

### Ambient cache (`android-sdk`)

The ambient cache stores resources encountered during normal rendering and is
separate from explicit offline regions:

- `setMaximumAmbientCacheSize` sets the byte limit.
- `invalidateAmbientCache` revalidates cached resources.
- `clearAmbientCache` evicts ambient data but retains resources required by
  offline regions.
- `putResourceWithUrl` prewarms a resource with response bytes and HTTP cache
  metadata.

### Database maintenance (`android-sdk`)

`packDatabase` compacts the offline database,
`runPackDatabaseAutomatically` controls automatic compaction, and
`resetDatabase` deletes and reinitializes the store. All are asynchronous
storage operations; never put them on a frame-rendering path.
