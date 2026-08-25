# Apollo Client and React

## Migration and package boundaries

### Public package boundaries and migration codemod (client-v4-migration)

Apollo Client 4 adds `rxjs` as a peer dependency. Import React APIs from
`@apollo/client/react`, `MockedProvider` from `@apollo/client/testing/react`,
and everything through public entry points rather than direct `.js` or `.cjs`
paths. Install dependencies and run the migration codemod:

```sh
npm install @apollo/client@latest graphql rxjs
npx @apollo/client-codemod-migrate-3-to-4 src
```

### Client transport and renamed options are explicit (client-v4-migration)

The `ApolloClient` constructor no longer accepts `uri`, `headers`, or
`credentials` shortcuts. Pass an `HttpLink`; move `name` and `version` under
`clientAwareness`, rename `connectToDevTools` to `devtools.enabled`, and rename
`disableNetworkFetches` to `prioritizeCacheValues`.

### Runtime target and development bundles (client-v4-migration)

The package targets environments available since 2023 and Node.js 20+, ships no
polyfills, and selects development behavior primarily through package export
conditions. Transpile or polyfill for older targets.

### React and GraphQL compatibility (4.0.0)

React 16 and `graphql` 15 are unsupported. `Query`, `Mutation`, and
`Subscription` render-prop components, React HOCs, and `ApolloConsumer` are
removed; use hooks and `useApolloClient`.

### Apollo Client 4 migration deprecations (3.14.0)

Client 3.14 warns about Client 4 removals throughout `ApolloClient` and React
APIs. `InMemoryCache`/`MockedProvider` `addTypename`, `canonizeResults`, and use
of `standby` with `client.query` are deprecated.

## Query and hook lifecycle

### Query lifecycle callbacks deprecated (3.13.0)

Avoid `onCompleted` and `onError` on `useQuery` and `useLazyQuery`; both options
are deprecated. Derive effects from result state or handle the execution
promise as appropriate.

### `useLazyQuery` is execute-driven (client-v4-migration)

Changing hook options does not execute a query. Put `variables` and `context`
on `execute`, all other options on the hook, and never execute during render or
SSR. Unmount or a newer execution aborts in-flight work with `AbortError`; call
`.retain()` on the returned promise only when it must finish.

```ts
const [execute] = useLazyQuery(QUERY, { fetchPolicy: "no-cache" });
const result = await execute({ variables, context }).retain();
```

### Watched-query lifecycle and refetch semantics changed (client-v4-migration)

`notifyOnNetworkStatusChange` defaults to `true`, and an uncached
`ObservableQuery` immediately emits loading. Queries are tracked only while
subscribed: `active`/`all` refetches omit unobserved queries, named standby
queries are included, and from 4.0.11 a `skipToken` query remains excluded until
its first execution supplies variables.

### Result completeness and streaming state (4.0.0)

Query-returning React hooks and `ObservableQuery` expose `dataState`: `empty`
means undefined data, `partial` requires partial-return behavior, `streaming`
means `@defer` work remains, and `complete` means fully satisfied. During
streaming, `loading` stays true and `networkStatus` is
`NetworkStatus.streaming`.

### `fetchMore` options no longer inherit uniformly (4.0.0)

`fetchMore` has its own default `errorPolicy: "none"`. Variables shallow-merge
without a replacement query; with a replacement query, supplied variables are
used as-is. Calling it for `cache-only` throws.

### `ObservableQuery` method replacements (4.0.0)

Replace `ObservableQuery.setOptions()` with public `reobserve()`. Replace
`ObservableQuery.result()` with RxJS conversion and
`firstValueFrom(from(observable))`.

### Event-driven query refetching (4.2.0)

Automatic focus/online refetching is opt-in through `RefetchEventManager` and
the built-in `windowFocusSource` and `onlineSource`. `refetchOn` accepts a
boolean, per-event map, or predicate. Per-query maps merge with
`defaultOptions.watchQuery.refetchOn`; omitted events continue to follow a
default boolean or predicate.

### Custom refetch events and handlers (4.2.0)

Augment `RefetchEvents` with custom payload types and provide an Observable
source, or register `true` and call `emit()` imperatively. Per-event handlers
can replace active-query refetching and receive `matchesRefetchOn`;
`defaultHandler`/`setDefaultEventHandler` changes the fallback. Return a
`RefetchQueriesResult`, or `void` to skip.

### Preloaded query refs honor watch-query defaults (4.2.0)

`preloadQuery` incorporates declared `DeclareDefaultOptions.WatchQuery` values.
For example, `errorPolicy: "all"` yields a ref type whose states include
`"complete" | "streaming" | "empty"`.

### Fully skipped queries return an empty object (4.1.0)

When all fields are skipped, result data is `{}` rather than `null`. This also
prevents `useSuspenseQuery` from suspending forever.

## Mutations and error policy

### `useMutation` completion errors reject (3.13.0)

