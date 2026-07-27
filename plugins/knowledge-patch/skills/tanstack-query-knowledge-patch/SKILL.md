---
name: tanstack-query-knowledge-patch
description: TanStack Query
version: 5.101.4
license: MIT
metadata:
  author: Nevaberry
---

# TanStack Query Knowledge Patch

Use this skill when implementing, migrating, reviewing, or debugging TanStack Query
core, React adapter, persistence, streaming, hydration, cancellation, or linting code.
Check the installed package version and adapter before applying an API shape, because
several entries replace earlier experimental or deprecated forms.

## Reference Index

| Reference | Topics |
| --- | --- |
| [api-migrations-and-types.md](references/api-migrations-and-types.md) | Removed and deprecated APIs, callback contexts, query filters, persister inference, `NoInfer`, and `skipToken` |
| [runtime-and-observers.md](references/runtime-and-observers.md) | Runtime classification, mount retries, mutation ordering, schedulers, timers, observer enablement, and render-time promises |
| [streaming-and-hydration.md](references/streaming-and-hydration.md) | Streamed-query contract, reducers, empty streams, reset refetches, SSR hydration, and timestamps |
| [cache-cancellation-and-tooling.md](references/cache-cancellation-and-tooling.md) | Persister migration, cancellation rollback, abort reasons, observer teardown, ESLint rules, and native Devtools |

## Breaking Changes and Deprecations First

### Stop importing `NoInfer` from query core

Query core no longer re-exports its custom `NoInfer<T>`. Use TypeScript's global
utility instead, and require TypeScript 5.4 or newer:

```ts
type StableKey<T> = NoInfer<T>
```

Remove imports such as this one:

```ts
// Remove this import.
import type { NoInfer } from '@tanstack/query-core'
```

### Move runtime checks to `environmentManager`

The direct `isServer` export is deprecated as the runtime-checking entry point.
Call `environmentManager.isServer()` for the effective classification. Keep the
legacy export only when a custom detector needs to delegate back to the library's
default value.

```tsx
import { environmentManager, isServer } from '@tanstack/react-query'

environmentManager.setIsServer(
  () => typeof window === 'undefined' && !('chrome' in globalThis),
)

const server = environmentManager.isServer()

// Restore default detection.
environmentManager.setIsServer(() => isServer)
```

`setIsServer` installs a global `() => boolean` callback. Treat it as shared runtime
state, especially in test suites and long-lived processes.

### Update streamed-query options

For the experimental streamed-query helper, use the current contract:

| Earlier form | Current form |
| --- | --- |
| `queryFn` | `streamFn` |
| `maxChunks` | Removed |
| Custom `reducer` without a seed | Supply `initialValue` |

`refetchMode: 'replace'` starts a replacement stream rather than retaining the
previous accumulation.

```tsx
queryFn: experimental_streamedQuery({
  streamFn: async function* () {
    yield 'ready'
  },
  initialValue: [] as string[],
  reducer: (all, chunk) => [...all, chunk],
  refetchMode: 'replace',
})
```

### Migrate fine-grained persistence

Use the `restoreQueries` API exposed by `experimental_createQueryPersister`, with
query filters, in place of `persisterRestoreAll`. The older
`createSyncStoragePersister` API is deprecated. Keep key inference narrow when
wrapping a persister; the current types infer query-function data from the persister
without widening the registered query key.

### Do not prefetch with `skipToken`

React prefetch-query options reject `skipToken` at the type level. A prefetch must
have a valid query function; conditionally skip the prefetch operation itself rather
than passing `skipToken` as that function.

## Callback Context Quick Reference

`QueryFunctionContext` exposes the active `QueryClient` as `client`. Mutation
functions and mutation lifecycle callbacks receive a context argument as well.

```tsx
useMutation({
  mutationFn: (variables, context) => save(variables, context),
  onSuccess: (data, variables, onMutateResult, context) => {},
})
```

In `onSuccess`, the `onMutateResult` argument is typed as defined. When maintaining
wrappers, preserve the full callback arity so the context and optimistic result are
not dropped.

