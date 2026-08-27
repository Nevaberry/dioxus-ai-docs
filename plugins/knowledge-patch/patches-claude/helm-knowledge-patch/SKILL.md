---
name: helm-knowledge-patch
description: Helm
version: "4.2.3"
license: MIT
metadata:
  author: Nevaberry
---


# Helm Knowledge Patch

## Use this patch

Load this patch for work involving:

- Helm 4 migrations, especially applications that embed the Go SDK;
- plugins, post-renderers, and plugin installation;
- install, upgrade, apply, wait, test, and server-side dry-run behavior;
- chart creation, templates, values coalescing, packaging, and caching;
- registry authentication and registry-backed dependencies;
- Kubernetes compatibility and maintained Helm 3 clients.

First identify whether the task concerns a chart, the CLI, an SDK integration,
or a plugin. A Helm 4 migration does not by itself require every Helm 3 chart
to change. Focus review on the affected integration points and behavior.

## Reference index

| Reference | Topics |
| --- | --- |
| [migration-sdk-and-plugins.md](references/migration-sdk-and-plugins.md) | Public SDK APIs, `slog`, chart API versions, WebAssembly plugins, post-renderers, plugin validation, support, security, and platform compatibility |
| [operations-and-delivery.md](references/operations-and-delivery.md) | Server-side apply, conflict retries, kstatus waiting, install atomicity, tests, server dry-runs, registries, caching, and reproducible archives |
| [charts-and-values.md](references/charts-and-values.md) | Experimental chart API v3, `helm create`, deprecated template flags, nil-value coalescing, and empty chart files |

## Choose the relevant surface

| Surface | First checks |
| --- | --- |
| Embedded SDK | Compile against the Helm 4 public APIs; review logging, chart API versions, apply, and wait paths |
| Plugin or post-renderer | Validate it against the Helm 4 plugin model and update plugin-installing clients |
| Chart or template | Retest nil coalescing, empty-file iteration, and any experimental chart API choice |
| CLI automation | Remove deprecated flags and exercise install, upgrade, dry-run, test, push, and dependency-download paths |
| Delivery pipeline | Verify deterministic packaging, cache assumptions, registry configuration, and supported platform artifacts |

## Breaking changes and migration priorities

### Review embedded SDK code

Helm 4 changes public SDK APIs. For applications that embed Helm:

1. Review calls against the Helm 4 API rather than assuming Helm 3 signatures.
2. Account for SDK support for multiple chart API versions.
3. Integrate logging through Go `slog` when Helm output must join the host
   application's logging pipeline.
4. Exercise the exact SDK paths used for server-side apply and waiting because
   their defaults and controls have changed.

Read
[migration-sdk-and-plugins.md](references/migration-sdk-and-plugins.md)
before changing an embedded integration.

### Recheck plugins and post-renderers

Helm 4 redesigns plugins to support WebAssembly. Post-renderers are plugins in
the new model, so include both ordinary extensions and post-renderers in the
migration inventory.

Upgrade older Helm 4 clients that install plugins, especially when plugin
sources are not fully trusted. Plugin handling was hardened against both a
missing-provenance bypass and version path traversal.

### Stop passing deprecated template note flags

Remove these unused `helm template` flags from scripts and wrappers:

- `--hide-notes`
- `--render-subchart-notes`

They are deprecated and should not be preserved as required compatibility
options.

### Retest values coalescing

Do not assume the previous treatment of chart-default `nil` values:

- chart-default `nil` values are no longer copied into coalesced values;
- `nil` is preserved when the chart default is an empty map.

Inspect final coalesced values for charts whose overrides depend on nil cleanup
or subchart coalescing.

### Plan the Helm 3 support transition

Helm 3 receives bug fixes through July 8, 2026 and security fixes through
November 11, 2026. Features are not backported during that transition, except
for Kubernetes client-library updates needed to support newer Kubernetes
versions.

Use those dates when deciding whether to maintain a Helm 3 path or complete a
Helm 4 migration. Maintained Helm 3 clients should also pick up relevant
provenance, OpenTelemetry, gRPC, and Go cryptography dependency updates.

## High-use operations

### Restore atomic installs

Use `--atomic` when a failed installation must roll back automatically:

```sh
helm install my-release ./chart --atomic
```

### Align and retry server-side apply

