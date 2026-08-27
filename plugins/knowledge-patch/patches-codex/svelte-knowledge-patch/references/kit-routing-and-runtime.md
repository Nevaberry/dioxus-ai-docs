# SvelteKit routing and runtime

## Errors and request state

### Server-rendered error boundaries

Error boundaries can catch failures during server rendering
(`sveltekit-2.54.0`), allowing the boundary fallback to render instead of the
error escaping the component tree.

### Build-time environment guards

`building` from `$app/environment` resolves correctly around explicit
environment validation (`sveltekit-2.65.0`). Guard runtime-only variables so
they may remain unset during a build:

```js
import { building } from '$app/environment';
import { env } from '$env/dynamic/private';

if (!building && !env.REQUIRED) {
	throw new Error('REQUIRED is not set');
}
```

## Paths, parameters, and loading

### Resolve query and hash suffixes

`resolve()` from `$app/paths` accepts a pathname containing a search string, a
hash, or both.

```js
import { resolve } from '$app/paths';
const href = resolve('/search?q=svelte#results');
```

### Keep matcher-narrowed parameter types

Page and layout parameters using matchers are type-narrowed in `$app/types`
(`sveltekit-2.55.0`). The narrower types flow through `$app/state` and hooks,
so matched routes should not need redundant casts.

### Preload code during initial loading

`preloadCode` is callable during initial page load. Start route-code fetching
there when it improves the initial transition rather than waiting until after
the load completes.

## Navigation lifecycle

During navigation, SvelteKit blurs the active element before updating the
component (`sveltekit-2.66.0`). Consequently, `blur` and `focusout` handlers see
the outgoing component's data. Snapshot restoration occurs after
`afterNavigate` callbacks.

SvelteKit rerouting may be asynchronous, so reroute decisions can await data or
other asynchronous work.

## Prerendering

### Validate root endpoints

A prerendered root `+server.js` must return HTML (`sveltekit-2.65.0`). A
non-HTML response at the root makes prerendering fail during the build.

### Avoid page and endpoint ambiguity

Prerendering prefers pages over endpoints. A prerenderable route containing
both `+page` and `+server` now fails early instead of producing ambiguous
output.

### Handle malformed crawl targets

Use `prerender.handleInvalidUrl` to control how malformed URLs discovered by
the prerender crawler are handled (`sveltekit-2.67.0`).

## Browser security and service workers

CSP source lists accept `ws:`, `wss:`, and `trusted-types-eval`. Add them only
when the application policy needs WebSocket or Trusted Types behavior.

`base` from `$service-worker` is available in development as well as
production, so service-worker code can honor a configured base path in both
environments.

## Server observability and protection

Initialize server observability reliably from `instrumentation.server.ts`.
SvelteKit applications can emit OpenTelemetry traces from this instrumentation
path.

Builds made with a non-production `NODE_ENV` still enable CSRF protection
(`svelte-5.56.5-5.56.9-kit-2.70.0-2.70.3`). Custom build environments must not
assume CSRF checks are omitted merely because `NODE_ENV` differs from
`production`.
