---
name: airflow-knowledge-patch
description: Apache Airflow
version: 3.3.0
license: MIT
metadata:
  author: Nevaberry
---


# Apache Airflow Knowledge Patch

Use this skill when authoring, upgrading, integrating, or operating Apache Airflow. Start with the quick guidance below, then open the topic reference that matches the work.

## Reference index

| Reference | Topics |
| --- | --- |
| [upgrade-and-compatibility.md](references/upgrade-and-compatibility.md) | Upgrade sequencing, stable interfaces, removed APIs, serialization, runtimes, pandas, and Dag bundles |
| [task-authoring-and-execution.md](references/task-authoring-and-execution.md) | Task context, XCom, callbacks, operators, HITL, state stores, retry policy, and durable execution |
| [scheduling-assets-and-deadlines.md](references/scheduling-assets-and-deadlines.md) | Scheduling defaults, Dag versions, backfills, Assets, partitions, clearing, Deadline Alerts, and teams |
| [api-cli-and-ui.md](references/api-cli-and-ui.md) | Authentication, REST semantics, `airflowctl`, CLI changes, UI streams, and sensitive configuration |
| [operations-logging-and-extensions.md](references/operations-logging-and-extensions.md) | Services, plugins, deployment, security, remote logs, metrics, and tracing |

## Upgrade first principles

### Author against `airflow.sdk`

Use the semver-governed SDK for Dag authoring and task execution:

```python
from airflow.sdk import Asset, DAG, dag, get_current_context, task
```

Move `Dataset*` names to their `Asset*` equivalents and `airflow.io.*` imports to `airflow.sdk.io.*`. Treat unlisted Python modules, metadata ORM/schema details, and Web UI HTML as internal.

Do not subclass built-in executors as a compatibility contract. For built-in operators, rely on documented parameters and behavior, not methods or class structure.

### Run a staged preflight

Before the core upgrade:

1. Move to a recent Airflow 2.x release, at least 2.7.
2. Back up the metadata database and clean it if appropriate.
3. Make Dag parsing and reserialization error-free.
4. Run Ruff Airflow checks and migrate provider imports.
5. Diagnose configuration changes, then migrate the database.

```bash
airflow db clean
airflow dags reserialize
ruff check dags/ --select AIR301 --show-fixes
ruff check dags/ --select AIR301 --fix --unsafe-fixes
airflow config update --fix
airflow db migrate
```

Ruff AIR301/AIR302 identify breaking changes; AIR311/AIR312 suggest recommended migrations. Import rewrites may require `--unsafe-fixes` and F401 cleanup.

### Install the standard provider

Core operators and sensors such as `BashOperator`, `PythonOperator`, `ExternalTaskSensor`, and `FileSensor` moved to `apache-airflow-providers-standard`. Install it and migrate imports before upgrading core when possible.

### Replace removed facilities

Use these replacements:

| Removed or changed | Replacement |
| --- | --- |
| SubDAGs | TaskGroups, Assets, or data-aware scheduling |
| SequentialExecutor | LocalExecutor, including with SQLite |
| Kubernetes hybrid executors | Multiple-executor configuration |
| SLAs | Deadline Alerts |
| CLI `--subdir` / `-S` | Dag bundles |
| REST `/api/v1` | Stable FastAPI `/api/v2` |
| `fail_stop` | `fail_fast` |
| Dataset APIs | Asset APIs |

Dags and XComs are no longer pickled. Keep embedded Dag values JSON-serializable and use a custom XCom backend for other representations.

## Task runtime rules

### Keep task code away from the metadata database

Task code cannot use metadata ORM models or sessions. Use Task Context and SDK accessors:

```python
from airflow.sdk import get_current_context

context = get_current_context()
ti = context["ti"]
connection = context["conn"].get("service")
variable = context["var"].value.get("setting")
```

Use stable REST endpoints or `apache-airflow-client` for broader access to Dag runs, task instances, Connections, Variables, and XComs. Obtain client tokens at `/auth/token`.

Import task-facing exceptions from the SDK:

```python
from airflow.sdk.exceptions import AirflowSkipException, TaskDeferred
```

### Pull XComs from an explicit producer

An unqualified pull searches the current task only. Name the upstream task when sharing state:

```python
value = ti.xcom_pull(task_ids="upstream_task", key="shared_state")
```

XCom keys cannot be empty. Do not depend on the API server deserializing unknown Python objects for display.

### Handle dateless event runs

