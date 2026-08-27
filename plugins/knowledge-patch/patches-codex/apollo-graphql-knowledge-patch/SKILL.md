---
name: apollo-graphql-knowledge-patch
description: Apollo GraphQL
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Apollo GraphQL Knowledge Patch

Use this skill when changing, upgrading, or debugging Apollo Client, Apollo
Server, Apollo Router, Apollo Connectors, or their integration points. Identify
the affected product and its installed version before applying guidance; these
products have independent release lines.

## How to use this patch

1. Read the project manifest, lockfile, Router configuration, and supergraph
   schema to identify the exact Apollo products in use.
2. Start with the breaking-change and deprecation notes below.
3. Open the topic reference that matches the task. Version attributions in the
   references determine whether an item applies.
4. Prefer project types, schemas, configuration validation, and tests when they
   establish behavior more narrowly than this patch.
5. For migrations, materialize configuration changes and exercise error,
   streaming, cache, and telemetry paths—not only successful queries.

## Reference index

| Reference | Topics |
| --- | --- |
| [Client and React](references/client-react.md) | Client migration, hooks, types, links, cache, SSR, mocks, refetching |
| [Server runtime](references/server-runtime.md) | Server migration, runtime requirements, integrations, incremental delivery, validation limits |
| [Router configuration and security](references/router-configuration-security.md) | Configuration, endpoints, JWT, CORS, HTTP limits, deployment, reloads, authorization |
| [Planning, execution, and demand control](references/planning-execution-demand.md) | Planning limits, coercion, validation, demand cost, error paths, result handling |
| [Caching and persisted queries](references/caching-persisted-queries.md) | Persisted queries, response and entity caches, Redis, invalidation, cache semantics |
| [Connectors and extension points](references/connectors-extensions.md) | Connector mappings, traffic, Rhai, coprocessors, Rust plugins, context keys |
| [Subscriptions and transport](references/subscriptions-transport.md) | Deduplication, WebSockets, multipart streaming, lifecycle limits, HTTP transport |
| [Telemetry and observability](references/telemetry-observability.md) | Metrics, spans, selectors, exporters, error reporting, cardinality |

## Breaking changes and deprecations

### Router configuration migration

Router major-version upgrades do not silently rewrite old configuration. Before
deploying Router v2, run `router config upgrade --diff`, materialize the result,
and use `router config schema` instead of the removed `--schema` flag. Expect
busy routers to reject work rather than queue it. See
[Router configuration and security](references/router-configuration-security.md).

### Router context and plugin migration

Router v2 namespaces built-in context keys under `apollo::...`, removes legacy
metric emission through specially named `tracing` fields, and changes plugin
service construction to build once and clone per request. Migrate custom code,
Rhai, coprocessors, and selectors together. See
[Connectors and extension points](references/connectors-extensions.md).

### Router metrics and exporters

Router v2 replaces or renames many Router-specific instruments with dotted
OpenTelemetry names. Jaeger and later Zipkin export should use OTLP. Do not
carry old dashboard names forward without checking their replacement
attributes. See [Telemetry and observability](references/telemetry-observability.md).

### Apollo Client 4 imports and construction

Install the `rxjs` peer dependency, import React APIs from
`@apollo/client/react`, and import `MockedProvider` from
`@apollo/client/testing/react`. Construct an `HttpLink` explicitly; constructor
shortcuts such as `uri`, `headers`, and `credentials` are gone. Use public
package entry points and run the migration codemod before manual cleanup.

```sh
npm install @apollo/client@latest graphql rxjs
npx @apollo/client-codemod-migrate-3-to-4 src
```

### Apollo Client 4 errors and observables

Client results expose a unified `error`; `ApolloError` and `result.errors` are
gone. Classify combined errors with their `.is()` guards. Network failures obey
`errorPolicy`, watched-query failures arrive through `next`, and Apollo
observables use RxJS semantics. Convert a watched query with `from()` when an
RxJS `Observable` is required.

### Apollo Client 4 React lifecycle

Render-prop components, HOCs, and `ApolloConsumer` are removed. Query lifecycle
callbacks on `useQuery` and `useLazyQuery` are deprecated. `useLazyQuery` is
execute-driven, `notifyOnNetworkStatusChange` defaults to true, and only
subscribed watched queries remain tracked. Review refetch and abort behavior in
[Client and React](references/client-react.md).

### Apollo Client typing declarations

