# Images, builds, and artifacts

Use this reference for Containerfile builds, image listing and transfer, registry trust, OCI
artifact lifecycle, artifact mounts, and artifact-specific APIs.

## Build behavior

### Squash without layers

Since 5.2.0, combine `--squash` with `--layers=false`:

```console
podman build --squash --layers=false .
```

### Base-image label inheritance

Since 5.5.0, `podman build --inherit-labels` controls whether labels are inherited from base
images and base stages. It defaults to `true`.

### SBOM options

Podman 5.7.0 corrects `podman build` so its SBOM-related options are honored.

### Process-substitution Containerfiles

Since 6.0.0, when `podman build -f` receives a process-substitution file, Podman supplies an empty
temporary directory as the build context. It no longer derives a context from the special file
path.

### Abandoned build containers

Since 5.4.0, remove build containers left behind by interrupted builds with:

```console
podman system prune --build
```

### Build-context security and compatibility

- Use 5.6.2 or later for Containerfile builds that combine a non-root user with cache mounts.
- Use 5.8.3 or later to prevent a malicious Git repository or tar archive from causing `ADD` or
  `COPY` to include files outside the build context.

## Build APIs and remote builds

### Several platforms in one request

Since 5.2.0, the Images Build API's `Platform` query parameter accepts a comma-separated list:

```text
linux/amd64,linux/arm64
```

One request can therefore build for several architectures.

### Suppress `/etc/hosts`

Since 5.4.0, Compat and Libpod Images Build endpoints accept boolean `nohosts`; set
`nohosts=true` to avoid creating `/etc/hosts` in the image.

### Remote build contexts

Since 5.6.0, the remote client supports `podman build --build-context`.

## Image creation, listing, and transfer

### Commit consistency

Since 6.0.0, `podman commit` pauses its source container by default while recording changes. Pass
`--pause=false` only when concurrent mutations and a potentially inconsistent result are
acceptable.

### Deterministic repository sorting

Since 5.3.0, `podman images --sort=repository` breaks equal-repository ties by tag, producing
deterministic ordering.

### Pull policy

Since 5.6.0, `podman pull --policy` selects the pull policy explicitly.

### Registry credentials and certificates

Since 5.7.0, `podman run` and `podman create` accept `--creds` and `--cert-dir` for authentication
and certificate selection when the requested image must be pulled.

### Signing

Builds compiled with optional Sequoia-PGP support expose `--sign-by-sq-fingerprint` since 5.7.0
for signing with a Sequoia-PGP key.

### Trust policy

Since 6.0.0, the `podman image trust` commands accept `--signature-policy`, and
`podman image trust set` requires it.

### SCP archive format

Since 6.0.0, `podman image scp --format` selects the archive format used during transfer.

## OCI artifact CLI lifecycle

### Preview to stable

Podman 5.4.0 introduced the preview artifact suite with `add`, `inspect`, `ls`, `pull`, `push`,
and `rm`. Treat that release's interface as pre-final. The suite became stable in 5.6.0 and is
available from the remote client and REST bindings.

```console
podman artifact ls
```

### Add and extend artifacts

Since 5.5.0:

- `podman artifact add --append` extends an existing artifact;
- `podman artifact add --file-type` sets the MIME type of the added file.

### Inspect and format metadata

Since 5.7.0:

- generic `podman inspect` accepts artifacts;
- `podman artifact inspect --format` formats artifact inspection;
- artifact list format field `VirtualSize` is integer bytes;
- artifact list format field `CreatedAt` is an RFC3339 timestamp;
- newly created artifacts receive `org.opencontainers.image.created` by default.

## Mount artifact contents

### Artifact mount type

Since 5.5.0, `--mount` on `podman create`, `podman run`, and `podman pod create` accepts
`type=artifact`:

```console
podman run --mount type=artifact,src=example.com/acme/data:latest,dst=/data IMAGE
```

### Exposed name and single-blob shape

Since 5.6.0, artifact mounts accept `name=` to select the filename exposed inside the container.
If the artifact has one blob and the destination does not already exist in the image, Podman
mounts that blob as a file at the destination rather than creating a directory.

## Artifact APIs

### Stable Libpod routes

The stable 5.6.0 artifact API includes list, inspect, pull, remove, tar-body add/append, push, and
extract operations. Principal routes are:

| Operation | Route |
| --- | --- |
| List | `GET /libpod/artifacts/json` |
| Inspect | `GET /libpod/artifacts/{name}/json` |
| Pull | `POST /libpod/artifacts/pull` |
| Add or append tar body | `POST /libpod/artifacts/add` |
| Remove | `DELETE /libpod/artifacts/{name}` |
| Push | `POST /libpod/artifacts/{name}/push` |
| Extract | `GET /libpod/artifacts/{name}/extract` |

### Service-local add

Since 6.0.0, `POST /libpod/local/artifacts/add` loads an artifact directly from the service host
without uploading a tar archive.

### Local image endpoint

Since 6.0.0, the existing `POST /libpod/local/images` endpoint requires an absolute `path` query
parameter.

## Artifact events and Quadlet

Since 6.0.0, artifact events include `create`, `pull`, `push`, and `remove`. Since 5.7.0, manage
artifacts declaratively with Quadlet `.artifact` units; consult the Quadlet reference for unit
installation and generated-service behavior.
