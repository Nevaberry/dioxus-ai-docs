# Clients, Observability, and Audit

Use this reference for command-line behavior, account dumps, option usage,
telemetry exporters, account-lock visibility, diagnostic collection, and Audit
Log configuration.

## mysql client commands

Most **mysql** client commands are gated by `--commands` in batch 9.4-9.6, and
the option is off by default. Enable commands explicitly when an interactive
session or script requires them:

```console
mysql --commands=ON
```

SQL sent to the server is distinct from client-side commands. Test automation
that uses commands such as source-file handling or command shortcuts.

## mysqldump

### Dump user accounts

In batch 9.2-9.3, `mysqldump --users` emits `CREATE USER` and `GRANT`
statements. Related selectors are:

- `--add-drop-user` to prefix `DROP USER`;
- `--include-user` to select accounts; and
- `--exclude-user` to omit accounts.

Review generated account DDL for authentication factors and environment-specific
grants before restoring it.

### Changed default interactions

`--column-statistics` is disabled by default. `--compact` now disables the
otherwise-default `--tz-utc`; the dump is therefore not extracted in UTC and
does not contain the corresponding time-zone statement. Set time-zone behavior
explicitly when portable temporal output matters.

## MySQL Configurator

Windows MySQL Configurator gains a CLI in MySQL 9.2, in batch 9.2-9.3. The
initial limitation to `configure` was lifted in MySQL 9.3, so other `--action`
operations execute. The Configurator can also enable the Enterprise Firewall
component or upgrade a firewall plugin installation.

## Option Tracker

Option Tracker in batch 9.2-9.3 covers binary logging, replicas, Group
Replication, and both optimizer types. Every feature exposes a global status
item named:

```text
option_tracker_usage:<feature_name>
```

Its JSON usage field changed from Boolean `used` to the counter `usedCounter`.
Update dashboards and schemas to store a number.

## Telemetry

### Signal and endpoint defaults

In batch 9.4-9.6:

- `telemetry.log_enabled` defaults off;
- `telemetry.metrics_enabled` defaults off;
- `telemetry.trace_enabled` defaults off; and
- the corresponding OTLP endpoint variables have no default.

Secret-header and provider settings can supply externally decoded exporter
credentials. The slow-query and general logs can feed Telemetry Logging.
Community Edition includes the Telemetry component in batch 9.7.0.

### Linux network namespaces

Exporters can use separate Linux network namespaces through:

- `telemetry.otel_exporter_otlp_traces_network_namespace`;
- `telemetry.otel_exporter_otlp_metrics_network_namespace`; and
- `telemetry.otel_exporter_otlp_logs_network_namespace`.

The network namespace must contain a working route to the configured endpoint.

## Account-lock visibility

Performance Schema adds `TEMPORARY_ACCOUNT_LOCKS` in batch 9.4-9.6. `HOST_CACHE`
also adds:

- `COUNT_ACCOUNT_LOCKED_ERRORS`; and
- `COUNT_TEMPORARY_ACCOUNT_LOCKED_ERRORS`.

Use the table for current lock state and the counters for accumulated connection
failures.

## Diagnostic Monitor

Enterprise Edition adds `mysqldm` in batch 9.4-9.6. It runs a predefined
diagnostic query set and writes JSON for support analysis. Its output directory,
iteration count, and delay are configurable. Treat the output as operational
diagnostic data when choosing storage and access controls.

## Audit Log

### Component installation and authorization

Enterprise Audit gains a modular Audit Log component in batch 9.4-9.6 for
component-based installation and configuration. Changing
`audit_log_rotate_on_size` requires `AUDIT_ADMIN`.

### Rotate by elapsed time

`audit_log.rotate_on_time` in batch 9.7.0 rotates audit logs according to
elapsed time. Validation of `audit_log_prune_seconds` also accounts for:

- `log_offload.log_analytics_schedule`; and
- `audit_log_rotate_on_time`.

Validate the retention and offload schedule as one policy rather than tuning
the variables independently.

### Recover from an invalid filter

At startup, Audit Log can recover from an invalid filter under
`audit_log.filter_recovery_mode`, or
`audit_log_filter_recovery_mode` for the plugin. The available modes are:

- `LOG_ALL_IF_INVALID_FILTER_DETECTED`;
- `LOG_NOTHING_IF_INVALID_FILTER_DETECTED`; and
- `ABORT_IF_INVALID_FILTER_DETECTED`.

Choose explicitly between maximum capture, no capture, and refusing startup.
Make the selection part of incident and availability policy.
