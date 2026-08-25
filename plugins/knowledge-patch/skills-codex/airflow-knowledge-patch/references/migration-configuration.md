# Migration and configuration

## Upgrade preflight and SDK boundary

Before the major upgrade, first reach Airflow 2.7 or later, preferably the
latest 2.x release. Back up the metadata database, optionally clean it, and
make sure every Dag parses and reserializes without errors. Ruff 0.13.1 or
later supplies Airflow checks: AIR301/AIR302 identify breaking changes and
AIR311/AIR312 recommend migrations. Import fixes can require
`--unsafe-fixes`; enable F401 handling to remove imports made stale by a move.

```bash
airflow db clean
airflow dags reserialize
ruff check dags/ --select AIR301 --show-fixes
ruff check dags/ --select AIR301 --fix --unsafe-fixes
```

Use `airflow.sdk` as the semver-governed Dag-authoring and task-runtime
interface. Rename `Dataset*` imports to `Asset*` and move `airflow.io.*` to
`airflow.sdk.io.*`. Unlisted Python APIs, metadata schema, and UI HTML remain
internal. Base extension interfaces are public, but built-in operator methods
and structure, and built-in executor implementations, are not safe subclassing
contracts. (3.0-upgrade)

## Task access to Airflow data

Tasks no longer open metadata ORM sessions. Workers use the Task Execution API;
task code uses context or SDK accessors for runtime state. For broader access
to Dag runs, task instances, Connections, Variables, or XComs, call the stable
REST API or `apache-airflow-client`; obtain client tokens from `/auth/token`.

```python
from airflow.sdk import get_current_context

context = get_current_context()
ti = context["ti"]
connection = context["conn"].get("service")
variable = context["var"].value.get("setting")
```

This Task Execution API boundary is part of the 3.0-upgrade batch.

## Standard provider imports

`BashOperator`, `PythonOperator`, `ExternalTaskSensor`, `FileSensor`, and other
formerly core operators, sensors, and triggers require
`apache-airflow-providers-standard`. Install the provider while still on
Airflow 2.x to migrate imports before the core upgrade. (3.0-upgrade)

## Services, database, and configuration migration

Use the updater to diagnose renamed or removed configuration and optionally
apply fixes before migrating the database:

```bash
airflow config update --fix
airflow db migrate
airflow api-server
airflow dag-processor
```

The API server replaces the webserver command. The Dag processor must run as a
separate process, including local development. Helm configuration under
`webserver` moves under `apiServer`. (3.0-upgrade)

The initial service-key moves are: (3.0.0)

| Old key | New key |
| --- | --- |
| `[webserver] web_server_host` | `[api] host` |
| `[webserver] web_server_port` | `[api] port` |
| `[webserver] web_server_worker_timeout` | `[api] worker_timeout` |
| `[webserver] web_server_ssl_cert` | `[api] ssl_cert` |
| `[webserver] web_server_ssl_key` | `[api] ssl_key` |

`workers` and `access_logfile` initially retain their names. Parser settings
including `dag_file_processor_timeout`, `parsing_processes`,
`file_parsing_sort_mode`, `max_callbacks_per_loop`,
`min_file_process_interval`, `stale_dag_threshold`, and `print_stats_interval`
move to `[dag_processor]`. Obsolete webserver, scheduler, and logging keys do
nothing; find them with `airflow config lint`.

Further API settings move from `[webserver]` to `[api]`: (3.1.0)

- `log_fetch_timeout_sec`, `hide_paused_dags_by_default`, `page_size`,
  `default_wrap`, `require_confirmation_dag_change`, and
  `auto_refresh_interval`;
- `[api] access_logfile` is replaced by `[api] log_config`, pointing to a
  `logging.config.fileConfig`-compatible file; and
- `[api] workers` defaults to `1`; horizontally scale with multiple API-server
  instances.

Remove the unused `instance_name_has_markup`, `warn_deployment_exposure`, and
`dag_stale_not_seen_duration` options.

## Plugin and auth migration

Plugins using `appbuilder_views`, `appbuilder_menu_items`, or
`flask_blueprints` must install the FAB compatibility provider or migrate to
`external_views`, `fastapi_apps`, and `fastapi_root_middlewares`.
(3.0-upgrade)

Simple Auth is the default auth manager. To retain FAB, install its provider
and configure:

```ini
[core]
auth_manager = airflow.providers.fab.auth_manager.fab_auth_manager.FabAuthManager
```

Custom security managers import `FabAirflowSecurityManagerOverride` from
`airflow.providers.fab.auth_manager.security_manager.override`. Auth-manager
routes use `/auth`; update redirects such as `/oauth-authorized/google` to
`/auth/oauth-authorized/google`. (3.0-upgrade)

## Removed facilities

Apply these replacements during the 3.0-upgrade:

- SubDAGs: use TaskGroups, Assets, or data-aware scheduling.
- SequentialExecutor: use LocalExecutor, which supports SQLite.
- CeleryKubernetesExecutor and LocalKubernetesExecutor: use multiple-executor
  configuration.
- SLAs: use Deadline Alerts.
- CLI `--subdir` and `-S`: use Dag bundles.
- REST `/api/v1`: use the FastAPI stable `/api/v2`.

The context keys `tomorrow_ds`, `tomorrow_ds_nodash`, `yesterday_ds`,
`yesterday_ds_nodash`, `prev_ds`, `prev_ds_nodash`, `prev_execution_date`,
`prev_execution_date_success`, `next_execution_date`, `next_ds`,
`next_ds_nodash`, and `execution_date` are removed. Use `logical_date` for the
requested trigger date, and `data_interval_start`/`data_interval_end` only for
timetable-resolved intervals. A manual run's interval need not equal its
supplied logical date.

Task-facing exceptions move to `airflow.sdk.exceptions`; old
`airflow.exceptions` proxies warn. Providers can import through
`airflow.providers.common.compat.sdk`. Invalid sensor `poke_interval` or
`timeout` values now raise `ValueError`, not `AirflowException`. (3.2.0)

`airflow.datasets`, `airflow.timetables.datasets`, and
`airflow.utils.dag_parsing_context` are removed. Use SDK-era asset, timetable,
and parsing surfaces. (3.2.0)

## Scheduling-default migration

`catchup_by_default=False` and `create_cron_data_intervals=False` are now the
defaults. A bare cron schedule therefore selects `CronTriggerTimetable`, not
`CronDataIntervalTimetable`. If tasks need interval boundaries or derived
`ds`/`ts` values, set `create_cron_data_intervals=True` before upgrading.
Switching it back after new-version runs exist skips one scheduled run to avoid
duplicating a `logical_date`. (3.0-upgrade)

## XCom pull migration

`ti.xcom_pull(key="shared_state")` searches the current task only. Name a
producer when reading a different task's value: (3.0-upgrade)

```python
value = ti.xcom_pull(task_ids="upstream_task", key="shared_state")
```
