# Logging and Observability

## Transaction-stage logging

### Destination-specific log profiles (since 3.1.0)

`log profile` assigns formats independently at the `accept`, `request`,
`connect`, `response`, `close`, `error`, or `any` transaction stage and ties
the profile to a particular log destination. One profile can emit at several
stages with destination-specific formats. The `do-log` action emits additional
logs while traffic is processed.

### Per-action profiles (since 3.4.0)

`do-log` can select a log profile per invocation. A frontend no longer has to
use the same profile for every `do-log` action merely because that profile was
chosen by its `log` line.

```haproxy
http-request do-log profile syslog
```

## Tracing

### Supported runtime-controlled tracing (since 3.1.0)

Tracing is supported rather than experimental, has a dedicated configuration
section, and is controllable through the Runtime API. Trace sources include
`h1`, `h2`, `h3`, `quic`, `qmux`, `fcgi`, `spop`, `peers`, and `check` for
focused advanced debugging.

### TLS tracing (since 3.2.0)

The Runtime API `trace` command has an `ssl` source for TLS-related events.

### ACME tracing (since 3.3.0)

The `acme` source exposes certificate-automation events.

```haproxy
traces
    trace acme sink stdout level user event +any verbosity clean start now
```

## Termination and diagnostic samples

### Conditional diagnostic fields (since 3.1.0)

The `when(condition)` converter returns its input unchanged when the condition
is true and no value otherwise. It can emit `bs.debug_str` and `fs.debug_str`
only under selected conditions.

`last_entity` and `waiting_entity` identify the operation interrupted by a
timeout or error. They can also expose the last evaluated rule behind an
accept, redirect, or deny.

### Multiple termination events (since 3.2.0)

`term_events` records a comma-separated sequence of request termination states
instead of only the final stream state. Add it directly to an access log, then
decode it with the supplied `term_events` program.

```haproxy
log-format "$HAPROXY_HTTP_LOG_FMT %[term_events]"
```

## Statistics and metrics

### Persistent reload statistics (since 3.3.0)

Experimental shared-memory statistics require
`expose-experimental-directives`, a global `shm-stats-file`, and a unique
`guid` on every participating frontend, backend, and server. Reloading
preserves the statistics, but restarting the process does not. `show stat
typed` marks each metric `P` for persistent or `V` for volatile.

```haproxy
global
    expose-experimental-directives
    shm-stats-file /dev/shm/haproxy-stats

frontend example
    guid a88e2a95-547e-47f1-b406-ea82ea47abcc
    bind :80
    use_backend webservers

backend webservers
    guid 3db38dc1-4aa8-4172-b7de-affb7f1f51a8
    server web1 172.16.0.12:80 check guid 775e29c2-0b97-4f19-9976-dba604b833f4
```

### Runtime diagnostic counters (since 3.3.0)

`show dev` reports thread-to-CPU bindings. `show info` reports added and
removed line counts for map and ACL files, helping identify automation that
continually adds entries without removing them.

### Stick-table update metric (since 3.4.0)

The Prometheus endpoint exports `haproxy_sticktable_local_updates`, a
cumulative gauge of local updates for each configured stick table, allowing
update rates to be monitored.

### HTTP/2 error-log scope (since 3.4.0)

`tune.h2.log-errors` selects stream-scope logging, connection-scope-only
logging, or no HTTP/2 error logging. Its default is the most verbose `stream`
mode.

### Stats page version display (since 3.4.0)

The Stats page hides the HAProxy version by default. Add `stats show-version`
to display it.

### Scoped administration and POST validation (since 3.4.3)

`stats admin` operations honor `stats scope`, preventing administration of
proxies excluded by the configured scope. Stats POST requests validate their
`Origin`. The stats administration interface remains documented as vulnerable
to CSRF and must be protected accordingly.

## Telemetry transition

### OpenTelemetry replacing OpenTracing (since 3.4.0)

OpenTelemetry support is available as an add-on replacing OpenTracing.
OpenTracing is officially deprecated and remains scheduled for removal in
3.5.
