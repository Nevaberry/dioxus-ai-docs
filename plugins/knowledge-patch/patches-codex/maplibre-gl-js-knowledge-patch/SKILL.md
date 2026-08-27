---
name: maplibre-gl-js-knowledge-patch
description: MapLibre GL JS
version: "6.0.0"
license: MIT
metadata:
  author: Nevaberry
---


# MapLibre GL JS Knowledge Patch

Use this skill when implementing, migrating, or debugging MapLibre GL JS code whose behavior depends on recent APIs, runtime requirements, event semantics, sources, projections, or rendering changes.

Determine the installed package version from the project manifest before applying version-specific advice. Prefer public map, source, and render-argument APIs over inheritance or internal transform details.

## Reference index

| Reference | Read when working with |
| --- | --- |
| [Camera, globe, and location](references/camera-globe-and-location.md) | Camera orientation, bounds fitting, globe queries, terrain elevation, geolocation, and URL hashes |
| [Controls, markers, and UI](references/controls-markers-and-ui.md) | Popups, marker appearance, accessibility, dragging, and keyboard behavior |
| [Events, types, and errors](references/events-types-and-errors.md) | Subscriptions, typed custom events, event classes, style lifecycle, and network failures |
| [Packaging and runtime](references/packaging-and-runtime.md) | ESM migration, workers, CSP, browser targets, WebGL setup, sanitization, and build artifacts |
| [Sources, tiles, and requests](references/sources-tiles-and-requests.md) | Vector and GeoJSON sources, overscaling, request transforms, validation, raster data, and image updates |
| [Styles, projections, and rendering](references/styles-projections-and-rendering.md) | Expressions, projections, custom layers, terrain, layer properties, shaders, and style images |

## Breaking migration essentials

### Import the ESM distribution correctly

The v6 package is ESM-only. Replace default imports with namespace or named imports:

```ts
import * as maplibregl from 'maplibre-gl';
// or
import {Map, setWorkerUrl} from 'maplibre-gl';
```

For direct browser loading, use a module script and the `.mjs` distribution:

```html
<script type="module">
  import {Map} from 'https://unpkg.com/maplibre-gl@^6.0.0/dist/maplibre-gl.mjs';
</script>
```

The final v6 browser build resolves its ESM worker as a module URL, including for cross-origin CDN use, and does not require the old CSP-specific bundle or a `worker-src blob:` exception. In a bundled application, call `setWorkerUrl()` once because a bundler may not preserve the worker URL relationship.

### Meet the runtime requirements

V6 output targets ES2022 and requires WebGL 2. Update browsers and build tooling or transpile at the application boundary when needed. Handle unavailable WebGL through the map's `error` event.

```js
map.on('error', handleMapError);
```

In v5, put context settings under `canvasContextAttributes`; do not pass former top-level options such as `antialias` or `preserveDrawingBuffer`.

```js
const map = new Map({
  container: 'map',
  canvasContextAttributes: {
    antialias: true,
    preserveDrawingBuffer: true,
    failIfMajorPerformanceCaveat: true,
    contextType: 'webgl2'
  }
});
```

### Do not chain event registration

`Evented.on()` returns a `Subscription`, not the evented object. Register listeners separately and retain a subscription only when it must be removed.

```js
const moveSubscription = map.on('move', onMove);
map.on('zoom', onZoom);
moveSubscription.unsubscribe();
```

In v6, discriminate event objects by `event.type`, not `instanceof`. Event classes and their generic maps are implementation-facing type structure, while the `type` field is the stable identification mechanism.

### Stop depending on `Map` inheritance

V6 `Map` composes a `Camera` and forwards its public API; it no longer extends `Camera`. Replace inheritance checks and access to `map.transform` with public map methods. `transform.getMatrixForModel` is removed.

### Update GeoJSON source calls

`GeoJSONSource.setData()` accepts only the data argument and no longer returns the source. Remove the old completion flag and method chains:

```js
source.setData(nextData);
```

Nested objects in GeoJSON properties now round-trip as objects and use the internal `__$json__` serialized prefix. Do not depend on the former unsupported representation.

### Resolve missing style images with the resolver

A `styleimagemissing` listener cannot satisfy the current request by calling `addImage()` in v6. Register a synchronous or asynchronous resolver; an asynchronous resolver must add the image before its promise settles.

```js
map.setMissingStyleImageResolver(async (id) => {
  const image = await generateImage(id);
  map.addImage(id, image);
});
```

Keep `styleimagemissing` only for observing images that remain unresolved.

### Rename promoted APIs and shader directives

The v5 `experimentalZoomLevelsToOverscale` option becomes `zoomLevelsToOverscale` in v6. Because slicing can change rendering and `queryRenderedFeatures()` results, set it explicitly to `undefined` when retaining the former overscaling behavior is important.

```js
const map = new Map({
  container: 'map',
  zoomLevelsToOverscale: undefined
});
```

Replace `#pragma mapbox` with `#pragma maplibre` in shared shader code.

## High-value current APIs

### Transform requests asynchronously

`setTransformRequest` accepts an async callback. Return `RequestParameters.referrerPolicy` when tile requests require a particular referrer policy.

```js
map.setTransformRequest(async (url) => ({
  url,
  referrerPolicy: 'no-referrer'
}));
```

### Use whole-layer opacity deliberately

`fill-layer-opacity` and `line-layer-opacity` composite uniformly across a complete layer. `line-layer-opacity` avoids opacity accumulation at overlapping line geometry; alpha embedded in `line-color` still stacks.

```js
paint: {'line-layer-opacity': 0.5}
```

### Type application events intentionally

For v5 TypeScript projects, declaration-merge `MapEventType` to define application events. Newer typed event-name checks may require explicit casts for names outside the map event map.

```ts
declare module 'maplibre-gl' {
  interface MapEventType {
    'app:ready': {type: 'app:ready'; payload: string};
  }
}

map.fire('app:ready' as any);
```

### Feed decoded images directly

When an overlay is already decoded, pass an `HTMLImageElement`, `HTMLCanvasElement`, `ImageBitmap`, or `ImageData` to `ImageSource.updateImage()` in `{image}` to avoid another network request.

```js
map.getSource('overlay').updateImage({image: decodedImage});
```

### Coordinate custom layers with projections

Use `getProjectionData` from the custom-layer render arguments rather than removed transform internals. During globe-to-Mercator transitions, read the live `defaultProjectionData.projectionTransition` value so custom drawing eases with built-in layers.

## Diagnostic checklist

When code compiles but behaves differently after an upgrade, check these areas before adding workarounds:

1. Confirm whether the application is on v5 or v6 and whether the consuming toolchain supports ESM and ES2022.
2. Check worker URL handling separately for direct browser ESM and bundler output.
3. Inspect listener return values, event names, and event discrimination.
4. Check whether overscaling, projection, or camera snapping changed the queried or displayed geometry.
5. Validate source updates, nested GeoJSON properties, terrain configuration, and custom source handling.
6. Distinguish whole-layer opacity from color alpha and built-in projection data from custom matrix assumptions.
7. Read the topic reference before changing APIs; several corrections remove the need for older compatibility workarounds.
