---
name: haproxy-knowledge-patch
description: HAProxy
version: 3.4.0
license: MIT
metadata:
  author: Nevaberry
---


# HAProxy Knowledge Patch

Load this skill when configuring, upgrading, debugging, or operating modern
HAProxy deployments. Treat the project configuration, runtime behavior, and
current maintenance branch as authoritative when they differ from general
guidance.

## Reference index

| Reference | Topics |
| --- | --- |
| [Filters, Lua, and Performance](references/filters-lua-and-performance.md) | CPU placement, compression, filters, connection pools, Lua APIs, and throttling |
| [Observability and Runtime APIs](references/observability-and-runtime.md) | Logs, traces, Runtime API, dynamic backends, statistics, samples, and diagnostics |
| [QUIC, HTTP, and Networking](references/quic-http-and-networking.md) | HTTP/1–3, QUIC, QMux, DNS, socket tuning, glitches, and retries |
| [Routing and Health Checks](references/routing-and-health.md) | Balancing, SPOP, server limits, reusable checks, retries, and backend switching |
| [TLS and Certificates](references/tls-and-certificates.md) | Certificate policy, ACME, SNI, ECH, key handling, TLS tracing, and crypto converters |
| [Upgrades and Maintenance](references/upgrades-and-maintenance.md) | Breaking changes, deprecations, branch policy, build requirements, and security hardening |

## Upgrade hazards first

Before validating an upgraded configuration, check these behavior changes:

- Duplicate proxy-section names and duplicate server names only warned in
  3.1.0 but became errors in 3.3.0. Rename them before upgrading.
- An ACL can no longer combine multiple match types after `-m`; ambiguous
  constructs such as `path_beg -m reg` also warn.
- A backend without `balance` uses `random`, not `roundrobin`, from 3.3.0.
  State the algorithm explicitly when distribution stability matters.
- HTTP backends enable `option abortonclose` by default from 3.3.0. Disable it
  explicitly only when abandoned client work must still reach the server.
- `dns-accept-family` defaults to `auto`, conditionally enabling IPv6 after
  connectivity probes.
- `cpu-policy` defaults to `performance`; automatic placement uses all cores
  and NUMA nodes rather than stopping at 64 threads.
- Empty configuration arguments warn and are intended to become errors. Use
  `${NAME[*]}` for a deliberately empty environment expansion.
- `http-send-name-header` may not target `connection`, `content-length`,
  `host`, or `transfer-encoding`.

Run a configuration check after every migration and resolve warnings rather
than carrying them into the next feature branch.

## Replace deprecated configuration

### Dispatch backends

Replace a deprecated `dispatch <address>` with a regular server at that
address. If legacy servers remain in the backend, give them weight zero to
preserve dispatch behavior.

```haproxy
backend legacy_dispatch
    server dispatch 192.0.2.10:8080
```

Replace `transparent` or `option transparent` with a zero-address server to
retain routing to the original TPROXY destination.

```haproxy
backend original_destination
    server tproxy 0.0.0.0
```

### Filters and global directives

- Replace the shared compression filter and `compression-direction` with
  `filter comp-req` and `filter comp-res`.
- Replace `tune.takeover-other-tg-connections` with
  `tune.idle-pool.shared`.
- Replace `tune.quic.frontend.*` spellings with `tune.quic.fe.*` and replace
  global `no-quic` with `tune.quic.listen on|off`.
- Start master-worker mode with `-W` or `-Ws` instead of the deprecated global
  `master-worker` directive.
- Move legacy C mailers to Lua. `program` sections and C mailers reached their
  removal point in 3.3.0.
- Move tracing integrations from the deprecated OpenTracing filter to the
  OpenTelemetry add-on before the planned 3.5 removal.

## Create and remove backends at runtime

Create a backend, add and enable its servers, then publish it. Routing skips
disabled or unpublished backends unless `force-be-switch` is set.

```text
add backend test-backend from mydefaults mode http
add server test-backend/server1 127.0.0.1:3000 check
enable server test-backend/server1
enable health test-backend/server1
publish backend test-backend
```

For safe removal:

1. Put every server into maintenance.
2. Wait for each server to become `srv-removable`, then delete it.
3. Unpublish the backend.
4. Wait for `be-removable`, then delete the backend.

Named `defaults` sections stay in memory to support dynamic creation. Set
`tune.defaults.purge` only when the deployment will not create backends at
runtime.

## Make health checks reusable

Define a named `healthcheck` section and select it on each server. A definition
can be shared across backends, and servers in one backend may choose different
checks.

