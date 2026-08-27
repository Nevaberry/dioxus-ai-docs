# Router Configuration, Security, and Deployment

## Configuration and lifecycle

### Configuration upgrades are explicit (router-v2-migration)

Router v2 does not apply upgrade migrations while loading configuration.
Preview with `router config upgrade --diff router.yaml`, materialize and commit
the upgraded file, and use `router config schema` instead of removed `--schema`.

### Automatic minor-version configuration migration (2.2.0)

Within one Router major, YAML migrations are applied automatically. Cross-major
migrations are not; regularly materialize changes with `router config upgrade`
before a major-version boundary.

### Busy routers reject instead of queue (router-v2-migration)

V2 backpressure rejects work rather than retaining it in memory, and stricter
traffic shaping can expose more HTTP 503/504 responses. Monitor CPU and logs,
then retune timeouts, concurrency, and rate limits for the workload.

### Remote supergraph polling was removed (router-v2-migration)

Remove `--apollo-uplink-poll-interval` and `APOLLO_UPLINK_POLL_INTERVAL`.
Supergraphs from `--supergraph-urls` or `APOLLO_ROUTER_SUPERGRAPH_URLS` no longer
hot reload; download remote schemas periodically to a local file when reloads
are needed.

### OCI tag references reload when their target changes (2.11.0)

The Router can poll mutable OCI tags—including generated variant and custom
tags—and reload when the referenced digest changes, enabling promotion by tag,
for example `artifacts.apollographql.com/my-org/my-graph:prod`.

### Failed reloads retry automatically (2.15.0)

Transient schema or related reload failures enter a retrying state. Defaults
are `reload.max_retries: 5` and `retry_delay: 10s`; zero disables retries, null
allows unlimited retries, and a new trigger resets the budget.

### Proxied Router release downloads (2.1.0)

Release downloads can use a remote proxy mirror when GitHub is unreachable from
the deployment environment.

### Bookworm builders for DIY Docker images (2.10.0)

Pin custom Rust builders to a Bookworm variant such as
`rust:1.91.1-slim-bookworm` so builder and runtime glibc match. Generic builders
can produce `GLIBC_2.39 not found` at startup.

### Helm deployment annotations (2.7.0)

Use chart `deploymentAnnotations` for Deployment metadata and `podAnnotations`
for pod metadata.

### Helm `ServiceMonitor` names follow the Router fullname (2.13.0)

`ServiceMonitor.metadata.name` uses the `router.fullname` helper and honors
`nameOverride`/`fullnameOverride`; a default release `my-release` changes from
`my-release` to `my-release-router`.

### Insecure graph-artifact registries can be allowlisted (2.13.0)

Explicitly allow trusted registry hostnames when graph artifacts must be pulled
over HTTP, such as a private registry or pull-through cache.

## HTTP listeners, paths, and connections

### Supergraph endpoint parameters use braces (router-v2-migration)

Use `/foo/{bar}/baz` instead of `:bar`; wildcards must be named and braced, for
example `/foo/{*rest}`.

### Trailing-slash-tolerant supergraph paths (2.14.0)

`supergraph.path` matching normalizes a trailing slash, so `/graphql` and
`/graphql/` reach the same configured endpoint.

### Configurable HTTP header-read timeout (2.2.0)

`server.http.header_read_timeout` controls header read time and defaults to the
previous hard-coded 10 seconds.

### HTTP/2 header-list size limit (2.9.0)

`limits.http2_max_headers_list_bytes` caps total HTTP/2 request-header size,
defaults to 16 KiB, and returns HTTP 431 when exceeded.

### HTTP/2 header limits cover every listener (2.10.0)

`limits.http2_max_headers_list_bytes` applies to TLS, cleartext TCP, and Unix-domain-socket
listeners; before 2.10 it covered TLS only.

### GET request content-type hardening (2.12.0)

