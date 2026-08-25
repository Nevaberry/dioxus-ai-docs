# SvelteKit routing and runtime

The versioned runtime behavior in this reference is attributed to
`sveltekit-2.54.0`, `sveltekit-2.55.0`, `sveltekit-2.65.0`,
`sveltekit-2.66.0`, and `sveltekit-2.67.0`.

## Rendering and error boundaries

### Server-rendered boundaries

Error boundaries can catch errors during server rendering. Their fallback can
render instead of letting the error escape the component tree.

## Paths and route types

### Resolve query strings and fragments

`resolve()` from `$app/paths` accepts pathnames containing a search string, a
hash, or both:

```js
import { resolve } from '$app/paths';

const href = resolve('/search?q=svelte#results');
```

### Matcher-narrowed parameters

Page and layout parameters that use matchers are type-narrowed in `$app/types`.
The narrower types flow through `$app/state` and hooks, so matched route
parameters do not require redundant casts.

### Asynchronous rerouting

SvelteKit rerouting can be asynchronous, so route resolution may await data or
other asynchronous decisions.

## Navigation lifecycle

### Initial-load preloading

`preloadCode` can run during the initial page load. Start route-code preloading
before that load completes when doing so helps the next navigation.

### Blur and snapshot ordering

During navigation, SvelteKit blurs the active element before updating the
component. `blur` and `focusout` handlers therefore see the outgoing
component's data. Snapshot restoration occurs after `afterNavigate` callbacks.

## Prerendering

### Root endpoints must return HTML

Prerendering fails when a root `+server.js` returns a non-HTML response. Treat
this as an invalid root prerender surfaced during the build.

### Page and endpoint ambiguity

Prerendering otherwise prefers pages over endpoints. A prerenderable route that
contains both `+page` and `+server` fails early because the output is ambiguous.

### Invalid crawled URLs

Use `prerender.handleInvalidUrl` to control how malformed URLs discovered by the
prerender crawler are handled.

## Environment and browser runtime

### Guard runtime-only validation

Use `building` from `$app/environment` when explicit validation should require a
variable only at runtime:

```js
import { building } from '$app/environment';
import { env } from '$env/dynamic/private';

if (!building && !env.REQUIRED) {
	throw new Error('REQUIRED is not set');
}
```

### Service-worker base paths

`base` from `$service-worker` is available during development as well as
production. Service-worker code can honor the configured base path in both.

## Security policy

### Additional CSP sources

SvelteKit CSP source lists accept `ws:`, `wss:`, and `trusted-types-eval`. Use
them when expressing WebSocket or Trusted Types policy.

### CSP-compatible hydration

Svelte can hydrate applications protected by a Content Security Policy; client
hydration no longer needs to be treated as incompatible with CSP-protected
pages.

## Server instrumentation

SvelteKit applications can emit OpenTelemetry traces. Initialize server-side
observability reliably from `instrumentation.server.ts`.
