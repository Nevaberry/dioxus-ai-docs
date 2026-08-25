# Camera, Globe, and Terrain

## Projection and globe presentation

### Expression-driven projection and Vertical Perspective

Projection type may be supplied as an expression, and Vertical Perspective is
available as a projection mode (since 5.0.0). Later, `global-state` became
valid in `projection.type`, so application state can select the projection
(6.1.0-6.4.1).

```js
map.setProjection({
  type: ['global-state', 'projection']
});
```

### Globe, terrain, atmosphere, sky, and fog

Globe mode supports terrain and an optional realistic atmosphere (since
5.0.0). Sky rendering is disabled on the globe and blends back during a
transition to Mercator. Fog is disabled for the unsupported Terrain3D-on-globe
combination.

### Spherical light transitions

Style light-position transitions interpolate in spherical coordinates in
6.0.0, not Cartesian coordinates. The path preserves radial distance and can
look different from the same transition in an earlier application.

## Globe queries and coordinates

### Queries across the international date line

`queryRenderedFeatures` handles globe-view query regions that cross the
international date line (since 5.4.0). Do not split these query regions merely
to work around wrapping.

### Unprojection at the horizon

On a globe, `unproject` clamps a point to the visible horizon instead of
returning a coordinate beyond the globe's visible surface (since 5.4.0).

### Marker drag longitude

Globe marker drag coordinates no longer carry an erroneous `+360` or `-360`
longitude offset (since 5.4.0). Use the longitude directly.

## Camera movement and fitting

### Pitch, roll, and drag rotation

The camera supports pitch beyond 90 degrees and a roll angle (since 5.0.0).
Drag rotation pivots around the center of the screen.

### `zoomSnap` in camera methods

`zoomSnap` applies to programmatic camera changes (since 5.20.0):

- `fitBounds` and `fitScreenCoordinates` snap downward so the requested bounds
  remain visible.
- `jumpTo`, `easeTo`, and `flyTo` snap to the nearest valid increment.
- In Vertical Perspective, `fitBounds` honors its `maxZoom` option.

### Drag sensitivity

`MapOptions.rotateSpeed` and `MapOptions.pitchSpeed` specify degrees of bearing
or pitch change per dragged pixel (6.1.0-6.4.1).

```js
const map = new Map({
  container: 'map',
  rotateSpeed: 0.5,
  pitchSpeed: 0.25
});
```

### Reduced motion

Set `MapOptions.reduceMotion` to configure reduced-motion behavior at map
construction time (since 5.12.0).

```js
const map = new Map({container: 'map', reduceMotion: true});
```

## Terrain elevation and edges

### Actual elevation values

`queryTerrainElevation` returns actual altitude in 5.0.0. Revisit calculations
that assumed the earlier numeric semantics.

### Configurable terrain skirts

`MapOptions.terrainSkirtLength` controls terrain skirt length in 6.0.0. Tune
it when a transparent map background exposes vertical artifacts at terrain
edges.

```js
const map = new Map({
  container: 'map',
  terrainSkirtLength: desiredSkirtLength
});
```

## Projection data for custom rendering

### Mercator matrices

Custom layers on Mercator receive non-translated matrices starting in 5.0.0.
Remove assumptions or compensating transforms written for translated matrices.

### Supported projection data

Custom-layer render argument objects expose `getProjectionData` in 6.0.0.
Use the render argument rather than internal map transforms to obtain current
projection data.

### Live globe transitions

`CustomRenderMethodInput.defaultProjectionData.projectionTransition` reports
the live globe-to-Mercator transition in 6.1.0-6.4.1 rather than remaining at
`1`. Use it to synchronize a custom layer with built-in layers.

