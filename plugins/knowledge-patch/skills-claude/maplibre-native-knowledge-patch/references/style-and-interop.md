# Style and interoperability

Use this reference when sharing style JSON or assets with GL JS, checking
Native style-spec support, building expressions, or mutating a loaded style.

## Compatibility is feature-specific (`native-style`)

A valid version 8 style that renders in GL JS is not necessarily
feature-equivalent on Android or iOS. For every root property, source option,
layer property, and expression, check the separate Native Android and Native
iOS support-table entry, its minimum version, and any linked unsupported issue.

Protocol support also arrives through Native releases. A browser-side protocol
registration API does not imply that a Native SDK can resolve the same scheme.

## Root and camera differences (`native-style`)

Android and iOS do not support:

- root `centerAltitude`;
- root `roll`; or
- root `state` and global-state functionality.

Native pitch is limited to 0–60 degrees, narrower than the GL JS ranges. This
root-style limitation is separate from newer platform camera-roll APIs.

## Fonts and glyphs (`native-style`)

Native supports a `glyphs` URL. Omitting `glyphs` to use local fonts is not
supported on Android or iOS. Conversely, basic root `font-faces` support begins
in Android 11.13.0 and iOS 6.18.0 even though GL JS does not support that root
property.

## Source coverage on iOS (`native-style`)

The iOS SDK maps vector, raster, raster-DEM, GeoJSON, and image sources to
typed `MLN*Source` classes. Canvas and video sources are unsupported on iOS.

## Assertions and coercions (`native-style`)

Expression results include the generic `value` type and concrete types such as
string, number, color, object, array, collator, and formatted text. Because
`get` returns `value`, assert a concrete type when a consuming expression
requires it:

```json
["string", ["get", "feature_property"]]
```

An assertion fails at evaluation time if the value has the wrong type. Names
beginning with `to-` are coercions rather than assertions and may include a
fallback:

```json
["to-number", ["get", "feature_property"], 0]
```

Choose an assertion when mismatched source data is an error. Choose coercion
when conversion and fallback are intended behavior.

## Native expression execution (`native-style`)

Android and iOS expose platform-specific builders, but the resulting
expression is parsed and evaluated by the shared C++ core. An Android layer
property can be assembled from nested builders:

```java
fillLayer.setProperties(
    fillColor(interpolate(
        exponential(0.5f), zoom(),
        stop(1.0f, color(Color.RED)),
        stop(5.0f, color(Color.BLUE)),
        stop(10.0f, color(Color.GREEN))
    ))
);
```

Builder syntax is platform-specific even when evaluation semantics are shared.

## Mutating a loaded style (`native-style`)

Android mutates a loaded `org.maplibre.android.maps.Style` proxy through typed
sources, layers, images, light, transitions, and indexed or relative layer
placement. iOS exposes corresponding operations through `MLNStyle`,
`MLNSource`, and `MLNStyleLayer`.

Wait until the style has loaded before mutating it. Use the platform's typed
property names; do not infer them directly from JSON keys.

## What actually crosses the Native/GL JS boundary (`native-js-interop`)

The documented architecture shares shaders, the style specification, and
render-test fixtures. It does not share the Map, Style, Layer, Glyph,
TileWorker, or rendering implementations. Compatible style JSON and assets can
cross the boundary, but fixture parity does not imply runtime API parity or
complete feature parity.

## Porting applications (`native-js-interop`)

There is no official one-to-one GL JS-to-Native method map. Port shareable
styles and assets, then implement map lifecycle, resources, gestures, offline
storage, annotations, and custom rendering against the target Native SDK.
Avoid translating browser calls mechanically.