If `onCompleted` throws, the mutation promise rejects; the thrown callback
error is not passed to `onError`. Handle it from the returned promise.

### `useMutation.ignoreResults` deprecated (3.13.0)

Use `useApolloClient()` and `client.mutate()` when a mutation result should not
synchronize into component state. Leaving deprecated `ignoreResults` in place
after removal can add rerenders.

### Mutation contexts can derive from hook defaults (4.1.0)

The mutate function's `context` can be a callback receiving hook-level context,
so execution-specific fields can extend rather than replace defaults.

```ts
await mutate({ context: defaults => ({ ...defaults, urgent: true }) });
```

### `client.query` data follows `errorPolicy` (4.2.0)

With effective `errorPolicy: "none"`, `client.query` types `data` as
non-nullable.

### Mutation results follow `errorPolicy` (4.2.0)

`ApolloClient.MutateResult<TData, TErrorPolicy>` maps `none` to guaranteed data
and no error, `all` to optional data and error, and `ignore` to optional data
without error. `client.mutate` and `useMutation` use declared mutation defaults
unless the call overrides them; `useMutation.Result.error` is undefined under
`ignore`.

### Mutation typing survives optimistic responses (4.2.10)

Adding `optimisticResponse` to `client.mutate` no longer widens the
error-policy-aware return type.

### Imperative query results follow their error policy (4.2.10)

`refetch`, `fetchMore`, and the `useLazyQuery` execute function specialize
their results from the supplied `errorPolicy`, instead of always exposing
optional data and error.

## Errors and observables

### RxJS and subscription behavior (client-v4-migration)

Apollo moved from `zen-observable` to RxJS. `ObservableQuery` is only a
`Subscribable`; wrap it in `from()` for RxJS APIs and replace instance operators
with `pipe` operators. Subscriptions deduplicate by default, and a late joiner
does not receive the connection's first server value. Set
`context.queryDeduplication: false` to opt out per subscription.

### Unified error model (client-v4-migration)

Results expose only `error`; `ApolloError` is removed. Use guards such as
`CombinedGraphQLErrors.is(error)`, `CombinedProtocolErrors.is(error)`, `ServerError.is`, and
`ServerParseError.is`. Network errors pass through, unusual thrown values
become `UnconventionalError`, and `ServerError.bodyText` replaces parsed
`result`.

### Error policies govern every error source (client-v4-migration)

Network errors follow `errorPolicy`: `none` rejects, `all` resolves with
`result.error`, and `ignore` resolves without it. `ObservableQuery` reports
failures in `next` rather than terminating through observer `error`.
Subscription GraphQL errors behave likewise, though unrecoverable network
failure may terminate a subscription.

### Link errors use one callback value (4.0.0)

`ErrorLink` callbacks receive one `error` property. Use combined-error guards
to classify it and `LinkError.is(error)` for failures originating in the link chain.

## Types and signatures

### Types are namespaced and context uses declaration merging (client-v4-migration)

Use API-owned names such as `ApolloLink.Result`, `ApolloClient.Options`,
`ObservableQuery.Result`, and `useQuery.Options`. The `TContext` generic is
removed; augment `DefaultContext`. Client cache-shape and cache serialization
generics are also removed.

### Default-option types require declarations from 4.2 (client-v4-migration)

Declare `defaultOptions` values such as `errorPolicy` and `returnPartialData`
under `ApolloClient.DeclareDefaultOptions` so result types reflect them. A
required declaration selects document-inferred modern signatures, which reject
manual result generics.

### Explicit signature-style overrides (4.2.0)

Set `TypeOverrides.signatureStyle` to `"modern"` for document-inferred,
default-aware signatures without a required default declaration. `"classic"`
temporarily preserves generic-taking signatures, but declared defaults then no
longer affect return types.

### Default declarations for multiple clients (4.2.0)

For clients with conflicting defaults, declare a narrow union. Optional
properties include the runtime default—`"none"` for `errorPolicy`—in inferred
results.

### Literal-variable queries retain precise option types (4.2.10)

Modern signatures preserve literal `errorPolicy` and `returnPartialData` when
document variables include constant types, keeping precise `data`/`dataState`.
They also reject unknown options even when another option is valid.

### Correct `subscribeToMore` callback variable type (3.13.0)

The second callback argument's `variables` are typed as the parent query's
variables, not the subscription's variables.

### Type-safe previous data in `ObservableQuery.updateQuery` (3.13.0)

The first previous-data argument is deprecated because it may be partial while
typed as complete. Use `previousData` and `complete` from the second argument;
returning `undefined` is explicitly supported to skip an update.

## Links, HTTP, and incremental delivery

### Links are class-based (client-v4-migration)

Prefer link classes over creator functions. `SetContextLink` uses
`(previousContext, operation)`. Use `ApolloLink` static composition; static
`concat` is deprecated in favor of `from`, and `from`/`concat`/`split` require
`ApolloLink` instances rather than bare handlers.

