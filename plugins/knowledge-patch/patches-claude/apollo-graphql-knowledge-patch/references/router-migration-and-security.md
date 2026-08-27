# Apollo Router Migration, Configuration, and Security

Use this reference for Router major upgrades, deployment configuration, authentication, HTTP hardening, licensing, and schema/config reload behavior.

## Router 2 upgrade invariants

### Configuration upgrades are explicit

For router-v2-migration, Router no longer applies major-version upgrade migrations while loading configuration. Preview and materialize changes before deployment. Replace removed `--schema` with `router config schema`.

```bash
router config upgrade --diff router.yaml
router config upgrade router.yaml > router.next.yaml
router config schema
```

### Automatic minor-version configuration migration

Since 2.2.0, YAML migrations within the current major are automatic. Cross-major migrations still are not; regularly materialize and commit them with `router config upgrade` before the next major.

### Remote supergraph polling was removed

For router-v2-migration, remove `--apollo-uplink-poll-interval` and `APOLLO_UPLINK_POLL_INTERVAL`. Schemas from `--supergraph-urls` or `APOLLO_ROUTER_SUPERGRAPH_URLS` no longer hot-reload; periodically download to a local file when reload is required.

### Supergraph endpoint parameters use braces

For router-v2-migration, change `:name` path parameters to `{name}` and use a named braced wildcard such as `{*rest}`.

### Header propagation paths require a JSONPath root

For router-v2-migration, body paths used for header propagation must start at `$`, for example `$.extensions.metadata[0].app_name`.

### Request context keys were namespaced

For router-v2-migration, update plugins, Rhai, coprocessors, and telemetry selectors to v2 names:

```text
apollo_authentication::JWT::claims            -> apollo::authentication::jwt_claims
apollo_authorization::authenticated::required -> apollo::authorization::authentication_required
apollo_authorization::scopes::required        -> apollo::authorization::required_scopes
apollo_authorization::policies::required      -> apollo::authorization::required_policies
apollo_operation_id                           -> apollo::supergraph::operation_id
apollo_override::unresolved_labels            -> apollo::progressive_override::unresolved_labels
apollo_override::labels_to_override           -> apollo::progressive_override::labels_to_override
apollo_router::supergraph::first_event         -> apollo::supergraph::first_event
apollo_telemetry::client_name                  -> apollo::telemetry::client_name
apollo_telemetry::client_version               -> apollo::telemetry::client_version
apollo_telemetry::studio::exclude              -> apollo::telemetry::studio_exclude
apollo_telemetry::subgraph_ftv1                -> apollo::telemetry::subgraph_ftv1
cost.actual                                    -> apollo::demand_control::actual_cost
cost.estimated                                 -> apollo::demand_control::estimated_cost
cost.result                                    -> apollo::demand_control::result
cost.strategy                                  -> apollo::demand_control::strategy
experimental::expose_query_plan.enabled        -> apollo::expose_query_plan::enabled
experimental::expose_query_plan.formatted_plan -> apollo::expose_query_plan::formatted_plan
experimental::expose_query_plan.plan           -> apollo::expose_query_plan::plan
operation_kind                                 -> apollo::supergraph::operation_kind
operation_name                                 -> apollo::supergraph::operation_name
persisted_query_hit                            -> apollo::apq::cache_hit
persisted_query_register                       -> apollo::apq::registered
```

Coprocessors may request `context: deprecated` (`true` is a deprecated alias), `context: all`, `false`, or a `selective` list. Selective keys cannot be mixed with deprecated names.

## Authentication and authorization

### JWT failures can be nonfatal

Since 2.1.0, `authentication.router.jwt.on_error` defaults to `Error`; `Continue` ignores processing failures and leaves claims unset. Inspect `apollo::authentication::jwt_status` for the outcome.

### Multiple JWT issuers per JWKS

