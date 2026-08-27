---
name: qwik-knowledge-patch
description: Qwik
version: "1.19.0"
license: MIT
metadata:
  author: Nevaberry
---


# Qwik Knowledge Patch

Use this skill when creating, upgrading, reviewing, or debugging Qwik and
Qwik City applications. Check the breaking changes and deprecations first,
then open the topic reference that matches the work.

## Reference index

| Reference | Topics |
| --- | --- |
| [Async Reactivity and State](references/async-reactivity-and-state.md) | Async computations, tasks, stores, `untrack()`, and computed notifications |
| [Build and Deployment](references/build-and-deployment.md) | Optimizer behavior, Vite options, assets, preloading, manifests, caching, CLI integrations, and deployment |
| [Components and Events](references/components-and-events.md) | MDX components, view-transition events, and error boundaries |
| [Migration and Packaging](references/migration-and-packaging.md) | Library publishing, mixed-generation consumers, and peer dependencies |
| [Router and Navigation](references/router-and-navigation.md) | Navigation blocking, previous URLs, rewrites, and redirect caching |
| [Server and Route Data](references/server-and-route-data.md) | Server errors, middleware responses, route-data caching, mocks, origins, and request events |

## Breaking changes and deprecations

### Do not use async `useComputed$` callbacks

Async `useComputed$` callbacks are deprecated. Reads made after the first
`await` are not tracked, and an initial promise restarts rendering. Move
asynchronous work to `useTask$` or `useResource$`.

### Remove deprecated task eagerness

The `eagerness` option on `useTask$` is deprecated as of 1.13. Remove it from
new work and do not base scheduling behavior on it.

### Migrate away from built-in service-worker prefetching

Automatic bundle preloading now uses `modulepreload` links and the bundle
graph. The built-in service-worker components are deprecated. For an
uncustomized worker, remove `service-worker.ts` but temporarily keep
`ServiceWorkerRegister` so old deployed workers and caches can be removed.
Retain the integration only for custom worker logic.

### Replace deprecated preload probability

The `preloadProbability` SSR option is deprecated as of 1.16.1. Use the
current preload controls, including the stable `maxIdlePreloads` concurrency
limit.

### Update asset and cache rules

Default assets use `assets/hash-name.ext`. Update deployment rules that rely
on older paths. Content-hashed files below `build/` and `assets/` should
normally receive a one-year immutable cache policy unless Rollup output names
have been customized.

### Match the supported Vite major

Qwik core and Qwik City use Vite 7 as of 1.16. Applications must install that
major directly. Vite is a peer dependency of the Qwik packages, which avoids
duplicate Vite imports but makes the application's dependency explicit.

### Republish libraries for current consumers

Qwik library builds stopped applying the Qwik transform as of 1.9. Library
authors should publish a new build and extend the accepted Qwik range with
`| ^2.0.0` where cross-generation consumption is intended.

## Build and deployment quick reference

### Preserve plugin transform ordering

The optimizer accepts `import ... with`, replaces eligible enums with
numbers, and delegates QRL grouping to Rollup. Keep CSS-in-JS and other
Rollup/Vite transforms ordered so they can process source before Qwik.

### Always transform library QRL files

A `qwikVite()` `fileFilter` cannot exclude `*.qwik.js`, `*.qwik.mjs`, or
`*.qwik.cjs`; those library QRL files are always processed.

### Configure experimental features explicitly

Pass feature names through the `experimental` array:

```ts
qwikVite({ experimental: ['noSPA', 'valibot', 'preventNavigate'] });
```

Use `noSPA` only for MPA-only applications that do not use `Link`.
`preventNavigate` enables `usePreventNavigate`, including asynchronous SPA
blocking and browser-dialog fallback for other unsaved-state navigation.

### Tune SSR preload behavior

```ts
renderToStream(<Root />, {
  ...opts,
  preload: { debug: true, maxIdlePreloads: 5 },
});
```

Use `debug` for preload diagnostics and `maxIdlePreloads` to cap concurrent
idle preloads. A prefetch strategy may set `linkFetchPriority` on generated
`modulepreload` links.

### Handle Qwikloader delivery intentionally

SSR normally loads Qwikloader from a separate bundle. Testing and unusual
network environments can opt back into embedding it:

```ts
renderToStream(<Root />, { ...opts, qwikLoader: 'inline' });
```

### Verify generated artifacts

The preloader bundle graph is emitted as an asset, and generated assets appear
in `q-manifest.json`. Current output filters `core.js` and `preloader.js`
references from both the manifest and bundle graph. Run `qwik check-client`
to detect a stale client bundle.

## Reactivity and state quick reference

### Unwrap stores only at integration boundaries

Use `unwrapStore()` when an API such as structured cloning or IndexedDB needs
the store's underlying content:

```ts
import { unwrapStore } from '@builder.io/qwik';

const copy = structuredClone(unwrapStore(store));
```

### Read without subscribing

`untrack()` accepts signals and stores directly, and its callback form accepts
arguments:

```ts
const value = untrack(signal);
const result = untrack((a, b) => a + b, 1, 2);
```

The expression `"prop" in store` has the opposite behavior: it creates a
subscription to changes in that property's presence.

### Expect value-based computed notifications

Computed signals notify listeners only when the computed value changes. A
dependency update that produces the same result does not notify them.

## Router and server quick reference

### Handle an absent previous URL

The router's previous URL is `undefined` on the first render. Guard code that
uses it rather than assuming a prior navigation exists.

### Rewrite without changing the visible URL

Throw the result of `RequestEvent.rewrite()` from the handler:

```ts
export const onRequest: RequestHandler = async ({ rewrite }) => {
  throw rewrite('/articles/42');
};
```

Multiple rewrite routes may target the same destination. The browser-visible
URL remains unchanged.

### Treat redirects as uncacheable by default

Redirects do not inherit a parent layout's `Cache-Control` header and default
to `no-store`. Apply an explicit policy only when the redirect is safe to
cache.

### Expect thrown client-call failures

Client calls to `server$` throw for 4xx statuses and statuses above 500; 499
is accepted. Middleware marked with `@plugin` can catch `server$` failures,
and server-function and route-loader errors use standardized handling.

## Component and integration quick reference

### Customize imported MDX

Imported MDX accepts a `components` prop, JavaScript expressions can read
props, and default-exported MDX layout components are honored:

```tsx
import Content from './markdown.mdx';
import MyComponent from './my-component';

export default component$(() => (
  <Content components={{ MyComponent }} />
));
```

### Listen for view transitions

Qwik emits a `CustomEvent` named `qviewTransition` when a view transition
starts. Use that exact event name for integration listeners.

### Use the framework error boundary

Qwik provides `ErrorBoundary`; `useErrorBoundary` also has corrected behavior
as of 1.13. Prefer these APIs for component-level failure handling.

### Enable optional integrations deliberately

The Tailwind integration supports Tailwind CSS 4, while the CLI can retain
Tailwind CSS 3. Scaffold compiled internationalization with
`qwik add compiled-i18`. Because the Vite `lint` option defaults to `false`,
enable linting explicitly when the build must run it.
