# Platform configuration and operations

Source batch: `official-changelog-2025-current`.

## Settings Store

3.4 introduces `SettingsStore` for global and scoped configuration. Read and
write permissions are added later, and the Dashboard gains a management page
in 3.6.

Since 3.4.2, prefer the context-first service signatures. The old order
remains temporarily accepted:

```ts
SettingsStoreService.get<T>(ctx, key)
SettingsStoreService.getMany(ctx, keys)
SettingsStoreService.set<T>(ctx, key, value)
SettingsStoreService.setMany(ctx, values)
```

## Required database migrations

- The 3.4 Settings Store needs a new table.
- 3.4 adds indexes for `Order.orderPlacedAt` and `JobItem.createdAt`.
- DefaultCachePlugin users upgrading through 3.2 need `precision(3)` on
  `CacheItem.expiresAt`.
- 3.6 provides `migrateAssetTranslationData()` for its asset-translation
  change.

## Server lifecycle hooks

`BootstrappedEvent` signals server readiness. `onBeforeAppListen` exposes the
Nest application immediately before listening starts.

## Scheduled tasks and job queues

Scheduled tasks can be triggered manually, receive a `RequestContext`, and
include a built-in database job-cleanup task.

Job options support priority. BullMQ honors configured Redis prefixes for both
queue and buffer storage.

## Telemetry and tracing

3.3 introduces `@vendure/telemetry-plugin` plus tracing across services,
cache, scheduled tasks, and job queues.

Core later adds anonymous telemetry collection and expands it to schema v2
with heartbeat, strategy, integration, feature-adoption, and other signals.

## GraphiQL

`@vendure/graphiql-plugin` is available as a standalone package.

## Public core exports

Core publicly exports:

- `OrderableAsset`;
- FSM utility functions; and
- the `Province` entity and `ProvinceService`.

## Direct dependencies

From 3.7, `@nestjs/terminus` is no longer supplied transitively. Custom health
checks must declare it directly.
