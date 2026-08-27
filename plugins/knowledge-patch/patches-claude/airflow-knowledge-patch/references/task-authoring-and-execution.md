# Task Authoring and Execution

Use this reference for task runtime access, callbacks, XCom behavior, operator authoring, retry policy, state, and non-Python execution.

## Runtime access and context

### Tasks no longer access the metadata database

Tasks and workers communicate with the API server through the Task Execution API. Task code must not use metadata ORM models or sessions. Use Task Context and SDK accessors during execution; for broader access to Dag runs, task instances, Connections, Variables, or XComs, use the stable REST API or `apache-airflow-client`. Obtain client tokens from `/auth/token`.

```python
from airflow.sdk import get_current_context

context = get_current_context()
ti = context["ti"]
connection = context["conn"].get("service")
variable = context["var"].value.get("setting")
```

### Context and manual-run dates

The 3.0 upgrade removes `tomorrow_ds`, `tomorrow_ds_nodash`, `yesterday_ds`, `yesterday_ds_nodash`, `prev_ds`, `prev_ds_nodash`, `prev_execution_date`, `prev_execution_date_success`, `next_execution_date`, `next_ds`, `next_ds_nodash`, and `execution_date` from context.

For manual runs, the resolved data interval need not be derived from or equal the supplied `logical_date`. Use `logical_date` for the requested trigger date and `data_interval_start`/`data_interval_end` only for timetable-resolved interval semantics.

```python
from airflow.sdk import get_current_context

requested_date = get_current_context()["logical_date"]
```

### Event-driven runs may have no logical date or data interval

Future `logical_date` values are rejected. Use `logical_date=None` to create a run at the current time. Asset-triggered runs and REST-triggered runs that omit it keep it as `None`, have no data interval, and omit `logical_date`, `data_interval_start`, and `data_interval_end` from task context. Inspect and guard `dag_run.logical_date`.

### Task SDK runtime access expanded

Since 3.2.0, the SDK can create Connections from URIs, `RuntimeTaskInstance` can retrieve the previous task instance, and `BaseXcom` is exported from `airflow.sdk`.

### Task exceptions moved into the SDK

Import task-facing exceptions such as `AirflowSkipException` and `TaskDeferred` from `airflow.sdk.exceptions`. Old `airflow.exceptions` proxies warn; providers can use `airflow.providers.common.compat.sdk`. Invalid sensor `poke_interval` or `timeout` arguments now raise `ValueError`, not `AirflowException`.

```python
from airflow.sdk.exceptions import AirflowSkipException, TaskDeferred
```

## XCom behavior

### XCom pulls are task-scoped by default

With the 3.0 upgrade, `ti.xcom_pull(key="shared_state")` searches only the current task. Name the producer when reading another task's XCom.

```python
value = ti.xcom_pull(task_ids="upstream_task", key="shared_state")
```

### XCom APIs reject unsafe or empty values

Since 3.1.0, the removed `enable_xcom_deserialize_support` option cannot make the API server deserialize unknown Python objects merely for display; non-native values use safer representations. `XCom.set()` and `XCom.get()` reject empty keys.

### Async tasks gained native XCom and hook access

Since 3.3.0, async tasks can use asynchronous XCom accessors and `BaseHook.aget_hook()` without synchronous calls. Structured XCom output can round-trip as Pydantic models when output types are registered from the worker-side Dag.

## Task lifecycle and callbacks

### Skipped tasks no longer receive success callbacks

`on_success_callback` is not invoked for a task marked `SKIPPED`.

### Teardown tasks survive DAG termination

Teardown tasks still run after early Dag-run termination. `TriggerRule.ALWAYS` is invalid for teardown tasks; choose a cleanup trigger rule that preserves upstream dependency semantics.

### `fail_stop` was renamed

Use the Dag argument `fail_fast`; the old `fail_stop` name is removed.

### Dag callbacks receive a state-relevant task instance

