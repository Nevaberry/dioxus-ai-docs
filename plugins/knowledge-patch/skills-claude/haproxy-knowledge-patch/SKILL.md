---
name: haproxy-knowledge-patch
description: HAProxy
version: 3.4.0
license: MIT
metadata:
  author: Nevaberry
---


# HAProxy Knowledge Patch

Use this skill for HAProxy configuration, migration, routing, Runtime API,
Lua, logging, TLS, QUIC, health-check, and operations work involving the
behaviors documented here. Determine the deployed branch and patch level,
then apply only guidance that matches it.

## Reference index

| Reference | Topics |
|---|---|
| [HTTP policy and data handling](references/http-policy-and-data-handling.md) | Compression, filters, delay actions, HTTP limits, samples, converters, ACLs, and Protobuf |
| [Logging and observability](references/logging-and-observability.md) | Log profiles, traces, termination diagnostics, statistics, metrics, and error logging |
| [Routing, backends, and health](references/routing-backends-and-health.md) | Balancing, retries, dynamic backends, SPOP, connection pools, and health checks |
| [Runtime API and Lua](references/runtime-api-and-lua.md) | Master CLI sessions, Runtime API commands, certificate operations, and Lua APIs |
| [TLS, QUIC, and networking](references/tls-quic-and-networking.md) | Certificate policy, ACME, SNI, QUIC, HTTP/3, QMux, and socket controls |
| [Upgrades and operations](references/upgrades-and-operations.md) | Breaking changes, deprecations, CPU defaults, startup diagnostics, branch maintenance, and upgrades |

## Breaking changes and migration priorities

### Make proxy and server names unique

Duplicate names across `frontend`, `listen`, `backend`, `defaults`, and
`log-forward` families, and duplicate server names, warned in 3.1 and became
breaking in 3.3. Rename collisions before moving to 3.3.

### Preserve the old balancing policy explicitly

A backend without `balance` uses `random` rather than `roundrobin` in 3.3.
Configure the former policy explicitly when distribution must remain the same:

```haproxy
backend application
    balance roundrobin
```

### Account for abort-on-close

HTTP backends enable `option abortonclose` by default in 3.3, allowing work to
stop before an abandoned request reaches a server. The option is also valid in
a frontend.

### Update compression configuration

Request and response compression use `filter comp-req` and `filter comp-res`
in 3.4. The shared compression filter and direction setting are replaced, and
`compression-direction` is deprecated.

```haproxy
backend application
    filter comp-res
    compression algo gzip
    compression type text/html text/plain application/json
```

Use `filter-sequence` when execution order must differ from declaration order.
A declared filter omitted from the sequence is skipped.

### Replace deprecated dispatch forms

Ahead of planned 3.5 removal, replace `dispatch <address>` with a regular
server named `dispatch` at the same address. Give other legacy servers weight
zero when that is necessary to preserve dispatch behavior.

```haproxy
backend legacy_dispatch
    server dispatch 192.0.2.10:8080
```

Replace `transparent` or `option transparent` with a zero-address server to
preserve routing to the original TPROXY address:

```haproxy
backend original_destination
    server tproxy 0.0.0.0
```

### Update renamed and retired directives

- Replace global `tune.quic.frontend.*` names with `tune.quic.fe.*` names.
- Replace global `no-quic` with `tune.quic.listen on` or
  `tune.quic.listen off`.
- Replace the global `master-worker` directive with command-line `-W` or
  `-Ws`.
- Treat backend `dispatch` and `option transparent` as deprecated.
- `program` sections and legacy C mailers were deprecated in 3.1 with removal
  scheduled for 3.3; Lua mailers are the supported replacement after removal.
- OpenTracing is deprecated and scheduled for removal in 3.5; OpenTelemetry
  is available as its add-on replacement.

### Fix configuration validation failures

- An ACL can no longer specify multiple match types after `-m`; the
  configuration fails instead of silently using the final type.
- Ambiguous combinations such as `path_beg -m reg` warn.
- `http-send-name-header` cannot target `connection`, `content-length`,
  `host`, or `transfer-encoding`.
- Empty arguments warn in 3.2 and were scheduled to become errors in the next
  version. Use `${NAME[*]}` for an intentionally empty environment expansion.

## Security and correctness priorities

### Protect the statistics administration interface

