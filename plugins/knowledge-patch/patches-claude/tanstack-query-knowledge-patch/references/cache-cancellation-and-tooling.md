# Cache Persistence, Cancellation, and Tooling

## Fine-grained persister migration

`experimental_createQueryPersister` exposes `restoreQueries` with query-filter support
in place of `persisterRestoreAll` (batch `5.66-5.90`). Migrate call sites to select
the queries that should be restored rather than preserving the all-at-once method
name in compatibility wrappers.

The older `createSyncStoragePersister` API is deprecated in the same batch. New
persistence code should use the fine-grained persister path.

Current persister generics infer `TQueryFnData` from the persister while preventing
the persister from widening `TQueryKey` (batch `5.101.4`). This keeps narrowed
registered keys and `DataTag`-branded wrapper results assignable. When introducing a
storage abstraction, retain those generic relationships instead of replacing them
with broad data and key types.

## Cancellation rollback semantics

Cancellation rollback was strengthened in batch `5.66-5.90`:

- the rollback snapshot incorporates intervening manual cache updates;
- a rollback never reverts the query to `undefined` data;
- the revert is performed synchronously.

This protects manual cache writes made while a cancellable operation is in flight.
Code following cancellation may observe the reverted state in the same synchronous
flow; do not assume it arrives in a later task.

## Abort reasons and observer teardown

Infinite queries propagate `AbortSignal.reason` (batch `5.101.4`). Cancellation
handlers can inspect the reason instead of receiving an abort with its cause erased.

A paused initial fetch is cancelled when its final observer unsubscribes (batch
`5.101.4`). Do not expect a paused, unobserved initial request to remain queued after
observer teardown.

For streamed queries, reading `context.signal` is recognized as signal consumption.
Together, these behaviors allow stream and infinite-query functions to participate in
reason-preserving cancellation.

## ESLint safeguards

The TanStack Query ESLint plugin expanded in batch `5.66-5.90`:

- `no-void-query-fn` catches query functions that return no data;
- `mutation-property-order` checks mutation option ordering;
- `no-rest-destructuring` now detects spread operations as well as the forms it
  already handled.

An object spread can subscribe code to the whole query result just as rest
destructuring can, so it is not a bypass for the fine-grained access pattern the rule
protects.

## Expo and React Native Devtools

TanStack Query Devtools support Expo and React Native applications (batch
`5.66-5.90`). Native application diagnostics can use the supported Devtools path
rather than assuming the integration is restricted to browser React applications.
