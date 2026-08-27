# Execution and Operations

## Run coordination and concurrency

### Queued coordinator default

Since 1.10.0, the queued run coordinator is the default. The Dagster daemon must
be running for runs to launch. To keep immediate, in-process launching, configure
the former coordinator explicitly:

```yaml
run_coordinator:
  module: dagster.core.run_coordinator.sync_in_memory_run_coordinator
  class: SyncInMemoryRunCoordinator
```

Run blocking for concurrency keys and pools is also enabled by default. With op
granularity, a run dequeues when at least one op can execute. With run
granularity, every pool used by the run must have an available slot.

Pool names accepted only letters, digits, dashes, and underscores in 1.10.0.
By 1.12.0, this was relaxed to any non-whitespace character, superseding both
the original restriction and an intermediate slash-only expansion.

### Early downstream execution

All executors accept `step_dependency_config.require_upstream_step_success`
since 1.11.0. Set it to `false` when a downstream step may start as soon as its
required outputs are available, even if the producing multi-asset step is still
running.

```json
{"step_dependency_config": {"require_upstream_step_success": false}}
```

## Custom executors and retry state

The 1.12-upgrade added retry recovery for resource-initialization failures in
executors that run steps in dedicated processes. A custom `Executor` must emit
and register a failure-or-retry event for each such failure; otherwise the run
can remain in `started`.

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

## Backfills, retries, and cancellation

`BackfillPolicy` is GA as of 1.11.0. Backfill submission uses a thread pool with
four daemon workers by default, asset backfills may carry run config, and a
failed backfill cancels its in-progress runs before terminating. A schedule's
`RunRequest` can select a subset of asset checks.

In 1.13.0, job backfills retry transient daemon failures.
`DAGSTER_MAX_ASSET_BACKFILL_RETRIES` was renamed to
`DAGSTER_MAX_BACKFILL_RETRIES`; the old environment variable remains a fallback.

Runs that supply only part of their config inherit defaults from the job-level
config for omitted sections as of 1.13.0.

## Daemons, schedules, sensors, and failure context

Schedule, sensor, and asset-daemon ticks dispatch instigators round-robin across
code locations starting in 1.13.0.

When a run fails because a step failed, the originating step error is available
on the run-failure sensor context as of 1.13.0. Use that error rather than
reconstructing the cause from run-level status alone.

## GraphQL clients and pagination

### Launch selections

`DagsterGraphQLClient.submit_job_execution` accepts `asset_selection` since
1.11.0.

### Event cursors and bounded selections

The `logsForRun` and `eventConnection` resolvers return at most 1,000 events per
query by default as of 1.11.0. Follow the returned cursor until no additional
pages remain.

In 1.13.0, `DagsterGraphQLClient` accepts `path_prefix` for a webserver mounted
below the URL root. The GraphQL `Run` type adds an optional selection `limit`
plus `assetSelectionCount` and `assetCheckSelectionCount`, so callers can request
bounded previews without losing true totals.

## Logs, errors, and heartbeats

Since 1.11.0, event error messages or stack traces larger than 500 KB are
truncated. Override the threshold with `DAGSTER_EVENT_ERROR_FIELD_SIZE_LIMIT`.

`DAGSTER_GRPC_PROXY_HEARTBEAT_TTL_SECONDS` sets the proxy gRPC heartbeat TTL;
the default is 30 seconds (1.11.0).

## Pipes

In 1.13.0, the preview `PipesCompositeMessageReader` supports multiple concurrent
message streams in one Pipes session.

`PipesK8sClient.run(delete_pod_on_completion=False)` retains its pod after the
run. `PipesEMRServerlessClient.dashboard_refresh_interval` controls Spark
dashboard refreshes and has a longer default so UI URLs remain valid during runs
(1.13.0).

## Operational API surfaces

The 1.12.0 `dg api` commands cover schedule and job metadata, asset-check
execution history, and asset partition status. In 1.13.0,
`dg api run launch` launches through the Dagster+ API.

Dagster+ SCIM Groups queries accept the `members.value eq` filter as of 1.13.0.
