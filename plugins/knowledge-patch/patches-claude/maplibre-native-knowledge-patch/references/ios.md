# iOS and Darwin

Use this reference for iOS/macOS distribution, `MLN*` APIs, sources,
networking, camera and snapshot behavior, offline packs, and Metal extensions.

## Distribution and module identity

### Swift Package repository (`ios-sdk`)

The Swift package comes from the distribution-only repository below, while
issues belong in the main `maplibre-native` repository. Import its module as
`MapLibre`.

```text
https://github.com/maplibre/maplibre-gl-native-distribution
```

### Static XCFramework (`ios-6.20.0`)

GitHub releases include a static XCFramework starting in 6.21.1. Choose the
static distribution intentionally when resolving linkage and embedding.

## Sources and style loading

### PMTiles and asset ranges (`ios-6.10.0`)

iOS 6.10 adds PMTiles sources through `pmtiles://`. From 6.14, PMTiles
metadata is always interpreted with the XYZ tile scheme. Version 6.14 also
adds byte-range request support to `AssetFileSource`.

### MLT vector tiles (`ios-6.20.0`)

iOS 6.20 parses vector-tile sources in MLT format.

### Style JSON initialization and cancellation (`ios-6.10.0`, `ios-6.20.0`)

Starting in 6.13, `MLNMapView` can be initialized with style JSON. In 6.22,
loading style JSON cancels any pending style request, so an explicit JSON load
supersedes an in-flight request rather than racing it.

### Synchronous GeoJSON updates (`ios-6.20.0`)

iOS 6.22 supports synchronous GeoJSON source updates for changes that must be
applied before execution continues. Use this selectively; normal source
updates need not block their caller.

### Complete vector-tile feature state (`ios-6.15.0`)

The 6.15 line completely applies feature-state changes in `GeometryTile` and
`SourceFeatureState` for vector-tile layers. Code using dynamic feature state
does not need to compensate for the earlier partial-update behavior.

### Dynamic texture atlas (`ios-6.10.0`)

iOS 6.14 introduces a dynamic texture atlas. When adopting it, render existing
styles and verify that their glyphs load correctly.

## Typed style APIs

### Cocoa vocabulary (`ios-sdk`)

The Cocoa API renames several style-spec concepts:

| Style concept | Cocoa term |
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

### Foundation expressions and predicates (`ios-sdk`)

Layout and paint attributes use `NSExpression` values backed by Cocoa types
such as `UIColor`, `CGVector`, and `UIEdgeInsets`; the older style-function API
is unsupported. Set `MLNVectorStyleLayer.predicate` with `NSPredicate`. Common
translations include `key != nil`, `key IN {…}`, `AND`, `OR`, and `NOT`.

### Non-obvious typed names (`ios-sdk`)

Do not derive typed property names mechanically from style JSON:

| Style property | Typed API |
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

### Coordinate ordering (`ios-sdk`)

`MLNCoordinateQuad` orders image-source corners counterclockwise, the opposite
of the style specification's clockwise order. `UIEdgeInsets(top:left:bottom:right:)`
is likewise counterclockwise while style-spec padding is clockwise.

## Custom layers and Metal interoperability

### Swift layers, repainting, and drawable v3 (`ios-6.10.0`)

iOS 6.11 allows custom style layers to be defined from Swift and provides a
method to trigger repainting. Version 6.12 introduces custom drawable layer
v3. Keep the layer contract matched to the API generation in use.

### Metal plugin layer contract (`ios-sdk`)

Darwin plugin layers are Metal-only and are neither annotations nor GL JS
custom layers. Subclass `MLNPluginLayer`, register the class with the map view,
and implement the class method `layerCapabilities` so the style parser can
instantiate the declared type. Capabilities declare the layer ID, required
render passes, and typed paint properties with defaults. Put initialization
values in the style layer's `properties` object and expression-capable values
in `paint`.

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

### Headless textures and custom projection (`ios-6.25.0`)

Version 6.26.1 exposes the headless backend's Metal texture for direct Metal
interoperability. Version 6.28 adds `nearClippedProjectionMatrix` to
`MLNCustomStyleLayer`, so custom layers can use the near-clipped projection
matrix.

## Observers, diagnostics, and attribution

### Map and source observer hooks (`ios-6.10.0`)

iOS and macOS observer hooks arrive in 6.12. Version 6.13 adds the previously
missing `sourceDidChange` event.

### Layer source notifications (`ios-6.25.0`)

In 6.28, layer observers are notified when a layer's source layer or source ID
changes.

### Action journal and renderer HUD (`ios-6.15.0`)

iOS 6.15 adds action-journal support and an adoption example. It also includes
a rendering-statistics view for inspecting renderer activity in an app.

### Source attribution (`ios-6.15.0`, `ios-6.20.0`)

`MLNSource.attributionHtmlString` exposes source HTML for custom attribution
interfaces. Starting in 6.21, iOS can hide attribution.

### Public scale bar (`ios-6.25.0`)

Version 6.25 exports `MLNScaleBar`, allowing application code to refer to the
SDK scale-bar type directly.

## Networking

### Expanded delegate lifecycle (`ios-6.20.0`)

iOS 6.20 adds network delegate methods and expands the lifecycle available to
delegate implementations.

### Response callback (`ios-6.25.0`)

In 6.28, `MLNNetworkConfiguration` forwards `didReceiveResponse` to its
delegate. Implementations can rely on receiving the response callback.

## Camera and snapshots

### Bounds and north snapping (`ios-6.10.0`, `ios-6.20.0`)

The map camera can be constrained to maximum bounds. Starting in iOS 6.20, the
rotate gesture threshold that snaps the map back to north is configurable.

### Frustum offset and roll (`ios-6.20.0`)

iOS 6.21 supports a frustum offset for omitting screen edges. Version 6.23 adds
basic camera-roll support; keep roll separate from bearing and pitch.

### Snapshot annotations (`ios-6.20.0`)

iOS 6.21 can add extra annotations to snapshotter output.

### Color relief and hillshade (`ios-6.20.0`)

iOS 6.24 adds Color-Relief Layers and updates the hillshade algorithms.

## Offline packs

### Imported databases (`ios-sdk`)

`MLNOfflineStorage.sharedOfflineStorage.packs` is the canonical in-memory pack
collection. After importing an offline database by file or URL, call
`reloadPacks` before using `packs` so it reflects merged regions.

### Region identifiers (`ios-6.25.0`)

Starting in 6.25, `MLNOfflinePack` exposes the underlying offline region
identifier on Darwin and iOS, allowing applications to identify packs by
region ID.
