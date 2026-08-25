# Cache, Sessions, Redis, and Filesystems

Cache stores and locks, session behavior, Redis integration, and filesystem adapters.

## Always-deferred flexible cache refreshes (2025-05)

`Cache::flexible()` accepts `alwaysDefer: true` to defer regeneration even when the current execution context would otherwise refresh immediately.

## Bounded filesystem traversal (2025-11)

`Filesystem::files()` and `directories()` accept a custom traversal depth, allowing bounded recursive discovery without switching to an all-depth operation.

```php
$files = File::files($path, depth: 2);
$directories = File::directories($path, depth: 2);
```

## Cache flush events (2025-03)

The new `CacheFlushed` event allows listeners to react when a cache store is flushed.

## Cache TTL contract (13.0-upgrade)

The cache `Store` and `Repository` contracts now include `touch`; custom cache stores must implement TTL extension with `touch($key, $seconds)`.

## Cache-backed sessions (2025-09)

Laravel includes a generic cache session driver, so session storage can use a configured cache store instead of requiring a cache-specific session driver.

```dotenv
SESSION_DRIVER=cache
SESSION_STORE=redis
```

## Cache-lock pruning control (2025-12)

Database-backed locks can opt out of their probabilistic pruning lottery when an application manages pruning separately.

## Cacheable Predis retry settings (2026-07)

Predis retry configuration accepts scalar values, allowing retry settings to be used with `config:cache`.

## Default cache and session identifiers (13.0-upgrade)

Framework fallback cache prefixes, Redis prefixes, and session cookie names now use hyphenated slugs and the suffixes `-cache-`, `-database-`, and `-session`. Applications that need their prior identifiers should explicitly set `CACHE_PREFIX`, `REDIS_PREFIX`, and `SESSION_COOKIE`.

## Driver-independent cache funnels (2026-02)

`Cache::funnel()` provides concurrency limiting with any cache driver instead of requiring a Redis-specific funnel.

## Encoded filesystem URLs (2026-05)

Filesystem-generated URL paths are now URL-encoded, while local adapters preserve directory separators, including when generating temporary URLs.

## Failover cache stores (2025-10)

Laravel includes failover cache support for falling back to another store when the primary store fails. Cache events emitted through failover identify the underlying store that handled the operation.

## Flexible reads through memoized cache stores (2025-05)

Memoized cache stores support `flexible()`, so `Cache::memo()->flexible('settings', [30, 120], fn () => loadSettings())` combines request-local memoization with stale-while-revalidate behavior.

## Local disk fallback root (12.0-upgrade)

When no `local` disk is explicitly configured, its root now defaults to `storage/app/private` instead of `storage/app`. Define the disk and its root explicitly to preserve the old location.

## Local temporary upload URLs (2026-02)

The local filesystem driver supports `temporaryUploadUrl()`, extending temporary upload URL generation beyond remote object-store disks.

## Memoized `Cache` attribute (2026-06)

The `Cache` contextual attribute supports memoization, so repeated attribute-backed reads can use Laravel's memoized cache layer during the same execution.

## Memoized cache stores (2025-04)

`Cache::memo()` wraps a cache store with an in-memory layer for the current execution, avoiding repeated underlying reads for values already resolved.

```php
$value = Cache::memo()->get('settings');
$value = Cache::memo('redis')->get('settings');
```

## Nested scoped disks (12.0.0)

A scoped filesystem disk may now use another scoped disk as its backing disk, allowing scopes to be layered.

## PhpRedis packed-number handling (2025-09)

Laravel exposes PhpRedis's pack-ignore-numbers option, allowing applications using PhpRedis packing to preserve numeric values according to that client option.

## PhpRedis TCP keepalive (2026-03-laravel-12)

The PhpRedis connector accepts a `tcp_keepalive` option, allowing Redis connections to configure TCP keepalive behavior.

## Predis 3 compatibility (2025-05)

Laravel's Redis integration supports `predis/predis` 3.x, so applications can upgrade without switching Redis clients.

## Predis cluster key lookup (2025-11)

`PredisClusterConnection` now implements `keys()`, allowing pattern-based key lookup through Predis-backed Redis cluster connections.

## Redis session prefixes (2026-07)

Redis-backed sessions support a session-specific prefix, allowing their keys to be separated from other Redis data.

## Redis tagged-cache flushing (2025-09)

Redis cache-tag flushes are now atomic, and tagged-cache flushing supports custom Redis connections, avoiding partial concurrent flushes and assumptions about the default connection.

## Refreshable cache locks (2026-06)

Cache locks can refresh their expiration, allowing long-running work to retain a lock without releasing and reacquiring it.

## Restricted cache unserialization (13.0-upgrade)

The default `cache.serializable_classes` value is `false`, so applications that cache PHP objects must allow-list their classes or switch to non-object payloads.

```php
'serializable_classes' => [
    App\Data\CachedDashboardStats::class,
],
```

## Scoped-disk exception behavior (2025-09)

A scoped filesystem disk now passes its `throw` option to the parent disk, so configured write failures throw consistently through the scoped adapter.

## Served-disk URI uniqueness (13.0.0)

Filesystem disks configured for serving must use distinct URIs; Laravel now throws when multiple served disks share a URI.

## Typed cache retrieval (2026-02)

Cache repositories now provide typed getters, allowing cached values to be retrieved through an accessor for the expected value type.

## Wider database cache expirations (2026-03-laravel-12)

Database cache expiration columns now use big integers; custom cache-table migrations should use the same width.
