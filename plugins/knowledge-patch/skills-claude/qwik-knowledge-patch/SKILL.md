---
name: qwik-knowledge-patch
description: Qwik
version: 1.19.0
license: MIT
metadata:
  author: Nevaberry
---


# Qwik Knowledge Patch

Use this skill when maintaining Qwik applications, libraries, Qwik City
routes, SSR integrations, or build tooling whose behavior depends on recent
Qwik changes. Inspect the application's package manifest and Vite
configuration before applying compatibility advice.

## Reference index

| Reference | Topics |
| --- | --- |
| [Build, Vite, and Assets](references/build-vite-and-assets.md) | Optimizer changes, asset paths, QRL processing, Vite options, preload delivery, caching, CLI integrations |
| [JSX, Events, and Serialization](references/jsx-events-and-serialization.md) | Raw stores, build constants, MDX, view transitions, serialization-safe reads |
| [Migration and Packages](references/migration-and-packages.md) | Library publishing, mixed-generation consumers, peer dependencies, Tailwind and Vite upgrades |
| [Reactivity and Async Computations](references/reactivity-and-async.md) | Async computation migration, task options, reactive membership, `untrack()`, computed notifications |
| [Router and Server Behavior](references/router-and-server.md) | Error flow, redirects, rewrites, request events, mocks, origins, navigation caching |

## Breaking changes and deprecations

### Install Vite in the application

`vite` is a peer dependency of Qwik, Qwik City, Qwik React, and Qwik Labs.
Declare it directly in the application so those packages do not resolve
duplicate Vite installations.

Qwik core and Qwik City use Vite 7. Keep the application toolchain on that
major when updating those packages.

### Review generated asset paths

Default built assets use `assets/hash-name.ext`. Update deploy rules, cache
rules, and assumptions about earlier output locations. Content-hashed files
under `build/` and `assets/` normally receive long-lived immutable caching,
unless custom Rollup naming makes their URLs unstable.

### Do not filter library QRL output

A `qwikVite()` `fileFilter` cannot exclude `*.qwik.js`, `*.qwik.mjs`, or
`*.qwik.cjs`. Qwik always processes these library QRL files.

### Rebuild published Qwik libraries

Qwik library builds no longer run the Qwik transform. Publish a fresh build
and, when supporting both package generations, extend the accepted Qwik range
with `| ^2.0.0`. See
[Migration and Packages](references/migration-and-packages.md) for the
dual-runtime dependency arrangement used by V2 consumers of V1 libraries.

### Move asynchronous work out of `useComputed$`

Async `useComputed$` callbacks are deprecated. Reads first made after an
`await` are not tracked, and the initial promise restarts rendering. Use
`useTask$` or `useResource$` for asynchronous work.

```tsx
useTask$(async ({ track }) => {
  const id = track(idSignal);
  await loadItem(id);
});
```

### Remove deprecated task and preload options

The `eagerness` option of `useTask$` is deprecated. Remove it before moving
the application to the next package generation.

`preloadProbability` is deprecated. Limit idle preload concurrency with the
stable `maxIdlePreloads` option instead.

```ts
renderToStream(<Root />, {
  ...opts,
  preload: { debug: true, maxIdlePreloads: 5 },
});
```

### Retire the built-in service-worker prefetch path

Qwik now derives `modulepreload` links from a bundle graph that includes
dynamic imports and path-to-bundle mappings. Built-in service-worker
components are deprecated.

For an uncustomized worker, remove `service-worker.ts` but temporarily keep
`ServiceWorkerRegister` so deployed workers and caches can be removed. Qwik
does not automatically unregister a worker containing custom logic. Add the
integration only when a legacy application still requires a customizable
worker:

```sh
qwik add service-worker
```

## High-value build and delivery changes

### Configure experimental Vite features explicitly

Pass feature names in the `experimental` array:

```ts
qwikVite({ experimental: ['noSPA', 'valibot', 'preventNavigate'] });
```

- `noSPA` supports MPA-only applications that do not use `Link`.
- `valibot` enables the experimental `valibot$` validator.
- `preventNavigate` enables `usePreventNavigate`, which can asynchronously
  block SPA navigation and uses browser dialogs for other unsaved-state exits.

### Understand loader and manifest delivery

SSR loads Qwikloader as a separate bundle. For tests or unusual networking,
embed it with `qwikLoader: 'inline'`.

The bundle graph is emitted as an asset, and `q-manifest.json` includes
generated assets. `core.js` and `preloader.js` references are filtered from
the manifest and bundle graph.

Use `check-client` to verify that the client bundle is current:

```sh
qwik check-client
```

### Set preload priority when needed

Prefetch strategies accept `linkFetchPriority` for generated
`modulepreload` links. Use it when the browser's default priority is not
appropriate for the route's critical bundles.

## High-value runtime changes

### Read stores without subscribing or proxying

Use `unwrapStore()` when an API such as `structuredClone()` or IndexedDB needs
the store's underlying value:

```ts
import { unwrapStore } from '@builder.io/qwik';

const copy = structuredClone(unwrapStore(store));
```

Use `untrack(signal)`, `untrack(store)`, or the callback form with arguments
when a read must not create a reactive subscription:

```ts
const value = untrack(signal);
const result = untrack((a, b) => a + b, 1, 2);
```

### Import build constants from the package root

`isDev`, `isBrowser`, and `isServer` are exported directly from
`@builder.io/qwik`. The older `@builder.io/qwik/build` entry point remains
available.

```ts
import { isBrowser, isDev, isServer } from '@builder.io/qwik';
```

### Account for computed equality

Computed signals notify listeners only when the computed result changes. A
dependency update that produces an equivalent result does not notify those
listeners.

## High-value router and server changes

### Use internal rewrites without changing the visible URL

`RequestEvent.rewrite()` internally redirects request handling while
preserving the URL shown by the browser. Throw the returned result:

```ts
export const onRequest: RequestHandler = async ({ rewrite }) => {
  throw rewrite('/articles/42');
};
```

Several rewrite routes may target the same destination. Invalid fan-in
assumptions in custom route validation should be removed.

### Handle server failures and redirects deliberately

Errors are standardized across `server$` functions and route loaders.
`@plugin` middleware can catch `server$` failures; client calls throw 4xx
statuses and statuses above 500, and status 499 is valid.

The send-request event receives a `Response` even for redirects. Redirects do
not inherit a parent layout's `Cache-Control`; they default to `no-store`.

### Treat the initial previous URL as optional

On the first router render, the previous URL is `undefined`. Guard it before
reading or comparing the value.

## Working method

1. Read `package.json` and confirm the installed Qwik, Qwik City, and Vite
   versions.
2. Inspect `qwikVite()` options, SSR render options, integration commands, and
   deploy cache rules before changing runtime code.
3. Follow the topic reference that matches the affected layer.
4. Preserve application-specific Rollup output naming, custom service-worker
   logic, and cache policy unless the change explicitly replaces them.
5. Run the application's type checks, client build, SSR build, and relevant
   router tests after applying compatibility changes.
