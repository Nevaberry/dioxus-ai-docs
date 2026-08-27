# Apollo Client Migration and Runtime APIs

Use this reference for the Client 3-to-4 migration, link and error APIs, runtime compatibility, SSR, incremental delivery, and modern result typing.

## Package and runtime migration

### Apollo Client 4 migration deprecations

Since 3.14.0, warnings and deprecation annotations across `ApolloClient` and React APIs identify behavior that changes or disappears in Client 4. `InMemoryCache` and `MockedProvider` `addTypename`, `canonizeResults`, and use of `fetchPolicy: "standby"` with `client.query` are deprecated.

### Preloaded-query promise conversion moved

Since 3.14.0, replace removed `queryRef.toPromise()` with `preloadQuery.toPromise(queryRef)`.

### Public package boundaries and migration codemod

For the client-v4-migration, install the new `rxjs` peer, move React APIs to `@apollo/client/react`, move `MockedProvider` to `@apollo/client/testing/react`, and stop direct `.js`/`.cjs` imports. Run the migration codemod, then review its link, removal, and client-setup edits.

```sh
npm install @apollo/client@latest graphql rxjs
npx @apollo/client-codemod-migrate-3-to-4 src
```

### Client transport and renamed options are explicit

For the client-v4-migration, constructor shortcuts `uri`, `headers`, and `credentials` are removed; configure an `HttpLink` as `link`. Move `name` and `version` under `clientAwareness`, rename `connectToDevTools` to `devtools.enabled`, and rename `disableNetworkFetches` to `prioritizeCacheValues`.

### React and GraphQL compatibility

Since 4.0.0, React 16 and `graphql` 15 are unsupported. Render-prop `Query`, `Mutation`, and `Subscription`, React HOCs, and `ApolloConsumer` are removed; use hooks and `useApolloClient`.

### Runtime target and development bundles

Client 4 targets environments available since 2023 and Node.js 20+, provides no polyfills, and selects development behavior mainly through package export conditions. Transpile or polyfill for older targets.

## Incremental delivery and subscriptions

### Incremental delivery and masking types are opt-in

For the client-v4-migration, `@defer` requires `incrementalHandler: new Defer20220824Handler()` and initially supports only the 2022-08-24 protocol. Enable custom-link incremental types and GraphQL Code Generator masking types through `TypeOverrides` declaration merging.

```ts
declare module "@apollo/client" {
  interface TypeOverrides extends
    Defer20220824Handler.TypeOverrides,
    GraphQLCodegenDataMasking.TypeOverrides {}
}
```

### RxJS and subscription behavior

For the client-v4-migration, observables move from `zen-observable` to RxJS. `ObservableQuery` is only `Subscribable`; wrap it with `from(observableQuery)` and replace instance operators with `pipe` operators. Subscriptions are deduplicated by default, and a late subscriber does not receive the connection's initial value. Disable per request with `context: { queryDeduplication: false }`.

### Client subscriptions are lazy and restartable

Since 4.0.0, `client.subscribe()` opens its connection only when subscribed. The returned observable has `restart()` to tear down the current link connection and recreate the request.

### GraphQL.js alpha 9 incremental delivery

Since 4.1.0, use `GraphQL17Alpha9Handler` for a server implementing GraphQL.js 17 alpha 9. Keep `Defer20220824Handler` for the older format; a mismatched handler can corrupt or reject results.

### `@stream` support is handler-dependent

Since 4.1.0, `Defer20220824Handler` and `GraphQL17Alpha2Handler` support `@stream`; encountering `@stream` without a handler throws. The older defer protocol has no stream metadata and truncates the existing array on the first chunk, while the stream-aware default merge truncates on the final chunk.

## Errors, lazy execution, and links

### Unified error model

For the client-v4-migration, results expose only `error` and `ApolloError` is removed. Classify grouped failures with `CombinedGraphQLErrors.is(error)` or `CombinedProtocolErrors.is(error)`; network errors pass through, unusual thrown values become `UnconventionalError`, and `ServerError`/`ServerParseError` are classes with `.is()` guards. `ServerError.bodyText` replaces parsed `result`.

### `useLazyQuery` is execute-driven

For the client-v4-migration, option changes do not execute a lazy query. Put `variables` and `context` on `execute`, other options on the hook, and never execute during render or SSR. Unmount or a newer execution aborts in-flight work with `AbortError`; use the returned promise's `.retain()` only when it must finish.

### Links are class-based

For the client-v4-migration, prefer `HttpLink`, `SetContextLink`, `ErrorLink`, `PersistedQueryLink`, and `RemoveTypenameFromVariablesLink` to creator functions. `SetContextLink` receives `(previousContext, operation)`. Use `ApolloLink` static composition; static `concat` is deprecated in favor of `from`, and `from`, `concat`, and `split` require `ApolloLink` instances rather than bare handlers.

