---
name: apollo-graphql-knowledge-patch
description: Apollo GraphQL
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Apollo GraphQL Knowledge Patch

Use this skill when work involves recent Apollo Client, Apollo Server, Apollo Router, or Apollo Connectors behavior. Identify the product and installed version first, then read only the relevant topic reference.

## Reference index

| Reference | Topics |
| --- | --- |
| [client-data-and-cache.md](references/client-data-and-cache.md) | Query and mutation lifecycles, fragments, cache writes, local state, mocks, refetch events |
| [client-migration.md](references/client-migration.md) | Client 4 migration, packages, links, errors, RxJS, incremental delivery, SSR, modern typing |
| [router-caching-and-traffic.md](references/router-caching-and-traffic.md) | Backpressure, traffic shaping, persisted queries, Redis, response/entity caches, subscriptions |
| [router-connectors-and-extensions.md](references/router-connectors-and-extensions.md) | Connector schemas and transport, coprocessors, Rhai, Rust plugins |
| [router-execution-and-delivery.md](references/router-execution-and-delivery.md) | Query planning, demand control, response validation, error paths, deferred delivery |
| [router-migration-and-security.md](references/router-migration-and-security.md) | Router upgrades, configuration, JWT, CORS, HTTP hardening, deployment, reloads |
| [router-observability.md](references/router-observability.md) | Metrics, selectors, spans, errors, exporters, cardinality, sampling |
| [server.md](references/server.md) | Server 5 runtime, integrations, proxying, incremental protocols, execution limits, HTTP hardening |

## Apply this patch

1. Determine whether the task concerns Client, Server, Router, Connectors, or an integration between them.
2. Read the project's manifest and lockfile to identify exact product versions before applying version-gated advice.
3. For upgrades, preserve the intermediate migrations described below and in the product reference; do not jump straight to renamed configuration.
4. For Router changes, check security, traffic, and telemetry defaults together because one upgrade can affect status codes, load shedding, and dashboards.
5. For incremental delivery, align the Client handler, Server GraphQL.js alpha, and `Accept` protocol exactly.
6. Preserve explicit compatibility overrides unless the task authorizes their removal.

## Breaking changes and required migrations

### Apollo Client 4

- Add the `rxjs` peer dependency.
- Import React APIs from `@apollo/client/react` and `MockedProvider` from `@apollo/client/testing/react`.
- Use only public entry points; remove direct `.js` and `.cjs` imports.
- Run `@apollo/client-codemod-migrate-3-to-4`, then inspect every change rather than assuming the codemod covers custom links and local state.
- Replace constructor `uri`, `headers`, and `credentials` with an explicit `HttpLink` supplied as `link`.
- Move client name/version under `clientAwareness`, `connectToDevTools` under `devtools.enabled`, and rename `disableNetworkFetches` to `prioritizeCacheValues`.
- Replace render-prop components, HOCs, and `ApolloConsumer` with hooks and `useApolloClient`.
- Replace `zen-observable` operators with RxJS `pipe` operators. Wrap `ObservableQuery` in `from()` when an RxJS `Observable` is required.
- Replace `ObservableQuery.setOptions()` with `reobserve()` and `result()` with `firstValueFrom(from(query))`.
- Replace removed `ApolloError` and split error properties with the unified `error` value and class guards.
- Use `operation.setContext()` because `getContext()` is frozen; read the cache from `operation.client.cache`.
- Opt into `@client` resolution with `LocalState`, and implement `fragmentMatches` in custom caches.

Read [client-migration.md](references/client-migration.md) before changing public imports, link composition, error handling, SSR, incremental handlers, or result types.

### Apollo Server 5

