# Apollo Router Caching, Traffic, Subscriptions, and Reloads

Use this reference for backpressure, rate limits, persisted queries, query-plan/entity/response caches, Redis, and long-lived subscription traffic.

## Traffic shaping and connections

### Busy routers reject instead of queue

For router-v2-migration, backpressure rejects work when busy instead of retaining it in memory. Stricter shaping may expose more 503/504 responses; monitor CPU and logs, then retune timeouts, concurrency, and rate limits.

### Connector-specific traffic shaping

Since 2.1.0, set connector-wide rules under `traffic_shaping.connector.all` and source rules under `traffic_shaping.connector.sources` using a `subgraph_name.source_name` key. Connector shaping does not support `deduplicate_query`.

### Entity cache keys changed

Since 2.1.0, entity-cache keys separate entity-key fields from representation variables, fixing directive cases such as `@requires`. Distributed query-plan caches use a changed hash, so expect regeneration cost on upgrade.

### Entity caching supports multiple keys

Router 2.1.3 fixes entity caching for types with multiple `@key` directives using different fields.

### Subscription deduplication can ignore headers

Since 2.3.0, list event-irrelevant headers under `subscription.deduplication.ignored_headers`; differences in those headers no longer prevent otherwise identical subgraph subscription deduplication.

### Local persisted-query manifest hot reload

Since 2.1.0, `persisted_queries.hot_reload: true` watches local manifests independently of the Router's `--hot-reload` flag.

### Persisted-query usage by ID

Since 2.2.0, usage reporting groups persisted-query traffic by persisted-query ID.

### Unknown persisted-query errors expose the operation name

Since 2.4.0, with manifest safelisting and APQ disabled, `PERSISTED_QUERY_NOT_IN_LIST` includes `extensions.operation_name` when the request supplied one.

### Safelisted operation bodies count toward persisted-query usage

Since 2.7.0, persisted-query usage includes safelisted operations submitted by body, not only by ID.

### HTTP connection-pool idle lifetime

Since 2.13.0, `pool_idle_timeout` configures idle keep-alive eviction for subgraphs, connector sources, and coprocessors. Default is 15 seconds rather than the earlier fixed 5; `null` disables idle eviction.

### Persisted-query IDs enter request context

Since 2.13.0, the persisted-query layer stores the resolved ID in request context, making it available to Rhai.

### Subgraphs over Unix domain sockets

Since 2.13.0, a subgraph endpoint may use a Unix socket URL whose `path` query parameter carries the request path, for example `unix:///tmp/some.sock?path=some_path`.

### `http2only` uses h2c for cleartext connections

Since 2.13.0, outbound `experimental_http2: http2only` uses HTTP/2 prior knowledge without TLS. Plain `enable` over cleartext still uses HTTP/1.1 because h2c upgrade is unavailable.

### Downstream response-size limits

Since 2.15.0, `limits.subgraph` and `limits.connector` support global and per-destination `http_max_response_size`; no default applies. Old Router-level fields migrate under `limits.router`. An oversized streaming body stops with `SUBREQUEST_HTTP_ERROR`, increments `apollo.router.limits.subgraph_response_size.exceeded` or `apollo.router.limits.connector_response_size.exceeded`, and marks the response span aborted for `response_size_limit`.

### File-upload operation-body timeout

Since 2.15.0, multipart upload `operation_body_timeout` independently bounds reading the operations field. It has no default and returns 504 / `GATEWAY_TIMEOUT` on expiry.

### Variable deduplication configuration deprecated

Since 2.16.0, `traffic_shaping.deduplicate_variables` is deprecated, ignored, and warns at startup because variable deduplication is always enabled. Remove it.

## Response and entity caching

### Entity-cache response headers are normalized

Since 2.6.0, one uncached entity fetch no longer forwards `Cache-Control` unchanged. It follows the common algorithm, emitting `max-age` without `s-maxage`.

### Redis-backed response caching

Since 2.8.0, `preview_response_cache` caches root query fields and entity representations in Redis, using subgraph `Cache-Control` for TTL and cache tags for targeted invalidation. Preview entity-cache deployments can migrate by renaming configuration.

### Entity-cache expiry and key regeneration

Since 2.8.0, an entity response whose `Age` exceeds `Cache-Control: max-age` is not stored. The cache-key version changed, so expect regeneration.

### Redis clients metric replaces connections

Since 2.8.0, `apollo.router.cache.redis.connections` is replaced by `apollo.router.cache.redis.clients`; it counts clients instead of underlying connections and removes `kind`.

### Per-subgraph response-cache key context

Since 2.9.0, `apollo::response_cache::key` may contain `subgraphs`. A subgraph entry replaces rather than merges with `all`, so repeat shared values there.

```json
{ "all": 1, "subgraphs": { "products": { "locale": "be" } } }
```

### Uniform response-cache timeout code

Since 2.9.0, both Tokio and Redis `apollo.router.operations.response_cache.*.error` metrics use code `timeout`.

### Response-cache Redis TTL location

Since 2.9.0, remove ineffective `redis.ttl`; put `ttl` on the relevant `preview_response_cache.subgraph` entry.

### Response caching is generally available

Since 2.10.0, production configuration uses GA namespace `response_cache`, replacing `preview_response_cache`.

### Clustered Redis read replicas

Since 2.10.0, read-only query-plan and response-cache commands go to Redis cluster replicas rather than primaries when replicas exist.

### Selective response-cache invalidation

