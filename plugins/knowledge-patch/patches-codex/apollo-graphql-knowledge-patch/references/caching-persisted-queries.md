# Caching and Persisted Queries

## Persisted queries and safelists

### Local persisted-query manifest hot reload (2.1.0)

`persisted_queries.hot_reload: true` watches configured local manifests without
a Router restart. It is independent of the process `--hot-reload` flag.

### Persisted-query usage by ID (2.2.0)

Usage reporting is keyed by persisted-query ID, enabling per-ID grouping.

### Unknown persisted-query errors expose the operation name (2.4.0)

With manifest safelisting and APQ disabled, `PERSISTED_QUERY_NOT_IN_LIST`
includes `extensions.operation_name` when the request supplied a name.

### Safelist logs distinguish bypassed enforcement (2.3.0)

Unknown-operation logs include `enforcement_skipped`: false means an external
operation was rejected, true means an internal operation bypassed enforcement.

### Safelisted operation bodies count toward persisted-query usage (2.7.0)

Usage metrics include safelisted operations submitted by body, not only those
submitted by ID.

### Persisted-query IDs enter request context (2.13.0)

The resolved persisted-query ID is stored in request context and is available
to Rhai.

### Local persisted-query manifest key (2.16.0)

Replace deprecated `persisted_queries.experimental_local_manifests` with the
equivalent `persisted_queries.local_manifests`; the former is removed in Router
3.x.

## Response-cache configuration and identity

### Redis-backed response caching (2.8.0)

`preview_response_cache` stores root query fields and entity representations
in Redis, uses subgraph `Cache-Control` for TTL, and supports cache tags for
targeted invalidation. Entity-cache configurations can migrate by renaming
options.

### Response caching is generally available (2.10.0)

Use production `response_cache`; the earlier namespace was
`preview_response_cache`.

### Per-subgraph response-cache key context (2.9.0)

`apollo::response_cache::key` may contain a `subgraphs` map. A named entry
replaces rather than merges with `all`, so repeat common values in overrides.

### Subgraph-stage cache identity customization (2.10.0)

Rhai and coprocessors can customize response-cache identity at subgraph stage,
for example by copying a request header into context `private_id`.

### Response-cache key and TTL semantics (2.12.0)

Schema changes produce new keys instead of serving stale entries. A multi-root
subgraph result is cached as one unit. Configured TTL is only a fallback when
the subgraph omits `Cache-Control: max-age`.

### Client `Cache-Control` emission is optional (2.15.0)

`response_cache.include_cache_control_header_on_router_response` defaults true.
False suppresses the client header without changing Redis, TTL, keys, or
debugger behavior.

## Entity keys and storage behavior

### Entity cache keys changed (2.1.0)

Keys separate entity-key fields from representation variables, fixing cases
such as `@requires`. This changes distributed plan-cache hashing, so upgrades
regenerate keys.

### Entity caching supports multiple keys (2.1.0)

Router 2.1.3 correctly caches types with multiple `@key` directives using
different fields.

### Entity-cache response headers are normalized (2.6.0)

A single uncached entity fetch follows the shared response-header algorithm:
emit `max-age`, omit `s-maxage`, rather than forwarding the subgraph header.

### Entity-cache expiry and key regeneration (2.8.0)

Do not store a response already expired because `Age` exceeds `max-age`. The
fix changes key version, so expect regeneration on upgrade.

### Interface objects participate in response caching (2.10.0)

Federation interface objects are treated as entities and their representations
can form cache keys.

### Nullable entity keys can be cached (2.11.0)

Nullable `@key` fields are accepted. Keep keys simple and avoid identities where
null is ambiguous.

### Additional nullable cache-key shapes (2.13.0)

Keys accept missing nullable fields and null items in nullable lists, extending
support for explicitly null fields.

## Cache-Control semantics

### GraphQL errors make cached responses `no-store` (2.13.0)

When a cacheable response contains GraphQL errors, the Router emits
`Cache-Control: no-store` so intermediaries do not retain partial data.

### Cache plugins distinguish `no-store` and `no-cache` (2.13.0)

`no-store` may serve an existing entry but prevents a new store. `no-cache`
prevents serving without revalidation but permits storage; the Router does not
perform the required revalidation.

### Response-cache `Cache-Control` semantics (2.16.0)

The cache accepts numeric `stale-if-error`, keeps `s-maxage` distinct from
`max-age`, treats extension-only headers as `no-store`, permits field-qualified
`no-cache`, expires future-dated entries, and lets `private` override `public`.
It also reads older Redis entries with boolean stale directives during rolling
upgrades.

## Redis and invalidation

### Clustered Redis read replicas (2.10.0)

Read-only query-plan and response-cache commands use cluster replicas rather
than primaries.

### Redis replica routing with even replica counts (2.16.0)

Clients connect to replicas eagerly, preventing read failure, backend fallback,
and CPU spikes caused by lazy round-robin routing with an even replica count.

### Response-cache Redis TTL location (2.9.0)

The ineffective `redis.ttl` field is removed. Put TTL on the relevant
`preview_response_cache.subgraph` entry for preview-era configurations.

### Selective response-cache invalidation (2.10.0)

The invalidation endpoint starts when invalidation is enabled globally or on
any named subgraph; `response_cache.subgraph.all.invalidation.enabled` is unnecessary when only
selected subgraphs accept invalidation.

### Response-cache invalidation failures are surfaced (2.11.0)

Invalidation failures return an error rather than remaining silent, so
`apollo.router.operations.response_cache.invalidation.error` may increase.

### Invalidation payloads reject unknown fields (2.11.0)

The invalidation endpoint returns HTTP 400 for fields outside its request
schema.

### Selective response-cache invalidation indexes (2.16.0)

Each subgraph can disable `subgraph`, `type`, or `cache_tag` indexes; all default
enabled. Disabled index types skip Redis writes and reject matching invalidation
requests with HTTP 400. Re-enabling does not backfill; flush the affected Redis
namespace first if old entries must participate immediately.

## Cache telemetry

### Cache-Control telemetry selector (2.9.0)

`response_cache_control` exposes computed subgraph Cache-Control values to
custom instruments, for example `max_age` for a seconds histogram.

### Uniform response-cache timeout code (2.9.0)

Tokio and Redis timeouts both report code `timeout` in
`apollo.router.operations.response_cache.*.error`.
