---
name: maplibre-gl-js-knowledge-patch
description: MapLibre GL JS
version: "6.0.0"
license: MIT
metadata:
  author: Nevaberry
---


# MapLibre GL JS Knowledge Patch

Use this skill when writing, migrating, reviewing, or debugging MapLibre GL JS
applications. Check the installed package version first, then apply only the
guidance that is relevant to that version. Prefer the application's manifest,
code, runtime behavior, and tests when they disagree with compatibility notes.

## Reference index

| Reference | Topics |
| --- | --- |
| [Camera, globe, and terrain](references/camera-globe-and-terrain.md) | Projection expressions, globe queries, camera movement, elevation, terrain, and globe-aware custom layers |
| [Events and controls](references/events-and-controls.md) | Subscriptions, typed events, style loading, geolocation, popups, box zoom, and marker interaction |
| [Runtime and migration](references/runtime-and-migration.md) | ESM packaging, workers and CSP, browser/WebGL requirements, API migrations, errors, hashes, and sanitization |
| [Sources, data, and requests](references/sources-data-and-requests.md) | Vector and GeoJSON sources, overscaling, request transforms, image sources, raster data, and validation |
| [Style and custom rendering](references/style-and-custom-rendering.md) | Data-driven paint/layout, opacity, style images, shader pragmas, custom layers, and light transitions |

## Start with the breaking changes

### Use ESM imports

The package is ESM-only. Replace default imports and legacy browser bundles
with namespace or named imports. Browser scripts must be modules.

```ts
import * as maplibregl from 'maplibre-gl';
import {Map, setWorkerUrl} from 'maplibre-gl';
```

```html
<script type="module">
  import {Map} from '/vendor/maplibre-gl.mjs';
</script>
```

The final browser distribution loads the worker as a module URL. Do not add a
`worker-src blob:` exception solely for this final loading path. Bundled
applications should configure the worker URL once when the bundler cannot
resolve it automatically.

### Require modern JavaScript and WebGL

Published code targets ES2022 and rendering requires WebGL 2. Update browsers
and tooling or transpile in the application. Handle missing WebGL through the
map's `error` event.

```js
map.on('error', handleMapError);
```

Canvas context settings belong under `canvasContextAttributes`; do not pass
`antialias`, `preserveDrawingBuffer`, or
`failIfMajorPerformanceCaveat` at the top level.

### Treat listener registration as a subscription

`on()` returns a `Subscription`, not the evented object. Register listeners
separately and retain a subscription when it must be removed.

```js
const subscription = map.on('move', onMove);
map.on('zoom', onZoom);
subscription.unsubscribe();
```

Do not identify event classes with `instanceof`; discriminate on `event.type`.
TypeScript event names and payloads are checked more strictly, and `Evented`
is abstract and generic over an event map.

### Stop depending on `Map` inheritance and internals

`Map` composes and forwards a `Camera`; it no longer inherits from one. Replace
inheritance checks, direct `map.transform` access, and
`transform.getMatrixForModel` with public map APIs.

`StyleLayer.queryIntersectsFeature` takes one
`QueryIntersectsFeatureParams` object instead of positional arguments.

### Update source mutation code

`GeoJSONSource.setData(data)` accepts one argument and returns no chainable
source. Remove `waitForCompletion` and do not call another method from its
result.

```js
source.setData(nextData);
```

Nested GeoJSON properties now round-trip as objects. Do not depend on their
former unsupported representation or on the internal `__$json__` encoding
prefix.

### Resolve missing style images through the resolver

`styleimagemissing` is observational when an image remains unresolved. Supply
missing images with `setMissingStyleImageResolver`; an asynchronous resolver
must add the image before its promise settles.

```js
map.setMissingStyleImageResolver(async (id) => {
  const image = await generateImage(id);
  map.addImage(id, image);
});
```

## High-use capabilities

### Configure vector-tile overscaling deliberately

Use `zoomLevelsToOverscale` for the public slicing/overscaling policy. Setting
it to `undefined` retains the previous overscaling behavior. Because slicing
can change rendering and `queryRenderedFeatures()` results, pin the value and
test high-zoom queries when migrating.

### Use async request transforms

Request transforms may be asynchronous and may set `referrerPolicy`.

```js
map.setTransformRequest(async (url) => ({
  url,
  referrerPolicy: 'no-referrer'
}));
```

Imported worker scripts can communicate with the worker environment and call
`makeRequest`.

### Prefer whole-layer opacity when overlap must not accumulate

Use `fill-layer-opacity` or `line-layer-opacity` to composite opacity across a
whole layer. `line-layer-opacity` avoids accumulation where line geometry
overlaps; alpha embedded in `line-color` still stacks.

```js
paint: {'line-layer-opacity': 0.5}
```

Line dash arrays, caps, miter limits, and round limits can be data-driven.
Raster-derived layers also expose resampling paint properties.

### Use global state for environment and projection values

`global-state` expressions work in `sky.*`, `light.*`, and `projection.type`.

```js
projection: {
  type: ['global-state', 'projection']
}
```

### Pass decoded images directly

`ImageSource.updateImage({image})` accepts an `HTMLImageElement`, canvas,
`ImageBitmap`, or `ImageData`, avoiding another network request.

```js
map.getSource('overlay').updateImage({image: decodedImage});
```

Style images that change frequently may provide `renderWithWebGL` through
`StyleImageInterface.data` so their pixels stay on the GPU path.

## Camera, globe, and terrain checks

- Projection type may be an expression, including Vertical Perspective.
- Globe queries crossing the international date line work directly.
- Globe `unproject` clamps to the visible horizon.
- Marker drag longitude on a globe no longer needs a full-world correction.
- Camera orientation supports pitch beyond 90 degrees and roll.
- `queryTerrainElevation` returns actual altitude.
- `zoomSnap` affects both fitting and direct camera methods, with different
  rounding rules; verify bounds remain visible.
- Use `rotateSpeed` and `pitchSpeed` to tune drag sensitivity.
- Use `terrainSkirtLength` to suppress visible terrain edges against a
  transparent background.

## Controls and accessibility checks

- `reduceMotion` configures map-level reduced-motion behavior.
- `Popup({padding})` keeps automatic placement away from container edges.
- `outofmaxbounds` is emitted only while geolocation tracking is enabled.
- Numeric marker opacity values are accepted, and covered markers receive
  `maplibregl-marker-covered` for state-specific CSS.
- Default markers expose an accessibility role matching whether they are
  interactive.
- Default draggable markers support arrow-key movement and Shift acceleration;
  custom elements must implement their own keyboard behavior.

## Working method

1. Inspect the installed `maplibre-gl` version and the application's loading
   mode: browser modules, a bundler, or self-hosted assets.
2. Read the migration and runtime reference before changing imports, workers,
   CSP, event typing, or internal camera access.
3. Open the topic reference for the feature being changed and preserve its
   version-specific caveats.
4. Exercise runtime paths that types cannot prove: worker loading, CSP,
   WebGL failure, globe transitions, source validation, and style diff events.
5. Test accessibility roles and keyboard behavior when markers or controls use
   custom DOM elements.

