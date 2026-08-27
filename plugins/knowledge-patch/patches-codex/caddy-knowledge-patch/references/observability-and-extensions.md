# Observability, CLI, builds, and extensions

## Metrics placement and lifecycle

Since 2.9.0, the Caddyfile `metrics` option is global rather than nested under `servers`. It supports optional per-host metrics and includes Go and process collectors.

```caddyfile
{
	metrics {
		per_host
	}
}
```

Metrics belong to the active configuration. Series from a replaced configuration do not persist after reload, so dashboards must tolerate series resets and disappearance.

The 2.11 line limits unbounded host cardinality in per-host metrics. `observe_catchall_hosts` explicitly opts catch-all hosts into observation, and later 2.11 releases can push metrics through the OpenTelemetry protocol.

Do not enable arbitrary per-host labels for unbounded public hostnames. Decide whether catch-all traffic needs a bounded aggregate or explicit host observation.

## Tracing

The 2.11 tracing module switches to OpenTelemetry auto-export and can attach configured span attributes. Deployment environment variables and collector reachability may therefore affect export without a Caddyfile transport block.

Access logs gain a `spanID` field and `{http.vars.span_id}` since 2.9.0, allowing logs to be correlated with trace spans.

## Access-log privacy

Access logs redact values for `Cookie`, `Set-Cookie`, `Authorization`, and `Proxy-Authorization` by default. Server-level `log_credentials` deliberately disables that protection.

Enable credential logging only when the destination, retention rules, support tooling, and all downstream exports are approved to hold secrets. Body fields can be equally sensitive.

Request matching and access logs recognize `Transfer-Encoding` since 2.9.0.

## File-log permissions and directories

Since 2.9.0, log file permissions are configurable, including for a file that already exists. Missing log directories are created automatically.

In the 2.11 line, directory modes are configurable and the configured file mode propagates to rotated files. Verify effective permissions after both startup and rotation; checking only the initial file is insufficient.

## Rotation and compression

File logs gain time-based rolling in the 2.11 line. As of 2.11.2, rotated logs support `zstd`, and `roll_gzip` is deprecated in favor of `roll_compression`.

Update old Caddyfiles and ensure archival tools recognize the chosen compression format.

## Sampling and journald

Caddyfile log sampling is available since 2.9.0 for high-volume output. In the 2.11 line, sampling intervals accept duration strings.

Later 2.11 releases add a journald encoder wrapper that preserves timestamps around wrapped JSON logs. Configure the wrapper when journald is the sink and downstream consumers still expect the original structured timestamp.

Sampling can hide rare failures. Keep unsampled error or audit paths when every event matters.

## Request, response, and ECH fields

The 2.11 line adds:

- `{http.request.body_base64}` for the base64-encoded request body;
- `{http.response.body}` for a captured response body used by `log_append`;
- an early-execution option for `log_append` fields needed before the handler chain ends; and
- HTTP logging fields and placeholders that expose ECH status.

```caddyfile
log_append request_body {http.request.body_base64}
log_append response_body {http.response.body}
```

Body fields are not a safe default for general access logging. Keep them narrowly scoped and apply retention and access controls.

## QUIC diagnostics

Set `QLOGDIR` to make Caddy write QUIC qlog data (since 2.9.0). qlogs can be large and may contain connection metadata; use a controlled diagnostic directory and remove captures after analysis.

TLS traffic secrets require the separate, highly sensitive `insecure_secrets_log` option described in [TLS and PKI](tls-and-pki.md).

## Event handlers

The global `events` block binds module-provided handlers to named events. Event payload fields are exposed through `{event.data.*}` placeholders.

```caddyfile
{
	events {
		on cert_obtained exec ./notify.sh {event.data.certificate_path}
	}
}
```

The `exec` handler in this example requires its plugin. Debug logging reveals emitted event names and payloads, which is useful when developing a handler.

Since 2.10.0, the event type lives in core, allowing core code to emit events as well as modules.

## CLI configuration input

### Format a selected file

Since 2.9.0, `caddy fmt` accepts `--config` and rejects multiple input configurations.

```sh
caddy fmt --config Caddyfile
```

### Adapt standard input

Since 2.10.0, `caddy adapt` can read its input from standard input.

```sh
caddy adapt --adapter caddyfile < Caddyfile
```

### Machine-readable module listing

The 2.11 line adds `caddy list-modules --json` for inventory and automation.

```sh
caddy list-modules --json
```

JSON configuration errors also include byte offsets where possible, allowing tooling to locate a failure precisely in the input document.

### Password hashing cost

Since 2.10.0, `caddy hash-password` accepts a configurable bcrypt cost. Higher costs slow both legitimate verification and brute-force attempts; benchmark the target hardware before choosing one.

## Adding packages

Since 2.9.0, `caddy add-package` accepts a version-qualified package path:

```sh
caddy add-package github.com/example/module@v1.2.3
```

Pin versions for reproducible custom binaries and retain the exact module inventory produced by `caddy list-modules --json`.

## Release and build baselines

Version 2.11.1 is the first published stable release in the 2.11 line. The unavailable 2.11.0 differs only in a CI job, so upgrade comparisons should use 2.11.1 as the stable starting point.

Build requirements changed materially:

- Caddy 2.10 switched from supporting the latest two Go minor releases to requiring the latest Go minor.
- Sources from 2.10.1 onward in that line require Go 1.25.0 or newer.
- Caddy 2.11 custom builds require Go 1.26.
- Caddy 2.11.2 release artifacts use Go 1.26.1.

Caddy 2.10 also moves to libdns 1.0-beta APIs. Older DNS provider modules are not source-compatible; upgrade provider packages before rebuilding or upgrading a custom binary.

## Embedding customization

The 2.11 line exposes `CustomBinaryName` and `CustomLongDescription`, allowing an embedded distribution to customize its executable name and long command description.

The `caddy run` command automatically sets `GOMEMLIMIT` since 2.10.0. Other subcommands and embedding paths do not receive that setup automatically.

## Extension API surface

### Commands, logging, matching, and request limits

- The command runner exposes a public `BuildContext`.
- Logging cores can supply a custom `zapcore.Core`.
- `PrivateRangesCIDR()` is exported for plugins.
- HTTP matcher modules can implement `MatchWithError` instead of communicating errors through request variables.
- Request-body limit handling uses the concrete `MaxBytesError` type.

These APIs are available since 2.9.0. Custom modules should migrate away from earlier workarounds once their minimum Caddy version includes them.

### Core networking and events

Core gains modular `network_proxy` support in 2.10.0. The event type also moves into core in that version, broadening the places that can emit event notifications.

### Contextual logging, transports, listeners, and parsing

The 2.11 line adds:

- custom `slog` handlers for contextual module logging;
- reverse-proxy transport interfaces for modifying transport behavior;
- packet-connection wrappers for listener integrations; and
- down-propagating Caddyfile `Helper.BlockState`, allowing nested directive parsing to share block state.

These are module contracts rather than user-facing directives. Gate code by the actual Caddy API version and test provisioning, cleanup, reload, and concurrent request behavior.
