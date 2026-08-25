# Apollo Router Connectors, Coprocessors, Rhai, and Plugins

Use this reference for Connector schemas and transport, coprocessor stages, Rhai behavior, and native Rust plugin migrations.

## Apollo Connectors

### Apollo Connectors are generally available

Since 2.0.0, Apollo Connectors are GA and provide a declarative GraphQL model over REST services. Preview deployments should follow the GA upgrade path.

### Connector TLS and client authentication

Since 2.1.0, configure custom CAs and mutual TLS under `tls.connector.sources`, keyed by `subgraph_name.source_name`, with `certificate_authorities` and `client_authentication.{certificate_chain,key}`.

### Connector context directives are preserved

Router 2.1.2 fixes introduction of a Connector dropping `@context` and `@fromContext`; deployments using them need 2.1.2+.

### Connector header propagation

Since 2.2.0, use `headers.connector.all` or `headers.connector.sources.<subgraph>.<source>`. Router YAML overrides headers set by schema `@connect` or `@source`.

### Connector URI expressions and encoding

Since 2.2.0, expressions may appear anywhere in or after the URI path, including query-parameter names. Expression results remain percent-encoded; valid literal `[`/`]` are no longer encoded and trailing slashes are preserved. Some placements require Federation 2.11+.

### Connectors honor response content types

Since 2.3.0, media types ending `/json` or `+json` parse as JSON; `text/plain` becomes a UTF-8 string at `$`; other types become JSON `null`. Missing `Content-Type` assumes JSON. Deserialization failure returns `CONNECTOR_DESERIALIZE` / `Response deserialization failed`.

### Connector variables work in nested input arguments

Since 2.3.0, variables inside nested input arguments are accepted by Connector operations.

### SigV4 configurations recover from the 2.3 regression

Since 2.4.0, Router fixes the 2.3.0 startup/access regression affecting otherwise valid SigV4 service configurations.

### Connector JSON parsing

Since 2.14.0, mapping expressions may apply `->jsonParse` to a JSON string and select from the result. Non-string or invalid JSON fails; inferred shape is `unknown`.

```text
payload->jsonParse { users { name } }
```

### Connectors default to specification v0.3

Since 2.14.0, latest/default Connector resolution selects `connect/v0.3`; schemas explicitly linked to `connect/v0.2` remain there.

### Connector v0.4 unifies selections and object literals

Since 2.15.0, `connect/v0.4` allows commas in nested selections, object-property shorthand, and top-level object literals without `$()`. Primitive values after `name:` are literals, not `$` lookups; qualify intended lookups, especially invalid GraphQL identifiers. v0.2/v0.3 parsing is unchanged.

### Connector string mapping methods

Since 2.15.0, `->split(separator[, limit])` supports dynamic separators, UTF-8 character splitting for an empty separator, and result limits. `->trim`, `->trimStart`, and `->trimEnd` remove Unicode whitespace. All reject non-string inputs.

### Requestless Connector mappings

Since 2.15.0, `@connect` may omit `http` and resolve by applying its `selection` to arguments or enclosing-object data, including nested mutations. Such mappings cannot reference response data, `$status`, or `$response`; composition rejects transport-derived references.

### Connector source configuration key

Since 2.15.0, replace deprecated `connectors.subgraphs` with `connectors.sources`; the old key warns and is scheduled for Router 3.x removal.

### Recursive Connector input types

Since 2.16.0, self-referential Connector input types compose safely; expression shape resolution stops cycles at unknown shape.

### Connector error extensions deep-merge

Since 2.16.0, when `isSuccess` is false, configured `errors.extensions` deep-merges with defaults, so a nested custom `http` object retains default `http.status`.

### Connector v0.4 list selection validation

Since 2.16.0, v0.4 composition recognizes fields under list-producing methods such as `->entries` and does not misclassify nested scalar-list projections such as `data->map(@->map(@->toString))` as object groups.

### Connector v0.4 no longer needs a preview flag

Since 2.16.0, linking `https://specs.apollo.dev/connect/v0.4` opts in. `connectors.preview_connect_v0_4` is a deprecated no-op and should be removed.

### Connector v0.4 migration CLI

Since 2.16.0, the separate `connect-migrate` tool compares a selection under its linked version and v0.4, classifying deterministic `$.` rewrites, unchanged selections, and manual cases. It is not in Router runtime; build it from `apollo-federation` with non-default Cargo feature `connect-migrate`.

## Coprocessors

