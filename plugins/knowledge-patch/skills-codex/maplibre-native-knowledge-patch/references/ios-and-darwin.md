# iOS and Darwin SDK

Use this reference for iOS and Darwin distribution, map configuration, style
APIs, sources, custom rendering, networking, snapshots, observers, and
offline packs.

## Distribution and integration

### Swift package

The Swift package comes from the distribution-only repository below and is
imported as `MapLibre`. File issues in the main `maplibre-native` repository.

```text
https://github.com/maplibre/maplibre-gl-native-distribution
```

### Static XCFramework

GitHub releases include a static XCFramework starting with iOS 6.21.1, part
of the `ios-6.20.0` compatibility line.

## Map initialization and camera

### Style JSON and request precedence

`MLNMapView` can be initialized with style JSON from iOS 6.13
(`ios-6.10.0`). From 6.22, loading style JSON cancels any pending style
request, so the JSON load supersedes the in-flight request.

### Bounds, north snap, frustum, and roll

- The camera can be constrained to maximum bounds.
- iOS 6.20 makes the rotate gesture's north-snap threshold configurable.
- iOS 6.21 supports a frustum offset that lets the renderer omit screen
  edges.
- iOS 6.23 adds basic camera-roll support.

## Sources and source data

### PMTiles

iOS 6.10 adds PMTiles through the `pmtiles://` URL scheme. From 6.14,
PMTiles metadata is always interpreted with the XYZ tile scheme.

### MLT and synchronous GeoJSON

iOS 6.20 parses vector-tile sources in MLT format. iOS 6.22 provides
synchronous GeoJSON source updates when a change must be applied before
execution continues.

### Typed source coverage

The iOS SDK maps vector, raster, raster-DEM, GeoJSON, and image sources to
typed `MLN*Source` classes. Canvas and video sources are unsupported.

### Source attribution HTML

`MLNSource.attributionHtmlString` is exposed in the `ios-6.15.0` line so a
custom attribution interface can retrieve source attribution as HTML.

### Asset range requests

`AssetFileSource` supports range requests from iOS 6.14.

## Runtime style APIs

### Cocoa vocabulary

The Cocoa API renames several style-spec concepts:

| Style concept | Cocoa API term |
| --- | --- |
| bounds | coordinate bounds |
| filter | predicate |
| function type | interpolation mode |
| id | identifier |
| image | style image |
| layer | style layer |
| property | attribute |
| SDF icon | template image |
| source | content source |

### Foundation expressions and predicates

Layout and paint attributes take `NSExpression` values backed by Cocoa types
such as `UIColor`, `CGVector`, and `UIEdgeInsets`; the older style-function
API is unsupported. Set `MLNVectorStyleLayer.predicate` with `NSPredicate`,
using forms such as `key != nil`, `key IN {…}`, `AND`, `OR`, and `NOT`.

### Typed property names

Do not mechanically translate JSON property names. Important mappings
include:

| Style property | Typed API property |
| --- | --- |
| `line-dasharray` | `lineDashPattern` |
| `raster-hue-rotate` | `rasterHueRotation` |
| `icon-image` | `iconImageName` |
| `icon-size` | `iconScale` |
| `text-field` | `text` |
| `text-font` | `textFontNames` |
| `text-size` | `textFontSize` |

Formatted symbol text uses `.fontNamesAttribute`, `.fontScaleAttribute`, and
`.fontColorAttribute`.

### Coordinate ordering

`MLNCoordinateQuad` orders image-source corners counterclockwise, opposite
the style specification's clockwise order. `UIEdgeInsets(top:left:bottom:right:)`
is also counterclockwise while style-spec padding is clockwise.

### Loaded-style mutation

Wait for style loading before mutating `MLNStyle`, `MLNSource`, or
`MLNStyleLayer`. Use the platform's typed properties rather than inferred JSON
names.

## Custom layers and renderer interoperation

### Swift custom layers and drawable v3

iOS 6.11 supports defining custom style layers from Swift and exposes a
method to trigger repaint. iOS 6.12 adds custom drawable layer v3.

### Metal plugin layers

Darwin plugin layers are Metal-only and are not ordinary annotations or
browser custom layers. Subclass `MLNPluginLayer`, register the class with the
map view, and implement `+layerCapabilities` so the style parser can
instantiate it. Capabilities declare the layer ID, render-pass needs, and
typed paint properties with defaults. Put initialization values in the style
layer's `properties` object and expression-capable values in `paint`.

```objc
+ (MLNPluginLayerCapabilities *)layerCapabilities {
    MLNPluginLayerCapabilities *caps = [MLNPluginLayerCapabilities new];
    caps.layerID = @"plugin-layer-metal-rendering";
    caps.requiresPass3D = YES;
    caps.layerProperties = @[
        [MLNPluginLayerProperty propertyWithName:@"scale"
                                    propertyType:MLNPluginLayerPropertyTypeSingleFloat
                                    defaultValue:@1.0]
    ];
    return caps;
}
```

### Texture and projection access

The dynamic texture atlas introduced in iOS 6.14 can affect existing glyph
loading; verify glyph rendering after adoption. Version 6.26.1 exposes the
headless backend's Metal texture for direct Metal interoperation. Version
6.28 adds `nearClippedProjectionMatrix` to `MLNCustomStyleLayer`.

## Observers and networking

### Map and source observer events

iOS and macOS observer hooks arrive in 6.12, with the missing
`sourceDidChange` event added in 6.13. In 6.28, layer observers are notified
when a layer's source layer or source ID changes (`ios-6.25.0`).

### Network delegate lifecycle

iOS 6.20 expands the network delegate lifecycle with additional methods. In
6.28, `MLNNetworkConfiguration` also forwards `didReceiveResponse` to its
delegate, so implementations can rely on that response callback.

## Snapshots, attribution, and diagnostics

### Snapshot output

iOS 6.21 allows attribution to be hidden. The same release can add extra
annotations to snapshotter output.

### Rendering statistics and action journal

The `ios-6.15.0` line adds an action journal with an adoption example and a
rendering-statistics view for inspecting renderer activity in an application.

### Public scale bar

iOS 6.25 exports `MLNScaleBar`, allowing application code to reference the
SDK scale-bar type directly.

## Feature state and layer rendering

### Complete vector-tile feature state

In the iOS 6.15 line, feature-state changes in `GeometryTile` and
`SourceFeatureState` are applied completely to vector-tile layers. Remove
workarounds for the earlier incomplete-update behavior.

### Color-Relief layers

iOS 6.24 adds Color-Relief layers and updates the hillshade algorithms.

## Offline packs and imported databases

### Region identifiers

Starting with iOS 6.25, `MLNOfflinePack` exposes its underlying region ID on
Darwin and iOS, so applications can identify packs directly.

### Import refresh

`MLNOfflineStorage.sharedOfflineStorage.packs` is the canonical in-memory pack
collection. After importing another offline database from a file or URL, call
`reloadPacks` before reading the collection so it reflects merged regions.
