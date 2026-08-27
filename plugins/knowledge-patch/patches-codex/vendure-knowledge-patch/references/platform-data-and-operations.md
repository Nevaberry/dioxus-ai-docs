# Platform, Data, and Operations

## Settings Store

3.4 introduces `SettingsStore` for global and scoped configuration. Read and
write permissions were added later, and a Dashboard management page arrives
in 3.6.

Since 3.4.2, prefer the context-first service signatures:

```ts
SettingsStoreService.get<T>(ctx, key)
SettingsStoreService.getMany(ctx, keys)
SettingsStoreService.set<T>(ctx, key, value)
SettingsStoreService.setMany(ctx, values)
```

The old argument order remains temporarily accepted.

## Required database migrations

### Settings and indexes

The 3.4 Settings Store needs a new table. 3.4 also adds indexes for
`Order.orderPlacedAt` and `JobItem.createdAt`.

### Cache precision

DefaultCachePlugin users upgrading through 3.2 need `precision(3)` on
`CacheItem.expiresAt`.

### Asset translations

3.6 provides `migrateAssetTranslationData()` for its asset-translation
change.

## Server lifecycle hooks

`BootstrappedEvent` signals server readiness. `onBeforeAppListen` exposes the
Nest application immediately before listening starts.

## Scheduled tasks

Scheduled tasks can be triggered manually, receive a `RequestContext`, and
include a built-in database job-cleanup task.

## Job queues

Job options support priority. BullMQ honors configured Redis prefixes for
both queue and buffer storage.

## Telemetry and tracing

3.3 introduces `@vendure/telemetry-plugin` and tracing across services, cache,
scheduled tasks, and job queues.

Core later adds anonymous telemetry collection and expands it to schema v2
with heartbeat, strategy, integration, feature-adoption, and other signals.

## CLI lifecycle and diagnostics

The CLI adds:

- Non-interactive operation.
- A `schema` command.
- `dev`, `build`, and `start` lifecycle commands.
- A `doctor` project check.

A codemod supports the Dashboard's Radix-to-Base-UI migration.

## Project scaffolding

New projects include the React Dashboard and can optionally scaffold a
Next.js storefront. Generated Dashboard configuration uses API URL `auto`.
Scaffolded projects read the server port from `VENDURE_SERVER_PORT`.

_Source batch: `official-changelog-2025-current`._