Types are namespaced with their APIs, context is augmented through
`DefaultContext`, and modern query and mutation result shapes depend on declared
default options and effective `errorPolicy`. Do not force obsolete result
generics onto modern signatures; use `TypeOverrides.signatureStyle` only as an
explicit migration choice.

### Apollo Server 5 prerequisites

Upgrade to Node.js 20 or newer and `graphql` 16.11 or newer. Import Express
middleware from `@as-integrations/express4` or `express5`; the standalone server
no longer embeds Express. Published JavaScript targets ES2023. See
[Server runtime](references/server-runtime.md).

### Apollo Server incremental delivery

Incremental delivery is tied to exact GraphQL.js prerelease protocols and the
matching client handler. Apollo Server 5.1 moved from the alpha-2 format to
alpha 9, and later legacy support requires an explicitly configured
compatibility executor. Align server version, GraphQL.js version, `Accept`
header, and Apollo Client incremental handler as one change.

### Removed or renamed configuration

- Replace Router `preview_response_cache` with `response_cache` once using the
  GA configuration.
- Replace `connectors.subgraphs` with `connectors.sources`.
- Replace `persisted_queries.experimental_local_manifests` with
  `persisted_queries.local_manifests`.
- Remove ignored `traffic_shaping.deduplicate_variables`; deduplication is
  always enabled.
- Remove the deprecated Connector v0.4 preview flag; the schema link opts in.
- Replace native Zipkin export with an OTLP endpoint and replace deprecated
  Router OpenTelemetry header helpers with `opentelemetry_http` types.

## High-value current patterns

### Suspense and result completeness

Use `useSuspenseFragment` when a Suspense boundary owns fragment loading.
Client query and hook results expose `dataState` as `empty`, `partial`,
`streaming`, or `complete`; use that discriminator rather than assuming that a
truthy `data` value is complete.

### Error-policy-aware imperative calls

`client.query`, `client.mutate`, `useMutation`, `refetch`, `fetchMore`, and the
`useLazyQuery` execute function specialize result types from their effective
`errorPolicy`. Preserve literal option values and declared defaults so types can
distinguish guaranteed data, optional data, and optional errors.

### Event-driven refetching

Configure a `RefetchEventManager` to opt into focus, online, or custom events.
Set `refetchOn` globally or per watched query, and use event handlers when the
default active-query refetch is not appropriate.

### Router response caching

Use the GA `response_cache` namespace. Treat subgraph `Cache-Control` as the
primary TTL source, with configured TTL only as fallback. Plan for cache-key
regeneration after schema or algorithm changes, and validate selective
invalidation indexes before relying on them operationally.

### Router protection limits

Review recursive-selection, HTTP header, response-body, planning time and
memory, rate, batch, upload, validation, and demand-control limits together.
Their failure status and scope differ: some reject the whole request, some skip
only a subgraph, and some can run in measurement mode.

### Connector version semantics

Connector parsing is selected by the schema's `connect` specification link.
The default moved to v0.3; v0.4 changes selection and object-literal parsing and
does not alter v0.2/v0.3 schemas. Use the migration CLI to distinguish safe
rewrites from mappings that need review.

### Sensitive-data controls

Router sensitive-header masking is enabled by default and applies across logs,
telemetry, coprocessor communication, and trace-header forwarding, but values
copied into coprocessor body or context are outside header masking. Prefer
allowlists for subgraph error extensions and test every response destination.

### Telemetry cardinality and semantics

Use dotted OpenTelemetry instrument names, keep duration units explicit, size
histogram buckets for configured timeouts, and watch the cardinality-overflow
counter. A per-view cardinality limit and aggregation can override the common
settings; raising limits consumes more memory.

### Streaming lifecycle

Subscription deduplication is configurable by header, authentication context,
and subgraph. Cap lifetime when appropriate, preserve the distinction between
GraphQL and transport errors, and monitor end-reason and rejection metrics.

## Verification checklist

- Validate Router YAML with the exact deployed binary.
- Exercise startup failure paths for CORS, telemetry selectors, JWT, and
  removed options.
- Test GraphQL errors, network errors, partial data, deferred chunks, and
  subscription termination separately.
- Test cache hits, stale entries, schema changes, Redis failure, and every
  enabled invalidation index.
- Verify metric names, units, attributes, resource labels, sampling, and
  cardinality in the actual observability backend.
- Compile TypeScript tests for every declared client default and each effective
  `errorPolicy` used by shared wrappers.
- Exercise Connector mappings under the specification version linked by the
  schema, including invalid and missing values.
