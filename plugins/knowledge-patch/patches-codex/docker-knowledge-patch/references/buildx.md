# Buildx, Bake, Imagetools, and Builders

Use this reference for Buildx and Bake configuration, source policies,
imagetools, exporters, remote builders, and driver behavior.

## Cache, export, and resource controls

### Build-cache space policies (28.0.0)

`docker buildx prune` adds `reserved-space`, `max-used-space`, and
`min-free-space` controls alongside `keep-bytes`. The build-prune API renames
`keep-bytes` to `reserved-space` and exposes the additional limits.

### Tar exporter creates parent directories (0.30.0)

The tar exporter now creates missing parent directories for its output
destination, so nested output paths no longer need to be prepared in advance.

### Registry exports skip Docker-store unpacking (0.31.0)

Images created in the Docker image store are no longer unpacked when the export
was initialized with `--push` or `-o type=registry`; workflows must not assume
these registry-oriented exports produced unpacked local content.

### Replacement-mode local exports (0.35.0)

The local exporter accepts `mode=delete` for build and Bake, replacing the
destination directory with the build result instead of merging into it. The
destination must be below the working directory unless
`--allow=buildx.local.delete` is supplied or the TUI confirms the action;
multi-platform exports require BuildKit 0.31.0 or later.

```console
docker buildx build --output type=local,dest=./out,mode=delete .
```

### Per-build CPU and memory limits (0.35.0)

Build requests can set CPU and memory limits with the build command's
`--resource` flag or a Bake target's `resource` key. This requires BuildKit
0.31.0 or later and Dockerfile 1.25.0 or later.

## Builder setup and operation

### Builder alias installation is deprecated (0.30.0)

`docker buildx install` and `docker buildx uninstall` are deprecated. Invoke
`docker buildx` directly instead of relying on aliases under `docker builder`.

### GitHub Actions provenance payloads (0.30.0)

The `docker-container` driver can add a GitHub Actions payload to provenance
with `provenance-add-gha=true`.

```console
docker buildx create --driver=docker-container --driver-opt=provenance-add-gha=true
```

### Remote-builder timeouts (0.32.0)

Many Buildx commands now accept `--timeout` to bound how long they wait for
responses from remote builders.

### Generally available DAP debugging (0.33.0)

Buildx's DAP debugger no longer requires the experimental-features flag, so
build debugging can be used without that opt-in.

### Persistent Kubernetes builders (0.34.0)

The Kubernetes driver adds persistent-storage options that change its builder
deployment to a StatefulSet backed by a persistent volume claim.

## Bake variables, paths, and expressions

### Direct and isolated Bake variables (0.31.0)

`docker buildx bake --var NAME=VALUE` sets Bake variables from the command line
instead of requiring environment variables. Bake can also disable environment
lookups when evaluation must ignore the host environment.

```console
docker buildx bake --var VERSION=1.2.3
```

### Semantic-version comparisons in Bake (0.31.0)

The Bake standard library adds `semvercmp`, allowing Bake definitions to
compare semantic versions without external preprocessing.

### Bake time functions (0.33.0)

Bake expressions add the `formattimestamp` and `unixtimestampparse` builtins,
allowing time values to be handled directly in Bake definitions.

### Overridable Bake secret sources (0.36.0)

Bake overrides can now replace the source of an already-declared secret,
allowing callers to redirect the secret without editing the Bake definition.

### Bake-file-relative paths (0.36.0)

Set `BUILDX_BAKE_FILE_RELATIVE_PATHS=true` to resolve files relative to the Bake
file instead of the current working directory.

```console
BUILDX_BAKE_FILE_RELATIVE_PATHS=true docker buildx bake -f ./build/docker-bake.hcl
```

## Source policies

### Experimental Rego source policies (0.31.0)

Buildx can enforce build source policies written in Rego. In this release policy
support is experimental and only local build contexts load policies; a matching
`Dockerfile.rego` or named-Dockerfile policy such as `app.Dockerfile.rego` is
loaded automatically, while `build --policy` supplies policy configuration
explicitly.

```console
docker buildx build --policy ./policy.rego .
```

Bake also auto-loads matching policies and accepts a target `policy` key. The
new `docker buildx policy eval` and `docker buildx policy test` subcommands
support policy authoring and testing.

### Policies for remote sources (0.32.0)

Rego source policies can now validate builds whose sources are remote Git
repositories or HTTP resources; policy enforcement is no longer limited to
local build contexts.

### Attestation-aware policies (0.32.0)

