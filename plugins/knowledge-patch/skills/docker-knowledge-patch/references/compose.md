# Docker Compose 5

Use this reference for Compose 5 migration, SDK embedding, Bake-backed builds, remote resources, lifecycle hooks, providers, publishing, watch behavior, and machine-readable output.

## Major-version migration

- Compose jumps directly from v2 to 5.0.0. Versions 3 and 4 were intentionally skipped to distinguish the product release from obsolete Compose file format versions 2.x and 3.x.
- Compose 5 removes the internal BuildKit builder and delegates builds to Docker Bake. Integrations must not depend on the former internal builder path.
- Compose 5.2.0 introduces a new algorithm for reconciling observed workload state with expected state. Regression-test how existing projects converge after upgrade.

## Compose as an SDK

- Compose 5.0.0 officially supports embedding as an SDK in third-party software.
- Configure the Compose service with functional parameters and provide `io.Reader` and `io.Writer` streams.
- The API can load Compose projects without requiring the Docker CLI.
- When a user rejects an interactive publish prompt, the Publish API returns `api.ErrCanceled` (since 5.1.0), allowing callers to distinguish cancellation from other failures.
- Configuration-variable extraction skips Compose model validation starting in 5.2.0, so tooling can discover interpolation variables without satisfying unrelated full-model validation.

## Build execution

- Builds are delegated to Bake starting in 5.0.0.
- `docker compose run SERVICE` ensures an image exists only for the requested service instead of preparing images for unrelated services (since 5.0.0).
- A service build accepts `build.no_cache_filter` to bypass cache for selected stages (since 5.0.0):

```yaml
services:
  app:
    build:
      context: .
      no_cache_filter:
        - build
```

- Compose 5.2.0 no longer puts remote URL build contexts in Bake's `fs.read` allowlist; remote inputs are not treated as local filesystem paths.

## OCI, Git, and remote resources

- Compose supports OCI and Git remote resources starting in 5.0.0.
- Compose projects sourced from OCI can be combined with override files.
- OCI artifacts work with Windows paths starting in 5.1.0; they no longer produce an invalid-path error.
- Compose preserves the `ssh://` scheme while resolving Dockerfile URLs (since 5.1.0), instead of treating those URLs as local paths.
- OCI artifact pulls use the Docker Desktop HTTP proxy when Compose runs through Docker Desktop (since 5.1.0).

## Service lifecycle and init containers

- Configured lifecycle hooks run when Compose restarts a service (since 5.0.0).
- One-off containers created by `docker compose run` execute the service's `post_start` hooks (since 5.1.0).
- External provider plugins receive a stop lifecycle hook during Compose shutdown (since 5.1.0).
- Compose recreates a container when the digest of an image used as a mount changes (since 5.1.0), preventing stale mounted content.
- Compose 5.3.0 natively supports pre-start init containers so initialization can finish before regular workload containers start.

## Start and wait

`docker compose start --wait` waits for started services rather than returning immediately (since 5.0.0):

```console
docker compose start --wait
```

## Environment files, `extends`, and publishing

- Environment-file mappings are initialized and passed while processing `extends` (since 5.1.0), so extended services resolve their values consistently.
- `docker compose publish` checks literal inline environment values for sensitive data (since 5.1.0).
- Publishing honors `required: false` for a missing `env_file` starting in 5.2.0; an absent optional file no longer fails publication.

## Provider protocol

- Provider plugins can send the `rawsetenv` message type starting in 5.2.0. Protocol producers and consumers must handle this additional variant.
- External providers also have the shutdown stop hook introduced in 5.1.0.

## Watch behavior

- A watched file change no longer rebuilds services mentioned through `depends_on` solely because of that dependency relationship (since 5.2.0).

## JSON output

- `docker compose ps --format json` emits JSON Lines starting in 5.2.0, not one JSON array.
- Parse one JSON value per line or aggregate the records explicitly.

## Older Engine API compatibility

- Against Engine APIs older than v1.44, Compose 5.1.0 restores the post-connect fallback for projects that attach containers to multiple networks.
