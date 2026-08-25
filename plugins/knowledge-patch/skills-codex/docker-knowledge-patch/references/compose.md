# Docker Compose 5

Use this reference for Compose SDK integration, build delegation,
reconciliation, lifecycle behavior, configuration, remote resources, publishing,
and Watch.

## Architecture and SDK integration

### Major-version numbering (5.0.0)

Compose jumps directly from v2 to v5: v3 and v4 were intentionally skipped to
distinguish this release line from the obsolete Compose file-format versions
2.x and 3.x.

### Official embeddable Compose SDK (5.0.0)

Compose is now officially supported as an SDK for third-party software. Its
service can be configured with functional parameters and caller-supplied
`io.Reader` and `io.Writer`, can load projects through the API, and no longer
requires Docker CLI abstractions.

### Bake replaces the internal builder (5.0.0)

Compose removes its internal BuildKit builder and delegates builds to Docker
Bake, as the `docker build` command does. Integrations that depended on the
internal builder must migrate to the delegated build path.

## Build and image behavior

### Target-only image preparation for `run` (5.0.0)

`docker compose run SERVICE` now ensures that an image exists only for the
target service instead of preparing images for unrelated services.

### Stage-selective cache bypass (5.0.0)

Compose build configuration accepts `build.no_cache_filter`, allowing named
stages to bypass cache without disabling cache for the whole build.

```yaml
services:
  app:
    build:
      context: .
      no_cache_filter:
        - dependencies
```

### Remote URL build contexts and Bake permissions (5.2.0)

Compose no longer adds remote URL build contexts to Bake's `fs.read` allowlist.
Remote contexts therefore remain URL inputs rather than being treated as
requiring local filesystem access.

### Platform-manifest digests for builds (5.4.0)

For builds, Compose uses the selected platform image-manifest digest instead of
the digest of an attested index. Automation comparing or pinning build inputs
should expect the platform-specific digest.

### Pull-policy refresh windows in `compose pull` (5.5.0)

`docker compose pull` now honors `pull_policy` refresh windows such as `daily`,
`weekly`, and `every_N`, so pulls respect the service's configured refresh
cadence.

```yaml
services:
  app:
    image: example/app:latest
    pull_policy: daily
```

### Build-only services in bridge mode (5.5.0)

In bridge mode, Compose no longer pulls the default image reference for a
service that exists only to build an image.

## Reconciliation and resource lifecycle

### Reconciliation of image mounts (5.1.0)

Compose now recreates a container when the digest of an image mounted into it
changes. Re-running reconciliation therefore applies updated mounted-image
content even when the service's own image and configuration are unchanged.

### New workload reconciliation algorithm (5.2.0)

Compose now uses a new algorithm to reconcile observed workload state with
expected state. Existing workloads can therefore behave differently after
upgrading even when their Compose files have not changed.

### Resource reconciliation plans (5.4.0)

Compose now models volume recreation and network lifecycle in its reconciliation
plan. Volume and network changes can therefore participate in the same planned
convergence as workloads.

### Pinned images for mounts and pre-start hooks (5.4.0)

Compose now pins `type:image` volume sources and `pre_start` hook images, and
resolves hook images alongside service images. Image resolution is therefore
consistent across services, image-backed volumes, and pre-start hooks.

### Image-digest reconciliation upgrade (5.5.0)

Compose now uses a new image-digest reconciliation process to avoid unnecessary
container recreation. The first `docker compose up` after upgrading may still
recreate existing containers once because their image digests are re-evaluated
under the new logic.

## Hooks, init containers, and service operation

### Lifecycle hooks on restart (5.0.0)

Configured service hooks now run on restart, so restart operations can trigger
lifecycle behavior instead of hooks being limited to other lifecycle paths.

### Waiting when starting services (5.0.0)

`docker compose start --wait` waits for services after starting them.

```console
docker compose start --wait
```

### Restored detach-key handling (5.0.0)

Compose restores detach-key support for attached sessions.

### Lifecycle hooks for one-off containers and providers (5.1.0)

`docker compose run` now executes the target service's `post_start` hooks.
External providers also gain a stop lifecycle hook, allowing provider-managed
resources to participate in Compose shutdown.

### Native pre-start init containers (5.3.0)

