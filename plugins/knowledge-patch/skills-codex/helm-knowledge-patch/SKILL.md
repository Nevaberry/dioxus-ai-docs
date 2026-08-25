---
name: helm-knowledge-patch
description: Helm
version: 4.2.3
license: MIT
metadata:
  author: Nevaberry
---


# Helm Knowledge Patch

## Use this patch

Load this patch for work involving:

- Helm 4 migrations, especially applications that embed the Go SDK.
- Plugins, post-renderers, registry authentication, or chart dependencies.
- Install, upgrade, apply, wait, test, and server-side dry-run behavior.
- Chart creation, values coalescing, packaging, caching, or `.Files.Lines`.
- Kubernetes compatibility and maintained Helm 3 clients.

Start by identifying whether the task concerns a chart, the CLI, an SDK
integration, or a plugin. A Helm 4 migration does not imply that every Helm 3
chart needs changes; focus review on affected integration points and changed
behaviors.

## Reference index

| Reference | Topics |
| --- | --- |
| [migration-sdk-and-plugins.md](references/migration-sdk-and-plugins.md) | Public SDK APIs, `slog`, plugins, post-renderers, validation, security updates, support, platform and Kubernetes compatibility |
| [operations-and-delivery.md](references/operations-and-delivery.md) | Server-side apply, waiting, atomic installs, dry-runs, tests, registries, caching, dependencies, and reproducible archives |
| [charts-and-values.md](references/charts-and-values.md) | Chart API v3, `helm create`, template flags, nil-value coalescing, and empty chart files |

## Breaking changes and migration priorities

### Review embedded SDK code

Helm 4 changes public SDK APIs, supports multiple chart API versions, and uses
Go `slog`. For applications that embed Helm:

1. Review calls against the Helm 4 API instead of assuming Helm 3 signatures.
2. Account for SDK handling of multiple chart API versions.
3. Connect Helm logging to the host logger through `slog` where needed.
4. Exercise the SDK paths used for apply and wait behavior.

Read
[migration-sdk-and-plugins.md](references/migration-sdk-and-plugins.md)
before changing an embedded integration.

### Recheck plugins and post-renderers

Helm 4 redesigns the plugin system around support for WebAssembly-based
plugins. Post-renderers are plugins in Helm 4 as well. During migration:

- Inventory ordinary extensions and post-renderers together.
- Validate each integration against the Helm 4 plugin model.
- Upgrade older Helm 4 clients that install plugins, especially when plugin
  sources are not fully trusted.

The client upgrade matters because plugin handling was hardened against both
a missing-provenance bypass and version path traversal.

### Stop passing deprecated template note flags

Helm 4.2 deprecates these unused `helm template` flags:

- `--hide-notes`
- `--render-subchart-notes`

Remove them from scripts and wrappers rather than preserving them as required
compatibility options.

### Retest values coalescing

Helm 4.2 changes nil handling during values coalescing:

- Chart-default `nil` values are no longer copied into coalesced values.
- `nil` is preserved when the chart default is an empty map.

Retest charts whose overrides depend on nil cleanup or subchart coalescing.
Inspect final coalesced values instead of relying on the previous cleanup
behavior.

## High-use operations

### Restore atomic installs

Helm 4.2 restores `--atomic` on `helm install`. Use it when an unsuccessful
installation should roll back automatically:

```sh
helm install my-release ./chart --atomic
```

### Align server-side apply behavior

Helm 4 supports server-side apply. Its SDK defaults are aligned with the CLI
defaults in Helm 4.2, so do not compensate for a default difference that no
longer exists. Keep explicit settings only when the application deliberately
overrides the shared defaults.

Server-side apply also retries Kubernetes conflicts in 4.2.4. Prefer a client
with that fix when concurrent resource updates otherwise abort operations on
the first conflict.

### Bound and diagnose waits

Helm 4 improves resource watching and waiting with kstatus. Fine-grained
context options can bound or cancel waits, and failed resources no longer
leave Helm waiting forever.

For wait-related work:

1. Use context controls to bound or cancel the operation.
2. Preserve failed-resource information for diagnosis.
3. Do not add an outer infinite wait to reproduce older behavior.

