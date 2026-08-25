# Camera, globe, and location

## Camera orientation and rotation (since 5.0.0)

The camera supports pitch beyond 90 degrees and a roll angle. Drag rotation pivots around the screen center. Code that clamps orientation to older limits or assumes a different pivot can remove those workarounds.

## Terrain elevation values (since 5.0.0)

`queryTerrainElevation` returns actual altitude. Recheck calculations that were written around its pre-v5 numeric semantics.

## Globe query and coordinate corrections (since 5.4.0)

`queryRenderedFeatures` correctly handles globe-view queries crossing the international date line; applications do not need to split these queries.

On globe maps, `unproject` clamps points to the visible horizon instead of returning a coordinate beyond the visible globe surface.

## Reduced motion at map construction (since 5.12.0)

Set `MapOptions.reduceMotion` to configure map-level reduced-motion behavior:

```js
const map = new Map({
  container: 'map',
  reduceMotion: true
});
```

## Custom box-zoom completion (since 5.20.0)

Use `boxZoom.boxZoomEnd` to customize what happens after a Shift-drag box selection finishes.

## Camera method snapping (since 5.20.0)

`zoomSnap` applies to programmatic camera operations:

- `fitBounds` and `fitScreenCoordinates` snap downward so the requested bounds stay visible.
- `jumpTo`, `easeTo`, and `flyTo` snap to the nearest valid increment.
- Under Vertical Perspective, `fitBounds` honors its `maxZoom` option.

## `Map` and `Camera` composition (since 6.0.0)

`Map` no longer inherits from `Camera`; it composes a camera and forwards the public camera API. Do not depend on inheritance, `map.transform`, or the removed `transform.getMatrixForModel`. Use public map methods and supported render arguments.

## Hash parsing (since 6.0.0)

Location hashes use `URLSearchParams` parsing and normalization. Encoded hashes such as `#10%2F3.00%2F-1.00` are accepted, and a bare hash such as `#foo` normalizes to `#foo=`. Tests comparing hash strings must account for this normalization.

## Drag sensitivity (since 6.1.0-6.4.1)

`MapOptions.rotateSpeed` and `MapOptions.pitchSpeed` define the bearing or pitch change, in degrees, per dragged pixel.

```js
const map = new Map({
  container: 'map',
  rotateSpeed: 0.5,
  pitchSpeed: 0.25
});
```
