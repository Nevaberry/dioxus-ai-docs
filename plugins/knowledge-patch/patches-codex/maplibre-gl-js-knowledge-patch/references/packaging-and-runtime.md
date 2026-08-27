# Packaging and runtime

## Canvas context configuration (since 5.0.0)

Former top-level WebGL options such as `antialias`, `preserveDrawingBuffer`, and `failIfMajorPerformanceCaveat` belong under `MapOptions.canvasContextAttributes`. Use `contextType` there to choose the WebGL version. The v5 runtime can request WebGL 2 with a WebGL 1 fallback.

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

## Production artifacts (since 5.0.0)

The unminified production build is no longer distributed. Select another shipped build instead of retaining a path to that artifact.

## Browser and image-request cleanup (since 5.20.0)

Compatibility paths for IE11 and browsers from before 2016 are removed in favor of native browser APIs. Image requests always send `Accept: image/webp`; do not expect the former Edge 18 detection workaround.

## Worker-script request access (since 5.20.0)

Scripts imported into workers can communicate with the worker environment and invoke `makeRequest` from within a worker.

## ESM-only package migration (since migration-v5-v6)

V6 removes the UMD and dedicated CSP bundles. It ships `maplibre-gl.mjs` and `maplibre-gl-worker.mjs`. Named npm imports remain valid, but default imports must become namespace or named imports.

```ts
import * as maplibregl from 'maplibre-gl';
// or
import {Map, setWorkerUrl} from 'maplibre-gl';
```

Direct browser loading requires a module script:

```html
<script type="module">
  import * as maplibregl from 'https://unpkg.com/maplibre-gl@^6.0.0/dist/maplibre-gl.mjs';
</script>
```

## Worker URLs and CSP migration (since migration-v5-v6)

During the migration path, direct browser ESM located its worker relative to `import.meta.url`; cross-origin CDN loading used a same-origin Blob URL and therefore required `blob:` in `worker-src`, while self-hosting did not. Bundled applications still needed one `setWorkerUrl()` call because bundlers could not reliably resolve that relationship.

```text
worker-src 'self' blob:;
img-src data: blob: 'self';
```

The final v6 loading behavior below supersedes the cross-origin Blob-worker requirement. Do not preserve the exception solely for the final build.

## Final module-worker loading (since 6.0.0)

The final ESM build loads its worker as a real module URL. CDN use auto-loads the cross-origin worker while preserving ESM semantics, so direct browser use no longer needs a CSP-specific bundle or `worker-src blob:` allowance. A bundled application should still configure its worker URL explicitly.

## JavaScript and WebGL requirements (since 6.0.0)

Published code targets ES2022. Update older browsers and tooling or add application-side transpilation when necessary. WebGL 1 support is removed and WebGL 2 is required. WebGL-unavailable failures arrive through the map's `error` event.

```js
map.on('error', handleMapError);
```

## Consecutive unsafe attributes (since 6.1.0-6.4.1)

The 6.4.1 `DOM.sanitize` correction removes a dangerous attribute even when it immediately follows another removed attribute. Upgrade applications relying on this sanitizer; before the correction, the second attribute could survive and execute.