Asset-triggered and REST-triggered runs can have `logical_date=None` and no data interval. Guard `dag_run.logical_date`; do not assume `logical_date`, `data_interval_start`, or `data_interval_end` exists in task context.

For manual runs, use `logical_date` for the requested trigger date. Use interval fields only for the timetable-resolved interval.

### Respect callback and teardown changes

`on_success_callback` does not run for `SKIPPED` tasks. Teardown tasks can run after early Dag termination, but cannot use `TriggerRule.ALWAYS`; choose a rule that preserves upstream dependency semantics.

## Scheduling and Assets

### Make cron interval semantics explicit

`catchup_by_default` and `create_cron_data_intervals` default to `False`. A bare cron schedule therefore uses `CronTriggerTimetable`, not `CronDataIntervalTimetable`.

If task logic depends on interval boundaries or derived `ds`/`ts` values, set `create_cron_data_intervals=True` before upgrading. Changing it after new runs exist can intentionally skip a scheduled run to avoid duplicating a `logical_date`.

### Use typed Asset references

Event maps no longer accept string keys. Use typed references or lookup helpers:

```python
outlet_events[Asset.ref(name="myasset")]
outlet_events[AssetAlias(name="myalias")]
outlet_events.for_asset(name="myasset")
outlet_events.for_asset_alias(name="myalias")
```

Partitioned Asset scheduling supports validation, composed mappings, temporal mappings, fan-out, rollup, wait policies, runtime keys, and partition-scoped clear/backfill operations. Open the scheduling reference before implementing a mapper because mapper names, imports, limits, and propagation rules matter.

### Treat Dag structure and bundle version as persisted state

Airflow stores historical Dag structures. Clear, rerun, backfill, and trigger operations can select the original or latest Dag-bundle version. Decide this explicitly when reproducibility matters.

## State, retry, and results

Use `task_state_store` and `asset_state_store` for persistent JSON state. Configure expiration, retention, row-size limits, and `clear_on_success`; select a worker-side backend with `[workers] state_store_backend` when metadata-database storage is unsuitable.

Use a custom retry policy when exception-specific retry decisions or custom delays are needed. Waiting failures from `TriggerDagRunOperator`, including failed triggered runs, participate in the policy.

Designate a Dag result with `@result` or a marked return-value XCom. The NDJSON Dag-run wait endpoint can then return the designated result.

## API and service migration

### Run the API server and Dag processor separately

```bash
airflow api-server
airflow dag-processor
```

Move API settings from `[webserver]` to `[api]` and parsing settings to `[dag_processor]`. Run `airflow config lint` to find ignored legacy options. In Helm values, move `webserver` configuration beneath `apiServer`.

Use `airflowctl` for remote administration and `airflow` for local operations. API v2 clients must expect validation errors as HTTP 422, send `logical_date` instead of `execution_date`, and preserve an omitted trigger date as `None`.

### Update authentication routes

Simple Auth is the default manager. To retain FAB, install its provider and configure `FabAuthManager`. Auth routes live below `/auth`; update external OAuth redirects accordingly.

### Choose API-server process behavior deliberately

Uvicorn is the default. For preloaded workers and zero-downtime FIFO recycling, install the Gunicorn extra and configure:

```ini
[api]
server_type = gunicorn
worker_refresh_interval = 43200
worker_refresh_batch_size = 1
```

## Extensions and observability

Plugins cannot register operators, hooks, sensors, or executors. Package them as ordinary Python classes and import them directly. Migrate legacy FAB plugin surfaces to `external_views`, `fastapi_apps`, and `fastapi_root_middlewares`, or install the compatibility provider.

Remote-log providers implement a no-argument `RemoteLogIO.from_config()`. Discovery prefers custom logging configuration, then a provider selected by the remote-log URI scheme, then the transitional local-settings fallback.

Review OpenTelemetry dashboards when upgrading: timer metrics are Histograms, Dag-processing metrics have new tags, and task execution has a dedicated `task.execute` span.

## Compatibility checks that prevent rollback traps

Upgrade every Airflow component before deploying pandas 3. Older components cannot read XComs carrying pandas 3 DataFrame names, and configuration allowlists do not repair that. Also audit dtype-sensitive code because pandas 3 reconstructs string and missing values differently.

When custom Dag bundles were migrated from 2.x, force a successful parse with `airflow dags reserialize` if legacy Dags remain incorrectly attached to `dags-folder`.
