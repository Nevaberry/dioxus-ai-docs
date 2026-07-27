# Runtime and Observer Behavior

## Runtime environment management

Query core and the React adapter provide `environmentManager` as a library-level
runtime-environment facility (batch `5.101.4`). Use its `isServer()` method wherever
behavior depends on TanStack Query's effective runtime classification.

The direct `isServer` export is deprecated as that checking API. Batch
`5.101-environment-manager` adds a global override for nontraditional environments,
such as extension workers:

```tsx
import { environmentManager, isServer } from '@tanstack/react-query'

environmentManager.setIsServer(
  () => typeof window === 'undefined' && !('chrome' in globalThis),
)

const server = environmentManager.isServer()

// Restore query core's default result.
environmentManager.setIsServer(() => isServer)
```

`setIsServer` replaces detection globally with a `() => boolean` callback. Restoring
the default means installing a callback that returns query core's exported `isServer`
value; merely ceasing to call the override does not express that restoration.

## Callback-based mount retries

In batch `5.101.4`, `retryOnMount` accepts a callback. The callback decides
dynamically whether an errored query retries when a new observer mounts.

```tsx
const query = useQuery({
  queryKey: ['answer'],
  queryFn: async () => 42,
  retryOnMount: () => true,
})
```

The React adapter also honors `retryOnMount` when `throwOnError` is a function. These
two functional policies are independent: a functional error-throwing policy does not
disable the mount retry decision.

## Mutation `onMutate` ordering

A mutation's local `onMutate` callback is invoked synchronously when there is no
global `mutationCache.config.onMutate` callback (batch `5.101.4`). This makes the
start of local optimistic work deterministic in that configuration.

The guarantee is conditional. When a global `onMutate` exists, do not extrapolate the
same local-only ordering guarantee; account for the cache-level lifecycle hook.

## Observer enablement state

`QueryObserver` results include `isEnabled` (batch `5.66-5.90`). It reports whether
the observer's current options enable its query. Consumers that need to display or
branch on effective enablement should use this result field instead of attempting to
recompute the decision from a subset of options.

## Scheduler and timer customization

Query core exports `defaultScheduler` (batch `5.66-5.90`). It also provides
`timeoutManager`, which lets a consumer replace the `setTimeout` and `setInterval`
implementations used internally by TanStack Query.

Use the manager when an environment supplies custom timers. Keep the substitution at
the library boundary so query operations share one coherent timer implementation.

## Error-state staleness

Existing data is always considered stale after its query enters an error state (batch
`5.101.4`). Do not infer freshness solely from the presence of data or a previous
update timestamp when the current status is error.

This matters for observer and retry logic: stale data can remain renderable while the
query still qualifies for the error-state refetch behavior.

## Render-time promise semantics

With `experimental_prefetchInRender`, batch `5.101.4` aligns promise rejection with
Suspense:

- rejection throws only when no data is available;
- observing the result's `promise` implicitly observes `data`.

Code that reads `promise` must therefore account for data observation even if it does
not separately access the `data` property. Existing data suppresses the no-data throw
path, but it remains stale when the query is in an error state.
