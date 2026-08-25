# Operations and deployment

## Run coordination and concurrency

### Queued coordination is the default (since 1.10.0)

The queued run coordinator is the default, so the Dagster daemon must be
running before runs launch. To retain immediate in-process launches, configure
the former coordinator explicitly:

```yaml
run_coordinator:
  module: dagster.core.run_coordinator.sync_in_memory_run_coordinator
  class: SyncInMemoryRunCoordinator
```

### Pool-aware blocking (since 1.10.0)

Run blocking for concurrency keys and pools is enabled by default. At op
granularity, a run is dequeued once at least one op can execute. At run
granularity, every pool used by a run must have a free slot.

Pool names initially accepted only letters, numbers, dashes, and underscores.
The `dagster-dbt`, `dagster-dlt`, and `dagster-sling` integrations support
pools.

### Relaxed pool names (since 1.12.0)

Pool names can contain any non-whitespace character. This replaces the earlier
letters, numbers, dashes, and underscores rule and its later slash allowance.
The Helm chart also accepts a `concurrency` setting for pools.

### Automatic code-location tags (since 1.12.0)

A run with a remote job origin automatically receives the
`dagster/code_location` tag. Use it for filtering or concurrency controls.

## Step and executor behavior

### Start downstream work after outputs are ready (since 1.11.0)

All executors accept `step_dependency_config.require_upstream_step_success`.
Set it to `false` to let a downstream step start after required upstream
outputs are available, even if the producing multi-asset step is still
running.

```json
{"step_dependency_config": {"require_upstream_step_success": false}}
```

### Resource initialization failures (1.12-upgrade)

Executors that run steps in dedicated processes can recover from resource
initialization failure through step retries. A custom `Executor` must emit and
register an explicit failure-or-retry event for every such failure. Without
that event, the run can remain in `started` status.

```python
if event.is_resource_init_failure:
    failure_or_retry_event = self.get_failure_or_retry_event_after_error(
        step_context,
        event.engine_event_data.error,
        active_execution.get_known_state(),
    )
    yield failure_or_retry_event
    active_execution.handle_event(failure_or_retry_event)
```

### Partial run configuration (since 1.13.0)

When a run supplies only part of its config, Dagster fills omitted portions
from the job-level config defaults.

## Definition validation

### Partition mappings and duplicate specs (since 1.11.0)

`dagster definitions validate` fails on invalid partition mappings, including
time-partitioned dependencies with different time zones. `Definitions` and
`AssetsDefinition` also reject distinct `AssetSpec` objects that share one
asset key.

### Owner validation (since 1.13.0)

Asset-job owners are validated when definitions load. Team-owner strings on
jobs, schedules, and sensors may contain special characters.

## Backfills and daemon dispatch

### Submission and failure cleanup (since 1.11.0)

Backfill submission uses a thread pool of four daemon workers by default.
Asset backfills can carry run config. When a backfill fails, Dagster cancels
its in-progress runs before terminating it.

### Fair tick dispatch and retry naming (since 1.13.0)

Schedule, sensor, and asset-daemon ticks dispatch instigators round-robin over
code locations. Job backfills retry transient daemon failures.

`DAGSTER_MAX_ASSET_BACKFILL_RETRIES` was renamed to
`DAGSTER_MAX_BACKFILL_RETRIES`; the old environment variable remains a
fallback.

## GraphQL clients and event limits

### Submission selection and pagination (since 1.11.0)

`DagsterGraphQLClient.submit_job_execution` accepts `asset_selection`.
`logsForRun` and `eventConnection` return at most 1,000 events by default.
Follow each response cursor to retrieve remaining logs.

### Mounted webservers and bounded previews (since 1.13.0)

`DagsterGraphQLClient` accepts `path_prefix` for a webserver mounted below the
URL root. The GraphQL `Run` type accepts an optional selection `limit` and
reports full `assetSelectionCount` and `assetCheckSelectionCount` values, so a
client can render bounded previews without losing the true totals.

### Error-field and heartbeat limits (since 1.11.0)

Event errors or stack traces larger than 500 KB are truncated.
`DAGSTER_EVENT_ERROR_FIELD_SIZE_LIMIT` changes that limit.

`DAGSTER_GRPC_PROXY_HEARTBEAT_TTL_SECONDS` changes the proxy gRPC heartbeat TTL
from its default of 30 seconds.

## Databases and local development

### Database migrations and PostgreSQL dependency (since 1.12.0)

MySQL installations must run `dagster instance migrate` for the `LongText`
migrations affecting bulk-action bodies and cached asset status data.

`dagster-postgres` no longer installs `psycopg2-binary` transitively. Declare
it directly when the deployment uses that driver.

### Development database pools (since 1.12.0)

`dg dev` and `dagster dev` accept database-pool controls including
`--db-pool-recycle` and `--db-pool-pre-ping`.

### Storage defaults (since 1.13.0)

- The SQLite event-log `busy_timeout` default increased from 5 to 30 seconds.
- `PickledObjectS3IOManager` uses an empty key prefix when no prefix is given.
- BigQuery, Snowflake, and DuckDB IO managers skip empty-DataFrame writes and
  emit a warning.

## Runtime compatibility

### Python and dependencies (since 1.11.0 and 1.12.0)

Dagster 1.11 supports Python 3.13 and protobuf 6.x, and removes the Click
`<8.2` cap. The Delta Lake integrations require `deltalake>=1.0.0` without an
API change.

Dagster 1.12 drops Python 3.9, making Python 3.10 the minimum. Core and most
libraries support Python 3.14; `dg plus deploy` supports Python 3.13 and 3.14.

### Failure-sensor context (since 1.13.0)

When a run fails because a step failed, the original step error is available
on the run-failure sensor context.
