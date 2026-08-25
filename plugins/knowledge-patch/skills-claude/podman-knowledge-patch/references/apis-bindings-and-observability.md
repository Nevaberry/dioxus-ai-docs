# APIs, bindings, and observability

## Remote connections and transport coverage

### TLS and connection URLs

Remote clients and `podman system service` support TLS and mutual TLS, including certificate-based
client authentication (since 5.7.0). Register protected TCP endpoints with
`podman system connection add`. TCP connection URLs retain and use an HTTP path prefix rather than
discarding it (since 5.3.0).

Commands that establish TLS connections can expose `--tls-details` for loading custom tuning from
a `containers-tls-details.yaml(5)` profile (6.0.0).

On Windows, machine VMs expose a Unix socket on the host filesystem that forwards API traffic into
the VM (since 5.3.0).

### Features that differ between local and remote clients

The remote client supports volume import/export, `podman build --build-context`, artifact commands,
and artifact REST bindings (since 5.6.0). Early `podman quadlet install`, `list`, `print`, and `rm`
commands were deliberately local-only; do not infer remote coverage from local CLI availability.

## API baselines and request handling

### Compat baseline and empty JSON bodies

The Docker-compatible API baseline is 1.44 (since 6.0.0). Endpoints that accept JSON also accept an
empty request body rather than rejecting it.

### Build and Kubernetes request bodies

- The Images Build API `Platform` query parameter accepts comma-separated platforms such as
  `linux/amd64,linux/arm64`, enabling one multi-platform request (since 5.2.0).
- Compat and Libpod Images Build accept `nohosts=true` to suppress `/etc/hosts` creation during a
  build (since 5.4.0).
- The Kubernetes YAML Play API accepts compressed context directories with content type
  `application/x-tar` (since 5.3.0).

### Local artifact, image, and pull endpoints

`POST /libpod/local/artifacts/add` loads an artifact from the service host instead of receiving a
tar archive (since 6.0.0). `POST /libpod/local/images` requires an absolute `path` query parameter.

The Libpod image Pull endpoint streams progress when `pullProgress=true` and returns an error HTTP
status on pull failure rather than always returning 200.

## Container, image, and secret API contracts

### Go binding source compatibility

In the REST Go bindings, `containers.Commit()` returns `types.IDResponse`, replacing the previous
identically shaped type (since 5.5.0). `containers.ExecCreate()` also takes a
`handlers.ExecCreateConfig` whose embedded struct differs from the earlier definition; update code
that relied on assignment through the old embedding.

For the v6 Go module, import `go.podman.io/podman/v6`. The artifact remove binding no longer takes a
redundant `nameOrID` argument (6.0.0).

### Compat create and exec inputs

Compat Container Create accepts `HostConfig.CgroupnsMode` and honors `base_hosts_file` from
`containers.conf` (since 5.6.0). Container creation also honors a volume `subpath` and the Libpod
`OCIRuntime` field (6.0.0).

Compat and Libpod exec-session creation at `/containers/$CID/exec` honors `ConsoleSize`
(5.8.6-6.1.0).

### Compat response shape changes

- System Info adds `DefaultAddressPools`, and Ping reports `Builder-Version: 1` (since 5.6.0).
- System DF removes `BuilderSize`; image lists always include `shared-size`, using `-1` when it was
  not requested; image inspect omits `VirtualSize` at Docker API 1.44 and newer (since 5.6.0).
- Forced container deletion removes only stopped containers, and container list/inspect status
  strings are translated to Docker-compatible values (since 5.6.0).
- Compat Image Inspect no longer returns `ContainerConfig`; read `Config`, matching Docker API 1.45
  behavior (since 5.7.0).
- Compat container-list entries include health-check data in `Health` and include `HostConfig`
  (6.0.0).
- Compat image Push ends with a JSON object containing the pushed tag, digest, and size (6.0.0).

### Secret and Quadlet routes

The Compat secret-removal route is plural: `DELETE /secrets/{name}`. It replaces the incorrectly
named `/secret/{name}` path (since 5.8.0).

The Libpod API exposes Quadlet discovery and management:

- `GET /libpod/quadlets/json` lists units (since 5.7.0).
- `GET /libpod/quadlets/{name}/file` returns a unit file and
  `GET /libpod/quadlets/{name}/exists` checks existence (since 5.8.0).
- `POST /libpod/quadlets` installs one or more units.
- `DELETE /libpod/quadlets` removes one or more units, while
  `DELETE /libpod/quadlets/{name}` removes one.

## Inspection and machine-readable output

### Inspect fields

Manifest inspection includes annotations (since 5.3.0). Container inspection adds
`HostConfig.AutoRemoveImage`, `Config.ExposedPorts`, `Config.StartupHealthCheck`, and `SubPath` in
applicable `Mounts` entries. Environment-variable secrets are omitted from inspect output rather
than disclosed.

Container inspection includes each joined network's ID, and remote-API-created containers no
longer report a synthetic create command (since 5.4.0). For a one-element container command,
inspect can put that element only in `Path`; parsers must accept an empty `Args`
(5.8.6-6.1.0).

### List and info output

- `podman image list --format json` adds `Repository` and `Tag` (6.0.0).
- An unset inspected `MemorySwappiness` is `nil`, not `-1` (6.0.0).
- `{{json .Labels}}` for container, pod, and volume lists emits comma-separated `key=value` text,
  not a JSON object (6.0.0).
- `podman info` reports every configured image store rather than only one (since 5.4.0).
- `podman info` reports CDI spec directories and discovered CDI devices (6.0.0).
- `podman info` adds free host memory alongside used and total memory (5.8.6-6.1.0).

## Events and operational visibility

Network create/remove events are emitted (since 5.4.0), and secret create/remove events are
emitted (since 5.5.0). Event consumers can use a key-only `label=KEY` filter (since 5.7.0).

Container `died` events add `OOMKilled`; artifact events cover create, pull, push, and remove; pod
and volume events include labels as attributes (6.0.0).

Quadlet generator errors are written to standard error as well as `/dev/kmsg`, allowing tools such
as `systemd-analyze --generators verify` to display them (5.8.6-6.1.0).