- Upgrade to Node.js 20+ and `graphql` 16.11+; ensure consumers support ES2023.
- Install `@as-integrations/express4` or `@as-integrations/express5`; middleware is no longer exported from `@apollo/server/express4`.
- Treat `startStandaloneServer` as a Node HTTP integration, not embedded Express.
- Account for built-in `fetch` in usage reporting, schema reporting, and subscription callbacks; old `global-agent` settings no longer proxy those calls.
- Expect invalid variable coercion to return HTTP 400 unless the temporary compatibility option disables it.
- Remove landing-page `precomputedNonce`.
- Add DOM libraries explicitly to integration-test TypeScript projects that rely on them.

Read [server.md](references/server.md) for the required GraphQL.js alpha/protocol pairing, legacy executor setup, coercion and validation limits, and standalone request hardening.

### Apollo Router 2

- Materialize cross-major YAML upgrades with `router config upgrade`; Router does not apply them during major-version startup.
- Replace the removed `--schema` flag with `router config schema`.
- Update context keys to their `apollo::...` names in plugins, Rhai, coprocessors, and telemetry selectors.
- Convert endpoint `:name` parameters to `{name}` and use named braced wildcards.
- Prefix body selector paths used for header propagation with `$`.
- Replace removed remote-supergraph polling with an explicit download-to-local-file workflow when hot reload is required.
- Expect busy Router instances to reject rather than queue work; rollout monitoring must include 503/504 responses and CPU.
- Move deprecated Router metrics and exporters to OpenTelemetry equivalents before upgrading dashboards.

Read [router-migration-and-security.md](references/router-migration-and-security.md) and [router-observability.md](references/router-observability.md) before a major upgrade.

## Apollo Client quick reference

### Query and mutation lifecycle

- Prefer `useSuspenseFragment` when a Suspense boundary should own incomplete-fragment loading.
- Do not add new `useQuery` or `useLazyQuery` `onCompleted`/`onError` logic; those callbacks are deprecated.
- In `updateQuery`, use second-argument `previousData` only when `complete` is true; return `undefined` to skip.
- Catch errors thrown by `useMutation` `onCompleted` through the returned promise.
- Replace `useMutation.ignoreResults` with `client.mutate()` when component result state is unwanted.
- Treat multipart query deduplication as lasting through the final chunk.

### Client 4 result behavior

- Branch on `dataState` (`empty`, `partial`, `streaming`, `complete`) instead of inferring completeness from `data` alone.
- Remember `notifyOnNetworkStatusChange` defaults to true and unobserved queries are not tracked for active/all refetches.
- Put `variables` and `context` on `useLazyQuery`'s execute call; option changes alone do not execute.
- Network and GraphQL failures obey `errorPolicy`; observable query failures normally arrive through `next`, not the observer's error callback.
- `fetchMore` defaults its own error policy to `none`, changes variable merging when a replacement query is supplied, and rejects `cache-only` use.
- Subscription observables are lazy and restartable; default subscription deduplication means a late subscriber misses the connection's initial value.

### Client type precision

- Declare runtime `defaultOptions` under `ApolloClient.DeclareDefaultOptions` when types must reflect them.
- Choose `TypeOverrides.signatureStyle: "modern"` for document-inferred, default-aware APIs; use `classic` only as a migration bridge.
- Keep multi-client default declarations narrow because optional declarations also admit the runtime default.
- Error-policy-aware types specialize `client.query`, mutations, lazy execute, `refetch`, and `fetchMore` results.

Read [client-data-and-cache.md](references/client-data-and-cache.md) for fragments, local fields, cache write extensions, partial arrays, mocks, and `RefetchEventManager`.

## Apollo Server quick reference

### Incremental delivery

- Initial Server 5 incremental delivery is pinned to GraphQL.js alpha.2 and the 2022-08-24 defer protocol.
- Server 5.1 moves to GraphQL.js alpha.9 and protocol v0.2.
- From Server 5.2, legacy protocol support requires both `@yaacovcr/transform` and an explicit `legacyExperimentalExecuteIncrementally` function.
- Match the client handler to the server protocol: an incorrect handler may reject or merge chunks incorrectly.

### Standalone hardening