Compose now natively supports init containers that run before the main workload
starts, making one-shot setup work a first-class part of service startup.

## Remote resources, proxies, and registries

### OCI and Git remote resources (5.0.0)

Compose supports OCI and Git remote resources, and Compose overrides now work
for OCI-sourced projects.

### Test-only insecure registries (5.0.0)

Compose adds `--insecure-registry`, explicitly reserved for testing rather than
production registry configuration.

### Remote-resource path and proxy handling (5.1.0)

Dockerfile path resolution now preserves an `ssh://` URL scheme, and OCI
artifacts no longer produce an invalid-path error solely because Compose is
running on Windows. Under Docker Desktop, OCI artifact pulls are routed through
the Desktop HTTP proxy.

### Loopback registries bypass the Desktop proxy (5.2.0)

When publishing through Docker Desktop, Compose now bypasses the Desktop proxy
for loopback registries. Publishing to a registry on the local machine no
longer incorrectly routes through that proxy.

### Insecure registries across `up` reloads (5.4.0)

When `docker compose up` reloads the project model, it now continues to honor
`--insecure-registry`.

## Configuration and environment processing

### Environment files during service extension (5.1.0)

Compose now initializes and passes its environment-file map while processing
`extends`. Extended service configurations therefore retain env-file context
during resolution.

### Variable extraction before config validation (5.2.0)

Compose skips model validation when extracting configuration variables.
`docker compose config --variables` can therefore report the variables a
configuration uses without first requiring the full model to validate.

### Optional environment files during publish (5.2.0)

`docker compose publish` now honors `required: false` for a missing `env_file`,
so optional local environment files do not prevent publication.

```yaml
services:
  app:
    env_file:
      - path: ./optional.env
        required: false
```

### Zero-replica services in configuration hashes (5.4.0)

Compose preserves zero-replica services when hashing configuration.
`docker compose config --hash` therefore continues to account for a service
when its desired replica count is zero.

### Config flags in resource-query output (5.4.0)

Configuration flags now apply to `--services`, `--volumes`, `--networks`,
`--models`, and `--hash`. Query-style `docker compose config` invocations
therefore use the requested configuration processing.

### Environment-aware configuration hashes (5.5.0)

Compose now resolves service environments when computing
`docker compose config --hash`, so the resulting hash reflects the resolved
service configuration.

## Publishing and provider integrations

### Publish cancellation and sensitive values (5.1.0)

The Compose SDK's publish operation returns `api.ErrCanceled` when a user
declines an interactive prompt, so callers can distinguish cancellation from
other failures. Publish's sensitive-data check also flags literal inline
environment values.

### Raw environment messages from provider plugins (5.2.0)

The provider-plugin protocol adds a `rawsetenv` message type. Provider
integrations must recognize this message instead of treating it as an unknown
provider response.

## Networks and events

### Status events after network reconnection (5.1.0)

Compose emits container status events after reconnecting a container to a
network. Consumers of the Compose event stream should expect the resulting
status update instead of treating reconnection as silent.

### Older-API multi-network fallback (5.1.0)

Compose restores its post-connect fallback for multi-network projects when the
negotiated Engine API is older than 1.44. Such projects can attach their
additional networks through the compatibility path instead of requiring a
newer daemon API.

## Command output

### Clean `build --print` output (5.0.0)

`docker compose build --print` now disables the progress UI, preventing progress
rendering from mixing with the printed build output.

### Image creation values in `images` (5.0.0)

`docker compose images` now displays an image's creation time, or `N/A` when it
is unavailable; output consumers must tolerate both forms.

### `ps` JSON output is JSON Lines (5.2.0)

`docker compose ps --format json` emits one JSON object per line, not a single
JSON array. Consumers must parse it as JSON Lines or combine the records
themselves.

## Watch behavior

### Compose Watch no longer rebuilds dependencies (5.2.0)

On a watched file change, Compose no longer rebuilds services referenced through
`depends_on` merely because they are dependencies of the changed service.

### Scoped image cleanup in Watch (5.5.0)

Compose Watch no longer prunes every dangling image in the project, avoiding
removal of unrelated dangling project images during a watch cycle.

### Unreadable directories in Watch (5.5.0)

Compose Watch now skips directories it cannot read instead of failing the watch
operation.