### Custom-link operation context changed

For the client-v4-migration, `operation.getContext()` is frozen; call `setContext()`. Replace context `cache`/`getCacheKey` with `operation.client.cache`, use `operation.operationType`, and call `execute(link, request, { client })` with the client third argument.

### GraphQL-over-HTTP response handling is stricter

For the client-v4-migration, HTTP links advertise `application/graphql-response+json,application/json;q=0.9` and interpret status by `Content-Type`. A non-200 `application/json` response becomes `ServerError`; mocks should use production's content type.

### Link errors use one callback value

Since 4.0.0, `ErrorLink` receives one `error` property instead of separate GraphQL, network, and protocol fields. Use combined-error guards; use `LinkError.is(error)` for errors originating in the link chain.

### `ObservableQuery` method replacements

Since 4.0.0, replace removed `ObservableQuery.setOptions()` with public `reobserve()`. Replace `ObservableQuery.result()` with RxJS `from()` plus `firstValueFrom()`.

## SSR, awareness, and test behavior

### Static SSR uses `prerenderStatic`

Since 4.0.0, `prerenderStatic` replaces `getDataFromTree`, `getMarkupFromTree`, and `renderToStringWithData`; it supports Suspense-enabled hooks with React 19 static rendering APIs.

### Enhanced client awareness is sent by default

Since 4.0.0, `HttpLink` and `BatchHttpLink` default `includeExtensions` to `true` and send `extensions.clientLibrary`. Disable this metadata with `enhancedClientAwareness: { transport: false }` where required.

### Mocked responses have realistic latency

For the client-v4-migration, `MockLink` assigns mocks without a delay a random 20–50 ms delay. Set `MockLink.defaultOptions = { delay: 0 }` only when immediate results are required.

### Enhanced client awareness can use headers

Since 4.1.0, enhanced client awareness supports a headers transport as well as request extensions.

### Static rendering exposes the renderer result

Since 4.1.0, `prerenderStatic` returns its `renderFunction` result and reports `aborted` correctly, supporting React 19.2 `resumeAndPrerender` flows.

## Type migration and error-policy-aware results

### Types are namespaced and context uses declaration merging

For the client-v4-migration, types live with APIs (`ApolloLink.Result`, `ApolloClient.Options`, `ObservableQuery.Result`, `useQuery.Options`). Replace the removed `TContext` generic by augmenting `DefaultContext`; the `ApolloClient` cache-shape and `ApolloCache` serialization generics are removed.

### Default-option types require declarations from 4.2

For the client-v4-migration, when `defaultOptions` sets `errorPolicy` or `returnPartialData`, mirror it under `ApolloClient.DeclareDefaultOptions` so result types reflect runtime defaults. A required declaration selects document-inferred signatures that reject manual result generics.

### Explicit signature-style overrides

Since 4.2.0, set `TypeOverrides.signatureStyle: "modern"` for document-inferred, default-aware signatures without a required default declaration. `"classic"` temporarily retains generic-taking signatures, but declarations then do not affect result types.

### Default declarations for multiple clients

Since 4.2.0, model conflicting client defaults as a narrow union. An optional declared property also includes its runtime default—`"none"` for `errorPolicy`—in inferred results.

### `client.query` data follows `errorPolicy`

Since 4.2.0, `client.query` types `data` as non-nullable when effective `errorPolicy` is `"none"`.

### Mutation results follow `errorPolicy`

Since 4.2.0, `ApolloClient.MutateResult<TData, TErrorPolicy>` maps `"none"` to `data: TData` with no error, `"all"` to possibly undefined data and optional error, and `"ignore"` to possibly undefined data with no error. `client.mutate` and `useMutation` use declared mutation defaults unless a call supplies its own `errorPolicy`; `useMutation.Result.error` is `undefined` under `"ignore"`.

### Mutation typing survives optimistic responses

Since 4.2.10, adding `optimisticResponse` to `client.mutate` preserves the error-policy-aware `data` and error return shape.

### Literal-variable queries retain precise option types

Since 4.2.10, modern signatures preserve literal `errorPolicy` and `returnPartialData` when document variables include constant types such as `TypedDocumentNode<Data, { type: "main" }>`. They no longer widen `data`/`dataState`, and they reject unknown options even when another valid property is present.

### Imperative query results follow their error policy

Since 4.2.10, `refetch`, `fetchMore`, and `useLazyQuery`'s execute function specialize return types from the supplied `errorPolicy` instead of always exposing `data: TData | undefined` and `error: ErrorLike | undefined`.
