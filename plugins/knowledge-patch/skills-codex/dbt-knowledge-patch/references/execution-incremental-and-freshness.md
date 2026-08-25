# Execution, Incremental Models, and Freshness

Use this reference for microbatch models, hooks and retries, source and model freshness, snapshots, seeds, and schema-only execution.

## Microbatch incremental models (1.9-guides)

The `microbatch` incremental strategy divides large time-series models into independently replaceable batches. dbt automatically filters direct `ref()` and `source()` parents that declare `event_time`, so the model SQL describes one batch and does not need an `is_incremental()` filter.

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

Set `event_time` independently on each direct parent that should be filtered:

```yaml
models:
  - name: stg_events
    config:
      event_time: my_time_field
```

An unconfigured parent is scanned completely for every batch. Use `ref('stg_events').render()` to deliberately opt a configured parent out of automatic filtering.

`begin`, `event_time`, and `batch_size` are required. Batch sizes are `hour`, `day`, `month`, or `year`. `lookback` defaults to one batch; `concurrent_batches: true` or `false` overrides automatic parallelism detection. PostgreSQL additionally requires `unique_key`, while Spark and BigQuery require `partition_by`.

Backfills require both UTC bounds:

```bash
dbt run --event-time-start "2024-09-01" --event-time-end "2024-09-04"
```

`event_time`, `begin`, and both CLI bounds are interpreted as UTC. `dbt retry` reruns only failed batches. A custom microbatch strategy macro also needs this project behavior flag:

```yaml
flags:
  require_batched_execution_for_custom_microbatch_strategy: true
```

## Microbatch context, hooks, and retries (1.10.0)

Model Jinja receives a `batch` context object. Pre-hooks execute only on the first batch and post-hooks only on the last. `dbt retry` honors `--threads`. From Core 1.10.20, a retry recomputes batches with the original invocation time rather than the retry time.

## Query-driven source freshness (1.10.0)

Source and table configs accept `loaded_at_field` and `loaded_at_query`, so freshness may be calculated by a SQL query:

```yaml
sources:
  - name: raw
    tables:
      - name: events
        config:
          loaded_at_query: "select max(_loaded_at) from raw.events"
```

## Model freshness (1.10.0 and 1.11.0)

Model freshness for adaptive jobs is config-only. It is skipped without `build_after`. A time-driven `build_after` requires both `count` and `period`:

```yaml
models:
  - name: orders
    config:
      freshness:
        build_after:
          count: 12
          period: hour
```

An update-driven trigger may instead specify `updates_on` without `count` or `period`:

```yaml
models:
  - name: orders
    config:
      freshness:
        build_after:
          updates_on: any
```

## Snapshot hard-delete handling (1.9-guides)

`hard_deletes` accepts `ignore` (the default), `invalidate`, and `new_record`. `invalidate` closes a deleted row by setting `dbt_valid_to`; `new_record` records the deletion as a new row and adds `dbt_is_deleted`.

```yaml
snapshots:
  - name: my_snapshot
    config:
      unique_key: id
      strategy: timestamp
      updated_at: updated_at
      hard_deletes: new_record
```

Legacy `invalidate_hard_deletes` remains supported but cannot be combined with `hard_deletes`. Existing snapshot tables are not migrated automatically; migrate their schema and data before changing modes, or use the new mode only for new snapshots. PostgreSQL, BigQuery, Snowflake, and Redshift support this config.

## Empty-run context (1.9.0)

Snapshots support `--empty`, and Jinja can inspect `flags.EMPTY`:

```jinja
{% if flags.EMPTY %}
  -- schema-only execution
{% endif %}
```

## Empty seed relations (1.12.0)

`dbt seed --empty` creates selected seed tables without loading their rows, which supports schema-only setup:

```bash
dbt seed --empty --select customers
```