## Runtime and Lifecycle Quick Reference

### Dynamic mount retries

`retryOnMount` accepts a callback, allowing each new observer mount to decide whether
an errored query should retry:

```tsx
const query = useQuery({
  queryKey: ['answer'],
  queryFn: async () => 42,
  retryOnMount: () => true,
})
```

The React adapter honors `retryOnMount` even when `throwOnError` is a function. Do
not assume a functional error policy bypasses the mount-retry decision.

### Mutation start ordering

A local mutation `onMutate` runs synchronously when no global
`mutationCache.config.onMutate` callback is configured. Code that starts local
optimistic work can rely on that ordering only in the absence of the global hook.

### Observer enablement

Read `QueryObserver` result `isEnabled` to inspect whether the observer's current
options enable its query. This reflects observer option state and avoids reconstructing
the enablement decision independently.

### Scheduling and timers

Query core exports `defaultScheduler`. It also exposes `timeoutManager`, through which
applications can replace the timer implementations TanStack Query uses for
`setTimeout` and `setInterval`. Configure timer substitution centrally rather than
patching individual query operations.

## Streaming, Rendering, and Hydration Quick Reference

When consuming streamed queries:

- Reading `context.signal` is recognized as consuming the abort signal.
- The reducer is not run twice for a chunk.
- An empty stream does not resolve to `undefined`.
- A reset refetch with `initialData` preserves an existing error state.
- A stream that resolves before hydration records `dataUpdatedAt`.

With `experimental_prefetchInRender`, promise rejection follows Suspense behavior:
the promise throws only when no data is available. Observing the result's `promise`
also implicitly observes `data`.

SSR hydration preserves infinite-query behavior. Hydrating an already-resolved
promise does not briefly expose pending or fetching state, and dehydrating then
rehydrating a pending query does not cause an unhandled promise rejection.

## Error, Staleness, and Cancellation Quick Reference

- Existing query data is always stale while the query is in an error state.
- Infinite queries propagate `AbortSignal.reason`.
- A paused initial fetch is cancelled when its last observer unsubscribes.
- Cancellation rollback includes intervening manual cache writes.
- Rollback never returns a query to `undefined` data.
- The rollback revert happens synchronously.

These guarantees matter when optimistic updates, manual cache writes, and cancelled
requests overlap. Do not implement an extra asynchronous rollback layer around the
core behavior without checking the resulting ordering.

## Type and Filter Quick Reference

Current `QueryFilters` types support:

- partial query keys;
- `readonly` query keys;
- query-key unions whose tuples have different lengths.

Persister types infer `TQueryFnData` from the persister while deliberately preventing
that persister from widening `TQueryKey`. Narrow registered keys and `DataTag`-branded
wrapper results remain assignable. Preserve these relationships in helper generics
instead of replacing them with a broad `QueryKey`.

## ESLint and Devtools Quick Reference

The query ESLint plugin includes two additional safeguards:

- `no-void-query-fn` rejects query functions that do not return query data.
- `mutation-property-order` enforces the expected ordering of mutation options.

The existing `no-rest-destructuring` rule also detects spread operations. Avoid using
an object spread as a disguised way to subscribe to every result property.

TanStack Query Devtools support Expo and React Native applications. Native projects
do not need to assume the Devtools are browser-only.

## Review Checklist

Before completing a change:

1. Remove query-core `NoInfer` imports and verify TypeScript 5.4 or newer.
2. Replace direct runtime classification with `environmentManager.isServer()`.
3. Check streamed-query option names and seed every custom reducer.
4. Keep mutation and query callback context parameters intact.
5. Do not use `skipToken` in React prefetch options.
6. Verify error-state staleness, cancellation rollback, and observer teardown behavior.
7. Preserve narrow query-key and persister inference in TypeScript wrappers.
8. Enable the applicable query ESLint safeguards.

Load the matching reference before changing subtle lifecycle or generic code; the
reference files contain the complete behavioral constraints behind this checklist.
