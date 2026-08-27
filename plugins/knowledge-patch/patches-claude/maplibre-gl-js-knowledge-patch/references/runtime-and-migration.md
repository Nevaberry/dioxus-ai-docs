# Runtime and Migration

## Distribution and imports

### Removed unminified production artifact

The unminified production build is not distributed starting in 5.0.0. Replace
references to that artifact with an available development or production build.

### ESM-only packaging

The migration-v5-v6 distribution removes UMD and dedicated CSP bundles and
ships `maplibre-gl.mjs` with `maplibre-gl-worker.mjs`. Named npm imports remain
valid. Replace a default import with a namespace or named import, and use a
module script for direct browser loading.

```ts
import * as maplibregl from 'maplibre-gl';
// or
import {Map, setWorkerUrl} from 'maplibre-gl';
```

```html
<script type="module">
  import * as maplibregl from 'https://unpkg.com/maplibre-gl@^6.0.0/dist/maplibre-gl.mjs';
</script>
```

## Worker loading and CSP

Migration-stage guidance in migration-v5-v6 described direct cross-origin ESM
loading through a same-origin Blob URL, with `worker-src 'self' blob:` and no
`setWorkerUrl()` call. It also required bundled applications to call
`setWorkerUrl()` once because bundlers cannot reliably resolve the worker from
`import.meta.url`; self-hosting did not require `blob:`.

The final 6.0.0 build supersedes that provisional browser/CDN behavior. It
loads the worker as a real module URL and auto-loads a cross-origin CDN worker
while preserving ESM semantics. The final direct-browser path needs neither a
CSP-specific bundle nor a `worker-src blob:` allowance. Retain explicit
`setWorkerUrl()` in bundled applications when the bundler cannot resolve the
worker.

Scripts imported into workers can communicate with the worker environment and
use `makeRequest` starting in 5.20.0.

## Browser, JavaScript, and WebGL requirements

### Canvas context options

In 5.0.0, former top-level WebGL options move to
`MapOptions.canvasContextAttributes`. `contextType` selects the WebGL version;
the v5 runtime can request WebGL 2 with a WebGL 1 fallback.

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

### Modern baseline

Published 6.0.0 code targets ES2022. Update old browsers and build tooling or
transpile at the application boundary. WebGL 1 is removed and WebGL 2 is
required; an unavailable context is reported through the map's `error` event.

```js
map.on('error', handleMapError);
```

Legacy IE11 and pre-2016 browser paths were removed in 5.20.0 in favor of
native APIs. Image requests always send `Accept: image/webp`; there is no Edge
18 detection workaround.

## Core API migrations

### `Map` and `Camera`

`Map` composes a `Camera` and forwards its public API in 6.0.0; it no longer
extends `Camera`. Replace code depending on inheritance or internal
`map.transform` access. `transform.getMatrixForModel` is removed; use public
map or custom-render argument APIs.

### `queryIntersectsFeature`

`StyleLayer.queryIntersectsFeature` takes one object satisfying
`QueryIntersectsFeatureParams` rather than positional arguments (since 5.0.0).

### Strong style-property types

Layout- and paint-property getter/setter signatures use the actual property types
in 6.0.0 instead of broad `string` and `any` types. Correct invalid
property names and values instead of widening them back to `any`.

## URL hash parsing

Hash location control uses `URLSearchParams` parsing and normalization in
6.0.0. Encoded strings such as `#10%2F3.00%2F-1.00` are accepted, and a bare
`#foo` normalizes to `#foo=`. Account for normalization in routing and tests.

## Error handling

Fetch failures such as CORS, DNS, and malformed URLs are delivered as
`AJAXError` through the map's `error` event in 5.0.0. Use its request details
when reporting or retrying a failed request.

## DOM sanitization

In 6.1.0-6.4.1, specifically 6.4.1, `DOM.sanitize` removes consecutive
dangerous attributes correctly. Earlier behavior could skip a dangerous
attribute immediately after another removed attribute, leaving it able to
execute. Upgrade rather than relying on the affected sanitizer.