### Coprocessor execution errors preserve null data

Since 2.2.0, a coprocessor GraphQL execution error returning `data: null` preserves that member in the client response.

### Coprocessor response validation

Since 2.5.0, top-level `coprocessor.response_validation` controls validation of GraphQL responses from coprocessors and defaults on. Subscription termination responses are handled correctly.

### Per-stage coprocessor endpoints

Since 2.8.0, router, supergraph, execution, and subgraph stages may each set a `url` overriding the global URL; global-only configurations remain valid.

### Coprocessor Unix sockets

Since 2.12.0, colocated coprocessors may communicate over Unix domain sockets rather than TCP.

### Connector-stage coprocessors

Since 2.12.0, coprocessors can run at `ConnectorRequest` and `ConnectorResponse`, with connector URI, headers, body, context, and service identity available where appropriate.

### Non-UTF-8 coprocessor headers degrade gracefully

Since 2.12.0, `externalize_header_map` warns with the invalid header name and returns all remaining valid headers instead of failing conversion.

### Coprocessor `context: true` no longer deletes keys

Since 2.13.0, merging a coprocessor response with `context: true` preserves returned keys, fixing the v2.10 regression that required `context: deprecated`.

### Response-stage conditions can test request headers

Since 2.13.0, response-stage coprocessor calls and telemetry events such as `on: response` may use `exists: { request_header: x-name }`; the test is resolved at request time and retained for response evaluation.

### Selective coprocessor response bodies

Since 2.14.0, supergraph, execution, and subgraph response stages can select `body.data`, `body.errors`, and `body.extensions` independently. Boolean `body` remains valid. A coprocessor can change only received fields; omitted fields keep original values.

### Coprocessor context deletion is stage-scoped

Since 2.16.0, at parallel subgraph stages, a coprocessor response may delete only context keys sent to that stage and cannot erase keys concurrently added by another stage.

## Rhai

### Rhai can read and rewrite URI schemes

Since 2.1.0, Rhai exposes `request.uri.scheme` and `request.subgraph.uri.scheme` as read/write, allowing HTTP-to-HTTPS rewrites.

### Rhai uses general hot reload

Since 2.1.0, with `--hot-reload`, Rhai source edits trigger the same Router reload as schema/config changes.

### Rhai no longer breaks multipart upload content types

Since 2.4.0, Rhai preserves multipart upload `Content-Type`, avoiding `invalid multipart request: Content-Type is not multipart/form-data` failures.

### Rhai callback duration metric

Since 2.14.0, `apollo.router.operations.rhai.duration` records every callback in seconds with `rhai.stage` and `rhai.succeeded`.

### Configurable Rhai string interning

Since 2.14.0, `rhai.intern_strings: false` disables default interning and may avoid write-lock contention when high-concurrency workloads continually create new strings.

## Rust plugins and native extensions

### Rust plugin APIs and service lifecycle changed

For router-v2-migration, `cargo-scaffold` is removed, although generated plugins still compile. A `tower::Service` pipeline is built once and cloned per request; construction hooks are not per-request.

- Replace `oneshot_checkpoint_async()` with `checkpoint_async()`.
- Replace `OneShotAsyncCheckpointLayer` with `AsyncCheckpointLayer`; call `.buffered()` before `.service(...)`.
- Replace `ExtensionsMutex::lock()` with `with_lock()`, `TestHarness::build()` with `build_supergraph()`, and `PluginInit::{new,try_new}()` with `{builder,try_builder}()`.
- Removed without listed replacements: `services::router::Response::map`, `SchemaSource::File.delay`, and `ConfigurationSource::File.delay`.
- Remove `Context::busy_time`, `Context::enter_active_request`, `BusyTimer`, and `BusyTimerGuard`; spans already carry processing duration.

### Rust plugins must emit metrics through OpenTelemetry

For router-v2-migration, `tracing` fields prefixed `counter.`, `histogram.`, `monotonic_counter.`, or `value.` no longer convert to metrics and log errors. Create instruments from `apollo_router::metrics::meter_provider()`.

### Rust plugin gauges are exported

Since 2.1.0, gauges created through `apollo_router::metrics::meter_provider()`, including `.u64_gauge()`, are exported.

### OpenTelemetry HTTP helpers deprecated

Since 2.16.0, replace `apollo_router::otel_compat::{HeaderExtractor, HeaderInjector}` with identical `opentelemetry_http::{HeaderExtractor, HeaderInjector}` types from `opentelemetry_http` 0.31+.
