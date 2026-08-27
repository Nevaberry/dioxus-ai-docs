# Observability and Runtime APIs

## Transaction-stage log profiles

HAProxy 3.1.0 adds `log profile`, allowing destination-specific formats at the
`accept`, `request`, `connect`, `response`, `close`, `error`, and `any` stages.
A profile may therefore emit several records during one transaction. The
`do-log` action emits an additional record while rules are running.

Since 3.4.0, each `do-log` invocation can select its own profile instead of all
invocations in a frontend inheriting the profile on the `log` line.

```haproxy
http-request do-log profile syslog
```

## Supported traces and runtime control

Tracing is supported, configured in a dedicated section, and controlled by the
Runtime API since 3.1.0. Sources include `h1`, `h2`, `h3`, `quic`, `qmux`,
`fcgi`, `spop`, `peers`, and `check`. The `ssl` source was added in 3.2.0 and
the `acme` source in 3.3.0.

```haproxy
traces
    trace acme sink stdout level user event +any verbosity clean start now
```

Keep trace scope and duration narrow on busy systems.

## Multi-event termination diagnostics

The 3.2.0 `term_events` fetch records the sequence of request termination
states as a comma-separated value, rather than exposing only the final stream
state. Append it to an access log, then decode it with the supplied
`term_events` utility.

```haproxy
log-format "$HAPROXY_HTTP_LOG_FMT %[term_events]"
```

## Conditional diagnostics

The 3.1.0 `when(condition)` converter returns its input only while its
condition is true. Use it to include `bs.debug_str` and `fs.debug_str` only
for selected failures. `last_entity` and `waiting_entity` identify the
operation interrupted by an error or timeout and can expose the final rule
behind an accept, redirect, or deny.

## Master CLI worker sessions

Since 3.2.0, select a worker by relative PID with `@@` instead of `@` to keep
the Master CLI session interactive until exit or command completion. The
master's prompt mode carries into the worker; `prompt` accepts `n`, `i`, and
`p`. Persistent sessions can subscribe to event rings, including the `dpapi`
ring initially used for ACME notifications.

## Runtime-created backends

HAProxy 3.4.0 can add, publish, unpublish, and delete whole backends through the
Runtime API. A backend is unroutable until published. `use_backend` and
`default_backend` skip disabled or unpublished targets unless
`force-be-switch` is set.

```text
add backend test-backend from mydefaults mode http
add server test-backend/server1 127.0.0.1:3000 check
enable server test-backend/server1
enable health test-backend/server1
publish backend test-backend
```

Remove safely by placing every server in maintenance, waiting for
`srv-removable`, deleting the servers, unpublishing the backend, waiting for
`be-removable`, and deleting it. Named `defaults` sections remain resident for
dynamic creation; `tune.defaults.purge` releases them when dynamic backends are
not used.

## Persistent and typed statistics

Experimental statistics persistence in 3.3.0 requires
`expose-experimental-directives`, a global `shm-stats-file`, and a unique
`guid` on every participating frontend, backend, and server. Reloads preserve
the shared statistics, but full process restarts do not. `show stat typed`
marks each metric `P` for persistent or `V` for volatile.

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

## Runtime diagnostics and version queries

In 3.3.0, `show dev` reports thread-to-CPU bindings and `show info` adds counts
of lines added to and removed from Map and ACL files. Use the latter to detect
automation that continually grows files. CLI version-only formats are `-vq`,
short version `-vqs`, and branch `-vqb`.

The `haproxy-dump-certs` script introduced in 3.3.0 writes certificates from a
stats or master socket to disk. Install the `halog` utility with
`make install-admin`; `make install` is no longer its installation target.

## Connection, TLS, counter, and date samples

The 3.2.0 `bc_reused` fetch says whether a transfer reused a backend
connection. ClientHello capability fetches are `req.ssl_cipherlist`,
`req.ssl_keyshare_groups`, `req.ssl_sigalgs`, and
`req.ssl_supported_groups`. `sc_key(<ctr>)` returns a tracked-counter key;
`table_clr_gpc(<idx>[,<table>])` and
`table_inc_gpc(<idx>[,<table>])` mutate a general-purpose counter and return
its previous or new value. `accept_date` and `request_date` fall back to the
session date when no stream exists, including early TLS handshake failures.

## Timeout, certificate, and thread samples

Added in 3.4.0, `cur_connect_timeout`, `cur_queue_timeout`, and
`cur_tarpit_timeout` expose current stream timeouts in milliseconds;
`fe_tarpit_timeout` exposes the frontend setting. `ssl_fc_crtname` returns the
selected incoming certificate name, and `tgroup` returns the zero-based thread
group position.

## Stick-table updates in Prometheus

The 3.4.0 Prometheus endpoint exports
`haproxy_sticktable_local_updates`, a cumulative gauge per configured stick
table. Derive a rate to alert on unexpected local write activity.

## Stats page and administration hardening

Since 3.4.0, the Stats page hides the HAProxy version by default. Add
`stats show-version` only if operators need it.

HAProxy 3.4.3 makes `stats admin` honor `stats scope`, preventing actions on
excluded proxies, and validates the `Origin` of Stats POST requests. The stats
administration UI remains documented as CSRF-vulnerable: isolate it, require
authentication, constrain scope, and do not treat Origin validation as the
only control.

## Sample converters and stricter decoding

The 3.4.0 `fe_exists` converter reports whether its input names a configured
frontend. In 3.4.3, Protobuf field lookup no longer permits nested-path
bypasses and rejects deprecated group wire types. Conversions that depended on
either ambiguous behavior now fail and should be covered by negative tests.
