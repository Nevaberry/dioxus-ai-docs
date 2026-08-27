---
name: airflow-knowledge-patch
description: Apache Airflow
version: "3.3.0"
license: MIT
metadata:
  author: Nevaberry
---



# Apache Airflow Knowledge Patch

Use this skill for Apache Airflow upgrades, Dag and task authoring, API and CLI
clients, plugins, deployment configuration, assets, partitions, execution, and
operations. Start with the migration rules and quick references below, then
open the topic reference that matches the work.

Prefer the project's manifest, constraints, configuration, code, and tests
when they demonstrate behavior that differs from this guidance. Check provider
versions separately from the core package because many operators and extension
surfaces ship independently.

## When to load this skill

Load it when:

- migrating a deployment or Dag from Airflow 2;
- importing authoring or runtime APIs in task code;
- updating API clients, CLI automation, plugins, or auth-manager integration;
- designing asset-aware, partitioned, HITL, deadline, or stateful workflows;
- changing scheduler, API-server, triggerer, logging, tracing, or container
  configuration;
- implementing custom serialization, XCom, retry, remote logging, or executor
  behavior; or
- diagnosing a behavioral change in scheduling, callbacks, reruns, task state,
  or Dag-run dates.

## Reference index

| Reference | Topics |
| --- | --- |
| [APIs, CLI, and UI](references/api-cli-ui.md) | Stable REST API, remote CLI, backfills, bulk operations, UI streams, HITL, and access workflows |
| [Assets, partitions, and state](references/assets-partitions.md) | Asset references, aliases, partition mapping, partition operations, team access, and state stores |
| [Dag and task authoring](references/dag-task-authoring.md) | Context, dates, callbacks, trigger rules, retries, templates, async tasks, results, and runtime access |
| [Execution and deployment](references/execution-deployment.md) | Executors, bundles, scheduler and triggerer controls, runtimes, containers, resumable jobs, and email |
| [Extensions, serialization, and XCom](references/extensions-serialization.md) | Plugin contracts, extra links, serialization paths, custom deserializers, XCom safety, and DataFrames |
| [Migration and configuration](references/migration-configuration.md) | Upgrade preflight, SDK imports, providers, services, auth, removed facilities, and configuration moves |
| [Observability and security](references/observability-security.md) | Structured logs, remote logs, metrics, tracing, transport security, masking, and correlation IDs |

## Breaking-change triage

### Author against `airflow.sdk`

Import stable Dag-authoring and task-runtime types from `airflow.sdk`. Metadata
ORM models, database sessions, unlisted Python APIs, Web UI HTML, built-in
operator internals, and built-in executor implementations are not stable
extension contracts.

```python
from airflow.sdk import Asset, DAG, dag, get_current_context, task
```

Task code must use context and SDK accessors. Use the REST API or
`apache-airflow-client` for broader metadata access.

### Install the standard provider

Core operators and sensors such as `BashOperator`, `PythonOperator`,
`ExternalTaskSensor`, and `FileSensor` require
`apache-airflow-providers-standard`. Install it before moving imports; it can
also be installed while the deployment still runs Airflow 2.

### Run separate API-server and Dag-processor services

The webserver command is replaced by `airflow api-server`, and the Dag
processor must run separately, including in local development.

```bash
airflow config update --fix
airflow db migrate
airflow api-server
airflow dag-processor
```

### Remove task-side metadata database access

Workers communicate through the Task Execution API. Replace ORM and session
use inside tasks with runtime context access:

```python
context = get_current_context()
connection = context["conn"].get("service")
variable = context["var"].value.get("setting")
```

### Migrate removed facilities

- Replace SubDAGs with TaskGroups, Assets, or data-aware scheduling.
- Replace SequentialExecutor with LocalExecutor; LocalExecutor supports SQLite.
- Replace hybrid Kubernetes executors with multiple-executor configuration.
- Replace SLAs with Deadline Alerts and `fail_stop` with `fail_fast`.
- Replace `/api/v1` with `/api/v2` and remote `airflow` CLI operations with
  `airflowctl` from `apache-airflow-client`.
- Replace CLI `--subdir`/`-S` with Dag bundles.
- Import operators, sensors, hooks, and executors from their packages, not the
  plugin namespace.

## Scheduling and context quick reference

### Make scheduling defaults explicit during migration

