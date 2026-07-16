# APIs, bindings, and observability

Use this reference for remote transport, Libpod and Compat contracts, Go bindings, inspect/list
fields, event consumers, and other machine-readable interfaces.

## Remote connections and transport

### TCP path prefixes

Since 5.3.0, `podman system connection add` preserves and uses HTTP path prefixes embedded in
`tcp://` URLs.

### TLS and mutual TLS

Since 5.7.0, both the remote client and `podman system service` support TLS and mutually
authenticated TLS, including certificate-based client authentication. Register a TLS-protected
TCP endpoint with `podman system connection add`.

### TLS detail profiles

Since 6.0.0, commands that establish TLS connections can expose `--tls-details` for custom tuning
read from a `containers-tls-details.yaml(5)` file.

### Remote command coverage

Since 5.6.0, the remote client supports:

- `podman volume import` and `podman volume export`;
- `podman build --build-context`;
- artifact commands and corresponding REST bindings.

Quadlet `install`, `list`, `print`, and `rm` were local-only when introduced in 5.6.0.

## Go module and bindings

### Module path

For 6.0.0, change imports from:

```go
github.com/containers/podman/v5
```

to:

```go
go.podman.io/podman/v6
```

### Container binding changes

Since 5.5.0:

- `containers.Commit()` returns `types.IDResponse` instead of the previous identically shaped
  type;
- `containers.ExecCreate()` receives a `handlers.ExecCreateConfig` with a different embedded
  struct, so assignments relying on the old promotion/embedding can fail.

### Artifact removal signature

Podman 6.0.0 removes the redundant `nameOrID` argument from `artifacts.Remove()`.

## Compatible API baseline

Since 6.0.0, the supported Docker-compatible API baseline is 1.44. Requests that take JSON accept
an empty body instead of rejecting it.

## Container API contracts

### Corrected create inputs

Since 6.0.0, API container creation honors:

- volume `subpath`;
- the Libpod `OCIRuntime` field.

Compat Container Create has also honored CDI devices since 5.4.0. Since 5.6.0, it accepts
`HostConfig.CgroupnsMode` and respects `base_hosts_file` from `containers.conf`.

### List and inspect responses

Since 6.0.0, Compat container-list responses include health-check data in `Health` and include
`HostConfig`.

Since 5.6.0:

- forced Compat deletion removes only stopped containers;
- container list and inspect responses translate status values to Docker-compatible forms.

### Image-created container inspection

Container inspection added these fields in 5.3.0:

- `HostConfig.AutoRemoveImage`;
- `Config.ExposedPorts`;
- `Config.StartupHealthCheck`;
- `SubPath` on each applicable `Mounts` entry.

Since 5.4.0, inspection includes the ID of each joined network. Containers created through the
remote API no longer report a spurious create command.

### Secret visibility

Environment-variable secrets used by a container have been omitted from `podman inspect` since
5.3.0.

## Image and artifact API contracts

### Image pull

Since 6.0.0, the Libpod image Pull endpoint:

- streams progress when `pullProgress=true`;
- returns an error HTTP status on pull failure instead of always returning 200.

### Image push completion

Since 6.0.0, Compat Image Push ends with a JSON object containing the pushed tag, digest, and
size.

### Image inspection compatibility

- Since 5.6.0, image inspection omits `VirtualSize` for Docker API 1.44 and newer.
- Since 5.7.0, Compat Image Inspect omits `ContainerConfig`; read `Config` instead, matching Docker
  API v1.45 behavior.

### Artifact and local routes

Use the images, builds, and artifacts reference for the stable artifact routes and
`POST /libpod/local/artifacts/add`. Since 6.0.0, `POST /libpod/local/images` requires an absolute
`path` query parameter.

## Quadlet API

### List

Since 5.7.0:

```http
GET /libpod/quadlets/json
```

lists Quadlets.

### File, existence, install, and removal

Since 5.8.0, the Libpod API includes:

| Operation | Route |
| --- | --- |
| Read a unit file | `GET /libpod/quadlets/{name}/file` |
| Test existence | `GET /libpod/quadlets/{name}/exists` |
| Install one or more units | `POST /libpod/quadlets` |
| Remove one or more units | `DELETE /libpod/quadlets` |
| Remove one named unit | `DELETE /libpod/quadlets/{name}` |

## Compat secrets route

Since 5.8.0, remove a secret through the plural route:

```http
DELETE /secrets/{name}
```

It replaces the incorrectly named `/secret/{name}` route.

## System and storage API fields

### Compat system information

Since 5.6.0:

- Compat System Info includes `DefaultAddressPools`;
- Compat Ping reports `Builder-Version: 1`.

### Compat disk-usage and image-list responses

Since 5.6.0:

- Compat System DF omits `BuilderSize`;
- image listing always includes `shared-size`, using `-1` when the value was not requested.

## Inspection and machine-readable CLI output

### Manifest and image output

- `podman manifest inspect` has emitted manifest annotations since 5.3.0.
- `podman image list --format json` includes `Repository` and `Tag` since 6.0.0.

### `podman info`

- Since 5.4.0, `podman info` reports every configured image store rather than only one.
- Since 6.0.0, it reports CDI specification directories and discovered CDI devices.
- It no longer reports one storage.conf path because unified configuration can source several
  files.

### Inspection values and label templates

Since 6.0.0:

- an unset `MemorySwappiness` is `nil`, not `-1`;
- `{{json .Labels}}` in container, pod, and volume list templates emits comma-separated
  `key=value` pairs rather than a JSON object.

## Events

### Resource coverage

- Network create/remove events have been emitted since 5.4.0.
- Secret create/remove events have been emitted since 5.5.0.
- Since 6.0.0, artifact events cover `create`, `pull`, `push`, and `remove`.

### Expanded attributes

Since 6.0.0:

- container `died` events include `OOMKilled`;
- pod and volume events include their labels as attributes.

### Label filter matching

Since 5.7.0, `podman events --filter label=KEY` supports a key-only label match; a value is not
required.
