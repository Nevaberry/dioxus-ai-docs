# Operations, Logging, and Extensions

Use this reference for service configuration, deployment, plugins, logging, tracing, security, and operational tooling.

## Plugins and extension contracts

### Plugins and Helm deployments

For the 3.0 upgrade, plugins using `appbuilder_views`, `appbuilder_menu_items`, or `flask_blueprints` must install the FAB provider compatibility layer or migrate to `external_views`, `fastapi_apps`, and `fastapi_root_middlewares`. In Helm values, move configuration from `webserver` to `apiServer` and review renamed and removed Airflow 3 options during the chart upgrade.

### Operator extra links are stored in XCom

The UI no longer runs custom operator-link code. A `BaseOperatorLink` declares an `xcom_key`, task execution stores the complete URL under that XCom key, and task-detail views retrieve it through the XCom backend.

### Plugins no longer register operators, hooks, or executors

Operators, sensors, hooks, and executors are plain Python classes. They cannot be registered or imported through the Airflow plugin namespace; import them directly from their packages.

```python
from my_plugin import MyHook
```

### Provider connection-form hooks are deprecated

Provider hook methods `get_connection_form_widgets` and `get_ui_field_behaviour` are deprecated as of 3.2.0.

### Extension hooks and plugin routes changed

Since 3.3.0, `BaseTrigger.on_kill()` handles user actions against a trigger, and `task_instance_mutation_hook` receives the related `DagRun`. Plugin navigation can opt into `nav_top_level`. `/auth` and `/pluginsv2` are reserved prefixes, and owner-link or extra-link `href` values are limited to HTTP, HTTPS, `mailto`, or relative URLs.

## API server and parser configuration

### Service and parser configuration moved

Since 3.0.0, API server options moved from `[webserver]` to `[api]`: `web_server_host` to `host`, `web_server_port` to `port`, `web_server_worker_timeout` to `worker_timeout`, `web_server_ssl_cert` to `ssl_cert`, and `web_server_ssl_key` to `ssl_key`. `workers` and `access_logfile` keep their names.

Dag parsing settings including `dag_file_processor_timeout`, `parsing_processes`, `file_parsing_sort_mode`, `max_callbacks_per_loop`, `min_file_process_interval`, `stale_dag_threshold`, and `print_stats_interval` moved to `[dag_processor]`. Other legacy `[webserver]` settings and obsolete scheduler/logging keys have no effect; use `airflow config lint`.

### API-server configuration moved again

In 3.1.0, move `log_fetch_timeout_sec`, `hide_paused_dags_by_default`, `page_size`, `default_wrap`, `require_confirmation_dag_change`, and `auto_refresh_interval` from `[webserver]` to `[api]`. Replace `[api] access_logfile` with `[api] log_config`, pointing at a `logging.config.fileConfig`-compatible file. `[api] workers` defaults to `1`; prefer multiple API-server instances for horizontal scaling.

`instance_name_has_markup`, `warn_deployment_exposure`, and `dag_stale_not_seen_duration` are removed.

### API-server output can be structured JSON

Set `[logging] json_logs` for newline-delimited JSON API-server access logs, warnings, exceptions, and other output. `airflow celery worker` does not support this mode in 3.2.0.

```ini
[logging]
json_logs = True
```

### Gunicorn enables rolling API-server workers

Install `apache-airflow-core[gunicorn]` and choose Gunicorn for preloaded, memory-sharing workers and zero-downtime FIFO recycling. Uvicorn is the default and does not support rolling restarts.

```ini
[api]
server_type = gunicorn
worker_refresh_interval = 43200
worker_refresh_batch_size = 1
```

## Deployment and process controls

### Edge Executor is generally available

Since 3.0.0, Edge Executor can run tasks in distributed or remote compute environments through the Task Execution API, enabling hybrid workers located near their data or applications.

### `DagBag` file statistics use real relative paths

Since 3.2.0, `FileLoadStat` includes nullable `bundle_path` and `bundle_name`. Paths no longer use a leading `/` to mean “relative to the Dags folder.” Custom tooling should use `pathlib.Path`, not that string convention.

### Container builds gained compliance controls

The `PYTHON_LTO` build argument makes Python link-time optimization configurable for FIPS builds. Docker builds can verify cryptographic signatures on Python source packages.

### Git Dag bundles support more repository setups

`GitDagBundle` supports submodules and HTTP URL authentication as of 3.2.0.

### Multiprocessing start methods are configurable per component

Since 3.3.0, `[core] mp_start_method` and `[core] mp_forkserver_preload` set global multiprocessing behavior. `[scheduler]`, `[triggerer]`, and `[dag_processor]` can override them.

## Secrets and transport security

### Secrets backend kwargs can be set independently

Since 3.2.0, configure individual secrets-backend arguments with `AIRFLOW__SECRETS__BACKEND_KWARG__<KEY>` instead of one combined kwargs value.

### API transport security is configurable

Since 3.3.0, the API client and server support mutual TLS and private certificate authorities. CORS credential behavior is configurable, and wildcard origins are rejected when credentials would make them unsafe. Connection tests can run asynchronously on workers, keeping Connection access away from the API server.

## Remote logging

### Remote-log handler discovery has a new contract

In 3.3.0, remote logging resolves in this order: custom `[logging] logging_config_class`, provider `RemoteLogIO` selected by the `remote_base_log_folder` scheme, then transitional `airflow_local_settings.py`. Provider handlers need a no-argument `from_config()` method. `airflow.logging_config.load_logging_config()` is deprecated, resolution is lazy, and callback subprocesses can upload remote logs.

## Metrics, logging, and tracing

### Logging and tracing gained operational controls

Since 3.2.0, `log_timestamp_format` customizes component timestamps, `uvicorn_logging_level` controls API access-log verbosity, and the Execution API propagates correlation IDs. The `executor.running_dags` gauge reports running Dags.

### OpenTelemetry metric contracts changed

Since 3.3.0, timer metrics are Histograms rather than Gauges. `dag_processing.last_run.seconds_ago` has `file_path`, `bundle_name`, and `file_name` tags; the legacy filename-suffixed metric stays enabled unless `[metrics] legacy_names_on` is disabled. Head sampling is supported, and custom samplers receive `dag_id`, `run_id`, and `run_type` attributes.

### Task execution has a dedicated OpenTelemetry span

Since 3.3.1, task execution has a `task.execute` span, and `dagrun.duration.failed` includes a `run_type` tag for trace and dashboard segmentation.