- Standalone accepts only UTF-8, UTF-16 LE/BE, and UTF-32 LE/BE request bodies.
- Standalone rejects a GET request carrying a non-JSON `Content-Type`; a headerless request remains subject to CSRF-preflight requirements.

## Apollo Router quick reference

### Security and HTTP behavior

- Keep introspection depth protection enabled unless a specific valid query requires otherwise.
- Treat invalid CORS as a startup error and configure per-origin policies explicitly.
- Configure JWT issuers and audiences as lists; validate string/array claim types and use per-JWKS `allow_missing_exp` only deliberately.
- Apply root authorization directives to individual fields when policy must remain subgraph-local.
- Expect strict input-object variable validation and GET content-type enforcement on current releases.
- Configure recursive-selection and downstream body-size limits rather than relying on unlimited input or response sizes.
- Header masking is active by default and spans logs, telemetry, coprocessors, and trace forwarding; copied body/context secrets need separate handling.

### Caching and traffic

- Use GA `response_cache`, not the earlier preview namespace.
- Put response-cache TTL on the subgraph entry; subgraph `Cache-Control: max-age` overrides configured fallback TTL.
- Treat `no-store` and `no-cache` differently: the former can serve old data but forbids storage, while the latter needs unsupported revalidation before serving.
- Plan for cache-key regeneration after schema, entity-key, or expiry algorithm changes.
- Flush a Redis namespace when re-enabling an invalidation index that must cover entries written while disabled.
- Current capacity/rate-limit rejection is HTTP 503; do not retain alerts built around the brief 429 behavior.
- Set `ignore_auth_context` for subscription deduplication only when streams are truly non-personalized.

Read [router-caching-and-traffic.md](references/router-caching-and-traffic.md) before changing Redis topology, cache invalidation, rate limits, subscriptions, or connection settings.

### Connectors and extensions

- Current default Connector resolution uses v0.3; explicitly linked v0.2 schemas remain unchanged.
- In v0.4, primitive object-property values are literals; qualify data lookups explicitly.
- Use the separate `connect-migrate` CLI to classify v0.4 rewrites and manual cases.
- Replace `connectors.subgraphs` with `connectors.sources` and remove the deprecated v0.4 preview flag.
- Use stage-specific coprocessor URLs and selective response bodies when only part of a payload may leave the Router.
- In Rust plugins, emit metrics through the Router OpenTelemetry meter provider and update the one-time cloned service lifecycle.

Read [router-connectors-and-extensions.md](references/router-connectors-and-extensions.md) for Connector content types, mapping syntax, TLS, coprocessor stages, Rhai behavior, and Rust API replacements.

### Execution and demand control

- Use query-planning cancellation `measure` mode before `enforce`; memory ceilings have platform/build constraints.
- Per-subgraph demand limits null only the skipped subgraph values while other work continues.
- Current actual-cost calculation includes intermediate subgraph work unless `response_shape` is selected.
- Enable result-coercion errors when clients should receive schema/value mismatches, including missing merged fields.
- Preserve entity-key and `__typename` dependencies when reasoning about deferred plan reduction.

Read [router-execution-and-delivery.md](references/router-execution-and-delivery.md) for exact planning, cost, response, and error-path behavior.

### Telemetry

- Generic `OTEL_EXPORTER_OTLP_*_ENDPOINT` variables now prevent Router startup; remove inherited values and configure exporters in Router YAML.
- Use `response_errors` and its aggregate selectors instead of capturing entire response bodies where possible.
- Size histogram buckets to cover configured timeouts; defaults stop at 10 seconds.
- Set cardinality limits knowingly, monitor the overflow metric, and remember overflow collapses into an `otel_metric_overflow` series.
- A view without explicit aggregation preserves a counter or gauge's native aggregation.
- Exporter-specific sampling cannot exceed the common trace sampler.
- `http_client` attributes attach to `http_request` and do not support conditions or static selectors.

Read [router-observability.md](references/router-observability.md) before editing dashboards, selectors, custom instruments, exporters, or trace sampling.