Since 2.10.0, the invalidation endpoint starts when invalidation is enabled globally or for any named subgraph; `response_cache.subgraph.all.invalidation.enabled` is unnecessary for selected-only invalidation.

### Subgraph-stage cache identity customization

Since 2.10.0, Rhai and coprocessors can customize response-cache identity at subgraph request stage, for example by copying a header into context `private_id`.

### Interface objects participate in response caching

Since 2.10.0, Federation interface objects are entities for response caching, and their representations can form entity keys.

### Nullable entity keys can be cached

Since 2.11.0, response caching accepts nullable `@key` fields. Keep identity shapes unambiguous when a key value is `null`.

### Response-cache invalidation failures are surfaced

Since 2.11.0, invalidation failures return errors instead of remaining silent and may increase `apollo.router.operations.response_cache.invalidation.error`.

### Invalidation payloads reject unknown fields

Since 2.11.0, the invalidation endpoint returns 400 for payload fields outside its schema.

### Response-cache key and TTL semantics

Since 2.12.0, schema changes yield new cache keys; old entries miss rather than serve stale-schema data. Multi-root subgraph responses cache as one unit. Configured TTL is only a fallback when the subgraph omits `Cache-Control: max-age`.

### Additional nullable cache-key shapes

Since 2.13.0, response/entity keys accept a missing nullable field or a nullable list item containing `null`, extending explicit-null support.

### GraphQL errors make cached responses `no-store`

Since 2.13.0, a response with GraphQL errors receives `Cache-Control: no-store` when the response-cache plugin would otherwise emit cache control.

### Cache plugins distinguish `no-store` and `no-cache`

Since 2.13.0, `no-store` may serve an existing entry but prevents storing a new one. `no-cache` prevents serving without revalidation yet permits storage; Router does not perform that revalidation.

### Client `Cache-Control` emission is optional

Since 2.15.0, `response_cache.include_cache_control_header_on_router_response` defaults to `true`; set `false` to suppress `Cache-Control` on client responses without changing Redis, TTL, cache keys, or debugger behavior.

### Selective response-cache invalidation indexes

Since 2.16.0, each subgraph can disable `subgraph`, `type`, or `cache_tag` invalidation indexes; all default on. Disabled kinds skip Redis writes and reject that invalidation request with 400. Re-enabling does not backfill: flush the affected namespace when older entries must participate immediately.

### Response-cache `Cache-Control` semantics

Since 2.16.0, response caching accepts numeric `stale-if-error`, preserves `s-maxage` separately from `max-age`, treats extension-only headers as `no-store`, permits field-qualified `no-cache`, expires future-dated entries, and lets `private` suppress `public`. It reads older boolean-serialized stale directives during rolling upgrades.

### Redis replica routing with even replica counts

Since 2.16.0, Redis clients eagerly connect to replicas, preventing read failures, backend fallthrough, and CPU spikes from lazy round-robin routing with an even replica count.

## Rate limits and subscriptions

### Enforced rate limits return HTTP 429

Since 2.11.0, enforced rate limits again returned 429 / `TOO_MANY_REQUESTS` rather than 503 / `SERVICE_UNAVAILABLE` used since Router 2.0. This was superseded by the later capacity behavior below.

### Capacity rate limiting returns HTTP 503

Since 2.13.0, exceeding router/subgraph rate limits or buffer capacity returns `503 Service Unavailable`, reverting the `429 Too Many Requests` change. Current clients, retries, and alerts should classify it as service load, not client-specific throttling.

### Subscription errors retain their protocol level

Since 2.6.0, in multipart HTTP subscriptions, a GraphQL error immediately followed by termination remains a GraphQL error rather than becoming a fatal transport error.

### WebSocket connection errors propagate without an ID

Since 2.7.0, Router accepts spec-valid `graphql-transport-ws` `connection_error` messages with payload but no `id` and propagates their errors.

### Known-size responses retain `Content-Length`

Since 2.9.0, known-size GraphQL responses use `Content-Length` instead of `transfer-encoding: chunked`; body-size hints are preserved client-to-router and router-to-subgraph.

### Subscription event counter semantics

Since 2.9.0, `apollo.router.operations.subscriptions.events` increments for events but not ping, pong, or close. Router relies on the WebSocket implementation's ping handling and avoids duplicate pongs before acknowledgement.

### WebSocket handshakes propagate trace context

Since 2.11.0, the initial HTTP upgrade to a subgraph carries trace headers. Individual messages on the established connection cannot add propagation headers.

### Subscription request builders restore plugin compatibility

Since 2.11.0, external plugins/crates can again use `SubscriptionTaskParams` with `execution::Request` builders, including tests.

### Subgraph compression headers are added after debugging capture

Since 2.11.0, `traffic_shaping` compression sets `content-encoding`; subgraph requests advertise `gzip`, `br`, or `deflate` via `accept-encoding`. These are added after the debug stack and do not appear in Connectors Debugger.

### AWS API Gateway can front multipart subscriptions

Since 2.13.0, HTTP multipart subscriptions work behind AWS REST API Gateway when response transfer mode is configured for streaming.

### Subscription deduplication can ignore JWT context

Since 2.15.0, decoded JWT claims independently contribute to subscription identity, so `ignored_headers` cannot make authenticated streams share a connection. Set `ignore_auth_context: true` only for non-personalized streams. Dedup defaults and overrides may be configured per subgraph.

### Maximum subscription lifetime

Since 2.15.0, `subscription.max_lifetime` closes a subscription at the configured duration with `SUBSCRIPTION_MAX_LIFETIME_EXCEEDED`; unset remains unlimited.
