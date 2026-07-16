# Remote queries and commands

## Contents

- [Inputs and request context](#inputs-and-request-context)
- [Template rendering](#template-rendering)
- [Refresh and invalidation](#refresh-and-invalidation)
- [Caching and failures](#caching-and-failures)
- [Live-query reconnects](#live-query-reconnects)

## Inputs and request context

The input types for remote `query`, `command`, and `prerender` functions may be
optional. Callers may omit an input when the declared type permits omission.

Remote functions receive URL information for their actual invocation. Code that
depends on the pathname, search parameters, or other URL state should use that
request context rather than reconstructing it from unrelated application state.

The optional-input and URL-context behavior is attributed to
`sveltekit-2.53.0`.

## Template rendering

Calling a remote function in a template no longer delays rendering by itself.
Explicitly await the call when the rendered result must wait for completion:

```svelte
<p>{await getSummary()}</p>
```

An unawaited invocation can proceed without gating the template. This behavior
is attributed to `sveltekit-2.54.0`.

## Refresh and invalidation

### Cross-query refresh

A remote query can refresh other remote queries. Use this to keep related cached
results synchronized when refreshing one result invalidates another.

### Navigation invalidation

Navigation with `invalidateAll` resets remote queries before navigation starts.
The destination route therefore does not begin with stale query state left over
from the previous route.

These refresh and reset semantics are attributed to `sveltekit-2.65.0`.

## Caching and failures

### Response cache policy

Remote function responses send:

```http
cache-control: private, no-store
```

This prevents personalized remote-query results from being stored by shared
caches.

### Transport errors

When a remote function request fails during transport, SvelteKit preserves its
HTTP status and error body. For example, a `401` or `403` produced by a `handle`
hook remains that failure instead of becoming a generic `500`.

### Consume failures without awaiting

Reading a failed remote function through `current` or `error` consumes the
failure without causing an unhandled promise rejection. Awaiting the function is
not the only safe way to observe a failure.

The cache and failure behavior is attributed to `sveltekit-2.65.0`.

## Live-query reconnects

Active `for await` consumers of `query.live` survive reconnects. Reconnect
completion settles even when the query is offline or interrupted, preventing
`invalidateAll()` from deadlocking. If a reconnect finishes without yielding a
new value, the query keeps its last value.

These reconnect semantics are attributed to `sveltekit-2.66.0`.
