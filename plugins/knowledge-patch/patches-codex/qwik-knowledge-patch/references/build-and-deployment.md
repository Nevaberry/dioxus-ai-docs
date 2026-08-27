# Build and Deployment

## Optimizer syntax and transform ordering

The optimizer understands `import ... with` and replaces enums with numeric
values where possible. QRL grouping is delegated to Rollup, so other
Rollup/Vite plugins, including CSS-in-JS transforms, can process code before
the Qwik transform. Preserve the required plugin order when a transform must
see the original source.

## Build asset paths

Default build assets use `assets/hash-name.ext`. Update deployment copy rules,
CDN paths, and cache patterns that assumed earlier output locations.

## Library QRL file filtering

A custom `qwikVite()` `fileFilter` cannot exclude these library QRL suffixes:

- `*.qwik.js`
- `*.qwik.mjs`
- `*.qwik.cjs`

The optimizer always processes these files.

## Experimental Vite features

`qwikVite()` accepts an `experimental` array:

```ts
qwikVite({ experimental: ['noSPA', 'valibot', 'preventNavigate'] });
```

- `noSPA` is for MPA-only applications that do not use `Link`.
- `valibot` enables the experimental `valibot$` validator.
- `preventNavigate` enables `usePreventNavigate`. It can block SPA navigation
  asynchronously and falls back to browser dialogs for other unsaved-state
  navigation.

## Module-preload fetch priority

Prefetch strategies may set `linkFetchPriority` for generated
`modulepreload` links. Use it when the browser should prioritize or
deprioritize those module fetches.

## Monorepo-aware integration installation

`qwik add` accepts `projectDir`, allowing an integration to target a package
or subproject rather than the repository root:

```sh
qwik add --projectDir=packages/my-package
```

## Direct build-constant exports

Import `isDev`, `isBrowser`, and `isServer` directly from
`@builder.io/qwik`. The older `@builder.io/qwik/build` entry point remains
available.

```ts
import { isBrowser, isDev, isServer } from '@builder.io/qwik';
```

## Tailwind integrations

The Tailwind integration supports Tailwind CSS 4. The CLI also permits
projects to continue using Tailwind CSS 3; select the intended major rather
than assuming the integration forces an upgrade.

## Lint default

The Vite `lint` option defaults to `false`. Enable it explicitly when linting
must be part of the build.

## Automatic bundle preloading

Qwik uses `modulepreload` links and a bundle graph containing dynamic imports
and path-to-bundle mappings. The server has built-in manifest support. Do not
expect the built-in service worker to provide the normal prefetch path.

## Service-worker migration

The built-in service-worker components are deprecated. For an uncustomized
worker:

1. Remove `service-worker.ts`.
2. Keep `ServiceWorkerRegister` temporarily so already deployed workers and
   caches are removed.
3. Remove the registration component after the migration has reached users.

Custom worker logic prevents automatic unregistration. Keep or add the
integration only when a legacy application needs a customizable worker:

```sh
qwik add service-worker
```

## Preload configuration

SSR preload options include `debug` and `maxIdlePreloads`. The latter is the
stable limit on concurrent idle preloads. `preloadProbability` is deprecated
as of 1.16.1.

```ts
renderToStream(<Root />, {
  ...opts,
  preload: { debug: true, maxIdlePreloads: 5 },
});
```

## Static-asset cache headers

Unless Rollup output naming has been customized, content-hashed files under
`build/` and `assets/` should normally be served with:

```http
Cache-Control: public, max-age=31536000, immutable
```

Do not apply that policy blindly to unhashed output.

## Qwikloader delivery

SSR normally loads Qwikloader from a separate bundle rather than embedding
it. Testing or unusual network setups can opt back into inline delivery:

```ts
renderToStream(<Root />, {
  ...opts,
  qwikLoader: 'inline',
});
```

## Manifest and preloader artifacts

The preloader bundle graph is emitted as an asset, and `q-manifest.json`
includes generated assets. Current generation filters `core.js` and
`preloader.js` references from both the manifest and bundle graph. Tools that
inspect these artifacts must not require those entries.

## Vite 7 toolchain

Qwik core and Qwik City moved to Vite 7 in 1.16. Keep the application
toolchain on that major to avoid integration and dependency incompatibility.

## Client-bundle freshness check

Use the CLI command below to verify that the client bundle is fresh:

```sh
qwik check-client
```

## Compiled internationalization

Scaffold the compiled-i18 integration directly:

```sh
qwik add compiled-i18
```

Source batches: `v1.8-1.13`, `v1.14-1.19`.
