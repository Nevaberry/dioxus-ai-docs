# Incremental Models, Snapshots, and Freshness

## Microbatch Incremental Strategy

The `1.9-guides` batch adds `microbatch` for large time-series data. dbt splits
work into independently replaceable time batches and automatically filters
direct `ref()` and `source()` inputs that have an `event_time`. Model SQL should
describe one batch and does not need an `is_incremental()` filter.

```sql
{{ config(
    materialized='incremental',
    incremental_strategy='microbatch',
    event_time='event_occurred_at',
    begin='2020-01-01',
    batch_size='day',
    lookback=3,
    full_refresh=false
) }}

select * from {{ ref('stg_events') }}
```

Configure `event_time` separately on every direct parent that should be
filtered:

```yaml
models:
  - name: stg_events
    config:
      event_time: my_time_field
```

An unconfigured parent is fully scanned for every batch. To deliberately opt a
configured parent out of automatic filtering, render it explicitly:

```sql
select * from {{ ref('stg_events').render() }}
```

Required settings are `begin`, `event_time`, and `batch_size`. Valid batch
sizes are `hour`, `day`, `month`, and `year`. `lookback` defaults to one batch.
Set `concurrent_batches: true` or `false` to override automatic parallelism
detection.

PostgreSQL additionally requires `unique_key`; Spark and BigQuery require
`partition_by`.

## Backfills and Retries

Backfills require both bounds:

```bash
dbt run --event-time-start "2024-09-01" --event-time-end "2024-09-04"
```

`event_time`, `begin`, and both CLI bounds are interpreted as UTC. `dbt retry`
reruns only failed batches.

A custom microbatch strategy macro also requires the
`require_batched_execution_for_custom_microbatch_strategy` behavior flag in
`dbt_project.yml`.

## Batch Context and Hooks

The `1.10.0` behavior adds a `batch` object to model Jinja. For microbatch
models, pre-hooks run only on the first batch and post-hooks only on the last.
Retries honor `--threads`.

From Core 1.10.20, `dbt retry` recomputes batches using the original invocation
time rather than the retry time.

## Snapshot Hard Deletes

Snapshots can use `hard_deletes: ignore`, `invalidate`, or `new_record`.
`ignore` is the default. `invalidate` closes a deleted row by setting
`dbt_valid_to`; `new_record` records deletion as another row and adds
`dbt_is_deleted`.

```yaml
snapshots:
  - name: my_snapshot
    config:
      unique_key: id
      strategy: timestamp
      updated_at: updated_at
      hard_deletes: new_record
```

The legacy `invalidate_hard_deletes` config remains supported but cannot be
combined with `hard_deletes`. Existing snapshot tables are not migrated
automatically. Migrate schema and data before changing modes, or limit the new
setting to new snapshots. PostgreSQL, BigQuery, Snowflake, and Redshift
support the configuration.

Snapshots also support `--empty`; Jinja can detect it with `flags.EMPTY`.

## Query-Driven Source Freshness

Core 1.10 lets source and table configs use `loaded_at_field` or
`loaded_at_query`, so freshness may be computed by SQL:

```yaml
sources:
  - name: raw
    tables:
      - name: events
        config:
          loaded_at_query: "select max(_loaded_at) from raw.events"
```

Source freshness may also be placed under `config`, and explicit null
freshness values are preserved.

## Model Freshness

Model freshness for adaptive jobs is config-only. It is skipped unless
`build_after` is present. In Core 1.10, a time-based trigger requires both
`count` and `period`:

```yaml
models:
  - name: orders
    config:
      freshness:
        build_after:
          count: 12
          period: hour
```

The `1.11.0` behavior permits an update-driven trigger using `updates_on`
without `count` or `period`:

```yaml
models:
  - name: orders
    config:
      freshness:
        build_after:
          updates_on: any
```
