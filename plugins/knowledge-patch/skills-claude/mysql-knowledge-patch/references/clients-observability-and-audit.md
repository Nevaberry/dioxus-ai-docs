# Clients, Observability, and Audit

Use this reference when updating command-line automation, dumps, telemetry,
diagnostics, account-lock monitoring, or Audit Log configuration.

## mysql and mysqldump

### Enable mysql client commands explicitly

Most **mysql** client commands are gated by `--commands`, which defaults off.
Enable them only where interactive tooling or scripts need them.

```console
mysql --commands=ON
```

### Dump accounts explicitly

`mysqldump --users` emits `CREATE USER` and `GRANT`. `--add-drop-user` prefixes
`DROP USER`; `--include-user` and `--exclude-user` select accounts.

### Recheck dump defaults and option interactions

`--column-statistics` defaults off. `--compact` disables the otherwise-default
`--tz-utc`, so compact dumps neither extract in UTC nor include a corresponding
time-zone statement. Set the required time-zone behavior explicitly.

## Option Tracker and account visibility

### Consume counters instead of Boolean usage

Option Tracker covers binary logging, replicas, Group Replication, and both
optimizer types. Each tracked feature exposes a global
`option_tracker_usage:<feature_name>` value. In JSON, the Boolean `used` field
is replaced by the counter `usedCounter`.

### Monitor temporary locks

Performance Schema includes `TEMPORARY_ACCOUNT_LOCKS`. `HOST_CACHE` adds
`COUNT_ACCOUNT_LOCKED_ERRORS` and `COUNT_TEMPORARY_ACCOUNT_LOCKED_ERRORS`.

## Telemetry

### Configure signals and endpoints explicitly

`telemetry.log_enabled`, `telemetry.metrics_enabled`, and
`telemetry.trace_enabled` default off. Their OTLP endpoint variables have no
default. The slow-query and general logs can feed Telemetry Logging.

Secret-header and provider settings can obtain externally decoded exporter
credentials. Configure secret handling alongside the endpoint rather than
embedding credentials in general configuration.

### Use exporter network namespaces on Linux

Place individual OTLP exporters in network namespaces with:

- `telemetry.otel_exporter_otlp_traces_network_namespace`
- `telemetry.otel_exporter_otlp_metrics_network_namespace`
- `telemetry.otel_exporter_otlp_logs_network_namespace`

## Diagnostics

Enterprise Edition includes `mysqldm`, which runs a predefined diagnostic
query set and writes JSON for support analysis. Its output directory, iteration
count, and delay are configurable.

## Audit Log

### Install the component and control privileges

Enterprise Audit provides a modular Audit Log component for component-based
installation and configuration. Changing `audit_log_rotate_on_size` requires
`AUDIT_ADMIN`.

### Rotate by elapsed time

`audit_log.rotate_on_time` rotates logs based on elapsed time. Validation of
`audit_log_prune_seconds` also accounts for
`log_offload.log_analytics_schedule` and `audit_log_rotate_on_time`.

### Choose invalid-filter startup behavior

The Audit Log component uses `audit_log.filter_recovery_mode`; the plugin uses
`audit_log_filter_recovery_mode`. Available modes are:

- `LOG_ALL_IF_INVALID_FILTER_DETECTED`
- `LOG_NOTHING_IF_INVALID_FILTER_DETECTED`
- `ABORT_IF_INVALID_FILTER_DETECTED`

Choose deliberately according to whether availability, fail-closed behavior,
or continued comprehensive logging has priority.
