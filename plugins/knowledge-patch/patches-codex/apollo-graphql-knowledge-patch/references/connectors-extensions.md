# Connectors and Router Extension Points

## Connector adoption and specification versions

### Apollo Connectors are generally available (2.0.0)

Router 2.0 makes Connectors generally available as a declarative way to map REST
services into a supergraph. Preview deployments should follow the Connector GA
upgrade path.

### Connectors default to specification v0.3 (2.14.0)

Unversioned/latest Connector resolution selects `connect/v0.3`; schemas linked
explicitly to `connect/v0.2` remain there.

### Connector v0.4 unifies selections and object literals (2.15.0)

For `connect/v0.4`, nested selections allow commas, object-property shorthand
is valid, and top-level object literals need no `$()` wrapper. A primitive after
`name:` is a literal, not a `$` lookup; qualify lookups explicitly, especially
REST keys that are invalid GraphQL names. V0.2/v0.3 parsing is unchanged.

### Connector v0.4 no longer needs a preview flag (2.16.0)

Linking `https://specs.apollo.dev/connect/v0.4` opts in. Remove deprecated no-op
`connectors.preview_connect_v0_4`.

### Connector v0.4 migration CLI (2.16.0)

The separate `connect-migrate` binary compares selections under their linked
version and v0.4, classifying deterministic `$.` rewrites, unchanged mappings,
and cases needing judgment. It is built from `apollo-federation` with the
non-default `connect-migrate` Cargo feature, not included in Router runtime.

## Connector mapping and execution

### Connector URI expressions and encoding (2.2.0)

Expressions can appear anywhere in or after the URI path, including parameter
names. Results remain percent-encoded; valid literal `[`/`]` are not encoded and
trailing slash is preserved. Some placements require Federation 2.11+.

### Connectors honor response content types (2.3.0)

Types ending `/json` or `+json` parse as JSON; `text/plain` becomes a UTF-8
string available as `$`; other types become null. Missing content type assumes
JSON. Parse failure emits `CONNECTOR_DESERIALIZE` with `Response deserialization
failed`.

### Connector variables work in nested input arguments (2.3.0)

Connector operations can use variables inside nested input arguments.

### Connector context directives are preserved (2.1.0)

Router 2.1.2 preserves `@context` and `@fromContext` when introducing a
Connector; users of these directives need 2.1.2+.

### Connector JSON parsing (2.14.0)

`->jsonParse` converts a JSON string to structured data for immediate selection.
Non-string or invalid input fails and the inferred parsed shape is `unknown`.

```text
payload->jsonParse { users { name } }
```

### Connector string mapping methods (2.15.0)

`->split(separator[, limit])` accepts data-derived separators, splits an empty
separator into UTF-8 characters, and optionally caps output. `->trim`,
`->trimStart`, and `->trimEnd` remove Unicode whitespace. All reject nonstrings.

### Requestless Connector mappings (2.15.0)

An `@connect` without `http` can map arguments or enclosing-object data,
including within nested mutations, without a request. It cannot reference
response body, `$status`, or `$response`; composition rejects those references.

### Recursive Connector input types (2.16.0)

Self-referential input types compose without infinite schema walking; expression
shape inference stops cycles at unknown shape.

### Connector error extensions deep-merge (2.16.0)

When `isSuccess` is false, configured `errors.extensions` deep-merge with
defaults, so a custom nested `http` object retains default `http.status`.

### Connector v0.4 list selection validation (2.16.0)

Composition recognizes fields beneath list-producing arrow methods such as
`->entries` and accepts nested scalar-list projections such as
`data->map(@->map(@->toString))` without treating them as object selections.

## Connector traffic, headers, and TLS

### Connector-specific traffic shaping (2.1.0)

Use `traffic_shaping.connector.all` or `traffic_shaping.connector.sources`
entries keyed
`subgraph_name.source_name`. Connector shaping does not support
`deduplicate_query`.

### Connector TLS and client authentication (2.1.0)

Configure custom CAs and mutual TLS under `tls.connector.sources`, keyed by
`subgraph_name.source_name`, using `certificate_authorities` and
`client_authentication.certificate_chain`/`key`.

### Connector header propagation (2.2.0)

Use `headers.connector.all` or `headers.connector.sources.<subgraph>.<source>`.
Router YAML takes precedence over schema `@connect`/`@source` headers.

### Header propagation paths require a JSONPath root (router-v2-migration)

Body paths in header propagation must start at `$`, for example
`$.extensions.metadata[0].app_name`.

### Connector source configuration key (2.15.0)

Replace deprecated `connectors.subgraphs` with `connectors.sources`; the old key
warns at startup and is removed in Router 3.x.

## Rhai

### Rhai can read and rewrite URI schemes (2.1.0)

`request.uri.scheme` and `request.subgraph.uri.scheme` are readable and writable,
allowing HTTP/HTTPS switching.

### Rhai uses general hot reload (2.1.0)

With process `--hot-reload`, Rhai source edits trigger the same reload mechanism
as schema/config edits.

### Rhai no longer breaks multipart upload content types (2.4.0)

Rhai processing preserves multipart upload `Content-Type`, avoiding invalid
multipart failures.

### Rhai callback duration metric (2.14.0)

`apollo.router.operations.rhai.duration` is a seconds histogram for each
callback; `rhai.stage` and `rhai.succeeded` identify stage and outcome.