Since 2.2.0, each `authentication.router.jwt.jwks` entry accepts `issuers`. Singular `issuer` is auto-migrated only for Router 2.x; update it before the next major.

### JWT audience validation

Since 2.4.0, a `jwks` entry may define `audiences`; reject a token when none matches.

### JWT audience arrays and stricter claim types

Since 2.11.0, `aud` may be a string or string array and succeeds if any configured audience matches; `null` and other types fail. `iss` must be a string or `null`, and a string must match configured issuers.

### Per-JWKS missing-expiry policy

Since 2.14.0, `allow_missing_exp: true` on an individual `jwks` entry permits a missing `exp`; a supplied expiration is still enforced.

### Multiple matching JWKS candidates

Since 2.14.0, issuer or audience failure on the first signature-matching JWKS entry does not stop validation. The Router tries other matching entries, supporting shared keys such as Azure AD B2C policies.

### Fully unauthorized requests return null data

Since 2.13.0, when all requested fields are unauthorized, the response has `data: null` and follows configured `errors.response` (`errors`, `extensions`, or `disabled`) and `errors.log`, matching partially unauthorized requests.

### Root-type authorization directives are graph-wide

Since 2.15.0, `@authenticated`, `@requiresScopes`, or `@policy` on a subgraph root `Query`, `Mutation`, or `Subscription` composes onto the shared supergraph root and affects every subgraph's root fields. Put directives on individual root fields for subgraph-local scope.

## Request, schema, and transport hardening

### Security validation is stricter

For router-v2-migration, `limits.introspection_max_depth: true` is the default; set it to `false` only for legitimate deep introspection. Invalid CORS prevents startup. Empty `Content-Type` is rejected earlier as potential CSRF with 400 rather than 415.

### Client batch-size limits

Since 2.1.0, `batching.maximum_size` rejects an oversized whole client batch with 422 and `BATCH_LIMIT_EXCEEDED`. Unset means unlimited.

### Resource-exhaustion query vulnerabilities

Router 2.1.1 fixes query patterns that could exhaust resources. Earlier versions need persisted queries, safelisting, and required IDs all enabled as mitigation:

```yaml
persisted_queries:
  enabled: true
  safelist: { enabled: true, require_id: true }
```

### Configurable HTTP header-read timeout

Since 2.2.0, `server.http.header_read_timeout` replaces the hard-coded 10-second wait while preserving 10 seconds as default.

### Fine-grained subgraph error inclusion

Since 2.2.0, `include_subgraph_errors.all` defines global redaction/extension allowlists and `subgraphs` refines them. Per-subgraph rules can extend or exclude global keys; `deny_extensions_keys` wins over the allowlist; `false` redacts all; omission inherits `all`. Prefer allowlists to avoid exposing unknown sensitive extensions.

### Native planning rejects unknown execution or security links

Since 2.4.0, the native planner rejects unknown `@link` specifications with purpose `EXECUTION` or `SECURITY`. Remove or correct the unknown link.

### Per-origin CORS policies

Since 2.5.0, `cors.policies` can match literal `origins` or regex `match_origins` and apply credentials/headers per origin. Keep a restrictive catch-all after trusted policies.

### Private Network Access per CORS policy

Since 2.9.0, each `cors.policies` entry may enable `private_network_access`; `access_id` and `access_name` are optional.

### HTTP/2 header-list size limit

Since 2.9.0, `limits.http2_max_headers_list_bytes` caps total HTTP/2 request-header size, defaults to 16 KiB, and returns 431 when exceeded.

### HTTP/2 header limits cover every listener

Since 2.10.0, `limits.http2_max_headers_list_bytes` applies to TLS, non-TLS TCP, and Unix-domain-socket listeners; earlier it covered TLS only.

### Query-validation error redaction

Since 2.12.0, `supergraph.redact_query_validation_errors: true` replaces all validation failures with one `invalid query` / `UNKNOWN_ERROR` response.

### Strict input-object variable validation

