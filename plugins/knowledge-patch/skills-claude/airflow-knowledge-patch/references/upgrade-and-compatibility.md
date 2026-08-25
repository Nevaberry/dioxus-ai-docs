# Upgrade and Compatibility

Use this reference for migration sequencing, public-interface boundaries, runtime support, serialization, and compatibility traps.

## Airflow 3 migration

### `airflow.sdk` is the stable authoring interface

For the **3.0-upgrade**, treat `airflow.sdk` as the semver-governed public interface for Dag authoring and task execution. Unlisted Python APIs, the metadata schema, and Web UI HTML are internal. Move decorators and core authoring types to the SDK, rename `Dataset*` imports to `Asset*`, and move `airflow.io.*` imports to `airflow.sdk.io.*`.

```python
from airflow.sdk import Asset, DAG, dag, get_current_context, task
```

Base extension interfaces are public. For built-in operators, parameters and behavior are stable but methods and class structure are not. Built-in executor implementations are not safe subclassing contracts.

### Upgrade preflight and compatibility checks

Upgrade to Airflow 2.7 or later first, preferably the latest 2.x. Back up and optionally clean the metadata database, then ensure Dag parsing and reserialization complete without errors. Ruff 0.13.1 or later provides Airflow rules: AIR301/AIR302 locate 3.0 breaks, while AIR311/AIR312 recommend migrations. Import-path changes can require `--unsafe-fixes`; enable F401 to remove stale imports.

```bash
airflow db clean
airflow dags reserialize
ruff check dags/ --select AIR301 --show-fixes
ruff check dags/ --select AIR301 --fix --unsafe-fixes
```

### Common operators moved to the standard provider

`BashOperator`, `PythonOperator`, `ExternalTaskSensor`, `FileSensor`, and other formerly core operators, sensors, and triggers require `apache-airflow-providers-standard`. Install that provider on Airflow 2.x and migrate imports before upgrading core.

### Configuration, database, and startup migration

Diagnose configuration changes with `airflow config update`, optionally apply them with `--fix`, and then migrate the database. Replace the webserver process with the API server and run the Dag processor separately, including in local development.

```bash
airflow config update --fix
airflow db migrate
airflow api-server
airflow dag-processor
```

### Removed facilities and API v2

Replace SubDAGs with TaskGroups, Assets, or data-aware scheduling. Replace SequentialExecutor with LocalExecutor, which supports SQLite. Replace CeleryKubernetesExecutor and LocalKubernetesExecutor hybrids with multiple-executor configuration. Deadline Alerts replace SLAs, Dag bundles replace CLI `--subdir`/`-S`, and the FastAPI stable `/api/v2` replaces `/api/v1`.

### DAG and XCom pickling are removed

Dags are always JSON-serialized, so embedded custom objects must be JSON-serializable. XCom pickling is also removed; use a custom XCom backend for values that need another representation.

## Public and internal interfaces

### Task SDK serialization has a versioned contract

Since **3.1.0**, versioned Dag-serialization contracts allow components deployed separately to be upgraded with less coordination. This is a decoupling foundation rather than complete code separation, which was planned for Airflow 3.2.

### Custom deserializers receive a loaded class

Since 3.1.0, `airflow.serialization.serializers` deserializers receive the loaded class, not a class-name string. Update custom signatures accordingly.

```python
def deserialize(cls: type, version: int, data: Any):
    ...
```

### Task-group serialization helpers are no longer public

Do not import `get_task_group_children_getter` or `task_group_to_dict` from `airflow.sdk.definitions.taskgroup`; they moved into server-side API services in 3.1.0.

### Serialization moved into the Task SDK

Since **3.2.0**, import `airflow.sdk.serde` and `airflow.sdk.serde.serializers.*`, not `airflow.serialization.serde` or `airflow.serialization.serializers.*`. The old paths warn and remain only until Airflow 4.

### Experimental and internal task methods were removed

`PriorityWeightStrategy.serialize()` and `.deserialize()` are removed. Internal `TaskInstance.run()`, `.render_templates()`, `.get_template_context()`, and related private members are also gone; use Task SDK and service interfaces instead.

### Legacy parsing and dataset modules are removed

`airflow.datasets`, `airflow.timetables.datasets`, and `airflow.utils.dag_parsing_context` no longer exist. Use their Airflow 3 SDK-era Asset, timetable, and parsing-context replacements.

## Runtime and dependency compatibility

### Runtime and database compatibility changed

Airflow 3.1.0 drops Python 3.9, supports Python 3.10 through 3.13, adds SQLAlchemy 2.0 compatibility, and supports the psycopg3 PostgreSQL driver.

### Runtime and official-image compatibility changed

Airflow 3.2.0 adds Python 3.14 support and requires SQLAlchemy 2. Official container images no longer include a MySQL client; add one in a derived image when needed.

### pandas 3 DataFrame XComs require an Airflow-first rollout

In **3.3.1**, Airflow recognizes both the pandas 2-era `pandas.core.frame.DataFrame` name and pandas 3's `pandas.DataFrame` name, so either pandas version can read XComs written by the other after Airflow is upgraded. Upgrade every Airflow component, especially workers, before introducing pandas 3. Older Airflow cannot read pandas 3 DataFrame XComs, `allowed_deserialization_classes` does not fix this, and rolling Airflow back strands those XComs until Airflow is upgraded again.

The reader's pandas version controls reconstructed dtypes. Under pandas 3, string columns use `str` rather than `object`, and missing values use `nan` rather than `None`. Audit dtype branches, identity checks, and `DataFrame.equals()` assertions.

## Dag bundle migration

### Custom Dag bundle upgrades repair legacy bundle names

The 2.x-to-3.x migration could label every legacy Dag as belonging to `dags-folder`, blocking runs when another bundle was configured. Since 3.3.1, the Dag processor performs a best-effort path-based repair at startup. Unmatched Dags repair on their next successful parse; run `airflow dags reserialize` to force that parse.