### Configurable Rhai string interning (2.14.0)

Set `rhai.intern_strings: false` to avoid the write-lock contention caused by
new strings under high concurrency; interning defaults enabled.

## Coprocessors

### Per-stage coprocessor endpoints (2.8.0)

Router, supergraph, execution, and subgraph stages may each override the global
coprocessor `url`; global-only configurations continue working.

### Coprocessor Unix sockets (2.12.0)

Colocated coprocessors can communicate over Unix domain sockets rather than TCP.

### Connector-stage coprocessors (2.12.0)

`ConnectorRequest` and `ConnectorResponse` stages expose URI, headers, body,
context, and service identity as appropriate through `coprocessor.connector`.

### Non-UTF-8 coprocessor headers degrade gracefully (2.12.0)

`externalize_header_map` warns with the invalid header name and returns all
remaining valid headers instead of failing conversion.

### Coprocessor `context: true` no longer deletes keys (2.13.0)

Context merging preserves returned keys with `context: true`, fixing the 2.10
regression that required `context: deprecated`.

### Selective coprocessor response bodies (2.14.0)

Supergraph, execution, and subgraph response stages can independently request
`body.data`, `body.errors`, and `body.extensions`. Boolean forms remain valid;
only received fields may be modified and omitted fields remain unchanged.

### Response-stage conditions can test request headers (2.13.0)

Response coprocessors and telemetry events may use
`exists: { request_header: x-name }`; the request-stage result is retained for
response evaluation.

### Coprocessor context deletion is stage-scoped (2.16.0)

At parallel subgraph stages, a coprocessor response may delete only context keys
sent to that stage, preserving keys concurrently added elsewhere.

## Rust plugins and service APIs

### Rust plugin APIs and service lifecycle changed (router-v2-migration)

`cargo-scaffold` is gone, though generated plugins still compile. A
`tower::Service` pipeline is built once and cloned per request. Replace:

- `oneshot_checkpoint_async()` with `checkpoint_async()`;
- `OneShotAsyncCheckpointLayer` with `AsyncCheckpointLayer`, adding
  `.buffered()` before `.service(...)`;
- `ExtensionsMutex::lock()` with `with_lock()`, `TestHarness::build()` with
  `build_supergraph()`, and `PluginInit::{new,try_new}()` with
  `{builder,try_builder}()`.

`services::router::Response::map`, `SchemaSource::File.delay`, and
`ConfigurationSource::File.delay` are removed without replacements.
`Context::busy_time`, `Context::enter_active_request`, `BusyTimer`, and
`BusyTimerGuard` are also removed; spans already represent processing duration.

### Rust plugins must emit metrics through OpenTelemetry (router-v2-migration)

`tracing` fields prefixed `counter.`, `histogram.`, `monotonic_counter.`, or
`value.` no longer become metrics and produce an error. Create instruments from
`apollo_router::metrics::meter_provider()`.

### Rust plugin gauges are exported (2.1.0)

Gauges, including `.u64_gauge()`, created through the Router `meter_provider()` are
exported.

### OpenTelemetry HTTP helpers deprecated (2.16.0)

Replace `apollo_router::otel_compat::{HeaderExtractor, HeaderInjector}` with
identical `opentelemetry_http::{HeaderExtractor, HeaderInjector}` 0.31+ types.

## Context compatibility

### Request context keys were namespaced (router-v2-migration)

Migrate plugins, Rhai, coprocessors, and selectors from legacy keys to v2 names:

```text
apollo_authentication::JWT::claims            -> apollo::authentication::jwt_claims
apollo_authorization::authenticated::required -> apollo::authorization::authentication_required
apollo_authorization::scopes::required        -> apollo::authorization::required_scopes
apollo_authorization::policies::required      -> apollo::authorization::required_policies
apollo_operation_id                           -> apollo::supergraph::operation_id
apollo_override::unresolved_labels            -> apollo::progressive_override::unresolved_labels
apollo_override::labels_to_override           -> apollo::progressive_override::labels_to_override
apollo_router::supergraph::first_event         -> apollo::supergraph::first_event
apollo_telemetry::client_name                 -> apollo::telemetry::client_name
apollo_telemetry::client_version              -> apollo::telemetry::client_version
apollo_telemetry::studio::exclude             -> apollo::telemetry::studio_exclude
apollo_telemetry::subgraph_ftv1               -> apollo::telemetry::subgraph_ftv1
cost.actual                                   -> apollo::demand_control::actual_cost
cost.estimated                                -> apollo::demand_control::estimated_cost
cost.result                                   -> apollo::demand_control::result
cost.strategy                                 -> apollo::demand_control::strategy
experimental::expose_query_plan.enabled       -> apollo::expose_query_plan::enabled
experimental::expose_query_plan.formatted_plan -> apollo::expose_query_plan::formatted_plan
experimental::expose_query_plan.plan          -> apollo::expose_query_plan::plan
operation_kind                                -> apollo::supergraph::operation_kind
operation_name                                -> apollo::supergraph::operation_name
persisted_query_hit                           -> apollo::apq::cache_hit
persisted_query_register                      -> apollo::apq::registered
```

Coprocessors can request legacy names with
`context: deprecated` (`true` is a deprecated alias), current names with
`context: all`, none with false, or a `selective` list. Selective current keys
cannot mix with deprecated names.