Router 2.12.1 rejects GraphQL GET requests with any `Content-Type` other than
`application/json` plus optional parameters, returning 415. Omitting the header
is still valid subject to CSRF checks. Treat this as security-critical for
cookie or Basic-authenticated graphs.

### Subgraphs over Unix domain sockets (2.13.0)

Subgraph URLs may use Unix sockets. Put the HTTP request path in the URL's
`path` query parameter, for example `unix:///tmp/some.sock?path=some_path`.

### HTTP connection-pool idle lifetime (2.13.0)

`pool_idle_timeout` controls idle keep-alive eviction for subgraphs, Connector
sources, and coprocessors. It defaults to 15 seconds rather than 5; null disables
idle eviction.

### `http2only` uses h2c for cleartext connections (2.13.0)

`experimental_http2: http2only` uses HTTP/2 prior knowledge without TLS for
subgraph, Connector, and coprocessor traffic. Plain `enable` without TLS remains
HTTP/1.1 because no h2c upgrade is performed.

### Known-size responses retain `Content-Length` (2.9.0)

Known-size GraphQL bodies keep `Content-Length` instead of chunked encoding;
body-size hints survive client-to-router and router-to-subgraph paths.

### Downstream response-size limits (2.15.0)

Set `limits.subgraph` and `limits.connector` global/per-destination
`http_max_response_size`; there is no default. Old Router-level fields migrate
under `limits.router`. Oversized streaming bodies stop early with
`SUBREQUEST_HTTP_ERROR`, increment the corresponding
`apollo.router.limits.subgraph_response_size.exceeded` or
`apollo.router.limits.connector_response_size.exceeded` metric, and mark the response
span aborted for `response_size_limit`.

### File-upload operation-body timeout (2.15.0)

`preview_file_uploads.protocols.multipart.limits.operation_body_timeout` bounds
only reading the operations field. It has no default and returns HTTP 504 with
`GATEWAY_TIMEOUT` when exceeded.

## CORS and request authentication

### Per-origin CORS policies (2.5.0)

`cors.policies` applies distinct rules using literal `origins` or regex
`match_origins`, so trusted sites can receive credentials or broader headers
while a catch-all remains restrictive.

### Private Network Access per CORS policy (2.9.0)

Each `cors.policies` entry can enable `private_network_access`; `access_id` and `access_name`
are optional.

### Security validation is stricter (router-v2-migration)

`limits.introspection_max_depth: true` is the default; disable only for legitimate deep
introspection. Invalid CORS prevents startup. Empty `Content-Type` is rejected
earlier as possible CSRF with HTTP 400 rather than 415.

### JWT failures can be nonfatal (2.1.0)

`authentication.router.jwt.on_error` defaults to `Error`. `Continue` ignores
JWT-processing errors, leaves claims unset, and records the outcome in
`apollo::authentication::jwt_status`.

### Multiple JWT issuers per JWKS (2.2.0)

Each `authentication.router.jwt.jwks` entry accepts `issuers`. Singular `issuer` auto-migrates during
Router 2.x but should be upgraded before the next major.

### JWT audience validation (2.4.0)

Each JWKS entry can declare `audiences`; a token is rejected when its `aud`
matches none.

### JWT audience arrays and stricter claim types (2.11.0)

`aud` may be a string or string array and passes when any value matches;
`null`/other types fail. `iss` must be string or null, and a string must match
configured issuers.

### Per-JWKS missing-expiry policy (2.14.0)

`allow_missing_exp: true` on a JWKS entry accepts tokens lacking `exp`; supplied
expiry values are still validated.

### Multiple matching JWKS candidates (2.14.0)

When JWKS entries reuse signing keys, issuer/audience failure on the first
signature match does not end validation; remaining matching entries are tried.

### Client-awareness metadata is validated (2.13.0)

Invalid client library names or versions in headers or operation extensions are
rejected. Metadata producers must emit valid values.

