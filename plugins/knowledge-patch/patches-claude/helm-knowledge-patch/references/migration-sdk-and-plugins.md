# Migration, SDK, Plugins, and Compatibility

Use this reference when migrating an embedded Helm integration, validating
plugins or post-renderers, maintaining a Helm 3 client, or selecting supported
Kubernetes and platform combinations.

## Embedded Helm SDK migration

### Public APIs and logging *(since 4.2.3)*

Helm 4 changes public SDK APIs. Compile embedded applications against the v4
APIs and review each call site rather than assuming Helm 3 signatures remain
valid. The SDK supports multiple chart API versions, so code that loads,
creates, or processes charts must not hard-code a single chart API assumption.

Helm 4 uses Go `slog`. Connect Helm logging through `slog` when an embedding
application needs Helm events in its modern structured logging pipeline.

A migration of SDK integrations does not imply that every Helm 3 chart needs
changes. Review the chart only where SDK, chart API, values, template, or
delivery behavior actually affects it.

### Apply and wait integration *(since 4.2.3)*

Exercise the embedded application's server-side apply and wait paths. Helm 4
supports server-side apply, and the 4.2 SDK defaults are kept consistent with
the CLI defaults. Avoid retaining compensating settings that exist only for an
old CLI/SDK mismatch.

Waiting uses improved kstatus-based resource watching. Helm 4.2 provides
fine-grained context options and avoids waiting forever after a resource has
failed. Thread the application's intended cancellation and timeout context into
the SDK operation, and retain failed-resource details in diagnostics.

## Plugin migration and security

### WebAssembly plugins and post-renderers *(since 4.2.3)*

Helm 4 redesigns its plugin system to support WebAssembly-based plugins.
Inventory both ordinary extensions and post-renderers: post-renderers are also
plugins in Helm 4 and belong in the same migration review.

Validate each integration against the Helm 4 plugin model. Do not treat a
working Helm 3 executable plugin or post-renderer as proof that the integration
has been migrated.

### Plugin installation hardening *(since 4.2.3)*

Helm 4.2 fixes a missing-provenance bypass and version path traversal in plugin
handling. Upgrade older Helm 4 clients that install plugins, particularly when
plugin sources are not fully trusted. Review both provenance validation and
version-derived paths in any wrapper around plugin installation.

## Helm 3 maintenance

### Support sunset *(since 4.2.3)*

Helm 3 receives bug fixes through July 8, 2026 and security fixes through
November 11, 2026. No features are backported during this transition, except
Kubernetes client-library updates needed to support newer Kubernetes versions.

Use the bug-fix and security-fix dates separately when planning a maintained
Helm 3 path. Do not expect a Helm 4 feature to be backported merely because
Helm 3 still receives fixes.

### Security dependency updates *(since 3.21.4)*

Helm 3.21.4 includes these dependency changes:

- provenance cryptography moves to `ProtonMail/go-crypto` for GO-2026-5932;
- OpenTelemetry updates to 1.44.0 for GO-2026-5158;
- gRPC updates to 1.82.1 for GO-2026-6061;
- `x/crypto` updates to 0.54.0, with `x/text` 0.40.0, for GO-2026-5970.

Upgrade maintained Helm 3 clients that need those fixes. If an application
embeds Helm, rebuild and retest it with the updated dependency graph rather
than treating a CLI binary upgrade as sufficient for the embedded copy.

## Kubernetes and release artifacts

### Kubernetes compatibility window *(since 4.2.3)*

Helm 4 uses an `n-3` Kubernetes compatibility policy. It makes no
forward-compatibility guarantee beyond the Kubernetes client version with
which the Helm client was built.

Helm 4.2.x uses Kubernetes 1.36 client libraries and supports Kubernetes
1.33.x through 1.36.x. Check both the actual Helm client line and target
cluster version; do not infer support from either version in isolation.

### Linux `loong64` artifacts *(since 4.2.3)*

Helm 4.2 provides official Linux `loong64` release artifacts. Use the official
artifact instead of treating the platform as requiring an unofficial build.

## Migration checklist

- Compile embedded code against Helm 4 public APIs.
- Review chart API assumptions in SDK call sites.
- Connect host logging through Go `slog` where required.
- Exercise explicit and default server-side apply behavior.
- Test successful, failed, canceled, and bounded waits.
- Inventory ordinary plugins and post-renderers together.
- Validate integrations against the Helm 4 plugin model.
- Upgrade plugin-installing clients for provenance and path hardening.
- Distinguish Helm 3 bug-fix and security-fix support dates.
- Update maintained Helm 3 clients for relevant dependency security fixes.
- Verify the Kubernetes compatibility window for each deployment target.
- Select the official `loong64` build when targeting that Linux architecture.
