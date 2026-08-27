# Styles, Sources, and Interoperability

Use this reference when porting a style or application between Native
platforms or between MapLibre GL JS and Native.

## Check compatibility feature by feature

A valid version 8 style that works in MapLibre GL JS is not necessarily
feature-equivalent on Android or iOS. For each root property, source option,
layer property, and expression, inspect the separate Native Android and Native
iOS support entries, minimum versions, and linked unsupported issues.

Protocol support also arrives through Native releases. Do not assume the
browser protocol-registration API exists on a Native target.

## Root and camera differences

Both Native Android and Native iOS lack `centerAltitude`, root `roll`, and
root `state` or global-state functionality. Native pitch is limited to 0–60
degrees rather than the wider browser ranges.

## Font handling

Native supports a `glyphs` URL. Omitting it to use local fonts is unsupported
on Android and iOS. Conversely, basic root `font-faces` support begins in
Android 11.13.0 and iOS 6.18.0 even though MapLibre GL JS does not support the
property.

## iOS source classes

iOS represents vector, raster, raster-DEM, GeoJSON, and image sources with
typed `MLN*Source` classes. Canvas and video sources are unsupported.

## Expression assertions and coercions

Expression results include generic `value` plus concrete string, number,
color, object, array, collator, and formatted-text types. Because `get`
returns `value`, assert the required concrete type when the consuming
expression needs one. A mismatched assertion fails during evaluation.

```json
["string", ["get", "feature_property"]]
```

Operators beginning with `to-` are coercions, not assertions, and can provide
a fallback:

```json
["to-number", ["get", "feature_property"], 0]
```

## Native expression execution

Android and iOS provide platform-specific expression builders, but the shared
C++ core parses and evaluates the resulting expression. Android can construct
a nested expression through typed builders:

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

## Runtime style mutation

Wait until a style is loaded before mutation.

- Android mutates `org.maplibre.android.maps.Style` with typed sources,
  layers, images, light, transitions, and indexed or relative layer placement.
- iOS performs corresponding operations through `MLNStyle`, `MLNSource`, and
  `MLNStyleLayer`.

Check each platform's typed property names. Do not derive them mechanically
from style JSON spelling.

## What is shared with MapLibre GL JS

The documented architecture shares shaders, the style specification, and
render-test fixtures between MapLibre GL JS and Native. It does not share the
runtime implementations of Map, Style, Layer, Glyph, TileWorker, or rendering.

Compatible style JSON and assets can cross the boundary. Visual fixture
parity does not establish public API parity or complete feature parity.

## Porting applications

There is no official one-to-one MapLibre GL JS-to-Native method mapping.
Port shareable styles and assets, then implement application integration with
the target Native SDK. Do not mechanically translate browser calls into
Android, iOS, Node, or Qt calls.
