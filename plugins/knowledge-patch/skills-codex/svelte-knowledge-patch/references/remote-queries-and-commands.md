# Remote queries and commands

## Inputs and invocation context

### Optional inputs

Remote `query`, `command`, and `prerender` inputs may be omitted when the
declared input type permits it (`sveltekit-2.53.0`). Keep the type optional
when no argument is a valid call rather than supplying a placeholder value.

### Request URLs

Remote functions receive the actual invocation URL. URL-dependent behavior can
use that request context rather than reconstructing or assuming the location.

## Rendering and consumption

### Await template calls that gate output

A remote function call in a template does not delay rendering just because it
was invoked (`sveltekit-2.54.0`). Use an explicit `await` when its completion
must gate output.

```svelte
<p>{await getSummary()}</p>
```

### Consume failures without rejection noise

Reading a failed remote function through `current` or `error` consumes the
failure without producing an unhandled promise rejection. Awaiting the remote
function is not the only safe consumption path.

## Refresh and invalidation

### Refresh related queries

One remote query can refresh other remote queries (`sveltekit-2.65.0`). Use
cross-query refreshes when related cached results must stay synchronized.

### Reset before invalidating navigation

Navigation with `invalidateAll` resets remote queries before navigation starts,
so the destination does not begin with stale query state.

## Cache and transport behavior

Remote function responses carry `cache-control: private, no-store`, preventing
personalized query results from entering shared caches. Override this only with
a deliberate understanding of the data's audience.

When transport fails, SvelteKit preserves the HTTP status and response body.
Failures such as `401` or `403` from a `handle` hook remain those failures
instead of becoming a generic `500`.

## Live-query reconnects

Active `for await` consumers of `query.live` survive reconnects
(`sveltekit-2.66.0`). Reconnect completion settles even when a query is offline
or interrupted, preventing `invalidateAll()` from deadlocking. When a reconnect
completes without yielding a new result, the query retains its last value.
