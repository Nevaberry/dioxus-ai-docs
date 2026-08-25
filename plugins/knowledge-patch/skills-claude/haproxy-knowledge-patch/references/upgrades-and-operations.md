# Upgrades and Operations

## Configuration parsing and validation

### Worker-owned parsing (since 3.1.0)

The master process only starts workers; workers parse configuration
themselves. This removes parse-then-undo work from the master and makes reload
operation more consistent, avoiding the older class of inconsistencies and
file-descriptor leaks.

### Duplicate names (3.1.0 to 3.3.0)

Duplicate names across proxy-section families such as `frontend`, `listen`,
`backend`, `defaults`, and `log-forward`, and duplicate server names, warn in
3.1.0 and become breaking in 3.3.0. HAProxy 3.1 otherwise introduced no
breaking changes.

### Empty arguments (since 3.2.0)

Empty arguments, including empty environment variables inside double quotes,
warn and were scheduled to become errors in the next version. Use `${NAME[*]}`
when an intentionally empty environment expansion is required.

### Startup diagnostics (since 3.3.0)

- Running as root without a global `user` directive warns.
- Leaving `expose-experimental-directives` enabled when no configured feature
  needs it warns.
- Oversized `thread-groups` ranges are trimmed with a warning against
  `nbthreads`; an emptied group is fatal.
- Static builds warn when `user` or `group` should be replaced by `uid` or
  `gid`.

## Deprecations and replacements

### Warning controls and scheduled removals (since 3.1.0)

Deprecated directives warn unless the global
`expose-deprecated-directives` option is set.

```haproxy
global
    expose-deprecated-directives
```

`program` sections and legacy C mailers were deprecated for removal in 3.3;
after removal Lua mailers are the supported replacement. The `opentracing`
filter was scheduled for deprecation in 3.3 and removal in 3.5.

### New warnings and renamed directives (since 3.3.0)

- Backend `dispatch` and `option transparent` warn as deprecated.
- Global `tune.quic.frontend.*` directives should use `tune.quic.fe.*`.
- Replace the global `master-worker` directive with command-line `-W` or
  `-Ws`.
- Replace global `no-quic` with `tune.quic.listen on` or
  `tune.quic.listen off`.

### Dispatch replacement

Ahead of planned 3.5 removal, replace `dispatch <address>` with a regular
server named `dispatch` at the same address. If the backend contains legacy
servers, give the other servers weight zero to preserve dispatch behavior.

```haproxy
backend legacy_dispatch
    server dispatch 192.0.2.10:8080
```

### Transparent dispatch replacement

Ahead of planned 3.5 removal, replace `transparent` or `option transparent`
with a server at `0.0.0.0`. This preserves routing to the original TPROXY
address.

```haproxy
backend original_destination
    server tproxy 0.0.0.0
```

### OpenTelemetry transition (since 3.4.0)

OpenTelemetry is available as an add-on replacing OpenTracing. OpenTracing is
officially deprecated and remains scheduled for removal in 3.5.

## CPU and thread placement

### Topology-aware placement (since 3.2.0)

Automatic CPU binding considers packages, NUMA nodes, CCXs, L3 caches, cores,
and threads. By default HAProxy still restricts itself to one NUMA node.
Systems with more than 64 threads need additional configuration to use them
all. Default limits rise to 1024 threads and 32 thread groups.

### New automatic defaults (since 3.3.0)

`cpu-policy` defaults to `performance`, so heterogeneous systems use only
performance cores by default. Automatic placement uses all available cores
and NUMA nodes and no longer has the previous 64-thread limit.

## DNS and connection protection

### Process-wide DNS family selection (since 3.2.0)

The global `dns-accept-family` directive accepts `ipv4`, `ipv6`, and `auto` to
disable an address family process-wide. `auto` probes IPv6 connectivity at
boot and every 30 seconds to determine whether IPv6 resolution remains
enabled.

As of 3.3.0, `dns-accept-family` defaults to `auto`, enabling IPv4 and
conditionally enabling IPv6 based on the recurring connectivity probe.

### CPU-gated protocol-glitch enforcement (since 3.2.0)

The global `tune.glitches.kill.cpu-usage` sets a 0–100 CPU percentage above
which connections exceeding a configured glitch threshold are killed. The
default `0` kills at the threshold regardless of CPU load. A nonzero setting
requires `tune.h2.fe.glitches-threshold` or
`tune.quic.frontend.glitches-threshold`.

## Command-line and build changes

### Version query formats (since 3.3.0)

The CLI accepts `-vq` for the version, `-vqs` for the short form, and `-vqb`
for the branch.

### Fast-forward control (since 3.3.0)

`tune.disable-fast-forward` is stable and can be configured without
`expose-experimental-directives`.

### Crash debugging (since 3.3.0)

`master-worker no-exit-on-failure` prevents all workers from being terminated
when one encounters a segmentation fault.

### Reload cap (since 3.3.0)

The default `mworker-max-reloads` value is 50.

### halog installation (since 3.3.0)

Build and install the `halog` utility with `make install-admin` rather than
`make install`.

### Linux version floor (since 3.3.0)

The default `linux-glibc` build target requires Linux 4.17 to support Kernel
TLS.

## Branch and patch maintenance

### Choose branch and patch level separately

Since 1.8, HAProxy normally emits two feature branches per year. Even-numbered
branches are LTS releases maintained for five years. Odd-numbered branches are
short-lived stable releases maintained for roughly 12–18 months for operators
prepared to upgrade and roll back more often.

On a maintained feature branch, keep the final bug-fix component current.
Fixes are conservatively backported, so patch-level maintenance does not
require adopting a new feature branch. Reproduce problems on the latest patch
before reporting them.

### Support snapshot

At the branch-maintenance snapshot of 2026-07-28, fully maintained releases
were 3.4.2 (LTS through 2031-Q2), 3.3.12 (stable through 2027-Q1), 3.2.21 (LTS
through 2030-Q2), and 3.0.25 (LTS through 2029-Q2). Branch 2.8 at 2.8.26
through 2028-Q2 and branch 2.6 at 2.6.31 through 2027-Q2 received critical
fixes only. Every other released branch in that matrix was unmaintained.

### Interpret maintenance queues

The pending-fixes table contains fixes already queued for the next release of
that maintenance branch. A separate list of later development-branch fixes is
only a candidate set: those fixes may not affect the maintenance branch, and
applicable fixes land on development before being backported.

At that snapshot, the latest 3.4, 3.3, and 3.2 releases each had zero queued
known bugs even though later development-branch fixes were listed.

Use severity to interpret urgency:

- `MINOR`: limited impact and seldom enough reason to update by itself.
- `MEDIUM`: normally warrants updating or temporarily disabling the affected
  feature.
- `MAJOR`: requires upgrading as soon as possible.
- `CRITICAL`: a short-term reliability or security issue without a workaround;
  immediate release and upgrade are expected.

## LTS-aware deprecation sequence

A working, supported setup on a non-LTS branch is promised to continue working
on the next LTS, so features are not removed between those branches. An LTS
also avoids adding warnings for supported configurations that were warning-free
on the preceding non-LTS.

Deprecations normally warn first in a non-LTS and become errors when removed in
the next non-LTS, at least a year later.
