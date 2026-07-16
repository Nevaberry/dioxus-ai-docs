# SvelteKit routing and runtime

## Contents

- [Server rendering](#server-rendering)
- [Paths and route parameters](#paths-and-route-parameters)
- [Navigation and preloading](#navigation-and-preloading)
- [Prerendering](#prerendering)
- [Environment validation](#environment-validation)
- [Security policy](#security-policy)
- [Service workers](#service-workers)
- [Rerouting](#rerouting)
- [Instrumentation](#instrumentation)

## Server rendering

Error boundaries can catch errors during server rendering. When a boundary
catches such an error, its fallback can render instead of letting the error
escape the component tree. This behavior is attributed to
`sveltekit-2.54.0`.

## Paths and route parameters

### Resolve query and hash suffixes

`resolve()` from `$app/paths` accepts a pathname with a search string, a hash,
or both:

```js
import { resolve } from '$app/paths';

const href = resolve('/search?q=svelte#results');
```

This behavior is attributed to `sveltekit-2.54.0`.

### Use matcher-narrowed types

Parameters for pages and layouts that use route matchers are narrowed in
`$app/types`. The narrowed types also flow through `$app/state` and hooks, so
matched parameters do not require redundant casts. This behavior is attributed
to `sveltekit-2.55.0`.

## Navigation and preloading

`preloadCode` may run during the initial page load. Start route-code preloading
before that load completes when doing so improves the transition.

During a navigation, the active element is blurred before the component update.
Consequently, `blur` and `focusout` handlers still observe the outgoing
component's data. Snapshots are restored only after `afterNavigate` callbacks
run.

Initial-load preloading is attributed to `sveltekit-2.65.0`; navigation ordering
is attributed to `sveltekit-2.66.0`.

## Prerendering

### Root response type

Prerendering fails when a root `+server.js` returns a non-HTML response. Treat
such a root endpoint as invalid during the build. This behavior is attributed to
`sveltekit-2.65.0`.

### Page and endpoint ambiguity

Prerendering prefers a page over an endpoint. If the same prerenderable route
contains both `+page` and `+server`, the build fails early rather than producing
ambiguous output. This behavior is attributed to `sveltekit-2.66.0`.

### Invalid crawled URLs

Use `prerender.handleInvalidUrl` to choose how invalid URLs found while crawling
are handled. This extends prerender policy to malformed crawl targets. The
option is attributed to `sveltekit-2.67.0`.

## Environment validation

`building` from `$app/environment` resolves correctly when it guards explicit
runtime environment validation. Runtime-only variables may remain unset during
the build:

```js
import { building } from '$app/environment';
import { env } from '$env/dynamic/private';

if (!building && !env.REQUIRED) {
	throw new Error('REQUIRED is not set');
}
```

This behavior is attributed to `sveltekit-2.65.0`.

## Security policy

SvelteKit CSP source lists accept `ws:`, `wss:`, and `trusted-types-eval`.
Include them when expressing WebSocket or Trusted Types requirements in the
application CSP. This support is attributed to `sveltekit-2.66.0`.

## Service workers

`base` from `$service-worker` is available during development. Service-worker
code can therefore honor a configured base path in development and production.
This behavior is attributed to `sveltekit-2.66.0`.

## Rerouting

SvelteKit rerouting can be asynchronous. Route resolution may await data or
another asynchronous decision before choosing the target route.

## Instrumentation

SvelteKit applications can emit OpenTelemetry traces. Initialize observability
code reliably from `instrumentation.server.ts` so server instrumentation is in
place for application work.