Since 3.2.0, a Dag callback receives a task instance relevant to the Dag's final state, not an arbitrary lexicographically selected instance.

### External task management has a TaskInstance API

Airflow 3.2.0 exposes a `TaskInstance` API for systems that manage task execution externally.

## Operator and task authoring

### Operators can override native template rendering

An operator can set `render_template_as_native_obj=True` or `False` to override the Dag setting. The default `None` inherits the Dag-level value.

### Retry backoff accepts a numeric multiplier

`retry_exponential_backoff` accepts a number such as `3.5`; `0` disables backoff. Python booleans remain compatible as `2.0` and `0.0`, but the REST schema is numeric and rejects booleans.

### `PythonOperator` accepts async callables

Since 3.2.0, pass an `async def` function directly as `python_callable`; user-managed event-loop code is unnecessary.

### `@task.stub` defines tasks implemented in other languages

Use `@task.stub` to declare a task in a Python-authored Dag when its implementation lives outside Python.

### `AgenticOperator` supports HITL review

Since 3.2.0, human review can be attached to `AgenticOperator` workflows.

### Task and operator loggers support structured fields

Since 3.1.0, `LoggingMixin.log`, including operator and hook loggers, is a structlog logger. Standard-library logging remains valid; structlog calls can attach searchable fields.

```python
self.log.info("Registering adapter", name=item.name)
```

## Human-in-the-loop execution

### Human-in-the-loop tasks

Airflow 3.1.0 adds `HITLOperator`, `ApprovalOperator`, and `HITLEntryOperator` in `apache-airflow-providers-standard`. A HITL task defers while awaiting an authorized UI or API response. Forms can show XCom values and Dag parameters, and notification helpers can link responders to the required-action page.

### HITL waiting has its own task state

Since 3.3.0, parked HITL tasks enter `awaiting_input` on the triggerer. Monitoring can distinguish this state, and `airflow dags test` waits for input rather than spinning indefinitely.

## State, retry, and results

### Tasks and assets have first-class state stores

Since 3.3.0, Task SDK accessors `task_state_store` and `asset_state_store` persist JSON state. Task state survives retries and runs. Both stores support `get`, `set`, `delete`, and `clear`, expiration and retention, optional `clear_on_success`, Core and Execution APIs, and asset-state access from triggers.

Storage defaults to the metadata database. `[workers] state_store_backend` selects a worker-side backend; retention garbage collection and row-size limits are configurable. `task_state_store.clear()` no longer accepts `all_map_indices`.

### Task retry policy is pluggable

A task can use a custom retry policy that decides whether and when to retry particular exceptions and can implement custom backoff. `TriggerDagRunOperator` waiting failures, including a failed triggered Dag run, participate in retry-policy handling.

### Dag runs can expose a designated result

Use `@result` to designate a TaskFlow task as the Dag result, or mark a return-value XCom as the result. The Dag-run NDJSON wait API can return that designated result without the caller naming an arbitrary task XCom.

## Durable and non-Python execution

### Java and Go task execution is experimental

In 3.3.0, `@task.stub(queue=...)` declarations can route through the experimental Coordinator layer. `JavaCoordinator` executes JVM tasks and `ExecutableCoordinator` executes native binaries such as Go programs. Those runtimes use the Execution API for Variables, Connections, and XComs while authoring and scheduling stay in Python.

### Spark jobs can survive worker failure

`ResumableJobMixin`, initially integrated with `SparkSubmitOperator`, tracks external work so execution can resume after worker failure instead of restarting it. Set `durable` to opt out of resumable behavior where required.

### `ResumableJobMixin` is now abstract

As of 3.3.1, custom subclasses must implement the mixin's required methods rather than relying on inherited defaults.

### Custom email backends now handle task alerts

Since 3.3.1, `email_on_failure` and `email_on_retry` honor `[email] email_backend` instead of always using `SmtpNotifier`. An unimportable backend path raises an error instead of silently falling back to SMTP.
