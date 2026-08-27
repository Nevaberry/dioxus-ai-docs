# Observability and security

## Structured task and operator logging

`LoggingMixin.log`, including hook and operator loggers, is a structlog logger.
Standard-library logging calls remain valid, while structured calls can attach
searchable fields. (3.1.0)

```python
self.log.info("Registering adapter", name=item.name)
```

## JSON service output

Set `[logging] json_logs = True` to emit API-server access logs, warnings,
exceptions, and other output as newline-delimited JSON. `airflow celery worker`
does not support this mode. (3.2.0)

```ini
[logging]
json_logs = True
```

## Logging and tracing controls

`log_timestamp_format` controls component timestamps and
`uvicorn_logging_level` sets API access-log verbosity. The Execution API
propagates correlation IDs. The `executor.running_dags` gauge counts running
Dags. (3.2.0)

## Remote-log handler discovery

Remote logging resolves lazily in this order: (3.3.0)

1. a custom `[logging] logging_config_class`;
2. a provider `RemoteLogIO` selected from the `remote_base_log_folder` scheme;
3. the transitional `airflow_local_settings.py` fallback.

Provider handlers implement a no-argument `from_config()` method.
`airflow.logging_config.load_logging_config()` is deprecated. Callback
subprocesses can upload remote logs.

## OpenTelemetry metrics and spans

Timer metrics are Histograms rather than Gauges.
`dag_processing.last_run.seconds_ago` includes `file_path`, `bundle_name`, and
`file_name` tags. The legacy filename-suffixed metric remains enabled unless
`[metrics] legacy_names_on` is disabled. Head sampling is supported, and
custom samplers receive `dag_id`, `run_id`, and `run_type`. (3.3.0)

Task execution has a dedicated `task.execute` span. The
`dagrun.duration.failed` metric includes a `run_type` tag for dashboard and
trace segmentation. (3.3.1)

## API transport security

The API server and client support mutual TLS and private certificate
authorities. Credentialed CORS is configurable, but wildcard origins are
rejected when credentials would make them unsafe. Connection tests can run
asynchronously on workers so the API server does not need direct access to
Connection secrets. (3.3.0)

## Backfill authorization

`BaseAuthManager.is_authorized_backfill` is removed. Backfills are authorized
through `requires_access_dag` for `DagAccessEntity.Run`. Update policies that
grant Backfill permission without Dag-run permission. (3.2.0)

## Secrets backend configuration

Set individual backend arguments with
`AIRFLOW__SECRETS__BACKEND_KWARG__<KEY>` environment variables instead of
constructing one combined kwargs value. (3.2.0)

## Team-scoped sensitive configuration

Sensitivity checks normalize `[<team>=<section>]` and
`AIRFLOW__<TEAM>___<SECTION>__<KEY>` to their base option. Consequently,
`AirflowConfigParser.as_dict(display_sensitive=False)`, configuration REST
endpoints, and `airflow config list` return `< hidden >` for team-scoped
sensitive values. An authorized caller that truly needs values must request
`display_sensitive=True`. (3.3.1)

Team-scoped `_cmd` and `_secret` entries remain masked in place. They are not
resolved and removed because those forms cannot be resolved for a team.