New Rego builtins validate signed Sigstore bundle attestations for HTTP
artifacts and can automatically fetch attestations from the GitHub API. Policies
can also inspect `input.image.provenance` and use provenance materials as
secondary inputs; provenance policy inputs require BuildKit 0.28 or later.

### PGP verification in source policies (0.33.0)

Policy evaluation adds the `verify_http_pgp_signature` builtin for verifying PGP
signatures on HTTP sources.

### Policy evaluation inputs and flags (0.33.0)

`docker buildx policy eval` accepts `--platform` to select the platform of
evaluated image sources and `-f -` to read a policy from standard input. The
long flag `--filename` is renamed to `--file`; the old name remains deprecated.

```console
docker buildx policy eval --platform linux/amd64 -f - docker.io/library/alpine:latest < policy.rego
```

### Default verification for Docker pipeline images (0.34.0)

Buildx can apply a default source policy that cryptographically verifies the
Docker-provided `docker/dockerfile`, `docker/dockerfile-upstream`, and
`docker/buildkit-syft-scanner` images before builds use them. This is opt-in
through `BUILDX_DEFAULT_POLICY` in this release, but is intended to become the
default later.

### Global policy options for Bake (0.34.0)

`docker buildx bake` adds `--policy`, allowing policy evaluation options to be
supplied globally rather than only through automatic discovery or target
configuration.

### Source-policy control of build-step network traffic (0.35.0)

With BuildKit 0.31.0 or later, a source policy can opt into the exec proxy by
returning `caps: {"exec.proxy": true}` in its evaluation decision, after which
ordinary `input.http` policy rules can control requests made by build steps. A
whole builder can instead opt in when it is created.

```console
docker buildx create --buildkitd-flags '--proxy-network'
```

### Authenticity checks for BuildKit release images (0.36.0)

The default source policy can now validate BuildKit release images when
`docker buildx create` creates a `docker-container` builder. This extends
authenticity checking to the BuildKit image used by the builder.

### Source-policy language additions (0.36.0)

Source policies now support the `array.flatten` builtin and OPA template
strings, making both forms available when authoring policy rules.

## Imagetools, attestations, and OCI layouts

### `imagetools create` preserves supply-chain metadata (0.30.0)

`docker buildx imagetools create` now preserves attestation manifests and
Cosign-based manifest signatures when assembling a new image.

### Imagetools metadata files (0.32.0)

`docker buildx imagetools create` accepts `--metadata-file`, allowing automation
to capture properties such as the created image's descriptor and digest without
scraping human-readable output.

```console
docker buildx imagetools create --tag registry.example/app:latest --metadata-file metadata.json alpine:latest
```

### Imagetools registry authentication (0.32.0)

Imagetools now uses the same authentication libraries as build commands, adding
support for scoped credentials and automatic credential fallback for Docker
Hardened Image registries.

### OCI layouts in imagetools (0.33.0)

`docker buildx imagetools create` and `inspect` now support OCI layout paths as
sources and destinations, including workflows that combine an OCI layout with
registry references.

### Stricter file-loaded descriptors in imagetools (0.36.0)

Imagetools commands now perform additional validation on descriptor inputs
loaded from files. Automation that supplied descriptors accepted by older
releases may now receive a validation error.

### Opting out of default OCI artifacts (0.36.0)

Buildx 0.36.1 adds `BUILDX_NO_DEFAULT_OCI_ARTIFACT` as an alternative to
`oci-artifact=false` when that option has not been set explicitly.

```console
BUILDX_NO_DEFAULT_OCI_ARTIFACT=true docker buildx build .
```

## Context identity and credentials

### Scoped registry credentials and fallback (0.31.0)

Buildx can load Docker configurations scoped to particular repositories or
authorization scopes, allowing credentials to be constrained more narrowly.
For builds using Docker Hardened Images or Docker Scout registries,
authentication falls back to Docker Hub credentials when no registry-specific
credentials are available.

### Project-scoped named contexts (0.32.0)

Named contexts in different projects now receive distinct shared keys instead
of colliding solely because they have the same context name. This prevents
destination overwrites across projects at some performance cost and requires
Dockerfile 1.22 or later.

### Named-context source metadata (0.32.0)

Bake now preserves the original URL of named contexts sent as inputs in request
metadata, allowing consumers of that metadata to retain the remote source
identity.

### 0.32.1 private Git credential fix (0.32.0)

Buildx 0.32.1 fixes possible failures when secret credentials are used to build
directly from a private Git repository as the remote source.
