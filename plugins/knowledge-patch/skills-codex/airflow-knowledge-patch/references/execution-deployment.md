# Execution and deployment

## Edge Executor

Edge Executor runs tasks in distributed or remote environments through the
Task Execution API. Use it for hybrid deployments whose workers need to remain
near their data or applications. It is generally available in the 3.0.0
batch.

## Dag versions and bundles

Task renames, dependency changes, and other structural changes are stored as
Dag versions in the metadata database and exposed through UI and API. The
triggerer does not initialize Dag bundles, so trigger implementations cannot
live only inside a bundle; install them somewhere importable on the
triggerer's `sys.path`. (3.0.0)

`rerun_with_latest_version` decides whether clear, rerun, backfill, and
`TriggerDagRunOperator` reruns use the original or latest bundle. Precedence is:
request parameter or CLI flag, Dag setting, `[core] rerun_with_latest_version`,
then a default of `False` for clear/rerun and `True` for backfill. (3.3.0)

Provider example Dags now use dedicated bundles named
`apache-airflow-providers-<distribution>-example-dags`, or
`<distribution>-example-dags` for third-party providers. API clients must stop
assuming provider examples belong to `dags-folder`. `[core] load_examples`
still controls their registration. (3.3.0)

A legacy upgrade could assign all old Dags to `dags-folder` even when a custom
bundle is configured. The Dag processor performs a best-effort path-based
repair at startup. Unmatched Dags repair on their next successful parse; run
`airflow dags reserialize` to force parsing. (3.3.1)

## Scheduler and triggerer lifecycle

`airflow scheduler --only-idle` makes `--num-runs` count only idle loops, so a
run-limited scheduler can finish triggered Dags and queued tasks before exit.
(3.2.0)

```bash
airflow scheduler --num-runs 1 --only-idle
```

Route queued triggers with `airflow trigger --queues`. Limit per-loop selection
with `max_trigger_to_select_per_loop` in high-availability triggerer
deployments. (3.2.0)

## API-server worker model

Uvicorn remains the default API server. To use preloaded memory-sharing
workers and zero-downtime FIFO recycling, install
`apache-airflow-core[gunicorn]` and select Gunicorn. (3.2.0)

```ini
[api]
server_type = gunicorn
worker_refresh_interval = 43200
worker_refresh_batch_size = 1
```

## Dag parsing statistics

`FileLoadStat` includes nullable `bundle_path` and `bundle_name`. Its paths are
real relative paths and no longer use a leading `/` to mean “relative to the
Dags folder.” Custom parser tooling should operate on `pathlib.Path` values
instead of relying on that string convention. (3.2.0)

## Rendered-field retention

`max_num_rendered_ti_fields_per_task` is renamed to
`num_dag_runs_to_retain_rendered_fields`; the old name is deprecated. Retention
counts the newest Dag runs rather than task executions, so sparse and
conditional tasks can retain fewer records than the old setting suggested.
(3.2.0)

## Runtime and database compatibility

The `3.1.0` runtime supports Python 3.10 through 3.13, removing Python 3.9.
It adds SQLAlchemy 2.0 compatibility and psycopg3 PostgreSQL-driver support.

The `3.2.0` batch adds Python 3.14, requires SQLAlchemy 2, and removes the
MySQL client from official images. Add that client to a derived image when
operators or administration scripts need it.

## Container build controls

Set the `PYTHON_LTO` build argument as needed for FIPS-oriented builds. Docker
builds can verify cryptographic signatures on Python source packages.
(3.2.0)

## Git Dag bundles

`GitDagBundle` supports repositories with submodules and HTTP URL
authentication. (3.2.0)

## Multiprocessing configuration

`[core] mp_start_method` and `[core] mp_forkserver_preload` configure process
startup globally. Override them per component in `[scheduler]`, `[triggerer]`,
or `[dag_processor]` when their workloads differ. (3.3.0)

## Non-Python task runtimes

Experimental Coordinator execution routes `@task.stub` declarations to
`JavaCoordinator` for JVM work and `ExecutableCoordinator` for native binaries
such as Go programs. Runtimes use the Execution API for Variables,
Connections, and XCom while Dags and scheduling remain in Python. (3.3.0)

## Resumable external jobs

`ResumableJobMixin`, initially used by `SparkSubmitOperator`, tracks external
work so it can resume after worker failure instead of submitting another job.
Operators can opt out with `durable=False`. (3.3.0)

`ResumableJobMixin` is abstract in the `3.3.1` batch. Custom subclasses must
implement every required method instead of relying on inherited defaults.

## Custom email backends

`email_on_failure` and `email_on_retry` honor `[email] email_backend` rather
than always using `SmtpNotifier`. An unimportable backend path raises an error
instead of silently falling back to SMTP. (3.3.1)
