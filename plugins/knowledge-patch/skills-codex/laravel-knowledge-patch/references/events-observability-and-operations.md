# Events, Observability, and Operations

Lifecycle events, logging, metrics, failure reporting, maintenance, reloads, and operational controls.

## API-aware maintenance mode (2026-07)

The `down` command now handles API and JSON routes, so non-HTML requests receive maintenance-mode handling as well.

## Callback-based exception report suppression (2025-07)

`dontReportUsing()` registers a callback that filters exceptions from reporting when a class-only `dontReport` list is not expressive enough.

## Datetime maintenance retries (2026-01)

The `down` command's `--retry` option accepts datetime values in addition to delay values, allowing the retry time to target the planned end of maintenance.

```shell
php artisan down --retry="2026-01-28 18:00:00"
```

## Extensible maintenance mode facade (2025-07)

The new `MaintenanceMode` facade exposes maintenance-mode driver extension, allowing applications to register custom maintenance backends through the facade.

## Migration and locale event data (2025-12)

Laravel dispatches a `MigrationSkipped` event for skipped migrations, and `LocaleUpdated` now includes the previous locale for listeners that need both sides of the change.

## Migration names in lifecycle events (2026-05)

`MigrationStarted` and `MigrationEnded` now include the migration name, allowing listeners to identify the migration being run.

## Monthly log rotation (2026-07)

Laravel 13 includes a monthly log driver and a corresponding logging channel configuration.

## Named event arguments (2026-02)

Event classes can be dispatched or broadcast with named constructor arguments, so callers no longer have to supply every event argument positionally.

```php
OrderShipped::dispatch(order: $order, notify: true);
```

## Opting listeners out of discovery (2026-05)

Auto-discovered event listeners can opt out of discovery when they should only be registered explicitly.

## Refreshable maintenance options (2026-02)

Running the `down` command while the application is already in maintenance mode can refresh its options instead of retaining stale settings.

## Reloadable service lifecycle (2025-12)

Laravel now provides a reload command and lets services register for reloading. Queue workers may also opt out of the `queuePaused` and `queueShouldRestart` cache checks when those controls are not needed.

## Selective log-context removal (2025-03)

`Log::withoutContext()` accepts keys to remove only selected values from subsequent log context.

```php
Log::withoutContext(['tenant_id', 'trace_id']);
```

## Single failover notifications (2026-01)

`CacheFailedOver` and `QueueFailedOver` now fire only for the first failure in a failover attempt, so listeners are not invoked once for every failed backend.

## Structured JSON logging (2026-04)

Laravel 13 introduces `JsonFormatter` for JSON log output, including exception context when the exception handler is not bound.