### Accept server-generated names in dry-runs

`--dry-run=server` accepts rendered resources that set
`metadata.generateName` instead of `metadata.name`. Validation and test
harnesses should allow that shape when the API server will generate the final
name.

### Collect all test-container logs

As of 4.2.4, `helm test` fetches logs from every container in each test pod.
Use those diagnostics when failures originate in a sidecar or another
secondary container.

### Keep registry clients and scopes available

For token-authenticated registry pushes, Helm 4.2.4 requests both `pull` and
`push` scopes. Upgrade when a registry rejects a token exchange that lacks the
complete scope set.

During `helm upgrade`, the registry client is also passed to
`downloader.Manager`, making credentials and client configuration available
while chart dependencies are downloaded.

## Chart creation and delivery

### Create an experimental chart API v3 chart

The SDK handles multiple chart API versions. When the experimental v3 gate is
enabled, Helm 4.2 exposes `helm create --chart-api-version`:

```sh
HELM_EXPERIMENTAL_CHART_V3=1 helm create demo --chart-api-version v3
```

Treat the environment gate and the explicit version option as a pair; the
option alone does not enable experimental v3.

### Use content-based caching

Helm 4 adds local content-based caching, including for charts. Identical
content can share cached data independently of source location. Compare
content when reasoning about cache reuse instead of assuming each path creates
distinct cached data.

### Expect reproducible archives

Chart archive builds are reproducible and idempotent in Helm 4. Repeated
packaging can support deterministic build and verification workflows. If
builds differ, investigate their inputs and surrounding workflow rather than
accepting archive nondeterminism as expected.

### Allow empty files in `.Files.Lines`

Helm 3.21.4 prevents `.Files.Lines` from panicking for an empty requested
chart file. Charts that iterate optional or generated files no longer need to
insert content solely to avoid that crash.

## Compatibility and maintained clients

### Match the Kubernetes window

Helm 4 follows an `n-3` Kubernetes compatibility policy and makes no
forward-compatibility guarantee beyond its compiled client version. Helm
4.2.x uses Kubernetes 1.36 client libraries and supports Kubernetes 1.33.x
through 1.36.x.

Check the Helm client line and target Kubernetes version before treating an
out-of-window pairing as supported.

### Plan for the Helm 3 support sunset

Helm 3 receives bug fixes through July 8, 2026 and security fixes through
November 11, 2026. Features are not backported during this transition except
for Kubernetes client-library updates needed to support newer Kubernetes
versions.

Use those dates when deciding whether to maintain a Helm 3 path or complete a
Helm 4 migration.

### Upgrade maintained Helm 3 clients for security fixes

Helm 3.21.4 changes provenance cryptography and updates OpenTelemetry, gRPC,
`x/crypto`, and `x/text` to address the listed Go advisories. Upgrade
maintained Helm 3 clients that need those dependency fixes; see the migration
reference for the exact packages and advisory identifiers.

### Select supported release artifacts

Helm 4.2 provides official Linux `loong64` release artifacts. Prefer those
artifacts when targeting that platform.

## Verification checklist

Before completing a Helm migration or behavior change:

- Compile and test embedded code against the Helm 4 public SDK APIs.
- Verify `slog` integration when Helm logging connects to a host logger.
- Exercise every plugin and post-renderer through the Helm 4 plugin system.
- Update plugin-installing clients where validation hardening is absent.
- Compare explicit server-side apply settings with aligned CLI and SDK
  defaults; test conflict retries where concurrent updates occur.
- Test successful, failed, canceled, and context-bounded wait paths.
- Test install rollback with `--atomic` where atomicity is required.
- Include a server dry-run fixture that uses `metadata.generateName`.
- Confirm `helm test` diagnostics include secondary containers.
- Exercise token-authenticated pushes and registry-backed dependency downloads.
- Remove deprecated template note flags from automation.
- Retest nil overrides, subchart values coalescing, and empty chart files.
- Package the same chart repeatedly when deterministic archives matter.
- Verify Helm and Kubernetes versions against the compatibility window.
- Read the relevant full reference before changing compatibility logic.
