# Images, builds, and artifacts

## Building images

### Squash without layers (5.2.0)

`podman build` permits `--squash` with `--layers=false`.

```console
podman build --squash --layers=false .
```

### Multi-platform Build API (5.2.0)

The Images Build API accepts comma-separated values in `Platform`, such as
`linux/amd64,linux/arm64`, to build several architectures in one request.

### Build toolchain progression (5.3.0, 5.5.0, 5.7.0, and 6.0.0)

Building Podman requires Go 1.22 from 5.3.0, Go 1.23 from 5.5.0, Go 1.24 from 5.7.0, and Go 1.25
from 6.0.0. Choose the floor for the source release being built.

### Abandoned build cleanup (5.4.0)

`podman system prune --build` removes build containers left by interrupted builds.

```console
podman system prune --build
```

### Build provenance (5.4.0)

Makefile builds accept `BUILD_ORIGIN`; its value identifies the packager in `podman version` and
`podman info`.

```console
BUILD_ORIGIN=distribution make
```

### Suppress `/etc/hosts` through the API (5.4.0)

Compat and Libpod Images Build accept boolean query parameter `nohosts`. Set `nohosts=true` to
avoid creating `/etc/hosts` in the image.

### Label inheritance (5.5.0)

`podman build --inherit-labels` controls label inheritance from base images and stages. It
defaults to true.

### Remote build contexts (5.6.0)

The remote client supports `podman build --build-context`.

### Restored build compatibility (5.6.0)

Use 5.6.2 or later when a Containerfile combines a non-root user with cache mounts.

### SBOM behavior (5.7.0)

Podman now honors its SBOM-related build options. Recheck pipelines that previously worked around
ignored settings.

### Build-context security fixes (5.8.0)

Use 5.8.3 or later to fix CVE-2026-44517, where `ADD` or `COPY` from a malicious Git repository
or tar archive could escape the build-context boundary. Use 5.8.4 or later to fix
CVE-2026-57231, where malformed image `Env` entries could expose host environment variables in a
container.

### Process-substitution Containerfiles (6.0.0)

When `podman build -f` receives a process-substitution file, Podman supplies an empty temporary
directory as the build context instead of deriving a context from that path.

## Image operations

### Deterministic repository sorting (5.3.0)

`podman images --sort=repository` uses tag as a secondary key when repositories match.

### Pull authentication and certificates (5.7.0)

`podman run` and `podman create` accept `--creds` and `--cert-dir` for authentication and trust
when pulling a missing image.

### Sequoia-PGP signing (5.7.0)

Builds compiled with optional Sequoia-PGP support expose `--sign-by-sq-fingerprint` for image
signing.

### Trust and transfer controls (6.0.0)

`podman image trust` commands accept `--signature-policy`, and `image trust set` requires it.
`podman image scp --format` selects the transfer archive format.

### Pull policy (5.6.0)

`podman pull --policy` selects pull policy explicitly.

### Retried manifest pushes (5.8.6-6.1.0)

`podman manifest push` accepts `--retry` and `--retry-delay`.

```console
podman manifest push --retry 3 --retry-delay 5s LIST DESTINATION
```

## OCI artifacts

### Preview command suite (5.4.0)

The initial `podman artifact add`, `inspect`, `ls`, `pull`, `push`, and `rm` interface is a preview
in 5.4.0 and is not yet final.

```console
podman artifact ls
```

### Artifact consumption and updates (5.5.0)

`podman create`, `run`, and `pod create` accept `--mount type=artifact`. `podman artifact add`
adds `--append` to extend an artifact and `--file-type` to set the added file's MIME type.

### Stable commands and remote coverage (5.6.0)

The command suite is stable. Artifact commands work through the remote client and REST bindings.

### Stable Libpod API (5.6.0)

The Libpod API supports list, inspect, pull, remove, tar-body add/append, push, and extract. Key
routes are:

- `GET /libpod/artifacts/json` and `GET /libpod/artifacts/{name}/json`;
- `POST /libpod/artifacts/pull` and `POST /libpod/artifacts/add`;
- `DELETE /libpod/artifacts/{name}`;
- `GET /libpod/artifacts/{name}/extract`;
- `/libpod/artifacts/{name}/push` for pushes.

### Mount naming and a single blob (5.6.0)

Artifact mounts accept `name=` to choose the exposed filename. If an artifact contains one blob
and its destination does not exist in the image, the blob mounts as a file at the destination,
not as a directory.

```console
podman run --mount type=artifact,src=example.com/acme/data:latest,dst=/data,name=payload IMAGE
```

### Metadata and inspection (5.7.0)

`podman inspect` accepts artifacts, and `podman artifact inspect` adds `--format`. List formatting
exposes `VirtualSize` as integer bytes and `CreatedAt` as an RFC3339 timestamp. New artifacts get
`org.opencontainers.image.created` by default.

### Local artifact API (6.0.0)

`POST /libpod/local/artifacts/add` loads an artifact from the service host without uploading a tar
archive. The existing `POST /libpod/local/images` endpoint now requires an absolute `path` query
value.

## Image and artifact API output

### Manifest annotations and image fields (5.3.0 and 5.6.0)

`podman manifest inspect` includes annotations. Compat System DF no longer has `BuilderSize`.
Image lists always have `shared-size`, using `-1` when it was not requested. Image inspection
omits `VirtualSize` for Docker API 1.44 and later.

### Compat image inspect (5.7.0)

Compat Image Inspect no longer returns `ContainerConfig`; read `Config`, matching Docker API
v1.45 behavior.

### Machine-readable image list (6.0.0)

`podman image list --format json` adds `Repository` and `Tag`.

### Libpod pull behavior (6.0.0)

The Libpod image Pull endpoint streams progress with `pullProgress=true` and returns an error HTTP
status when a pull fails instead of always returning 200.

### Compat image Push completion (6.0.0)

Compat image Push finishes with a JSON object containing the pushed tag, digest, and size.

## Commit consistency

### Pause by default (6.0.0)

`podman commit` pauses the source container while recording changes. Use `--pause=false` only when
concurrent mutation and a potentially inconsistent commit are acceptable.
