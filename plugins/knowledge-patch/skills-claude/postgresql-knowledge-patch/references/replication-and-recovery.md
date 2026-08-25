# Replication and Recovery

## Synchronize logical slots for failover (17.0)

Mark a logical slot for failover with the fifth argument of
`pg_create_logical_replication_slot()` or set `failover = true` on a
subscription. On a standby, `sync_replication_slots` synchronizes failover
slots, and `pg_sync_replication_slots()` requests synchronization explicitly.
Use `synchronized_standby_slots` to name physical slots that must catch up
before decoded changes become visible to subscribers.

```sql
SELECT *
FROM pg_create_logical_replication_slot(
  'orders_slot', 'pgoutput', false, false, true
);

CREATE SUBSCRIPTION orders_sub
  CONNECTION 'host=publisher dbname=app'
  PUBLICATION orders_pub
  WITH (failover = true);
```

## Convert and upgrade replicas (17.0)

`pg_createsubscriber` converts a physical standby into a logical replica.
When the old cluster is PostgreSQL 17 or newer, `pg_upgrade` carries valid
logical slots and full subscription state forward so replication can resume
without a fresh copy. Slot diagnostics include `invalidation_reason` and
`inactive_since`.

## Bound replication resources (18.0)

`idle_replication_slot_timeout` automatically invalidates slots that remain
inactive. `max_active_replication_origins` separates the active-origin limit
from `max_replication_slots`.

## Publish generated columns and monitor conflicts (18.0)

Generated columns named in a publication column list are published. Without a
column list, `publish_generated_columns` determines whether they are included.
Subscription streaming defaults to `parallel`. `ALTER SUBSCRIPTION` can change
a slot's two-phase behavior, and apply conflicts are logged and counted in
`pg_stat_subscription_stats`.

## Use replication command-line controls (18.0)

`pg_createsubscriber` adds `--all`, `--clean`, and `--enable-two-phase`.
`pg_recvlogical --enable-failover` creates a failover-capable slot;
`--enable-two-phase` replaces the deprecated `--two-phase` spelling, and
`--drop-slot` no longer requires `--dbname`.
