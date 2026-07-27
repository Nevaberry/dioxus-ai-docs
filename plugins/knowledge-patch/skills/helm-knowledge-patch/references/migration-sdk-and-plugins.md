# Migration, SDK, Plugins, and Compatibility

This topic-organized reference incorporates the included Helm `4.2.3` batch.

## Scope a Helm 4 migration

Helm 4 changes several integration surfaces, but the major release does not
imply that every Helm 3 chart needs changes. Separate the review into:

- Go applications that embed the Helm SDK.
- Plugins and post-renderers.
- Charts whose behavior depends on changed values coalescing.
- Automation that passes deprecated or restored CLI flags.
- Client and cluster compatibility.

Review the relevant surface rather than treating all charts as incompatible.

## Public SDK APIs and logging

Helm 4 changes public SDK APIs. Code that embeds Helm should be reviewed
against the v4 APIs rather than relying on Helm 3 signatures or behavior.

The Helm 4 SDK supports multiple chart API versions. This capability is also
used by the experimental chart API v3 creation path described in
[charts-and-values.md](charts-and-values.md).

Helm 4 uses Go `slog`. Embedded applications can integrate Helm logging with
modern loggers through that logging model. During migration, review:

- Logger construction and injection.
- Any adapters around older logging assumptions.
- Routing of Helm records into the host application's logging setup.
- Tests that assert emitted or captured logging behavior.

The operational SDK surface also includes server-side apply defaults and
fine-grained wait contexts. See
[operations-and-delivery.md](operations-and-delivery.md).

## WebAssembly plugins and post-renderers

Helm 4 redesigns the plugin system to support WebAssembly-based plugins.
Extension integrations should be validated against this new plugin model.

Post-renderers are plugins in Helm 4. Treat them as part of the plugin
migration:

1. Inventory post-renderers along with other extensions.
2. Check how each integration is loaded and invoked.
3. Re-run the paths that depend on rendered output transformation.
4. Avoid assuming an unchanged chart proves its post-renderer integration is
   unchanged.

## Plugin validation hardening

Helm 4.2 fixes two plugin-handling vulnerabilities:

- A missing-provenance bypass.
- Version path traversal.

Upgrade older Helm 4 clients that install plugins, especially when plugin
sources are not fully trusted. This guidance applies to the installing client;
changing a chart alone does not supply the validation hardening.

## Kubernetes compatibility

Helm 4 follows an `n-3` Kubernetes compatibility policy. It does not promise
forward compatibility beyond the Kubernetes client version with which Helm
was built.

Helm 4.2.x:

- Uses Kubernetes 1.36 client libraries.
- Supports Kubernetes 1.33.x, 1.34.x, 1.35.x, and 1.36.x.

When diagnosing a client/cluster issue, establish both versions before
assuming that a newer cluster is supported by forward compatibility.

## Helm 3 support transition

The Helm 3 support schedule is:

| Support type | Through |
| --- | --- |
| Bug fixes | July 8, 2026 |
| Security fixes | November 11, 2026 |

No features are backported during the transition. The exception is
Kubernetes client-library updates needed to support newer Kubernetes
versions.

Use the distinction between bug fixes, security fixes, and feature
development when planning a migration or setting maintenance expectations.

## Platform artifacts

Helm 4.2 adds official Linux `loong64` release artifacts. Use the official
artifact for that operating-system and architecture combination rather than
assuming a locally produced build is the only option.
