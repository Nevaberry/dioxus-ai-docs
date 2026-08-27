# Clients, Observability, and Audit

## mysql and mysqldump

### Disabled mysql client commands (9.4-9.6)

Most **mysql** client commands require `--commands`, which is off by default.
Enable commands explicitly when interactive workflows or scripts need them:

```console
mysql --commands=ON
```

### Dumping accounts (9.2-9.3)

`mysqldump --users` emits `CREATE USER` and `GRANT`. Add `--add-drop-user` to
prefix `DROP USER`; use `--include-user` and `--exclude-user` to select accounts.

### Dump-option defaults (9.2-9.3)

`--column-statistics` is disabled by default. `--compact` disables the
otherwise-default `--tz-utc`, so it can extract values without UTC conversion and
without a corresponding time-zone statement in the dump.

## Configuration and usage tracking

### MySQL Configurator CLI (9.2-9.3)

Windows MySQL Configurator added a CLI in 9.2. Initially only `configure` ran; in
9.3, other `--action` operations execute too.

### Option Tracker counters (9.2-9.3)

Option Tracker covers binary logging, replicas, Group Replication, and both
optimizer types. Each feature exposes a global
`option_tracker_usage:<feature_name>` value. In JSON output, the Boolean `used`
field is replaced by the counter `usedCounter`.

## Telemetry

### Network namespaces (9.2-9.3)

Linux OTLP exporters can enter separate network namespaces through:

- `telemetry.otel_exporter_otlp_traces_network_namespace`
- `telemetry.otel_exporter_otlp_metrics_network_namespace`
- `telemetry.otel_exporter_otlp_logs_network_namespace`

### Signal, endpoint, and credential configuration (9.4-9.6)

`telemetry.log_enabled`, `telemetry.metrics_enabled`, and
`telemetry.trace_enabled` default off. Their OTLP endpoint variables have no
default. Secret-header and provider settings can supply externally decoded
exporter credentials. The slow-query and general logs can feed Telemetry Logging.

## Account and server diagnostics

### Temporary account locks (9.4-9.6)

Performance Schema provides `TEMPORARY_ACCOUNT_LOCKS`. `HOST_CACHE` includes
`COUNT_ACCOUNT_LOCKED_ERRORS` and `COUNT_TEMPORARY_ACCOUNT_LOCKED_ERRORS`.

### Diagnostic Monitor (9.4-9.6)

Enterprise Edition includes `mysqldm`, which runs a predefined diagnostic query
set and writes JSON for support analysis. Its output directory, iteration count,
and delay are configurable.

## Audit Log

### Component and size rotation (9.4-9.6)

Enterprise Audit has a modular Audit Log component for component-based
installation and configuration. Changing `audit_log_rotate_on_size` requires
`AUDIT_ADMIN`.

### Time-based rotation (9.7.0)

`audit_log.rotate_on_time` rotates logs after elapsed time. Validation of
`audit_log_prune_seconds` accounts for both
`log_offload.log_analytics_schedule` and `audit_log_rotate_on_time`.

### Invalid-filter recovery (9.7.0)

At startup, configure `audit_log.filter_recovery_mode` for the component or
`audit_log_filter_recovery_mode` for the plugin. Available modes are:

- `LOG_ALL_IF_INVALID_FILTER_DETECTED`
- `LOG_NOTHING_IF_INVALID_FILTER_DETECTED`
- `ABORT_IF_INVALID_FILTER_DETECTED`

Choose explicitly according to whether audit continuity, restricted output, or
startup refusal is safest for the deployment.
