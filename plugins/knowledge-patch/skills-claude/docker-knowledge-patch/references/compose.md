# Docker Compose 5

## Major migration and SDK

### Version numbering

Compose 5.0.0 jumps directly from v2 to v5. Versions 3 and 4 were skipped to
avoid confusion with obsolete Compose file-format labels 2.x and 3.x. Do not
infer that intermediate product major versions or new file-format versions
exist.

### Embeddable SDK

Compose 5.0.0 officially supports third-party SDK use. Configure its service
with functional parameters and caller-provided `io.Reader`/`io.Writer`, and
load projects through the API without depending on Docker CLI abstractions.

Publish through the SDK returns `api.ErrCanceled` when a user declines an
interactive prompt since 5.1.0. Handle that separately from operational errors.

## Build behavior

### Bake delegation

Compose 5.0.0 removes its internal BuildKit builder and delegates builds to
Docker Bake, as `docker build` does. Remove integrations with the former
internal builder path and account for Bake permissions and output.

### Stage-selective cache bypass

Use `build.no_cache_filter` to bypass cache only for selected named stages:

```yaml
services:
  app:
    build:
      context: .
      no_cache_filter:
        - dependencies
```

### Print output

Since 5.0.0, `docker compose build --print` disables the progress UI, keeping
rendered progress separate from the printed build definition.

### Remote contexts and permissions

Compose 5.2.0 no longer adds remote URL build contexts to Bake's `fs.read`
allowlist. They remain URL inputs and do not gain unnecessary local filesystem
permission.

Compose 5.4.0 uses the selected platform manifest digest for builds rather than
the digest of an attested index. Pinning and comparisons must expect the
platform-specific digest.

Compose 5.5.0 bridge mode no longer pulls the default image reference for a
service whose only purpose is to build an image.

## Image preparation and reconciliation

### Target-only `run`

Compose 5.0.0 `docker compose run SERVICE` prepares an image only for the target
service rather than unrelated services.

### Image-backed mounts

Compose 5.1.0 recreates a container when the digest of an image mounted into it
changes. Compose 5.4.0 pins `type:image` volume sources and `pre_start` hook
images, resolving hook images alongside service images.

### Workload reconciliation

Compose 5.2.0 introduces a new observed-versus-expected workload reconciliation
algorithm. Regression-test existing project convergence even when configuration
is unchanged.

Compose 5.4.0 includes volume recreation and network lifecycle in the
reconciliation plan, so non-workload resources participate in planned
convergence too.

Compose 5.5.0 updates image-digest reconciliation to avoid unnecessary
container recreation. The first `docker compose up` after upgrading may still
recreate existing containers once while their digests are re-evaluated.

### Pull refresh windows

Compose 5.5.0 `docker compose pull` honors `pull_policy` windows such as
`daily`, `weekly`, and `every_N`.

```yaml
services:
  app:
    image: example/app:latest
    pull_policy: daily
```

## Lifecycle hooks and init containers

Compose 5.0.0 runs configured lifecycle hooks on restart. Compose 5.1.0 runs
the target's `post_start` hooks for `docker compose run` and adds a stop hook
for external providers. Hook implementations must be safe on those paths.

Compose 5.3.0 adds native pre-start init containers for one-shot setup before
the main workload. Compose 5.4.0 resolves and pins their images along with
service and image-mount images.

## Start, attach, and events

Compose 5.0.0 supports `docker compose start --wait`:

```console
docker compose start --wait
```

It also restores detach-key handling in attached sessions.

Since 5.1.0, reconnecting a container to a network emits container status
events. Event consumers must treat the resulting update as normal rather than
assuming network reconnection is silent.

## Providers

Provider-managed resources receive a stop lifecycle hook since 5.1.0.
Compose 5.2.0 adds provider protocol message `rawsetenv`; provider integrations
must recognize it as an environment message rather than rejecting it as
unknown.

## OCI and Git remote resources

Compose 5.0.0 supports OCI and Git remote resources, including Compose
overrides for OCI projects.

Compose 5.1.0 preserves `ssh://` during Dockerfile path resolution, avoids an
invalid-path failure for OCI artifacts on Windows, and routes OCI pulls through
the Docker Desktop HTTP proxy. These are source- and platform-specific paths;
retain the URL scheme until the correct resolver handles it.

## Engine API fallback

Compose 5.1.0 restores post-connect attachment for multi-network projects when
the negotiated Engine API is older than v1.44. Keep API negotiation enabled so
the compatibility path can attach additional networks.

## Environment files and configuration resolution

### Extended services

Compose 5.1.0 initializes and passes the environment-file map while processing
`extends`, preserving env-file context in extended configurations.

### Variable discovery

Compose 5.2.0 skips model validation while extracting configuration variables.
`docker compose config --variables` can enumerate inputs even when the full
model would not yet validate.

### Optional publish env files

Compose 5.2.0 `publish` honors `required: false` for a missing `env_file`:

```yaml
services:
  app:
    env_file:
      - path: ./optional.env
        required: false
```

Publish's sensitive-data check flags literal inline environment values since
5.1.0. Do not treat a literal as safe merely because it did not come from a
file.

## Configuration queries and hashes

Compose 5.4.0 applies configuration processing flags to query forms
`--services`, `--volumes`, `--networks`, `--models`, and `--hash`. It also
preserves zero-replica services in the configuration hash.

Compose 5.5.0 resolves service environments when computing
`docker compose config --hash`; hashes therefore reflect the resolved service
configuration. Pin relevant environment inputs when comparing hashes.

## Publish and registry handling

Compose 5.0.0 adds `--insecure-registry` strictly for testing. Compose 5.4.0
continues honoring it when `docker compose up` reloads the project model.

Compose 5.2.0 bypasses the Docker Desktop proxy for loopback registries during
publish. Local registry traffic should remain local rather than being routed
through the Desktop proxy.

`publish` supports optional missing env files as above, distinguishes interactive
cancellation through `api.ErrCanceled`, and checks literal environment values
for secrets.

## Watch

Compose 5.2.0 no longer rebuilds services merely because they appear in
`depends_on` for a service affected by a watched change.

Compose 5.5.0 limits Watch cleanup instead of pruning every dangling image in
the project, avoiding removal of unrelated dangling project images. It also
skips unreadable directories rather than aborting the watch operation.

## Machine-readable and display output

### `ps` JSON framing

Compose 5.2.0 `docker compose ps --format json` emits one JSON value per line,
not a single array. Parse JSON Lines or collect the records explicitly.

### Image creation time

Compose 5.0.0 `docker compose images` displays image creation time or `N/A` when
unavailable. Output consumers must tolerate both.

## Upgrade checklist

1. Remove internal-builder and Docker CLI abstraction dependencies from SDK
   integrations.
2. Test existing workloads through workload, image-digest, volume, and network
   reconciliation after each upgrade.
3. Verify hook ordering and image pinning for restart, `run`, provider stop, and
   pre-start initialization.
4. Exercise old-API multi-network fallback and remote OCI/Git paths on each
   target platform.
5. Fix JSON Lines parsers, configuration-hash expectations, and Watch cleanup
   assumptions.
6. Keep insecure registries test-only and distinguish publish cancellation from
   failure.
