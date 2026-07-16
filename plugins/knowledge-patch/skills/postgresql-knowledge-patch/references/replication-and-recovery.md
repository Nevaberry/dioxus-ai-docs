# Replication and Recovery

Batch attribution: `17.0`, `18.0`.

## Make logical slots survive publisher failover

Create a failover-capable logical slot with the fifth argument of
`pg_create_logical_replication_slot()`, or set `failover = true` on a
subscription.

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

On a standby, `sync_replication_slots` synchronizes failover slots and
`pg_sync_replication_slots()` requests synchronization immediately.
`synchronized_standby_slots` identifies physical standby slots that must catch
up before decoded changes become visible to subscribers.

Logical-slot diagnostics include `invalidation_reason` and `inactive_since`.

## Convert and upgrade replicas

`pg_createsubscriber` converts a physical standby to a logical replica. It can
operate across every eligible database with `--all`, clean up after failure
with `--clean`, and enable two-phase decoding with `--enable-two-phase`.

An upgrade carries valid logical slots and complete subscription state forward,
so replication can resume without a fresh data copy when the source cluster is
PostgreSQL 17 or later.

`pg_recvlogical --enable-failover` creates a failover-capable slot.
`--enable-two-phase` replaces the deprecated `--two-phase` spelling, and
`--drop-slot` no longer requires `--dbname`.

## Bound replication resources

`idle_replication_slot_timeout` automatically invalidates inactive slots.
`max_active_replication_origins` separates the limit for active origins from
`max_replication_slots`.

## Publish generated columns and monitor apply conflicts

A generated column named in a publication column list is published. When the
publication has no column list, `publish_generated_columns` controls whether
generated columns are sent.

Subscription streaming defaults to `parallel`. `ALTER SUBSCRIPTION` can change
the slot's two-phase behavior. Apply conflicts are written to the server log
and counted in `pg_stat_subscription_stats`.
