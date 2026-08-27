# Remote queries and commands

The versioned remote-function behavior in this reference is attributed to
`sveltekit-2.53.0`, `sveltekit-2.54.0`, `sveltekit-2.65.0`, and
`sveltekit-2.66.0`.

## Inputs and invocation context

### Optional inputs

The input types of remote `query`, `command`, and `prerender` functions may be
optional. Omit an input when its declared type permits omission.

### Request URL

A remote function receives URL information for the request that invoked it.
URL-dependent logic should use that invocation URL.

### Await template calls explicitly

Calling a remote function in a template does not by itself delay rendering.
Use `await` when the call must finish before output is rendered:

```svelte
<p>{await getSummary()}</p>
```

## Refresh and invalidation

### Cross-query refreshes

A remote query can refresh other remote queries. Use this to keep related
cached results synchronized when one query refreshes.

### `invalidateAll` reset timing

Navigation with `invalidateAll` resets remote queries before navigation begins,
so the next route does not start with stale query state.

### Live reconnects

Active `for await` consumers of `query.live` survive reconnects. Reconnect
completion settles even if the query is offline or interrupted, preventing
`invalidateAll()` from deadlocking. If a reconnect completes without yielding a
value, the query retains its last value.

## Response policy and failures

### Private, non-stored responses

Remote function responses send `cache-control: private, no-store`. Preserve
that policy for personalized query results rather than exposing them to a shared
cache.

### Transport errors retain details

When a remote request fails in transport, SvelteKit preserves the HTTP status
and error body. For example, a `401` or `403` produced by a `handle` hook does
not become a generic `500`.

### Consume failures without awaiting

Reading a failed remote function through `current` or `error` consumes the
failure without causing an unhandled promise rejection. Awaiting the function
is not the only safe consumption path.
