# Buildx, Bake, Imagetools, and Builders

## Exporters and output control

### Tar destinations

Buildx 0.30.0 makes the tar exporter create missing parent directories for its
destination. Nested output paths no longer need a separate preparation step.

### Registry exports

Since 0.31.0, an image made in the Docker image store is not unpacked locally
when export starts with `--push` or `-o type=registry`. Do not treat a
registry-oriented export as evidence that local unpacked content exists.

### Replacement-mode local exports

Buildx 0.35.0 local output supports `mode=delete`, replacing the destination
rather than merging into it. By default the destination must be under the
working directory; elsewhere requires `--allow=buildx.local.delete` or TUI
confirmation. Multi-platform use requires BuildKit 0.31.0 or later.

```console
docker buildx build --output type=local,dest=./out,mode=delete .
```

Treat this as a destructive operation: validate the resolved destination and
grant the permission narrowly.

### Default OCI artifacts

Buildx 0.36.1 adds environment variable `BUILDX_NO_DEFAULT_OCI_ARTIFACT` as an
alternative to `oci-artifact=false` when that output option is not explicit.

```console
BUILDX_NO_DEFAULT_OCI_ARTIFACT=true docker buildx build .
```

## Imagetools

### Preserve and capture metadata

Buildx 0.30.0 `imagetools create` preserves attestation manifests and
Cosign-based manifest signatures while assembling an image.

Buildx 0.32.0 adds `--metadata-file`, allowing automation to capture the
created descriptor and digest without parsing human output.

```console
docker buildx imagetools create \
  --tag registry.example/app:latest \
  --metadata-file metadata.json alpine:latest
```

### Authentication and OCI layouts

Buildx 0.32.0 aligns Imagetools authentication with builds, including scoped
credentials and automatic Docker Hardened Images credential fallback.

Buildx 0.33.0 makes `imagetools create` and `inspect` accept OCI layout paths as
sources and destinations, including mixed layout/registry workflows.

### Descriptor validation

Buildx 0.36.0 validates file-loaded descriptor inputs more strictly. Older
automation may now fail; correct the descriptor instead of assuming all
previously accepted input was valid.

## Builders and command lifecycle

### Builder aliases

Buildx 0.30.0 deprecates `docker buildx install` and `uninstall`. Invoke
`docker buildx` directly instead of installing aliases under `docker builder`.

### Remote-builder timeouts

Buildx 0.32.0 adds `--timeout` to many commands. Bound waits to remote builders
where available and handle deadline failure separately from build failure.

### Kubernetes persistence

Buildx 0.34.0 Kubernetes builders can use persistent storage. The driver
options replace the deployment with a StatefulSet backed by a persistent
volume claim; account for stateful rollout and cleanup semantics.

### BuildKit image authenticity

Buildx 0.36.0 extends the default source policy to authenticate BuildKit release
images when `buildx create` makes a `docker-container` builder. This protects
the builder image itself, not only sources used by its builds.

## Bake variables, functions, and paths

### Direct and isolated variables

Buildx 0.31.0 adds `bake --var NAME=VALUE` and an option to disable environment
lookups. Use them to make evaluation inputs explicit and reproducible.

```console
docker buildx bake --var VERSION=1.2.3
```

Bake's standard library also gains `semvercmp` in 0.31.0. Buildx 0.33.0 adds
`formattimestamp` and `unixtimestampparse`.

### Bake-file-relative paths

Buildx 0.36.0 can resolve files relative to the Bake file rather than the
current directory:

```console
BUILDX_BAKE_FILE_RELATIVE_PATHS=true docker buildx bake -f ./build/docker-bake.hcl
```

### Secret source overrides

Buildx 0.36.0 lets a Bake override replace the source of an already-declared
secret. This supports caller-controlled secret locations without editing the
Bake definition; retain secret scoping and avoid logging the replacement.

## Named contexts and source identity

Buildx 0.32.0 gives same-named contexts in different projects distinct shared
keys. This prevents destination overwrites at some performance cost and
requires Dockerfile 1.22.0 or later.

The same release preserves a named context's original URL in request metadata,
allowing provenance and integrations to retain remote source identity. Buildx
0.32.1 fixes failures when secret credentials build directly from a private Git
remote.

## Source policies

### Local policy introduction

Buildx 0.31.0 introduces experimental Rego policy for local contexts. A
matching `Dockerfile.rego` or `app.Dockerfile.rego` auto-loads; `build --policy`
selects a policy explicitly. Bake auto-loads policies and accepts target
`policy`. Use `buildx policy eval` and `policy test` while authoring.

```console
docker buildx build --policy ./policy.rego .
```

### Remote sources and attestations

Buildx 0.32.0 extends policy to Git and HTTP sources. New builtins validate
signed Sigstore bundle attestations for HTTP artifacts and can retrieve
attestations from GitHub. Policies can inspect `input.image.provenance` and use
provenance materials as secondary inputs; that provenance input requires
BuildKit 0.28.0 or later.

Buildx 0.33.0 adds `verify_http_pgp_signature`. `policy eval` gains
`--platform` and `-f -`; long flag `--filename` becomes deprecated in favor of
`--file`.

```console
docker buildx policy eval --platform linux/amd64 -f - \
  docker.io/library/alpine:latest < policy.rego
```

Buildx 0.36.0 adds `array.flatten` and OPA template strings to policy authoring.

### Default Docker pipeline verification

Buildx 0.34.0 can cryptographically verify Docker-provided
`docker/dockerfile`, `docker/dockerfile-upstream`, and
`docker/buildkit-syft-scanner` images through an opt-in default policy selected
with `BUILDX_DEFAULT_POLICY`. This verification is intended to become the
default in a later release, so test both explicit policy and future-default
behavior. Buildx 0.36.0 extends default checking to the BuildKit release image
used by a new docker-container builder.

### Bake-wide policy options

Buildx 0.34.0 adds global `bake --policy`, in addition to automatic discovery
and target-level configuration.

```console
docker buildx bake --policy ./policy.rego
```

### Build-step network proxy

With BuildKit 0.31.0 or later, Buildx 0.35.0 policies can opt a build into the
exec proxy by returning `caps: {"exec.proxy": true}`. Normal `input.http`
rules can then govern build-step requests. A builder-wide opt-in is:

```console
docker buildx create --buildkitd-flags '--proxy-network'
```

## Resources

Buildx 0.35.0 adds per-build CPU and memory constraints through build
`--resource` or Bake target `resource`. It requires BuildKit 0.31.0 or later and
Dockerfile 1.25.0 or later. Detect those dependencies before emitting the
option.

## Credentials

Buildx 0.31.0 loads Docker configurations scoped to repositories or auth
scopes. Constrain credentials narrowly. Docker Hardened Images and Docker Scout
registries fall back to Docker Hub credentials when no registry-specific
credential is present; Buildx 0.32.0 brings the same libraries and fallback to
Imagetools.

## Debugging and provenance

The DAP debugger becomes generally available in Buildx 0.33.0 and no longer
needs experimental features.

Buildx 0.30.0 `docker-container` builders can add a GitHub Actions payload to
provenance with `provenance-add-gha=true`:

```console
docker buildx create --driver=docker-container \
  --driver-opt=provenance-add-gha=true
```

## Upgrade checklist

1. Remove dependency on builder aliases and human-readable Imagetools output.
2. Verify whether registry output should be locally unpacked.
3. Resolve Bake variables, secret sources, and paths from explicit inputs.
4. Test source policy against every source class and builder image in scope.
5. Grant deletion, network proxy, filesystem, device, CPU, and memory
   capabilities as narrowly as possible.
