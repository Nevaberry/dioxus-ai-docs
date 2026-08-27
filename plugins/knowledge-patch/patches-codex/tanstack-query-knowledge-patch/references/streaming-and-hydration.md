# Streaming and Hydration

## Creating a streamed query

Query core added `experimental_streamedQuery` in batch `5.66-5.90`. The current
contract uses `streamFn`, has no `maxChunks` option, and requires `initialValue` when
a custom `reducer` is present.

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

`refetchMode: 'replace'` selects replacement behavior for a refetch. Migrate wrappers
and examples away from the earlier `queryFn` name and remove `maxChunks` rather than
silently accepting it.

## Stream reducer and empty-stream guarantees

Batch `5.101.4` tightens the streamed-query execution guarantees:

- the reducer is not executed twice for the same reduction step;
- an empty stream no longer produces `undefined`;
- consumption of `context.signal` is recognized by the query machinery.

The required `initialValue` for a custom reducer provides its meaningful empty-stream
value. Reducers should still be written without relying on duplicate execution for
side effects.

## Reset refetches with initial data

A streamed query preserves an existing error state during a reset refetch when
`initialData` is configured (batch `5.101.4`). Do not treat the presence of initial
data during that transition as proof that the error was cleared.

Because data in an error state is considered stale, render code may show data while
the state remains eligible for retry or refetch behavior.

## Resolution before hydration

When a stream resolves before hydration, the query records `dataUpdatedAt` (batch
`5.101.4`). Consumers that compare timestamps after hydration should rely on the
recorded update time rather than assuming a pre-hydration resolution lacks one.

## SSR and promise hydration

SSR hydration in batch `5.101.4` preserves infinite-query behavior. Hydrating an
already-resolved promise no longer creates a transient pending or fetching report.
This prevents UI and loading indicators from observing a state that does not match
the resolved promise.

Pending queries are also safe across dehydration and rehydration: that sequence no
longer causes unhandled promise rejections. Do not add a catch solely to mask the old
hydration artifact; handle genuine query errors at the intended application boundary.

## Cancellation interaction

Reading a stream's `context.signal` counts as consuming the signal (batch `5.101.4`).
This ensures cancellation-aware stream functions participate in the core's abort
behavior. Infinite-query abort-reason propagation and last-observer teardown are
covered in `cache-cancellation-and-tooling.md`.
