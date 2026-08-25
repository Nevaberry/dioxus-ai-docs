# Style and Custom Rendering

## Data-driven line styling

### Dash arrays

`line-dasharray` accepts data-driven expressions in 5.8.0. Wrap constant array
results in `literal` when using them inside an expression.

```js
paint: {
  'line-dasharray': [
    'match',
    ['get', 'kind'],
    'rail', ['literal', [2, 2]],
    ['literal', [1, 0]]
  ]
}
```

### Geometry-dependent layout values

`line-cap`, `line-miter-limit`, and `line-round-limit` support data-driven
expressions in 5.20.0.

```js
layout: {
  'line-cap': ['match', ['get', 'cap'], 'round', 'round', 'butt']
}
```

## Raster-derived layer sampling

Raster, hillshade, and color-relief layers expose resampling paint properties
in 5.20.0. Raster nearest-neighbor sampling is selected as follows; its
behavior is corrected in that batch.

```js
paint: {'raster-resampling': 'nearest'}
```

## Layer compositing and geometry

### Whole-layer opacity

`fill-layer-opacity` and `line-layer-opacity` composite opacity uniformly over
an entire layer in 6.0.0. `line-layer-opacity` prevents opacity accumulation
where line geometry overlaps. Alpha embedded in `line-color` still stacks.

```js
paint: {'line-layer-opacity': 0.5}
```

### Rounded fill-extrusion corners

`fill-extrusion-rounded-corner-distance` rounds corners by a distance in
meters in 6.1.0-6.4.1. It defaults to `0`, is clamped to 20% of each adjacent
edge, and leaves turns below 5 degrees sharp.

```js
layout: {'fill-extrusion-rounded-corner-distance': 2}
```

### Icon offset placement

Icon offsets are no longer scaled with the icon in 6.0.0. Adjust offsets in
symbol layouts that depended on the former coupling.

## Environment expressions and light

### Global state

`global-state` expressions work in `sky.*`, `light.*`, and `projection.type`
in 6.1.0-6.4.1. These style-wide values can react to application global state.

```js
projection: {
  type: ['global-state', 'projection']
}
```

### Spherical light interpolation

Light-position transitions use spherical rather than Cartesian interpolation
in 6.0.0. The path preserves radial distance and can render differently from
an earlier transition with the same endpoints.

## Style images

### Missing-image resolver

During migration-v5-v6, a `styleimagemissing` listener can no longer resolve
the current request by calling `Map#addImage`. Register
`Map#setMissingStyleImageResolver` instead. A resolver may be synchronous or
asynchronous, but async code must add the image before its promise settles.
The event remains useful for observing images that stay unresolved.

```js
map.setMissingStyleImageResolver(async (id) => {
  const image = await generateImage(id);
  map.addImage(id, image);
});
```

### GPU-rendered images

In 6.1.0-6.4.1, `StyleImageInterface.data` may be an object with a
`renderWithWebGL` callback. Use it for frequently changing images such as
animated icons when updated pixels should stay on the GPU rather than moving
through the CPU.

## Custom shader and layer APIs

### Shader pragma spelling

Shared shader code must use the MapLibre pragma during migration-v5-v6.

```diff
-#pragma mapbox
+#pragma maplibre
```

### Mercator matrices

Custom layers on Mercator maps receive non-translated matrices starting in
5.0.0. Remove assumptions built around the former translated matrices.

### Projection render arguments

Custom-layer argument objects expose `getProjectionData` in 6.0.0. Obtain
projection data from the supported arguments instead of map internals.

### Live globe transitions

`CustomRenderMethodInput.defaultProjectionData.projectionTransition` reports
the live globe-to-Mercator transition in 6.1.0-6.4.1 instead of staying fixed
at `1`, allowing custom layers to ease with built-in layers.

## Typed style access

In 6.0.0, TypeScript getter and setter signatures for layout and paint
properties use each property's actual type instead of broad `string` and
`any`. Correct the property name or value when an old loosely typed call stops
compiling.