### Root-type authorization directives are graph-wide (2.15.0)

`@authenticated`, `@requiresScopes`, or `@policy` on a subgraph root type
composes onto the shared supergraph root and affects fields from all subgraphs.
Apply directives to individual root fields for subgraph-local policy.

### Fully unauthorized requests return null data (2.13.0)

If every selected field is unauthorized, the Router returns `data: null` and
honors configured `errors.response` (`errors`, `extensions`, or `disabled`) and
`errors.log`, matching partial-authorization behavior.

### Fine-grained subgraph error inclusion (2.2.0)

`include_subgraph_errors.all` can define message redaction and an extension
allowlist, then named `subgraphs` can refine it. Named rules may extend the
allowlist or `exclude_global_keys`; `deny_extensions_keys` overrides the global
allowlist, `false` redacts everything, and an omitted subgraph inherits `all`.
Prefer allowlists because denylists can expose unforeseen sensitive fields.

### Warning-state licenses enforce restrictions (2.11.0)

Restricted features are blocked even in license warning state; using one now
returns an error rather than continuing.

## Resource and traffic limits

### Client batch-size limits (2.1.0)

`batching.maximum_size` rejects an oversized whole client batch with HTTP 422
and `BATCH_LIMIT_EXCEEDED`; unset remains unlimited.

### Enforced rate limits return HTTP 429 (2.11.0)

At this point in the release line, rate-limit enforcement returned HTTP 429
`TOO_MANY_REQUESTS` rather than the Router 2.0-era 503
`SERVICE_UNAVAILABLE`. Update retry and alert
classification when running this version.

### Capacity rate limiting returns HTTP 503 (2.13.0)

Router 2.13 again returns HTTP 503 when router/subgraph rate or buffer capacity
is exceeded. Classify this as service load rather than client-specific
throttling. This supersedes the 2.11 behavior for later versions.

### Recursive-selection limit (2.16.0)

`limits.router.max_recursive_selections` sets the fragment-expansion ceiling;
default remains 10,000,000. `limits.router.warn_only: true` warns instead of
rejecting, and `APOLLO_ROUTER_DISABLE_SECURITY_RECURSIVE_SELECTIONS_CHECK`
remains an escape hatch.

### Sensitive-header masking (2.16.0)

Header masking is active even without a `masking` block across logs, telemetry,
coprocessors, and Apollo trace-header forwarding. The built-in case-insensitive
list combines with global/per-subgraph additions unless `replace_defaults: true`;
Connectors inherit their parent subgraph. Telemetry selectors may override with
`redact: mask` or `redact: allow`. The shared `http_client` layer applies only
global rules, and secrets copied into coprocessor body/context are not masked.

### Resource-exhaustion query vulnerabilities (2.1.0)

Router 2.1.1 fixes simple-query denial-of-service paths. Earlier releases need
all three mitigations: persisted queries enabled, safelist enabled, and
`require_id: true`.

### Variable deduplication configuration deprecated (2.16.0)

Remove `traffic_shaping.deduplicate_variables`. It is deprecated, ignored, and
warns at startup because variable deduplication is always enabled.

## TLS, proxies, and service connectivity

### SigV4 configurations recover from the 2.3 regression (2.4.0)

Router 2.4 fixes the 2.3.0 regression that rejected some valid SigV4
configuration and blocked SigV4 services.

### Subgraph compression headers are added after debugging capture (2.11.0)

`traffic_shaping` sets `content-encoding`; every subgraph request advertises
`gzip`, `br`, or `deflate` through `accept-encoding`. These are added after the
debug stack, so they do not appear in the Connectors Debugger.

### GraphOS OTLP exporters honor HTTP proxies (2.14.0)

HTTP-based GraphOS OTLP export respects `HTTP_PROXY`, `HTTPS_PROXY`, and
`NO_PROXY`. TLS-inspecting proxies require their root certificate in the Router
trust store.
