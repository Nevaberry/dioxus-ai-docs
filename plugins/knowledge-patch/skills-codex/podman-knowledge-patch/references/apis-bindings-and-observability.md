# APIs, bindings, and observability

## Remote connections and transport

### TCP path prefixes (5.3.0)

`podman system connection add` preserves and uses HTTP path prefixes in `tcp://` URLs.

### Remote command coverage (5.6.0)

The remote client supports volume import/export and `podman build --build-context`. Artifact
commands work remotely and through REST bindings. Test local and remote paths separately because
coverage was added incrementally.

### TLS and mutual TLS (5.7.0)

The remote client and `podman system service` support TLS and mutually authenticated TLS,
including certificate-based client authentication. `podman system connection add` can register a
TLS-protected TCP endpoint.

### TLS detail profiles (6.0.0)

TLS-capable commands can expose `--tls-details` for settings loaded from a
`containers-tls-details.yaml(5)` file.

## Go bindings

### Container binding type changes (5.5.0)

`containers.Commit()` returns `types.IDResponse` instead of the previous identically shaped type.
`containers.ExecCreate()` receives a changed embedded struct in `handlers.ExecCreateConfig`, so
assignments depending on the old embedding may fail to compile.

### Module path and artifact removal (6.0.0)

Move imports from `github.com/containers/podman/v5` to `go.podman.io/podman/v6`. Remove the
redundant `nameOrID` argument from calls to `artifacts.Remove()`.

## Inspect, list, and info output

### Expanded inspect data (5.3.0)

`podman manifest inspect` emits manifest annotations. Container inspect adds:

- `HostConfig.AutoRemoveImage`;
- `Config.ExposedPorts`;
- `Config.StartupHealthCheck`;
- `SubPath` on relevant `Mounts` entries.

### Inspection and image-store information (5.4.0)

Container inspect includes each joined network's ID. Containers created by the remote API no
longer report a spurious create command. `podman info` reports every configured image store.

### Artifact output (5.7.0)

`podman inspect` accepts artifacts. `podman artifact inspect --format` provides templates, while
artifact list formatting exposes `VirtualSize` as integer bytes and `CreatedAt` as RFC3339.

### Machine-readable changes (6.0.0)

- `podman image list --format json` adds `Repository` and `Tag`.
- `podman info` reports CDI spec directories and discovered CDI devices.
- An unset inspected `MemorySwappiness` is `nil`, not `-1`.
- `{{json .Labels}}` in container, pod, and volume list templates emits comma-separated
  `key=value` pairs rather than a JSON object.

### Free host memory (5.8.6-6.1.0)

`podman info` adds free host memory alongside used and total memory. Monitoring parsers should
accept the expanded output.

### One-element command inspection (5.8.6-6.1.0)

For a container command with one element, inspect puts that element only in `Path`; `Args` is
empty instead of duplicating the command.

## Compat API request and response contracts

### Create, info, and ping inputs (5.6.0)

Compat Container Create accepts `HostConfig.CgroupnsMode` and respects `base_hosts_file` from
containers.conf. Compat System Info adds `DefaultAddressPools`. Compat Ping reports
`Builder-Version: 1`.

### Data and deletion responses (5.6.0)

- Compat System DF removes `BuilderSize`.
- Image listing always contains `shared-size`, using `-1` when it was not requested.
- Image inspection omits `VirtualSize` for Docker API 1.44 and newer.
- Forced container deletion removes only stopped containers.
- Container list and inspect translate statuses to Docker-compatible values.

### Image inspect compatibility (5.7.0)

Compat Image Inspect no longer returns `ContainerConfig`; clients must read `Config`, matching
Docker API v1.45.

### Secret removal route (5.8.0)

Use plural `DELETE /secrets/{name}`. It replaces the incorrectly named `/secret/{name}` route.

### Compatible baseline and empty JSON (6.0.0)

The supported Docker-compatible API baseline is 1.44. Requests that take JSON accept an empty
body instead of rejecting it.

### Container list and push completion (6.0.0)

Compat container-list responses include health-check data in `Health` and add `HostConfig`.
Compat image Push ends with a JSON object containing the tag, digest, and size.

### Corrected container-create inputs (6.0.0)

API-based container creation honors volume `subpath` and the Libpod `OCIRuntime` field.

### Exec console size (5.8.6-6.1.0)

Compat and Libpod exec creation at `/containers/$CID/exec` honors `ConsoleSize` from the exec
configuration.

## Libpod resource APIs

### Multi-platform build request (5.2.0)

The Images Build endpoint accepts a comma-separated `Platform` query value such as
`linux/amd64,linux/arm64`.

### Tar Kubernetes contexts (5.3.0)

The Kubernetes YAML Play endpoint accepts a compressed context directory with content type
`application/x-tar`.

### Build host-file control (5.4.0)

Compat and Libpod Images Build accept `nohosts=true` to suppress `/etc/hosts` creation in the
image.

### Artifact routes (5.6.0)

The stable artifact API supports list, inspect, pull, remove, tar-body add/append, push, and
extract through `/libpod/artifacts/...` routes. Use the local endpoint below only for content that
already exists on the service host.

### Quadlet routes (5.7.0 and 5.8.0)

`GET /libpod/quadlets/json` lists units. The 5.8.0 API adds per-unit file and existence queries,
bulk or single installation, and bulk or single removal.

### Local artifact and image endpoints (6.0.0)

`POST /libpod/local/artifacts/add` loads an artifact directly from the service host without a tar
upload. `POST /libpod/local/images` requires an absolute `path` query parameter.

### Image Pull errors and progress (6.0.0)

The Libpod image Pull endpoint streams progress when `pullProgress=true`. A failed pull returns an
error HTTP status instead of an unconditional 200.

## Events

### Network and secret resources (5.4.0 and 5.5.0)

Events cover network creation/removal and secret creation/removal.

### Filter matching (5.7.0)

`podman events --filter label=KEY` supports key-only label matching.

### Expanded event schema (6.0.0)

Container `died` events add `OOMKilled`; artifact events cover `create`, `pull`, `push`, and
`remove`; pod and volume events include their labels as attributes.
