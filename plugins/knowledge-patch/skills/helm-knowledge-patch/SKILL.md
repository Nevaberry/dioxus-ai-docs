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
- Plugin or post-renderer integrations.
- Install, apply, wait, and server-side dry-run behavior.
- Chart creation, values coalescing, packaging, or caching.
- Kubernetes compatibility and Helm 3 support planning.

Start by identifying whether the task concerns a chart, the CLI, an SDK
integration, or a plugin. A Helm 4 migration does not by itself require every
Helm 3 chart to change; focus review on the affected integration points and
behaviors.

## Reference index

| Reference | Topics |
| --- | --- |
| [migration-sdk-and-plugins.md](references/migration-sdk-and-plugins.md) | Public SDK APIs, `slog`, chart API versions, WebAssembly plugins, post-renderers, plugin validation, support and platform compatibility |
| [operations-and-delivery.md](references/operations-and-delivery.md) | Server-side apply, kstatus waiting, install atomicity, server dry-runs, content caching, reproducible archives |
| [charts-and-values.md](references/charts-and-values.md) | Experimental chart API v3, `helm create`, deprecated template flags, nil-value coalescing |

## Breaking changes and migration priorities

### Review embedded SDK code

Helm 4 changes public SDK APIs. For code that embeds Helm:

1. Review calls against the Helm 4 API rather than assuming Helm 3 signatures.
2. Account for SDK support for multiple chart API versions.
3. Integrate logging through Go `slog` where the host application needs to
   connect Helm output to a modern logger.
4. Exercise the SDK paths used for apply and wait behavior, because their
   defaults and controls also changed.

Read
[migration-sdk-and-plugins.md](references/migration-sdk-and-plugins.md)
before changing an embedded integration.

### Recheck plugins and post-renderers

Helm 4 redesigns the plugin system to support WebAssembly-based plugins.
Post-renderers are plugins in Helm 4 as well. During migration:

- Inventory both ordinary extensions and post-renderers.
- Validate each integration against the Helm 4 plugin model.
- Do not treat a post-renderer as an unrelated migration surface.
- Upgrade older Helm 4 clients that install plugins, especially when plugin
  sources are not fully trusted.

The upgrade recommendation matters because Helm 4.2 hardens plugin handling
against a missing-provenance bypass and version path traversal.

### Stop passing deprecated template note flags

Helm 4.2 deprecates these unused `helm template` flags:

- `--hide-notes`
- `--render-subchart-notes`

Remove them from scripts and wrappers instead of preserving them as required
compatibility options.

### Retest values coalescing

Helm 4.2 changes nil handling during values coalescing:

- Chart-default `nil` values are no longer copied into coalesced values.
- `nil` is preserved when the chart default is an empty map.

Retest charts whose overrides depend on nil cleanup or subchart coalescing.
Inspect the final coalesced values rather than relying on prior cleanup
behavior.

### Plan for the Helm 3 support sunset

Helm 3 receives bug fixes through July 8, 2026 and security fixes through
November 11, 2026. Features are not backported during this transition, except
for Kubernetes client-library updates needed to support newer Kubernetes
versions.

Use those dates when deciding whether to maintain a Helm 3 path or complete a
Helm 4 migration.

## High-use operations

### Restore atomic installs

Helm 4.2 restores `--atomic` on `helm install`. Use it when a failed
installation should be rolled back automatically:

```sh
helm install my-release ./chart --atomic
```

### Align server-side apply behavior

Helm 4 supports server-side apply. In Helm 4.2, the SDK defaults for
server-side apply are kept consistent with the CLI defaults.

When comparing CLI and embedded behavior, avoid compensating for a default
difference that no longer exists. Keep explicit settings only when the
application intends to override the shared defaults.

### Bound and diagnose waits

Helm 4 improves resource watching and waiting using kstatus. Helm 4.2 adds
fine-grained context options for waiting and avoids waiting forever after a
resource has failed.

For wait-related work:

1. Use the available context controls to bound or cancel the operation.
2. Preserve failed-resource information for diagnosis.
3. Do not add an outer infinite wait to compensate for older behavior.

### Accept server-generated names in dry-runs

`--dry-run=server` accepts rendered resources that set
`metadata.generateName` instead of `metadata.name`. Validation and test
harnesses should allow this shape when the API server will generate the final
name.

## Chart creation and delivery

### Create an experimental chart API v3 chart

The SDK can handle multiple chart API versions. Helm 4.2 exposes
`helm create --chart-api-version` when the experimental v3 gate is enabled:

```sh
HELM_EXPERIMENTAL_CHART_V3=1 helm create demo --chart-api-version v3
```

Treat both the environment gate and the explicit version option as part of
the workflow. Do not assume the option alone enables experimental v3.

### Use content-based caching

Helm 4 adds local content-based caching, including for charts. Identical
content can share cached data independently of the source location.

When reasoning about cache reuse, compare content rather than assuming each
source path or location necessarily creates distinct cached data.

### Expect reproducible archives

Chart archive builds are reproducible and idempotent in Helm 4. Repeated
packaging can therefore support deterministic build and verification
workflows.

If repeated builds differ, investigate inputs and the surrounding workflow
instead of accepting archive nondeterminism as expected Helm behavior.

## Compatibility checks

### Match the Kubernetes window

Helm 4 follows an `n-3` Kubernetes compatibility policy and makes no
forward-compatibility guarantee beyond the client version it was built with.
Helm 4.2.x uses Kubernetes 1.36 client libraries and supports Kubernetes
1.33.x through 1.36.x.

Check both the Helm client line and target Kubernetes version before treating
an out-of-window combination as supported.

### Select supported release artifacts

Helm 4.2 provides official Linux `loong64` release artifacts. Prefer those
artifacts when targeting that platform.

## Verification checklist

Before completing a Helm 4 migration or behavior change:

- Compile and test embedded code against the Helm 4 public SDK APIs.
- Verify `slog` integration if Helm logging is connected to a host logger.
- Exercise every plugin and post-renderer through the Helm 4 plugin system.
- Update plugin-installing clients where the validation hardening is absent.
- Compare explicit server-side apply settings with the aligned CLI and SDK
  defaults.
- Test successful, failed, canceled, and context-bounded wait paths.
- Test install rollback with `--atomic` where atomicity is required.
- Include a server dry-run fixture that uses `metadata.generateName`.
- Remove the deprecated template note flags from automation.
- Retest nil overrides and subchart values coalescing.
- Package the same chart repeatedly when deterministic archives matter.
- Verify the Helm/Kubernetes version pairing against the compatibility
  window.
- Read the relevant full reference before changing compatibility logic.
