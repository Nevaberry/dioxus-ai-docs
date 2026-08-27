# Migration, SDK, Plugins, and Compatibility

## Embedded SDK migration

### Review public API changes

Helm 4 changes public SDK APIs (since 4.2.3). Code that embeds Helm should be
compiled and tested against the v4 API rather than relying on Helm 3 method
signatures or behaviors. This SDK migration surface does not imply that every
Helm 3 chart needs changes.

The Helm 4 SDK can handle multiple chart API versions. Preserve that ability
when host code loads, creates, or processes charts instead of assuming a
single chart API version.

### Integrate logging with `slog`

Helm 4 uses Go `slog` (since 4.2.3), allowing embedded Helm logging to connect
to modern host loggers. Exercise the logging path when migrating an embedded
integration, including any handler or context behavior supplied by the host.

## Plugins and post-renderers

### Adopt the Helm 4 plugin model

Helm 4 redesigns the plugin system to support WebAssembly-based plugins
(since 4.2.3). Inventory and test every extension when moving a CLI or an
embedded integration to Helm 4.

Post-renderers are plugins in Helm 4. Treat post-renderer commands and
ordinary extensions as one migration surface rather than reviewing only the
integrations already labeled as plugins.

### Require hardened plugin validation

Helm 4.2 fixes a missing-provenance bypass and version path traversal in
plugin handling (since 4.2.3). Upgrade older Helm 4 clients that install
plugins, especially when their plugin sources are not fully trusted.

After upgrading, retest plugin installation as well as execution. Installation
is the path directly affected by provenance and version-path validation.

## Kubernetes compatibility

### Apply the `n-3` policy

Helm 4 follows an `n-3` Kubernetes compatibility policy (since 4.2.3). It does
not promise forward compatibility beyond the Kubernetes client version with
which the Helm client was built.

Helm 4.2.x uses Kubernetes 1.36 client libraries. Its supported Kubernetes
window is 1.33.x through 1.36.x. Check both the Helm line and the target
cluster version before diagnosing behavior or claiming that a combination is
supported.

## Helm 3 maintenance

### Plan around support dates

Helm 3 receives bug fixes through July 8, 2026 and security fixes through
November 11, 2026 (since 4.2.3). During this transition, features are not
backported. The exception is Kubernetes client-library updates required to
support newer Kubernetes versions.

Use the support window to decide whether a maintained product still needs a
Helm 3 path or should finish its Helm 4 migration. Do not plan on new Helm 4
features appearing in Helm 3.

### Pick up security dependency updates

Helm 3.21.4 includes the following dependency changes:

- Provenance cryptography migrates to `ProtonMail/go-crypto` for
  GO-2026-5932.
- OpenTelemetry updates to 1.44.0.
- gRPC updates to 1.82.1.
- `x/crypto` updates to 0.54.0.
- `x/text` updates to 0.40.0.

The dependency updates address GO-2026-5158, GO-2026-6061, and GO-2026-5970
in addition to the provenance change. Upgrade maintained Helm 3 clients that
need these fixes.

## Platform artifacts

### Use official Linux `loong64` builds

Helm 4.2 supplies official Linux `loong64` release artifacts (since 4.2.3).
Prefer those artifacts over an ad hoc build when deploying the Helm CLI on
that platform.

## Migration review

For an SDK, plugin, or compatibility migration:

1. Identify whether the integration embeds the SDK, invokes the CLI, installs
   a plugin, or runs a post-renderer.
2. Compile embedded code against Helm 4 and test the chart API versions it
   actually consumes.
3. Connect and test `slog` output when the host owns logging.
4. Test all plugins and post-renderers through the Helm 4 plugin model.
5. Confirm plugin-installing clients include provenance and path hardening.
6. Compare the target cluster with the Kubernetes client version and `n-3`
   window.
7. Apply the Helm 3 support dates and dependency fixes to maintained legacy
   clients.
8. Choose the official Linux `loong64` artifact where applicable.
