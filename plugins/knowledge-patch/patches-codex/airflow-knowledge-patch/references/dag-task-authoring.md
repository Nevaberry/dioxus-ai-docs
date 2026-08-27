# Dag and task authoring

## Logical dates and data intervals

Future logical dates are rejected. Pass `logical_date=None` to create a run at
the current time. Asset-triggered runs and REST-triggered runs that omit the
date keep it as `None`, have no data interval, and omit `logical_date`,
`data_interval_start`, and `data_interval_end` from task context. Guard
`dag_run.logical_date` before using it. (3.0.0)

For manual runs, the supplied logical date and timetable-resolved data interval
are independent concepts. Use `logical_date` for logic about the requested
trigger date; use `data_interval_start` and `data_interval_end` only for
interval semantics. (3.0-upgrade)

## Completion, callbacks, pools, and teardown

- `on_success_callback` is not called when a task is marked `SKIPPED`.
  (3.0.0)
- Effective `priority_weight` is capped by available pool slots; a high weight
  cannot override pool capacity. (3.0.0)
- Teardown tasks execute after early Dag-run termination. They cannot use
  `TriggerRule.ALWAYS`; choose a trigger rule that retains upstream dependency
  semantics. (3.0.0)
- Use the Dag argument `fail_fast`; `fail_stop` is removed. (3.0.0)
- Dag callbacks receive a task instance relevant to the Dag's final state,
  rather than an arbitrary lexicographically selected instance. (3.2.0)

`ALL_DONE_MIN_ONE_SUCCESS` waits until all upstream tasks are done and requires
at least one success. Skipped upstream tasks retain normal skip propagation.
(3.1.0)

## Human-in-the-loop tasks

`HITLOperator`, `ApprovalOperator`, and `HITLEntryOperator` are supplied by
`apache-airflow-providers-standard`. A HITL task defers while it awaits an
authorized UI or API response. Forms can show XCom values and Dag parameters;
notification helpers can link responders to the required-action page. (3.1.0)

`AgenticOperator` can attach HITL review to agentic workflows. (3.2.0)

HITL tasks use the distinct `awaiting_input` state while parked on the
triggerer. Monitoring should recognize it; `airflow dags test` waits for the
input instead of spinning. (3.3.0)

## Deadline Alerts

Deadline timing can be relative to Dag-run queued time, logical date, or a
fixed datetime, with positive or negative intervals. In the `3.1.0` batch this
experimental feature accepts only `AsyncCallback`.

The `3.2.0` batch adds experimental `SyncCallback`, executed on an executor
selected by its `executor` argument, and permits a Dag `deadline` list that
mixes synchronous and asynchronous callbacks. At that stage, synchronous
callbacks cannot read metadata-database Connections.

The `3.3.0` batch allows synchronous callbacks to access Connections and
Variables. Alerts also gain names, Variable-resolved intervals, Core API
endpoints, and `callback_execution_timeout`.

## Retry behavior

`retry_exponential_backoff` accepts a numeric multiplier such as `3.5`.
`0` disables backoff. Python booleans remain compatible in task code as `2.0`
and `0.0`, but the REST schema is numeric and rejects booleans. (3.2.0)

A task can supply a custom retry policy that decides whether and when to retry
for selected exceptions or custom backoff. `TriggerDagRunOperator` wait
failures, including a failed triggered Dag run, participate in that policy.
(3.3.0)

## Templates, callables, and external implementations

An operator can set `render_template_as_native_obj=True` or `False` to override
the Dag setting; `None` inherits the Dag-level choice. (3.2.0)

`PythonOperator` accepts an `async def` `python_callable` directly; do not
manage an event loop around it. (3.2.0)

`@task.stub` declares a task whose implementation is outside Python. (3.2.0)
The Coordinator layer can route such declarations to experimental
`JavaCoordinator` for JVM tasks or `ExecutableCoordinator` for native binaries
such as Go programs. Those runtimes use the Execution API for Variables,
Connections, and XCom while authoring and scheduling remain in Python.
(3.3.0)

## Continuous Dags

A Dag with `schedule="@continuous"` can omit `start_date`; it starts
immediately when unpaused. (3.2.0)

## Task SDK runtime access

The SDK can construct Connections from URIs, `RuntimeTaskInstance` can retrieve
the previous task instance, and `BaseXcom` is exported from `airflow.sdk`.
(3.2.0)

Async tasks have native asynchronous XCom accessors and
`BaseHook.aget_hook()`. Structured XCom outputs can round-trip as Pydantic
models when the worker-side Dag registers the output types. (3.3.0)

## Dag-designated results

Use `@result` to designate a TaskFlow task as the Dag result, or mark a
return-value XCom as the result. The Dag-run NDJSON wait API can then return
that result without the caller naming an arbitrary task XCom. (3.3.0)

## Removed task internals

`PriorityWeightStrategy.serialize()` and `.deserialize()` are removed. So are
internal `TaskInstance.run()`, `.render_templates()`,
`.get_template_context()`, and their related private members. Do not rebuild
task execution around these internals. (3.2.0)
