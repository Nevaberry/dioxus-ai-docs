# Apollo Client Data, Cache, and Refetch Behavior

Use this reference when changing query lifecycles, cache policies, fragments, mutations, mocks, or automatic refetching.

## Hooks, observable queries, and mutations

### Suspense-aware fragment reads

Since 3.13.0, `useSuspenseFragment` is a drop-in replacement for `useFragment` that suspends until the requested fragment data is complete. Put the loading state in a Suspense boundary.

### Query lifecycle callbacks deprecated

Since 3.13.0, `onCompleted` and `onError` on both `useQuery` and `useLazyQuery` are deprecated. Do not build new lifecycle logic around them, and plan to migrate existing uses.

### Type-safe previous data in `ObservableQuery.updateQuery`

Since 3.13.0, the first previous-data callback argument is deprecated because it may be partial despite its complete-data type. Read `previousData` and `complete` from the second argument; return `undefined` to skip an update.

```ts
observableQuery.updateQuery(
  (_unsafe, { previousData, complete }) => complete ? previousData : undefined
);
```

### `useMutation` completion errors reject

Since 3.13.0, an exception from a `useMutation` `onCompleted` callback rejects the mutation promise and is not passed to `onError`. Catch it from the returned promise.

### `useMutation.ignoreResults` deprecated

Since 3.13.0, `ignoreResults` is deprecated and can cause extra renders after removal. For a mutation whose result should not synchronize into component state, use `useApolloClient()` and call `client.mutate()`.

### Multipart query deduplication lasts through completion

Since 3.13.0, deduplication of multipart queries such as `@defer` remains active until the final response chunk, not merely the first chunk.

### Correct `subscribeToMore` callback variable type

Since 3.13.0, `variables` in the second argument of a `subscribeToMore` callback is typed as the parent query's variables, not the subscription's variables.

### Watched-query lifecycle and refetch semantics changed

In the Client 4 migration, `notifyOnNetworkStatusChange` defaults to `true`, and an uncached `ObservableQuery` emits a loading result immediately. Queries are tracked only while subscribed: `"active"` and `"all"` refetches exclude unobserved queries, named standby queries are refetched, and from 4.0.11 a `skipToken` query is excluded until first executed with variables.

### Error policies govern every error source

In the Client 4 migration, network errors obey `errorPolicy`: `none` rejects, `all` resolves with `result.error`, and `ignore` resolves without the error. `ObservableQuery` reports failures in `next` results rather than terminating through `error`; subscription GraphQL errors do likewise, although an unrecoverable network failure can terminate a subscription.

### Result completeness and streaming state

Since 4.0.0, `ObservableQuery` and data-returning React hooks expose `dataState`: `empty` means `data` is `undefined`, `partial` is possible with `returnPartialData`, `streaming` means `@defer` delivery is unfinished, and `complete` means fully satisfied. During streaming, `loading` stays `true` and `networkStatus` is `NetworkStatus.streaming`.

### `fetchMore` options no longer inherit uniformly

Since 4.0.0, `fetchMore` has its own default `errorPolicy: "none"`. Without a replacement query, variables are shallow-merged; with one, supplied variables are used as-is. It throws for a `cache-only` query.

### Mutation contexts can derive from hook defaults

Since 4.1.0, the `context` passed to the mutate function returned by `useMutation` may be a callback receiving the hook-level context, so per-execution fields can extend rather than replace defaults.

```ts
await mutate({ context: base => ({ ...base, urgent: true }) });
```

## Fragments, cache writes, and local state

### Supertype field policies stay isolated

Since 3.14.0, a subtype's field-policy setup no longer overwrites or merges into field policies declared on a supertype.

### Local state is an opt-in subsystem

In the Client 4 migration, `@client` requires `new LocalState({ resolvers })` passed as `localState`. Resolver context is `{ requestContext, client, phase }`; ordinary resolution warns and converts `undefined` to `null`; non-scalar objects require `__typename`; thrown resolver errors become GraphQL errors; and `@export` requires a matching variable definition with non-null values for required variables.

### Custom caches require fragment matching

In the Client 4 migration, custom cache implementations must provide `fragmentMatches`. `InMemoryCache` already does; `LocalState` throws when a custom cache does not.

### Fragment APIs accept richer sources

Since 4.1.0, `useFragment`, `useSuspenseFragment`, and `client.watchFragment` accept an array in `from` and return an index-aligned data array. Fragment watches accept `from: null` and emit `{ data: null, dataState: "complete", complete: true }`. `readFragment`, `watchFragment`, and `updateFragment` expose `from`.

### Cache writes carry extensions into merge functions

Since 4.1.0, `cache.write`, `cache.writeQuery`, and `client.writeQuery` accept `extensions`; field-policy `merge` functions receive them. Extensions received from operations are also forwarded during cache writes.

### Partial array reads preserve `undefined` entries

Since 4.1.0, `InMemoryCache` preserves explicit `undefined` items returned by an array field's `read` function, allowing partial arrays to trigger a network fetch.

### Custom caches coordinate `@client` resolution

Since 4.1.0, a cache `read` for an `@client` field receives `existing: undefined`, so default parameters work. A custom `ApolloCache` may return `true` from `resolvesClientField`; `false` or no implementation makes `LocalState` warn and fall back to `null`.

### Fully skipped queries return an empty object

Since 4.1.0, a query whose every field is skipped returns `{}` rather than `null`; this also prevents `useSuspenseQuery` from suspending indefinitely.

## Mocks and refetch events

### Mock variables are matched in `request.variables`

Since 4.0.0, `MockLink` removes `variableMatcher`. Set `request.variables` to a predicate to match multiple variable sets.

```ts
{ request: { query: QUERY, variables: vars => vars.id !== undefined }, result }
```

### Event-driven query refetching

Since 4.2.0, automatic event refetching is opt-in through `RefetchEventManager`. Built-in `windowFocusSource` and `onlineSource` events refetch active queries by default. `refetchOn` accepts a boolean, an event map, or a predicate receiving the source and payload; local maps merge with `defaultOptions.watchQuery.refetchOn`, so omitted local events retain the default behavior.

```ts
const manager = new RefetchEventManager({
  sources: { windowFocus: windowFocusSource, online: onlineSource },
});
const client = new ApolloClient({ cache, link, refetchEventManager: manager });
useQuery(QUERY, { refetchOn: { windowFocus: true } });
```

### Custom refetch events and handlers

Since 4.2.0, augment `RefetchEvents` for typed custom payloads and provide an Observable source, or register `true` and call `emit()` imperatively. Per-event `handlers` may replace the active-query refetch and receive `matchesRefetchOn`; `defaultHandler` or `setDefaultEventHandler` changes the fallback. A handler returns `RefetchQueriesResult` or `void` to skip refetching.

### Preloaded query refs honor watch-query defaults

Since 4.2.0, `preloadQuery` incorporates declared `DeclareDefaultOptions.WatchQuery` settings. For example, an `errorPolicy: "all"` declaration produces `PreloadedQueryRef<TData, TVariables, "complete" | "streaming" | "empty">`.
