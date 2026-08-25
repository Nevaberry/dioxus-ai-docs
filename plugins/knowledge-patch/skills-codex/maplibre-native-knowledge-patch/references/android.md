# Android SDK

Use this reference for Android dependency upgrades, renderer selection,
sources, style behavior, snapshots, and offline storage.

## Upgrade and dependency gates

### Minimum SDK and native loading

The `android-12.0.0` line raises the minimum Android SDK from 21 to 23. Set
the application's `minSdk` to at least 23 before upgrading.

From 12.1, a failed `System.loadLibrary` call throws instead of leaving the
native library silently unloaded. Handle the exception and diagnose package,
ABI, or loader problems at startup.

### Published renderer artifacts

The standard `org.maplibre.gl:android-sdk` artifact uses Vulkan beginning in
the `android-13.0.0` line. Stay on OpenGL ES with the explicit artifact:

```kotlin
implementation("org.maplibre.gl:android-sdk-opengl:13.4.0")
```

Vulkan surface snapshots arrive in 13.3 and Vulkan custom layers in 13.4.
Audit those capabilities when migrating from OpenGL ES.

Android 13.5 adds a `multiBackend` Gradle flavor that can switch between
OpenGL and Vulkan at runtime (`android-13.5.0`). It is distinct from the
single-backend `opengl` and `vulkan` source-build flavors.

## Camera, symbols, and snapshots

### Frustum offset and camera roll

Android 12.2 can set a frustum offset so the renderer omits screen edges.
Android 13.0 adds camera roll.

### Snapshotter controls

Android 12.0.1 allows snapshots to hide attribution, and 12.1 adds padding to
`MapSnapshotter`.

### Pitched-map icon offsets

Android 13.1 disables icon scaling when icon offsets are used on pitched maps.
Visually regress styles that combine pitch and icon offsets because placement
can differ after upgrade.

### Location-indicator bearing placement

Android 13.5 can move the symbol location indicator bearing down the image
stack, allowing the bearing element's relative placement to be configured.

## Sources and tile formats

### PMTiles

PMTiles-backed map data is supported from Android 11.8
(`android-11.8.0`). From Android 13.3, PMTiles resources also participate in
the ambient cache.

### MLT vector tiles

Android 12.1 parses vector-tile sources in MLT format. Android 13.4 also
supports MLT tiles encoded with FastPFOR.

### Synchronous GeoJSON updates

Android 12.3 introduced synchronous GeoJSON source updates for callers that
must observe a source change before execution continues. Android 13.0 then
replaced the short-lived individual synchronous setter methods: construct the
source with synchronous updates enabled and use the ordinary update methods.

```kotlin
GeoJsonOptions().withSynchronousUpdate(true)
```

Android 13.5 adds `setOverrideSynchronousUpdate` for sources that already
exist, so construction-time `GeoJsonOptions` is no longer the only selection
point.

### Binary custom vector sources

Android 13.5 exposes core `CustomVectorSource` support for delivering vector
tile content as binary data.

## Layers, expressions, and feature state

### Color-Relief and hillshade

Android 13.0 adds Color-Relief layers and updates the hillshade algorithms.
Version 13.0.1 fixes Color-Relief and hillshade layers becoming invisible
above fill layers on Vulkan, the default backend for this release line.

### Feature state

Android 13.4 adds runtime per-feature state. Android 13.5 also repaints symbol
paint properties when the feature state they depend on changes; applications
no longer need a separate style change to force that symbol repaint.

### Rounded fill extrusions

Android 13.4 adds a fill-extrusion property for rounded building corners.

### Expression additions

Android 13.5 adds `split` and `join`. String expression processing is
Unicode-aware, including non-ASCII text, and the core color parser accepts
HSL colors with an alpha component.

## Annotation migration

The core `Annotation` hierarchy has been deprecated since 7.0.0, including
`Marker`, `Polyline`, `Polygon`, `MarkerOptions`, and `IconFactory`. Use the
separate MapLibre Annotation Plugin for new overlay work.

## Offline regions and ambient cache

### Explicit regions

`OfflineManager.getInstance(context)` manages persistent region definitions
and opaque application metadata. Operations are asynchronous and callbacks
arrive on the main thread. Attach a region observer for progress and errors.

- `setDownloadState` pauses or resumes fetching; already downloaded resources
  remain usable.
- `invalidate` revalidates the region's resources.
- `updateMetadata` replaces the opaque application metadata.
- `delete` removes the region definition and makes its resources eligible for
  eviction.

### Ambient cache

The ambient cache contains resources encountered during normal rendering and
is separate from explicit regions.

- `setMaximumAmbientCacheSize` sets its byte limit.
- `invalidateAmbientCache` revalidates cached resources.
- `clearAmbientCache` evicts ambient data but retains resources required by
  offline regions.
- `putResourceWithUrl` prewarms it with response bytes and HTTP cache
  metadata.

### Database maintenance

`packDatabase` compacts the offline database,
`runPackDatabaseAutomatically` controls automatic compaction, and
`resetDatabase` deletes and reinitializes the store. These asynchronous
storage operations should not run during frame rendering.
