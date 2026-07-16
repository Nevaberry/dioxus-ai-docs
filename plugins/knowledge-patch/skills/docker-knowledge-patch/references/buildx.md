# Buildx, Bake, Imagetools, and Builders

Use this reference for Buildx and Bake inputs, source-policy enforcement, exporters, Imagetools, builder drivers, provenance, credentials, and resource controls.

## Build and Bake inputs

- `docker buildx bake --var NAME=VALUE` directly assigns a Bake variable without requiring an environment variable of the same name (since 0.31.0):

```console
docker buildx bake --var TAG=v1.2.3
```

- Bake can disable host-environment lookups so its configuration is evaluated without ambient environment values (since 0.31.0).
- Bake expressions add `semvercmp` for semantic-version comparisons (since 0.31.0).
- Bake expressions add `formattimestamp` and `unixtimestampparse` for time conversion (since 0.33.0).
- Remote Bake builds preserve Git context subdirectories and avoid inconsistent contents when a context path includes a subdirectory (since 0.33.0).
- An empty `BUILDKIT_SYNTAX` build-argument override is accepted starting in 0.33.0.

## Source-policy lifecycle

### Define and run Rego policies

Buildx 0.31.0 introduces experimental Rego source policy for local build contexts:

- A matching `Dockerfile.rego` or `app.Dockerfile.rego` loads automatically.
- Pass additional policy configuration with `build --policy` or a Bake target's `policy` key.
- Use `buildx policy eval` and `buildx policy test`; policies can use custom built-ins and gitsign checks.

```console
docker buildx build --policy ./policy.rego .
```

Buildx 0.32.0 extends source-policy validation to Git and HTTP build sources:

```console
docker buildx build --policy ./policy.rego https://github.com/example/project.git
```

### Verify artifacts and provenance

- Buildx 0.32.0 adds policy built-ins for signed Sigstore bundle attestations on HTTP artifacts and can retrieve attestations automatically through the GitHub API.
- Policies can inspect attestation fields through `input.image.provenance`; provenance materials arrive as secondary policy inputs. This requires BuildKit 0.28.0 or later.
- Buildx 0.33.0 adds `verify_http_pgp_signature` for PGP verification of HTTP sources.
- `buildx policy eval` accepts `--platform` for image-source selection and `-f -` for a policy on standard input (since 0.33.0).
- `policy eval --filename` is renamed to `--file`; the old spelling is deprecated (since 0.33.0).

### Apply policy globally

- `docker buildx bake --policy` supplies global policy-evaluation options starting in 0.34.0; policy settings need not live only on individual targets.
- Set `BUILDX_DEFAULT_POLICY` to enable a built-in policy that cryptographically verifies Docker-provided pipeline images (since 0.34.0).
- The built-in policy covers `docker/dockerfile`, `docker/dockerfile-upstream`, and the `docker/buildkit-syft-scanner` image used for SBOM generation. It is opt-in in 0.34.0 but intended to become the default later.

### Inspect build-step network traffic

With BuildKit 0.31.0 or later, a policy can return `caps: { "exec.proxy": true }` to opt into the exec proxy (since Buildx 0.35.0). Network requests made by run steps then appear as ordinary `input.http` sources to policy rules.

Enable the proxy for the entire builder instead when appropriate:

```console
docker buildx create --buildkitd-flags '--proxy-network'
```

## Credentials

- Buildx can load Docker configuration scoped to particular repositories or authorization scopes instead of only registry-wide configuration (since 0.31.0).
- When credentials for Docker Hardened Images (`dhi.io`) or Docker Scout registries are absent, authentication falls back to Docker Hub credentials (since 0.31.0).

## Exporters and local outputs

- The tar exporter creates missing parent directories for its output automatically (since 0.30.0):

```console
docker buildx build --output type=tar,dest=out/releases/image.tar .
```

- Docker-store exports with `--push` or `--output type=registry` skip local unpacking (since 0.31.0).
- Local output for `build` and `bake` accepts `mode=delete` to replace the destination directory rather than merging into it (since 0.35.0):

```console
docker buildx build --output type=local,dest=out,mode=delete .
```

- Without extra approval, a delete-mode destination must be below the working directory.
- For another destination, pass `--allow=buildx.local.delete` or confirm in the TUI.
- Multi-platform delete mode requires BuildKit 0.31.0 or later.

## Cache space policy

`docker buildx prune` accepts these space-policy filters starting with the Engine 28.0.0 toolchain:

- `reserved-space`
- `max-used-space`
- `min-free-space`
- `keep-bytes`

Engine API v1.48 renames `POST /build/prune` parameter `keep-bytes` to `reserved-space` and adds `max-used-space` and `min-free-space`; account for the CLI/API name boundary.

## CPU, memory, and device access

- `docker buildx build --resource` and Bake's `resource` key set CPU and memory limits starting in 0.35.0.
- Resource limits require BuildKit 0.31.0 or later and Dockerfile v1.25.0 or later.
- Engine builder configuration includes a `device` entitlement for builds requiring device access.

## Imagetools and OCI layouts

- `docker buildx imagetools create` preserves attestation manifests and Cosign manifest signatures rather than discarding them (since 0.30.0).
- `imagetools create --metadata-file` writes properties of the newly created image, including its descriptor and digest (since 0.32.0):

```console
docker buildx imagetools create --metadata-file image-metadata.json -t registry.example/app:latest registry.example/app:amd64 registry.example/app:arm64
```

- `imagetools create` and `imagetools inspect` accept OCI-layout paths as sources and destinations; layout paths can be combined with registry references (since 0.33.0).
- Local OCI-layout definitions handle Windows paths correctly (since 0.34.0).

## Named contexts

- Starting in 0.32.0, identically named contexts in different projects receive distinct shared keys, preventing one project's destination from overwriting another's.
- This cross-project isolation can reduce performance and requires Dockerfile 1.22.0 or later.

## Builder drivers and persistence

- The `docker-container` driver can add a GitHub Actions payload to provenance with `provenance-add-gha=true` (since 0.30.0):

```console
docker buildx create --driver=docker-container --driver-opt=provenance-add-gha=true
```

- The Kubernetes driver gains persistent-storage options in 0.34.0. Enabling them changes the builder from its transient form to a StatefulSet with a persistent volume claim.

## Timeouts and debugging

- Many Buildx commands accept `--timeout` to bound waits for remote-builder responses (since 0.32.0).
- The DAP debugger is generally available and no longer requires the experimental-features flag (since 0.33.0).

## Installation and release artifacts

- `docker buildx install` and `docker buildx uninstall` are deprecated (since 0.30.0). Invoke `docker buildx` directly instead of installing aliases below `docker builder`.
- Buildx release artifacts are signed and built with Docker GitHub Builder starting in 0.31.0.
