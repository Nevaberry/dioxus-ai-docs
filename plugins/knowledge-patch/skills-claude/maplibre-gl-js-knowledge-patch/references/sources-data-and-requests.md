# Sources, Data, and Requests

## Vector-tile formats and identifiers

### MapLibre Tiles encoding

Vector sources consume MapLibre Tiles by setting `encoding: 'mlt'` (since
5.12.0).

```js
map.addSource('mlt-data', {
  type: 'vector',
  tiles: ['https://example.com/tiles/{z}/{x}/{y}'],
  encoding: 'mlt'
});
```

### Cluster feature IDs with `promoteId`

For clustered circle data using `promoteId`, an unclustered feature receives
its promoted ID and a clustered feature receives `cluster_id` (since 5.0.0).
Do not expect the unclustered feature ID to be undefined.

## Tile level of detail and overscaling

### Public LOD control

Tile level-of-detail control is exposed through the public API in 5.4.0, so
applications can influence tile selection without relying on internals.

### Experimental slicing in v5

`MapOptions.experimentalZoomLevelsToOverscale` in 5.12.0 controls how many
zoom levels are sliced versus scaled during vector-tile overscaling. It can
improve high-zoom performance. A value of `4` or less can prevent Safari
crashes in affected scenarios.

```js
const map = new Map({
  container: 'map',
  experimentalZoomLevelsToOverscale: 4
});
```

### Promoted slicing option

During migration-v5-v6, the option becomes `zoomLevelsToOverscale`. Slicing
can change rendering and `queryRenderedFeatures()` results. Set it explicitly
to `undefined` to retain the previous overscaling behavior.

```js
const map = new Map({
  container: 'map',
  zoomLevelsToOverscale: undefined
});
```

## GeoJSON updates and representation

### Updating GeoJSON-VT-backed data

GeoJSON data backed by GeoJSON-VT can be updated, including through diff
updates, in 5.20.0. A complete tile index no longer has to remain static.

### `GeoJSONSource.setData`

In 6.0.0, `setData` accepts only the data argument. Its `waitForCompletion`
parameter is removed and it no longer returns the source instance. Do not pass
a second argument or chain from the call.

```js
source.setData(nextData);
```

### Nested feature properties

Nested objects in GeoJSON feature properties are encoded and parsed back as
objects in 6.0.0. Their serialized representation uses the `__$json__` prefix.
Code must not rely on the former unsupported representation or treat the
internal prefix as an application data contract.

## Request customization and workers

### Async transforms and referrer policy

`setTransformRequest` accepts an async callback in 5.20.0.
`RequestParameters.referrerPolicy` controls the policy for tile requests.

```js
map.setTransformRequest(async (url) => ({
  url,
  referrerPolicy: 'no-referrer'
}));
```

### Imported worker scripts

Scripts imported into workers can communicate with the worker environment and
call `makeRequest` starting in 5.20.0.

### Image request behavior

Image requests always send `Accept: image/webp` in 5.20.0. The earlier Edge 18
detection workaround was removed with other legacy browser paths.

## Source validation

In 6.0.0, `map.setTerrain` validates its terrain configuration, and
`raster-dem` sources passed to `map.addSource` are no longer skipped during
validation. A custom source registered with `addSourceType`, however, does not
invalidate the whole style merely because the style specification lacks a
schema for it.

## Raster and image sources

### Raw alpha channel data

Use `RasterTileSource#setPremultiplyAlpha(false)` in 6.0.0 to preserve raw
RGBA when the alpha channel carries data rather than opacity.

```js
map.getSource('raw-raster').setPremultiplyAlpha(false);
```

### Decoded image updates

`ImageSource.updateImage` accepts an already-decoded `HTMLImageElement`,
`HTMLCanvasElement`, `ImageBitmap`, or `ImageData` in `{image}` in
6.1.0-6.4.1, avoiding another request.

```js
const source = map.getSource('overlay');
source.updateImage({image: decodedImage});
```

