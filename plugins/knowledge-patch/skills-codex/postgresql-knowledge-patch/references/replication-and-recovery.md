# Replication and Recovery

Use this reference for logical-slot failover, standby coordination,
subscription behavior, replica conversion, and logical-replication tools. The
changes are attributed to `17.0` and `18.0`.

## Synchronize logical slots for failover

PostgreSQL 17 logical slots can be marked for failover with the fifth argument
to `pg_create_logical_replication_slot()` or with a subscription option:

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

Enable `sync_replication_slots` on the standby or call
`pg_sync_replication_slots()` to request synchronization.
`synchronized_standby_slots` lists physical standby slots that must catch up
before decoded changes can become visible to subscribers. Coordinate the two
settings so logical decoding cannot outrun the failover standby.

## Convert and upgrade replicas without a new copy

PostgreSQL 17 `pg_createsubscriber` converts a physical standby into a logical
replica. `pg_upgrade` carries valid logical slots and full subscription state
forward when the old cluster is PostgreSQL 17 or newer, allowing replication
to resume without another data copy.

Slot diagnostics include `invalidation_reason` and `inactive_since`.

## Bound replication resources

PostgreSQL 18 `idle_replication_slot_timeout` automatically invalidates
inactive slots. `max_active_replication_origins` separates the active-origin
limit from `max_replication_slots`.

## Publish generated columns intentionally

In PostgreSQL 18, generated columns named in a publication column list are
published. Without a column list, `publish_generated_columns` decides whether
generated columns are included.

Subscription streaming now defaults to `parallel`. `ALTER SUBSCRIPTION` can
change the slot's two-phase behavior. Apply conflicts are logged and counted in
`pg_stat_subscription_stats`.

## Use current logical-replication utilities

PostgreSQL 18 `pg_createsubscriber` adds `--all`, `--clean`, and
`--enable-two-phase`. `pg_recvlogical --enable-failover` creates a
failover-capable slot; `--enable-two-phase` replaces the deprecated
`--two-phase` spelling. `pg_recvlogical --drop-slot` no longer requires
`--dbname`.