Stats administration remains documented as vulnerable to CSRF. Stats POST
requests validate `Origin`, and `stats admin` operations honor `stats scope`,
so scoped administration cannot reach excluded proxies.

### Bound TLS 1.3 KeyUpdate work

Use `tune.ssl.keyupdate-rate-limit` to place an explicit rate bound on
peer-triggered TLS 1.3 KeyUpdate processing.

### Apply protocol abuse controls

- `quic-initial` rules can reject, accept, silently drop a datagram with
  `dgram-drop`, or `send-retry` during the QUIC handshake.
- `tune.glitches.kill.cpu-usage` gates threshold-based connection termination
  by CPU usage; its default `0` kills at the configured threshold regardless
  of load.
- HTTP/2 frame and RST_STREAM batch limits can constrain overload and reset
  attacks. Values from 1 through 10 for `tune.h2.fe.max-rst-at-once` mitigate
  RST attacks, though very low values can add interactive or gRPC latency.
- HTTP/1 glitch thresholds exist independently for frontend and backend
  multiplexers; graceful close begins at 75% of the threshold when
  threshold-based termination is enabled.

### Expect stricter Protobuf conversion

Protobuf lookup rejects nested-path bypasses and deprecated group wire types.
Inputs relying on either behavior fail conversion.

## Routing and health quick reference

### Create a backend at runtime

A runtime-created backend is unavailable for routing until published. Build
it, enable its server and health, and publish it:

```text
add backend test-backend from mydefaults mode http
add server test-backend/server1 127.0.0.1:3000 check
enable server test-backend/server1
enable health test-backend/server1
publish backend test-backend
```

For safe removal, place every server in maintenance, wait for
`srv-removable`, delete the servers, unpublish the backend, wait for
`be-removable`, and delete the backend.

### Reuse health-check definitions

A named `healthcheck` section can contain a supported check type and its
`http-check` or `tcp-check` actions. Select it from a server with the
`healthcheck` argument.

### Select retry behavior dynamically

`set-retries` works in `tcp-request` and `http-request` rules. Custom stream
timeouts and maximum retries remain initialized correctly after backend
selection.

```haproxy
http-request set-retries 0 if METH_POST
```

Use `retry-on 421` when a misdirected request should be retried against a
different capable backend server.

### Enforce a backend connection ceiling

Add server argument `strict-maxconn` when `maxconn` must count open TCP
connections rather than concurrent HTTP requests.

## TLS and QUIC quick reference

### Attach policy to a certificate

Use frontend `ssl-f-use` to reference a certificate in `crt-store` and attach
certificate-specific TLS versions, ALPN, ciphers, or signature algorithms
without an external crt-list.

### Handle automatic backend SNI

HAProxy derives server-side SNI from the HTTP `host` header in 3.3.
`sni-auto` and `no-sni-auto` control traffic behavior; `check-sni-auto` and
`no-check-sni-auto` control health checks.

### Distinguish experimental transports

- Backend HTTP/3 uses a `quic4@` server address and requires
  `expose-experimental-directives` plus normal backend TLS verification.
- QMux carries QUIC frames over an ordered reliable byte stream and requires
  `expose-experimental-directives` with `alpn h3` on the relevant TCP
  `bind` or `server` line.
- Encrypted Client Hello uses the experimental `ech` bind argument, and
  clients must retrieve its public key from DNS.

## Observability and runtime quick reference

### Log at transaction stages

`log profile` assigns destination-specific formats at `accept`, `request`,
`connect`, `response`, `close`, `error`, or `any`. `do-log` emits additional
logs during processing and can select a profile per invocation in 3.4.

```haproxy
http-request do-log profile syslog
```

### Use focused supported tracing

Tracing is supported and controlled through the Runtime API. Sources include
`h1`, `h2`, `h3`, `quic`, `qmux`, `fcgi`, `spop`, `peers`, `check`, `ssl`,
and `acme`.

### Preserve statistics only across reloads

Experimental shared-memory statistics require
`expose-experimental-directives`, `shm-stats-file`, and unique `guid` values
on participating frontends, backends, and servers. They survive reloads but
not process restarts.

## Applying the references

Open the reference matching the current task before changing configuration.
Keep version-dependent syntax tied to its stated introduction or transition,
especially for compression, QUIC naming, balancing defaults, deprecations,
and experimental features.
