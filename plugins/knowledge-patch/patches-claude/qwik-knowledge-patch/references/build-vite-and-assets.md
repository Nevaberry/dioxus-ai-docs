# Build, Vite, and Assets

## Optimizer syntax and transform ordering

Since 1.8, the optimizer understands `import ... with` and replaces enums
with numbers when possible. QRL grouping is delegated to Rollup, so other
Rollup or Vite plugins, including CSS-in-JS transforms, can process code
before Qwik applies its transform.

When plugin ordering matters, preserve the ordering required by the upstream
transform rather than assuming Qwik groups QRLs first.

## Default build asset paths

Default built assets use `assets/hash-name.ext`. Deployment rules, CDN paths,
and cache matchers that assume earlier output locations must be updated.

## Library QRL file processing

`qwikVite()` always processes library QRL files named `*.qwik.js`,
`*.qwik.mjs`, or `*.qwik.cjs`. A custom `fileFilter` cannot exclude them.

## Experimental Vite features

`qwikVite()` accepts an `experimental` array:

```ts
qwikVite({ experimental: ['noSPA', 'valibot', 'preventNavigate'] });
```

- `noSPA` is for MPA-only applications that do not use `Link`.
- `valibot` enables the experimental `valibot$` validator.
- `preventNavigate` enables `usePreventNavigate`. It can asynchronously block
  SPA navigation and falls back to browser dialogs for other unsaved-state
  navigation.

## Module-preload fetch priority

Prefetch strategies accept `linkFetchPriority` for generated
`modulepreload` links. Set it when route-critical preloads need an explicit
browser fetch priority.

## Monorepo-aware integrations

`qwik add` accepts `projectDir`, allowing an integration to target a package
or subproject instead of the repository root:

```sh
qwik add --projectDir=packages/my-package
```

## Lint default

The `lint` option defaults to `false`. Enable it explicitly when the build is
expected to lint.

## Automatic bundle preloading

Since 1.14, Qwik uses `modulepreload` links and a bundle graph rather than its
service workers for prefetching. The graph includes dynamic imports and
path-to-bundle mappings, and the server has built-in manifest support.

The built-in service-worker components are deprecated. For an uncustomized
worker, remove `service-worker.ts` but keep `ServiceWorkerRegister`
temporarily so already-deployed workers and caches are removed. Automatic
unregistration does not occur when the worker contains custom logic.

Only add the service-worker integration when a legacy application still
needs a customizable worker:

```sh
qwik add service-worker
```

## Preload configuration

SSR preload options include `debug` and the stable `maxIdlePreloads`, which
limits concurrent idle preloads. `preloadProbability` is deprecated since
1.16.1.

```ts
renderToStream(<Root />, {
  ...opts,
  preload: { debug: true, maxIdlePreloads: 5 },
});
```

## Cache headers

Content-hashed files under `build/` and `assets/` should normally use:

```http
Cache-Control: public, max-age=31536000, immutable
```

Do not apply that policy blindly when Rollup output naming has been
customized and URLs are no longer content-addressed.

Qwik City navigation honors the cache headers of `q-data.json` instead of
forcing a fresh download. Its default cache duration is one hour.

## Qwikloader delivery

Since 1.15, SSR loads Qwikloader from a separate bundle rather than embedding
it. Since 1.17, tests or unusual network setups can opt back into embedding
it:

```ts
renderToStream(<Root />, {
  ...opts,
  qwikLoader: 'inline',
});
```

## Manifest and preloader artifacts

The preloader bundle graph is emitted as an asset. `q-manifest.json` includes
generated assets. By 1.19, `core.js` and `preloader.js` references are
filtered from both the manifest and bundle graph.

## Client bundle freshness

Use the CLI's `check-client` command to verify that the client bundle is
fresh:

```sh
qwik check-client
```

## Compiled i18n integration

Scaffold compiled-i18 support directly:

```sh
qwik add compiled-i18
```
