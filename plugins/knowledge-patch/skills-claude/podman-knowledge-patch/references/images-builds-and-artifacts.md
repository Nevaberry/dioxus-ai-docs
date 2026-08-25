# Images, builds, and artifacts

## Build behavior and cleanup

### Layering, labels, and contexts

`podman build --squash --layers=false` is valid (since 5.2.0):

```console
podman build --squash --layers=false .
```

`podman build --inherit-labels` controls labels inherited from base images and base stages and
defaults to true (since 5.5.0). SBOM-related build options are honored after their regression was
corrected (since 5.7.0).

When `podman build -f` receives a process-substitution file, the build receives an empty temporary
directory as its context instead of deriving a context directory from the substituted file path
(6.0.0).

Use `podman system prune --build` to remove abandoned build containers left by prematurely ended
builds (since 5.4.0):

```console
podman system prune --build
```

### Registry authentication and pull policy

`podman run` and `podman create` accept `--creds` and `--cert-dir` when a missing workload image
must be pulled with authentication or custom certificates (since 5.7.0). `podman pull --policy`
selects the pull policy (since 5.6.0).

### Build compatibility and security

Podman 5.6.2 restores Containerfile builds that combine a non-root user with cache mounts. Podman
5.8.3 fixes a boundary escape where `ADD` or `COPY` from a malicious Git repository or tar archive
could include files outside the build context. Do not process affected untrusted inputs on older
releases.

## Image listing, transfer, and signing

`podman images --sort=repository` sorts equal repository names by tag for deterministic ordering
(since 5.3.0).

`podman image trust` accepts `--signature-policy`, and `image trust set` requires it (6.0.0).
`podman image scp --format` chooses the transfer archive format.

Builds compiled with optional Sequoia-PGP support expose `--sign-by-sq-fingerprint` for signing
with a Sequoia-PGP key (since 5.7.0).

`podman manifest push` accepts `--retry` and `--retry-delay` for automated retries
(5.8.6-6.1.0):

```console
podman manifest push --retry 3 --retry-delay 5s LIST DESTINATION
```

## OCI artifact lifecycle

### Command maturity and basic operations

The `podman artifact` command suite began as a preview in 5.4.0 and is stable from 5.6.0. The
stable commands are `add`, `inspect`, `ls`, `pull`, `push`, and `rm`:

```console
podman artifact ls
```

`podman inspect` can inspect artifacts, while `podman artifact inspect --format` formats artifact
details (since 5.7.0). Artifact list templates expose `VirtualSize` as integer bytes and `CreatedAt`
as an RFC3339 timestamp. Newly created artifacts receive `org.opencontainers.image.created` by
default.

### Adding and extending artifacts

`podman artifact add --append` extends an existing artifact, and `--file-type` supplies the MIME
type for an added file (since 5.5.0). The stable Libpod API supports list, inspect, pull, remove,
tar-body add/append, push, and extract operations (since 5.6.0):

- `GET /libpod/artifacts/json`
- `GET /libpod/artifacts/{name}/json`
- `POST /libpod/artifacts/pull`
- `POST /libpod/artifacts/add`
- `DELETE /libpod/artifacts/{name}`
- `GET /libpod/artifacts/{name}/extract`
- `/libpod/artifacts/{name}/push` for pushes

Artifact commands are also available through the remote client and REST bindings. For content
already on the service host, `POST /libpod/local/artifacts/add` avoids a tar upload (6.0.0).

### Mounting artifact contents

Container and pod creation accept `--mount type=artifact` (since 5.5.0). Use `name=` to select the
filename exposed inside the container (since 5.6.0). If the artifact contains one blob and the
destination does not already exist in the image, Podman mounts that blob as a file at the
destination instead of creating a directory.

```console
podman run --mount type=artifact,src=example.com/acme/data:latest,dst=/data,name=payload IMAGE
```

Use a Quadlet `.artifact` unit when the artifact should be managed as a systemd-backed resource.

## Image and artifact API output

Artifact events report create, pull, push, and remove (6.0.0). Compat image Push ends with a JSON
object containing tag, digest, and size. The Libpod pull endpoint returns a failing HTTP status on
failure and optionally streams progress with `pullProgress=true`.

Malformed image `Env` entries could expose host environment variables before the 5.8.4 fix. Treat
untrusted affected images as unsafe on earlier releases.
