# APIs, CLI, and UI

## Scheduler-managed backfills

Backfills are no longer separate CLI jobs. The scheduler handles them as Dag
runs, including versioning and observability, and users start and monitor them
through the UI or REST API. (3.0.0)

## Stable REST API semantics

Use the FastAPI `/api/v2` surface for external automation. Validation failures
return HTTP 422. Requests use `logical_date`, not `execution_date`; an omitted
trigger date stays `None`. (3.0.0)

API search and mutation become more expressive in the `3.2.0` batch:

- search parameters can express OR;
- Dags can be filtered by timetable type;
- bulk task-instance endpoints accept wildcard `dag_id` and `dag_run_id`;
- task-instance search supports `operator_name_pattern`, `pool_pattern`, and
  `queue_pattern`; and
- bulk PATCH endpoints accept `update_mask`.

External task-management systems can use the TaskInstance API instead of
reaching into server internals. (3.2.0)

`api.page_size` is deprecated; use `api.fallback_page_limit` for the fallback
pagination cap. (3.2.0)

For partition and state filters introduced later, see
[Assets, partitions, and state](assets-partitions.md#clearing-backfills-and-event-propagation).

## Dag-run NDJSON wait stream

Watch a run through
`GET /api/v2/dags/{dag_id}/dagRuns/{dag_run_id}/wait`. The response repeatedly
emits JSON updates until completion. The `result` query parameter can include
an XCom value, allowing quasi-synchronous integrations without polling.
(3.1.0)

```bash
curl -H "Accept: application/x-ndjson" \
  "http://localhost:8080/api/v2/dags/ml_pipeline/dagRuns/manual_2024_01_15/wait?result=inference_task"
```

A Dag can later designate its own result; clients can request that result
instead of identifying a task XCom. (3.3.0)

## Local and remote CLI responsibilities

Use `airflow` for local operations. Use `airflowctl`, distributed with
`apache-airflow-client`, for remote actions such as triggering Dags and
managing Connections. (3.0.0)

Replace removed CLI spellings as follows: (3.0.0)

- `--ignore-depends-on-past` becomes `--depends-on-past ignore`;
- `airflow dags list-runs` takes `dag_id` positionally; and
- `airflow tasks list --tree` becomes `airflow dag show`.

Connection and Variable listings hide sensitive values by default. Use
`--show-values` only when output handling is safe; `--hide-sensitive` makes the
choice explicit. `connections list --conn-id` is removed, so retrieve one
Connection with `airflow connections get`. (3.2.0)

## Clear, import, maintenance, and trigger controls

Dag clear accepts `only_new` to clear only newly added task instances.
`pools import` and `connections import` accept
`--action-on-existing-key`. `airflow db init` again accepts
`--use-migration-files`, and database cleaning can explicitly include or
exclude Dags. (3.2.0)

The `trigger` command accepts `--queues`, routing triggers by task queue to
specific Triggerer hosts. `max_trigger_to_select_per_loop` caps per-loop
selection in high-availability Triggerer deployments. (3.2.0)

Partition-range clear and backfill controls are documented in
[Assets, partitions, and state](assets-partitions.md#clearing-backfills-and-event-propagation).

## UI task and HITL state

Task-instance grid summaries use
`GET /ui/grid/ti_summaries/{dag_id}?run_ids=...`, returning one
`GridTISummaries` JSON line per run. The single-run
`/ui/grid/ti_summaries/{dag_id}/{run_id}` endpoint is removed. This remains a
UI endpoint, not the stable external REST surface. (3.2.0)

The UI can add, edit, and delete XCom values. HITL task details show complete
approval and rejection history. (3.2.0)

## React Apps and external views

React Apps are an experimental plugin surface for full applications and
dashboard or menu integrations. Backend plugins can also register
`iframe_views` for external content in navigation and Dag pages. (3.1.0)

For route restrictions and navigation controls, see
[Extensions, serialization, and XCom](extensions-serialization.md#plugin-hooks-navigation-and-routes).

## Development and self-service access

The CLI supports hot reload with `--dev`. `auth list-envs` reports configured
CLI environments and authentication state. The UI can generate JWTs for API
and CLI access. (3.2.0)
