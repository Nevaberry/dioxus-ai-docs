# API, CLI, and UI

Use this reference for authentication, REST clients, command-line migrations, UI endpoints, and interactive administration.

## Authentication and remote administration

### Authentication changes

For the 3.0 upgrade, Simple Auth is the default auth manager. To retain FAB, install its provider and set `auth_manager` to `airflow.providers.fab.auth_manager.fab_auth_manager.FabAuthManager`. Custom security managers import `FabAirflowSecurityManagerOverride` from `airflow.providers.fab.auth_manager.security_manager.override`.

Auth-manager routes are under `/auth`; update external OAuth redirects such as `/oauth-authorized/google` to `/auth/oauth-authorized/google`.

### Remote administration moved to `airflowctl`

Since 3.0.0, use `airflow` for local operations and `airflowctl`, distributed in `apache-airflow-client`, for remote operations such as triggering Dags or managing Connections.

## REST API behavior

### REST API v2 tightened request semantics

Clients must treat validation failures as HTTP 422, send `logical_date` instead of `execution_date`, and expect an omitted trigger date to stay `None`.

### DAG runs can be watched as an NDJSON stream

Since 3.1.0, `GET /api/v2/dags/{dag_id}/dagRuns/{dag_run_id}/wait` emits repeated JSON updates until completion. Use `result` to include an XCom result and build quasi-synchronous integrations without client-side status polling.

```bash
curl -H "Accept: application/x-ndjson" \
  "http://localhost:8080/api/v2/dags/ml_pipeline/dagRuns/manual_2024_01_15/wait?result=inference_task"
```

### REST search and bulk updates are more expressive

Since 3.2.0, search parameters support OR, Dags can be filtered by timetable type, and bulk task-instance endpoints accept wildcard `dag_id` and `dag_run_id`. Task-instance search supports `operator_name_pattern`, `pool_pattern`, and `queue_pattern`; bulk PATCH endpoints accept `update_mask`.

### API fallback pagination replaces page size

`api.page_size` is deprecated in favor of `api.fallback_page_limit`.

## CLI changes

### Deprecated CLI spellings were removed

Replace `--ignore-depends-on-past` with `--depends-on-past ignore`. Pass `dag_id` positionally to `airflow dags list-runs`. Replace `airflow tasks list --tree` with `airflow dag show`.

### CLI listings hide sensitive values by default

Since 3.2.0, `connections list` and `variables list` hide sensitive values unless `--show-values` is used; `--hide-sensitive` is also available. `connections list --conn-id` is removed, so retrieve a single Connection with `airflow connections get`.

### Development and access workflows gained self-service tools

The CLI supports hot reload through `--dev`, `auth list-envs` displays configured CLI environments and authentication status, and the UI can generate JWTs for API and CLI access.

## UI and extensions

### React Apps are an experimental plugin surface

Airflow 3.1.0 adds experimental full React applications and dashboard/menu integrations to the modern UI. Backend plugins also gain `iframe_views` for external views in navigation and Dag pages.

### UI task summaries use one NDJSON stream

Since 3.2.0, fetch task-instance summaries from `GET /ui/grid/ti_summaries/{dag_id}?run_ids=...`, which emits one `GridTISummaries` JSON line per run. The single-run `/ui/grid/ti_summaries/{dag_id}/{run_id}` endpoint is removed.

### XCom and HITL state can be managed in the UI

The UI can add, edit, and delete XCom values. HITL task details show the full approval and rejection history.

## Sensitive configuration

### Team-scoped sensitive configuration is masked

Since 3.3.1, sensitivity checks normalize `[<team>=<section>]` and `AIRFLOW__<TEAM>___<SECTION>__<KEY>` to the base option. `AirflowConfigParser.as_dict(display_sensitive=False)`, config REST endpoints, and `airflow config list` return `< hidden >` for team-scoped sensitive values. Authorized callers that require real values must explicitly request `display_sensitive=True`.

Team-scoped `_cmd` and `_secret` entries remain masked in place rather than being resolved and removed, because team resolution of those forms is unsupported.