Since 2.12.0, fields inside input-object variables are validated against their GraphQL types, including unknown-field rejection. Use `supergraph.strict_variable_validation: measure` only to retain non-enforcing behavior during rollout.

### GET request content-type hardening

Router 2.12.1 rejects GraphQL GET requests with any `Content-Type` other than `application/json` plus optional parameters, returning 415. Omitting it remains valid subject to CSRF checks. Prioritize this for cookie or HTTP Basic authentication.

### Client-awareness metadata is validated

Since 2.13.0, invalid client-library names or versions in headers or operation extensions are rejected; producers must send valid values.

### Trailing-slash-tolerant supergraph paths

Since 2.14.0, Router normalizes trailing slashes while matching `supergraph.path`; `/graphql` accepts both `/graphql` and `/graphql/`.

### Recursive-selection limit

Since 2.16.0, `limits.router.max_recursive_selections` configures the fragment-expansion ceiling (default 10,000,000). `limits.router.warn_only: true` makes it warn; `APOLLO_ROUTER_DISABLE_SECURITY_RECURSIVE_SELECTIONS_CHECK` remains an escape hatch.

### Sensitive-header masking

Since 2.16.0, sensitive header values are masked in logs, telemetry, coprocessor messages, and Apollo trace-header forwarding even without a `masking` block. Built-in and configured global/per-subgraph lists are additive unless `replace_defaults: true`; Connectors inherit the parent subgraph rules.

Telemetry selectors may override with `redact: mask` or `redact: allow`. The shared `http_client` layer applies global rules only, and a secret copied into coprocessor body/context is not masked there.

## Deployment, artifacts, and reloads

### Proxied Router release downloads

Since 2.1.0, release downloads may use a remote proxy mirror when GitHub is unreachable from the deployment.

### Health-check endpoints can be disabled again

Since 2.3.0, health-check endpoints can again be disabled after the Router 2.0 plugin conversion temporarily removed that behavior.

### Helm deployment annotations

Since 2.7.0, Helm `deploymentAnnotations` applies to the Deployment; `podAnnotations` remains separate.

### Bookworm builders for DIY Docker images

Since 2.10.0, the DIY Dockerfile pins a Bookworm Rust builder (for example `rust:1.91.1-slim-bookworm`) to match the Bookworm runtime glibc. Generic builders may select a newer glibc and fail with `GLIBC_2.39 not found`.

### OCI tag references reload when their target changes

Since 2.11.0, Router polls mutable OCI tag references, including generated variant and custom tags, and reloads when the tag points to a new artifact, for example `artifacts.apollographql.com/my-org/my-graph:prod`.

### Warning-state licenses enforce restrictions

Since 2.11.0, restricted features are blocked even while a license is in warning state.

### Self-hosted subscriptions are available on every GraphOS plan

Since 2.11.0, all GraphOS plans may use self-hosted Router subscriptions, but the Router must connect to GraphOS with an API key and graph ref because the feature remains licensed.

### Helm `ServiceMonitor` names follow the Router fullname

Since 2.13.0, the chart derives `ServiceMonitor.metadata.name` from `router.fullname`, honoring `nameOverride` and `fullnameOverride`; a default `my-release` changes to `my-release-router`.

### Insecure graph-artifact registries can be allowlisted

Since 2.13.0, trusted registry hostnames can be allowlisted for HTTP artifact pulls, supporting private registries and pull-through caches without broadly permitting insecure transport.

### Failed reloads retry automatically

Since 2.15.0, transient schema or related reload failure retries instead of permanently retaining the previous schema. `reload.max_retries` defaults to 5 (`0` disables, `null` is unlimited), `retry_delay` defaults to 10 seconds, and a new trigger resets the retry budget.

### Local persisted-query manifest key

Since 2.16.0, replace deprecated `persisted_queries.experimental_local_manifests` with behavior-equivalent `persisted_queries.local_manifests`; the old key is scheduled for Router 3.x removal.
