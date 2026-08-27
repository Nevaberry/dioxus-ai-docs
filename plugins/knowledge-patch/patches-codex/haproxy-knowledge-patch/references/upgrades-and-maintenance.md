# Upgrades and Maintenance

## Worker-owned configuration parsing

Since 3.1.0, the master only starts workers and each worker parses the
configuration itself. This removes the master's old parse-and-undo sequence,
making reload behavior consistent and avoiding the related file-descriptor
leaks. Investigate parse failures in worker startup rather than assuming the
master already validated and materialized all configuration state.

## Deprecated-directive warnings

HAProxy 3.1.0 warns on deprecated directives unless the global
`expose-deprecated-directives` option is present.

```haproxy
global
    expose-deprecated-directives
```

Use that switch only as a temporary compatibility measure. `program` sections
and legacy C mailers were scheduled for removal in 3.3.0, with Lua mailers as
the supported replacement. The OpenTracing filter was scheduled for
deprecation in 3.3.0 and removal in 3.5.

OpenTelemetry support is available as an add-on in 3.4.0 and replaces
OpenTracing. Complete the integration migration before the removal point.

## Duplicate names become errors

HAProxy 3.1.0 detects and warns about duplicate names across `frontend`,
`listen`, `backend`, `defaults`, and `log-forward` section families, as well
as duplicate server names. Those duplicates became errors in 3.3.0. HAProxy
3.1 otherwise introduced no breaking changes. Rename collisions before moving
to 3.3 or later.

## Empty arguments

Since 3.2.0, empty configuration arguments warn, including an empty environment
variable expanded inside double quotes, and were scheduled to become errors
in the next version. Use `${NAME[*]}` when an empty expansion is intentional.

## Startup diagnostics

HAProxy 3.3.0 adds targeted startup checks:

- running as root without a global `user` directive warns;
- leaving `expose-experimental-directives` enabled when no configured feature
  needs it warns;
- `thread-groups` ranges larger than `nbthreads` are trimmed with a warning,
  while a group trimmed to empty is fatal;
- static builds warn when `user` or `group` should be `uid` or `gid`.

Treat these as deployment defects rather than suppressing the messages.

## Crash retention and reload caps

For crash investigation in 3.3.0, `master-worker no-exit-on-failure` keeps the
other workers alive when one receives a segmentation fault. Use it only with
an operational plan for a partially degraded process set.

The default `mworker-max-reloads` is 50 from 3.3.0. Account for that cap in
automation that performs frequent reloads.

## New and renamed deprecations

HAProxy 3.3.0 warns that backend `dispatch` and `option transparent` are
deprecated. Replace them before their planned 3.5 removal.

```haproxy
backend legacy_dispatch
    server dispatch 192.0.2.10:8080

backend original_destination
    server tproxy 0.0.0.0
```

If a dispatch backend retains other legacy servers, set those servers to
weight zero to preserve dispatch behavior. The zero-address server preserves
routing to the original TPROXY destination.

Also migrate:

- `tune.quic.frontend.*` globals to `tune.quic.fe.*`;
- the global `master-worker` directive to the `-W` or `-Ws` command-line
  option;
- global `no-quic` to `tune.quic.listen on|off`;
- the shared compression filter and deprecated `compression-direction` to
  3.4.0 `filter comp-req` and `filter comp-res`;
- `tune.takeover-other-tg-connections` to 3.4.0
  `tune.idle-pool.shared`.

## Strict configuration validation

In 3.3.0, an ACL may not specify several match types after `-m`; a
configuration that previously used only the final type now fails. Ambiguous
combinations such as `path_beg -m reg` warn and should be rewritten with an
unambiguous fetch and matcher.

The same release forbids `http-send-name-header` from targeting
`connection`, `content-length`, `host`, or `transfer-encoding`, because
rewriting those fields can create an invalid HTTP request.

## Build and install changes

The default `linux-glibc` build target requires Linux 4.17 from 3.3.0 to
support Kernel TLS. Verify the build host and runtime kernel floor together.

Install the `halog` administration utility with `make install-admin`; it is no
longer installed by `make install`.

## LTS-aware deprecation sequence

HAProxy's compatibility policy says a supported setup on a non-LTS branch
continues to work on the next LTS, so features are not removed between those
branches. An LTS also avoids adding warnings for configurations that were
supported and warning-free on the preceding non-LTS. A deprecation normally
warns first in a non-LTS and is removed as an error in the next non-LTS at
least one year later.

Use this sequence to schedule migration, but resolve warnings early rather
than relying on the full grace period.

## Choose branch and patch level separately

Since 1.8, HAProxy normally publishes two feature branches each year.
Even-numbered branches are LTS and maintained for five years. Odd-numbered
branches are short-lived stable lines, maintained roughly 12–18 months, for
operators prepared to upgrade and roll back more frequently.

Within a maintained branch, keep the final bug-fix component current. Fixes
are backported conservatively, so patch-level maintenance does not require a
feature-branch upgrade. Reproduce a suspected defect on the latest patch in
its branch before reporting it.

## Maintenance snapshot from the source batch

At the 2026-07-28 branch-maintenance snapshot, fully maintained releases were:

| Release | Status |
| --- | --- |
| 3.4.2 | LTS through 2031-Q2 |
| 3.3.12 | Stable through 2027-Q1 |
| 3.2.21 | LTS through 2030-Q2 |
| 3.0.25 | LTS through 2029-Q2 |

Branches 2.8 at 2.8.26 through 2028-Q2 and 2.6 at 2.6.31 through 2027-Q2
received critical fixes only. Every other released branch in that matrix was
unmaintained. This is a dated snapshot: consult the current maintenance table
before selecting a branch.

## Interpret maintenance bug queues

The pending-fixes table lists fixes already queued for the next release of a
maintenance branch. A separate list of fixes made later on the development
branch is only a candidate pool: a candidate may not affect the maintenance
branch, and an applicable fix lands on development before backporting. At the
snapshot above, the latest 3.4, 3.3, and 3.2 releases each had zero queued
known bugs even though later development fixes were listed.

Use severity to determine urgency:

- `MINOR`: limited impact and seldom a reason to update by itself;
- `MEDIUM`: normally update or temporarily disable the affected feature;
- `MAJOR`: upgrade as soon as possible;
- `CRITICAL`: a short-term reliability or security problem with no workaround,
  requiring an immediate release and upgrade.