Helm 4 supports server-side apply. Its SDK defaults are aligned with the CLI
defaults, so remove compensating configuration that existed only to bridge a
default mismatch. Keep explicit settings when the application intentionally
overrides the shared behavior.

Server-side apply also retries Kubernetes conflicts. Concurrent resource
updates are therefore less likely to abort an operation on the first conflict;
retain normal operation bounds and error handling around retries.

### Bound and diagnose waits

Helm 4 improves resource watching and waiting with kstatus. Use the available
fine-grained context controls to bound or cancel waits, and preserve failed
resource information for diagnosis. Do not add an outer infinite wait to
compensate for older behavior; a failed resource no longer needs to leave Helm
waiting forever.

### Accept server-generated names in dry-runs

For `--dry-run=server`, accept rendered resources with
`metadata.generateName` instead of `metadata.name`. The API server can generate
the final name, so validation fixtures should allow this resource shape.

### Collect all test-container logs

`helm test` fetches logs from every container in each test pod. Diagnostics can
therefore include sidecars and other secondary containers. Preserve and inspect
the complete log set rather than assuming only the primary container matters.

### Carry registry configuration through delivery

Token-authenticated `helm push` requests both `pull` and `push` scopes. Upgrade
when a registry rejects a push because token exchange did not request the full
scope set.

During `helm upgrade`, the registry client is passed to `downloader.Manager`.
Dependency downloads can therefore use the operation's registry credentials
and client configuration.

Read [operations-and-delivery.md](references/operations-and-delivery.md) before
changing apply, wait, registry, test, or packaging workflows.

## Chart creation and delivery

### Create an experimental chart API v3 chart

Enable the experimental gate and select the API version explicitly:

```sh
HELM_EXPERIMENTAL_CHART_V3=1 helm create demo --chart-api-version v3
```

The option alone does not enable experimental chart API v3. Treat both the
environment gate and the explicit version selection as required workflow
inputs.

### Iterate empty chart files safely

`.Files.Lines` can iterate a requested chart file even when it is empty. Charts
with optional or generated files no longer need placeholder content solely to
avoid a panic. Keep application-level handling when an empty file has a
semantic meaning.

### Use content-based caching

Helm 4 caches local data, including charts, by content. Identical content can
share cached data independently of source location. Compare content when
reasoning about reuse instead of assuming that every source path creates a
distinct cached object.

### Expect reproducible archives

Chart archive builds are reproducible and idempotent. Repeated packaging can be
used in deterministic build and verification workflows. If builds differ,
investigate the inputs and surrounding workflow rather than accepting archive
nondeterminism as normal.

Read [charts-and-values.md](references/charts-and-values.md) before changing
chart creation, template automation, coalescing behavior, or file iteration.

## Compatibility checks

### Match the Kubernetes window

Helm 4 follows an `n-3` Kubernetes compatibility policy and does not guarantee
forward compatibility beyond the client version with which it was built. The
Helm 4.2.x line uses Kubernetes 1.36 client libraries and supports Kubernetes
1.33.x through 1.36.x.

Check both the Helm client line and target Kubernetes version before treating
an out-of-window pairing as supported.

### Select supported release artifacts

Official Linux `loong64` artifacts are available in the Helm 4.2 line. Prefer
those release artifacts when targeting that platform.

## Verification checklist

Before completing a Helm migration or behavior change:

- compile and test embedded code against the Helm 4 public SDK APIs;
- verify `slog` integration if Helm logging joins a host logger;
- exercise every plugin and post-renderer through the Helm 4 plugin system;
- update plugin-installing clients where validation hardening is absent;
- remove deprecated template note flags from automation;
- inspect nil overrides and subchart values after coalescing;
- test successful, failed, canceled, and context-bounded wait paths;
- compare explicit server-side apply settings with aligned CLI and SDK
  defaults, then test conflict handling;
- test install rollback with `--atomic` where atomicity is required;
- include a server dry-run fixture that uses `metadata.generateName`;
- include multi-container test pods when test diagnostics matter;
- verify push token scopes and authenticated dependency downloads;
- exercise `.Files.Lines` with an empty chart file;
- package the same chart repeatedly when deterministic archives matter;
- verify the Helm/Kubernetes pairing against the compatibility window;
- read the relevant full reference before changing compatibility logic.
