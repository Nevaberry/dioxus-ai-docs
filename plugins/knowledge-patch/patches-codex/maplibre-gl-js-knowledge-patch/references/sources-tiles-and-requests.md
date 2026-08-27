# Sources, tiles, and requests

## Feature intersection arguments (since 5.0.0)

`StyleLayer.queryIntersectsFeature` accepts one object conforming to `QueryIntersectsFeatureParams`, not positional arguments. Wrap the former arguments in the parameter object.

## Cluster IDs with promoted IDs (since 5.0.0)

For clustered circle data configured with `promoteId`, an unclustered feature receives its promoted ID and a clustered feature receives `cluster_id`. Do not retain checks that expect an unclustered feature ID to be undefined.

## Public tile LOD control (since 5.4.0)

Tile level-of-detail control is available through the public API. Use it when application requirements need to influence tile selection rather than reaching into internal selection behavior.

## MapLibre Tiles sources (since 5.12.0)

To consume MapLibre Tiles vector data, declare the source with `encoding: 'mlt'`.

```js
map.addSource('mlt-data', {
  type: 'vector',
  tiles: ['https://example.com/tiles/{z}/{x}/{y}'],
  encoding: 'mlt'
});
```

## Vector-tile slicing while overscaling (since 5.12.0)

`MapOptions.experimentalZoomLevelsToOverscale` controls how many zoom levels are sliced and how many are scaled during vector-tile overscaling. This can improve high-zoom performance. A value of `4` or less can prevent Safari crashes in affected cases.

```js
const map = new Map({
  container: 'map',
  experimentalZoomLevelsToOverscale: 4
});
```

## Updating GeoJSON-VT data (since 5.20.0)

GeoJSON data backed by GeoJSON-VT can be updated, including with diff updates. It no longer requires a completely static tile index.

## Async request transformation (since 5.20.0)

`setTransformRequest` accepts an async callback. `RequestParameters.referrerPolicy` controls the referrer policy for tile requests.

```js
map.setTransformRequest(async (url) => ({
  url,
  referrerPolicy: 'no-referrer'
}));
```

## Promoted overscaling option (since migration-v5-v6)

The v5 experimental option becomes `zoomLevelsToOverscale` in v6. Tile slicing can change rendering and `queryRenderedFeatures()` results. Set it explicitly to `undefined` when the application must retain the previous overscaling behavior.

```js
const map = new Map({
  container: 'map',
  zoomLevelsToOverscale: undefined
});
```

## GeoJSON `setData` return and parameters (since 6.0.0)

`GeoJSONSource.setData` takes only the data argument. The `waitForCompletion` parameter is removed, and the method no longer returns the source instance. Remove the second argument and do not chain a source method from the result.

```js
source.setData(nextData);
```

## Nested GeoJSON properties (since 6.0.0)

Nested objects in feature properties are encoded and parsed back as objects. The serialized representation uses the `__$json__` prefix. Code that read or created the previous unsupported object representation must adjust.

## Terrain and source validation (since 6.0.0)

`map.setTerrain` validates its terrain configuration. `raster-dem` sources passed to `map.addSource` also undergo validation. A custom source registered through `addSourceType`, however, does not invalidate the entire style merely because the style specification has no schema for it.

## Preserving raster alpha data (since 6.0.0)

Call `RasterTileSource#setPremultiplyAlpha(false)` when the alpha channel is data rather than opacity and raw RGBA values must be preserved.

```js
map.getSource('raw-raster').setPremultiplyAlpha(false);
```

## Updating an image source with decoded data (since 6.1.0-6.4.1)

`ImageSource.updateImage` accepts an already-decoded `HTMLImageElement`, `HTMLCanvasElement`, `ImageBitmap`, or `ImageData` in `{image}`. This avoids another network request.

```js
const source = map.getSource('overlay');
source.updateImage({image: decodedImage});
```