`catchup_by_default` and `create_cron_data_intervals` default to `False`.
Bare cron schedules therefore use `CronTriggerTimetable`. Set
`create_cron_data_intervals=True` before upgrading when tasks depend on data
interval boundaries or derived date strings.

### Guard event-driven dates

Asset-triggered and REST-triggered runs may have `logical_date=None` and no
data interval. Do not assume `logical_date`, `data_interval_start`, or
`data_interval_end` exists in task context. Manual-run logical dates and
timetable-resolved intervals also have distinct meanings.

### Scope XCom pulls to their producer

An unqualified XCom pull searches only the current task. Name the producer when
reading shared state:

```python
value = ti.xcom_pull(task_ids="upstream_task", key="shared_state")
```

### Use current task and callback semantics

- Skipped tasks do not receive `on_success_callback`.
- Teardown tasks still run when a Dag run terminates, but cannot use
  `TriggerRule.ALWAYS`.
- `ALL_DONE_MIN_ONE_SUCCESS` waits for every upstream task and requires at
  least one success.
- A Dag callback receives a task instance relevant to the Dag's final state.
- Effective priority weight cannot exceed available pool slots.

## Assets, partitions, and state quick reference

### Use typed asset-event keys

String keys do not address `inlet_events`, `outlet_events`, or
`triggering_asset_events`. Use `Asset`, `AssetAlias`, `Asset.ref`, or the
lookup helpers.

```python
outlet_events[Asset.ref(name="myasset")]
outlet_events.for_asset_alias(name="myalias")
```

### Design partition mappings with explicit limits

Partition mappings support validation, composition, fan-out, rollup, temporal
windows, wait policies, and runtime keys. Bound fan-out with
`partition_mapper_max_downstream_keys` or a per-mapper override. Partition
selectors also flow through clear and backfill operations.

### Store durable JSON state through SDK accessors

`task_state_store` and `asset_state_store` expose `get`, `set`, `delete`, and
`clear`, with expiration and retention controls. Task state can survive retries
and runs. Select a worker backend with `[workers] state_store_backend` when the
metadata database is not the desired store.

## API, UI, and integration quick reference

### Treat API validation and dates precisely

The stable API reports validation failures as HTTP 422, uses `logical_date`
instead of `execution_date`, and preserves an omitted trigger date as `None`.
Use wildcard and pattern filters, update masks, partition selectors, and bulk
operations where supported instead of client-side loops.

### Wait for a Dag run with NDJSON

The Dag-run wait endpoint streams JSON status updates and can return either a
named XCom result or the Dag-designated result. Consume it incrementally with
`Accept: application/x-ndjson`; do not parse the response as one JSON object.

### Keep UI endpoints UI-scoped

Grid task summaries use one NDJSON stream with one line per run. UI routes and
payloads are not substitutes for the stable REST API in external clients.

## Extension and serialization quick reference

### Keep custom values JSON-safe

Dags and XComs are not pickled. Ensure embedded Dag objects are JSON
serializable and use a custom XCom backend for other representations. Empty
XCom keys are invalid, and the API server does not deserialize unknown Python
objects merely for display.

### Update custom serializers

Custom deserializers receive the loaded class, not a class-name string. Import
serialization from `airflow.sdk.serde` and
`airflow.sdk.serde.serializers.*`; the old server-side paths are transitional.

### Return extra links through XCom

The UI no longer executes custom operator-link code. Declare an `xcom_key` on
the `BaseOperatorLink` and store the complete URL under that key.

## Operational quick reference

### Choose the API-server worker model deliberately

Uvicorn is the default. For preloaded workers and rolling FIFO recycling,
install `apache-airflow-core[gunicorn]`, set `[api] server_type = gunicorn`,
and configure worker refresh interval and batch size.

### Use structured logging and tracing contracts

Task and operator loggers accept structured key/value fields. API-server JSON
logs use `[logging] json_logs`; Celery workers do not support that mode. Treat
OpenTelemetry timer metrics as Histograms, account for new metric tags, and
expect a dedicated `task.execute` span.

### Secure API transport and sensitive configuration

API clients and servers can use mutual TLS and private CAs. Do not combine
credentialed CORS with wildcard origins. Team-scoped sensitive options are
masked through configuration APIs and CLI output unless an authorized caller
explicitly requests their values.