```haproxy
healthcheck app_http
    type httpchk
    http-check connect alpn h2
    http-check send meth HEAD uri /health ver HTTP/2 hdr Host www.example.com

backend webservers
    server web1 10.0.0.1:80 check healthcheck app_http
```

Use `init-state` when a server must remain down after startup or maintenance
until its first successful check. Use `check-reuse-pool` when checks should
reuse idle connections, and `strict-maxconn` when a server limit counts open
TCP connections rather than concurrent HTTP requests.

## Protect HTTP and QUIC listeners

- Cap HTTP/2 frame batches with `tune.h2.fe.max-frames-at-once` and
  `tune.h2.be.max-frames-at-once`.
- Set `tune.h2.fe.max-rst-at-once` between 1 and 10 to mitigate RST floods;
  very low values may add latency to interactive or gRPC traffic.
- Recycle long-lived HTTP/2 connections with
  `tune.h2.fe.max-total-streams`.
- Configure HTTP/1 glitch thresholds with `tune.h1.fe.glitches-threshold` and
  `tune.h1.be.glitches-threshold`.
- Gate threshold-based termination by CPU with
  `tune.glitches.kill.cpu-usage`; `0` means kill at the threshold regardless
  of CPU load.
- Filter abusive clients during the QUIC handshake with `quic-initial` rules.
- Bound a QUIC connection's lifetime request count with
  `tune.quic.fe.stream.max-total`.
- Bound peer-triggered TLS 1.3 KeyUpdate work with
  `tune.ssl.keyupdate-rate-limit`.

## Automate certificates carefully

Use `ssl-f-use` with a `crt-store` when certificates need independent TLS
versions, ALPN, cipher, or signature policy. For automatic server-side SNI,
use `sni-auto` or `no-sni-auto`; health checks have separate
`check-sni-auto` controls.

Built-in ACME begins as a single-load-balancer workflow. HTTP-01 issuance
requires the ACME challenge map to serve `/.well-known/acme-challenge/`.
Certificates created by the early workflow exist only in memory until saved
with `dump ssl cert`. DNS-01 automation uses the Data Plane API, writes issued
certificates to disk, and still requires manual synchronization across
multiple load balancers.

Protect passphrase scripts named by `ssl-passphrase-cmd`; HAProxy reuses
previously obtained passphrases before invoking the script again. ECH and
backend HTTP/3 remain experimental and require
`expose-experimental-directives`.

## Debug with staged logs and traces

Use `log profile` to assign formats independently at `accept`, `request`,
`connect`, `response`, `close`, `error`, or `any`. `do-log` emits additional
records during processing and can select a profile per invocation.

Add `term_events` to access logs when the final termination code is
insufficient. It records the sequence of termination states and can be decoded
with the supplied `term_events` utility. Use `when(condition)` to emit fields
such as `bs.debug_str` or `fs.debug_str` only when useful; `last_entity` and
`waiting_entity` locate the operation or rule behind an error or timeout.

Supported traces are configured in a dedicated `traces` section and controlled
through the Runtime API. Select focused sources such as `h1`, `h2`, `h3`,
`quic`, `qmux`, `ssl`, `acme`, `spop`, `peers`, or `check` instead of enabling
broad diagnostics indefinitely.

## Select a maintained branch

Choose feature-branch policy separately from patch-level maintenance. Even
feature branches are LTS releases maintained for five years; odd branches are
short-lived stable releases for operators prepared to upgrade more often.
Keep the final bug-fix component current and reproduce issues on the latest
patch before reporting them.

Treat a pending-fixes queue as fixes already selected for that maintenance
branch. A list of later development-branch fixes is only a candidate set, not
proof that the maintained branch is affected. Use severity to prioritize:
`MINOR` seldom justifies an update alone, `MEDIUM` normally warrants an update
or disabling the feature, `MAJOR` calls for a prompt upgrade, and `CRITICAL`
calls for an immediate release and upgrade.

## Verification checklist

1. Run the HAProxy configuration check and eliminate duplicate-name, empty
   argument, ACL-type, deprecated-directive, and privilege warnings.
2. State balancing, CPU, DNS-family, abort-on-close, and QUIC behavior
   explicitly when defaults affect correctness.
3. Test health checks, retry counts, custom timeouts, and backend selection
   together; custom stream settings are applied after backend selection in
   current 3.4 maintenance releases.
4. Exercise reloads separately from process restarts when relying on shared
   statistics or runtime-only certificate state.
5. Protect the stats administration endpoint against CSRF, restrict it with
   `stats scope`, and verify POST `Origin` handling.
6. Confirm the deployed branch is maintained and update to its latest patch
   before diagnosing a known defect.