### Custom-link operation context changed (client-v4-migration)

`operation.getContext()` is frozen; mutate via `setContext()`. Use
`operation.client.cache` instead of context `cache`/`getCacheKey`, inspect
`operation.operationType`, and call `execute(link, request, { client })`.

### GraphQL-over-HTTP response handling is stricter (client-v4-migration)

HTTP links advertise `application/graphql-response+json,application/json;q=0.9`
and interpret status using the response media type. A non-200
`application/json` response becomes `ServerError`; mocks should use production
content types.

### Incremental delivery and masking types are opt-in (client-v4-migration)

`@defer` requires `incrementalHandler: new Defer20220824Handler()`. Enable
custom-link incremental and code-generator masking types through `TypeOverrides`
declaration merging; Client 4 initially supports the 2022-08-24 protocol.

### Multipart query deduplication lasts through completion (3.13.0)

For multipart queries such as `@defer`, query deduplication remains active until
the final response chunk.

### GraphQL.js alpha 9 incremental delivery (4.1.0)

Use `GraphQL17Alpha9Handler` for the GraphQL.js 17 alpha-9 format. Older formats
still need `Defer20220824Handler`; mismatches can produce malformed results.

### `@stream` support is handler-dependent (4.1.0)

`Defer20220824Handler` and `GraphQL17Alpha2Handler` support `@stream`; using it
without a handler throws. The older defer protocol has no stream metadata and
truncates on the first chunk, while the stream-aware default merge truncates on
the final chunk.

### Enhanced client awareness is sent by default (4.0.0)

`HttpLink` and `BatchHttpLink` default `includeExtensions` to true and add
`extensions.clientLibrary`. Disable transport metadata with
`enhancedClientAwareness.transport: false` when needed.

### Enhanced client awareness can use headers (4.1.0)

Enhanced awareness supports header transport as well as request extensions.

### Client subscriptions are lazy and restartable (4.0.0)

`client.subscribe()` connects only after subscription. The returned observable
has `restart()` to tear down and recreate its link request.

## Cache, fragments, and local state

### Suspense-aware fragment reads (3.13.0)

`useSuspenseFragment` replaces `useFragment` when a Suspense boundary should own
loading and waits until requested fragment data is complete.

### Preloaded-query promise conversion moved (3.14.0)

Replace removed `queryRef.toPromise()` with
`preloadQuery.toPromise(queryRef)`.

### Supertype field policies stay isolated (3.14.0)

Subtype field policies no longer overwrite or merge into the declared field
policy of a supertype.

### Fragment APIs accept richer sources (4.1.0)

`useFragment`, `useSuspenseFragment`, and `client.watchFragment` accept arrays in
`from` and return index-aligned arrays. Watches accept `from: null` and emit a
complete null result. `readFragment`, `watchFragment`, and `updateFragment`
expose `from`.

### Cache writes carry extensions into merge functions (4.1.0)

`cache.write`, `cache.writeQuery`, and `client.writeQuery` accept `extensions`,
which reaches field-policy merge options. Operation extensions are forwarded
during normal cache writes too.

### Partial array reads preserve `undefined` entries (4.1.0)

`InMemoryCache` preserves explicit `undefined` array items returned by field
`read`, allowing partial arrays to trigger a network fetch.

### Local state is an opt-in subsystem (client-v4-migration)

`@client` requires `new LocalState({ resolvers })` in `localState`. Resolver
context is `{ requestContext, client, phase }`; undefined becomes null with a
warning, nonscalar objects need `__typename`, thrown errors become GraphQL
errors, and `@export` needs a matching variable definition and non-null values
for required variables.

### Custom caches require fragment matching (client-v4-migration)

Custom caches must implement `fragmentMatches`; `LocalState` throws otherwise.
`InMemoryCache` already implements it.

### Custom caches coordinate `@client` resolution (4.1.0)

Cache reads for `@client` receive undefined rather than forced null. A custom
cache can return true from `resolvesClientField`; otherwise unresolved local
fields warn and fall back to null.

## SSR and testing

### Static SSR uses `prerenderStatic` (4.0.0)

Replace `getDataFromTree`, `getMarkupFromTree`, and `renderToStringWithData`
with `prerenderStatic`, which supports Suspense-enabled hooks and React 19
static rendering.

### Static rendering exposes the renderer result (4.1.0)

`prerenderStatic` returns its `renderFunction` value and reports `aborted`
correctly, supporting React 19.2 `resumeAndPrerender` flows.

### Mocked responses have realistic latency (client-v4-migration)

Mocks without explicit delay wait a random 20–50 ms. Set
`MockLink.defaultOptions = { delay: 0 }` only when immediate global behavior is
required.

### Mock variables are matched in `request.variables` (4.0.0)

`variableMatcher` is removed. Put a predicate in `request.variables` to match
multiple variable values.
