# Styles, projections, and rendering

## Projection expressions and Vertical Perspective (since 5.0.0)

Projection type may be an expression. Vertical Perspective is available as a projection mode.

## Globe, terrain, and atmosphere (since 5.0.0)

V5 supports globe mode, terrain on the globe, and an option for realistic globe atmosphere. Sky rendering is disabled while on the globe and blended back during a transition to Mercator. Fog is disabled for the unsupported combination of Terrain3D on the globe.

## Mercator custom-layer matrices (since 5.0.0)

Custom layers on Mercator maps receive non-translated matrices. Update custom rendering code that assumes the former translated matrices.

## Data-driven dash arrays (since 5.8.0)

`line-dasharray` accepts data-driven expressions, so each feature can select its pattern.

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

## Resampling raster-derived layers (since 5.20.0)

Raster, hillshade, and color-relief layers expose resampling paint properties. Nearest-neighbor raster sampling is available, with corrected behavior in this release.

```js
paint: {'raster-resampling': 'nearest'}
```

## Data-driven line geometry (since 5.20.0)

`line-cap`, `line-miter-limit`, and `line-round-limit` accept data-driven expressions.

```js
layout: {
  'line-cap': ['match', ['get', 'cap'], 'round', 'round', 'butt']
}
```

## Shader pragma migration (since migration-v5-v6)

Shared shader code must use the MapLibre pragma spelling.

```diff
-#pragma mapbox
+#pragma maplibre
```

## Missing style image resolution (since migration-v5-v6)

A `styleimagemissing` listener cannot fulfill the current image request by calling `Map#addImage`. Register `Map#setMissingStyleImageResolver`; it may return synchronously or asynchronously. Async code must add the image before the resolver promise settles.

```js
map.setMissingStyleImageResolver(async (id) => {
  const image = await generateImage(id);
  map.addImage(id, image);
});
```

The event remains useful for observing images that stay unresolved.

## Typed style property access (since 6.0.0)

TypeScript signatures for layout- and paint-property getters and setters use the actual type of each property rather than broad `string` and `any` types. Correct property names and values that previously compiled only because of the loose signatures.

## Whole-layer opacity (since 6.0.0)

`fill-layer-opacity` and `line-layer-opacity` composite opacity uniformly across an entire layer. `line-layer-opacity` avoids accumulation where line geometry overlaps; transparency in `line-color` continues to stack.

```js
paint: {'line-layer-opacity': 0.5}
```

## Configurable terrain skirts (since 6.0.0)

`MapOptions.terrainSkirtLength` controls terrain skirt length. Adjust it when transparent map backgrounds expose vertical artifacts at terrain edges.

```js
const map = new Map({
  container: 'map',
  terrainSkirtLength: desiredSkirtLength
});
```

## Projection data for custom layers (since 6.0.0)

Custom-layer argument objects expose `getProjectionData`. Obtain current projection data from the supported render arguments instead of removed transform internals.

## Spherical light transitions (since 6.0.0)

Style light-position transitions interpolate in spherical coordinates rather than Cartesian coordinates. The transition preserves radial distance and can follow a visibly different path from v5.

## Icon offset placement (since 6.0.0)

Icon offsets are no longer scaled with the icon. Adjust symbol offsets that relied on the former coupling.

## Global state in environment and projection expressions (since 6.1.0-6.4.1)

`global-state` expressions work in `sky.*`, `light.*`, and `projection.type`, allowing these style-wide values to react to application global state.

```js
projection: {
  type: ['global-state', 'projection']
}
```

## Rounded fill-extrusion corners (since 6.1.0-6.4.1)

The `fill-extrusion-rounded-corner-distance` layout property specifies a corner radius in meters. It defaults to `0`, is clamped to 20% of each adjacent edge, and leaves turns below 5 degrees sharp.

```js
layout: {
  'fill-extrusion-rounded-corner-distance': 2
}
```

## GPU-rendered style images (since 6.1.0-6.4.1)

`StyleImageInterface.data` may be an object with a `renderWithWebGL` callback. Use it for frequently changing images, such as animated icons, that should render on the GPU without transferring updated pixels through the CPU.

## Live globe transitions in custom layers (since 6.1.0-6.4.1)

`CustomRenderMethodInput.defaultProjectionData.projectionTransition` reports the live globe-to-Mercator transition rather than remaining fixed at `1`. Use it to ease custom layers in step with built-in layers.
