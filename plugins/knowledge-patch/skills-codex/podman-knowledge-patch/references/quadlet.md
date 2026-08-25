# Quadlet

## Unit types and discovery

### Build units (5.2.0)

Quadlet accepts `.build` units. They build images under systemd management for use by Quadlet
containers.

### Runtime unit directory (5.3.0)

System Quadlets are also read from `/run/containers/systemd`, enabling transient units alongside
persistent unit directories.

### OCI artifact units (5.7.0)

`.artifact` units manage OCI artifacts as systemd-backed resources alongside container, image,
build, pod, network, and volume units.

### Packaged user units (6.0.0)

Quadlet searches `/usr/share/containers/systemd/users` and
`/usr/share/containers/systemd/users/${UID}` so packages can install user units globally or for a
specific UID.

## Installation and local management

### Local commands (5.6.0)

`podman quadlet install`, `list`, `print`, and `rm` manage units for the current user. In 5.6.0,
these commands are local-only and unavailable through the remote client.

```console
podman quadlet list
```

### Bundled installation (5.8.0)

One input file can install several units. Put `---` on its own line between units and begin every
section with `# FileName=<name>`.

```ini
# FileName=app.container
[Container]
Image=docker.io/library/alpine:latest
---
# FileName=data.volume
[Volume]
```

### Management API (5.8.0)

The Libpod API provides:

- `GET /libpod/quadlets/{name}/file` and `GET /libpod/quadlets/{name}/exists`;
- `POST /libpod/quadlets` to install one or more units;
- `DELETE /libpod/quadlets` to remove one or more units;
- `DELETE /libpod/quadlets/{name}` to remove one unit.

`GET /libpod/quadlets/json`, introduced in 5.7.0, lists units.

### Installation layout (6.0.0)

Installations and auxiliary files are stored in subdirectories rather than tracked in a `.app`
file. Manual tools must understand the new layout.

### Scriptable listing (6.0.0)

`podman quadlet list` adds `--noheading`, applies it automatically with `--format`, exposes a
container unit's pod through `Pod`, and accepts `--filter status=...`.

### Safe replacement (5.8.6-6.1.0)

Podman 5.8.6 fixes CVE-2026-19730. `podman quadlet install --replace` now truncates the
destination, preventing trailing content when the new file is shorter. Use 5.8.6 or later for
in-place replacement.

## Drop-ins, ordering, and generated services

### Broader drop-ins (5.2.0)

Quadlet searches top-level type drop-ins such as `container.d` and `pod.d`, plus truncated
unit-name drop-ins such as `unit-.container.d`.

### Image startup ordering (5.2.0)

Generated `.image` units depend on `network-online.target` and are ordered after the network is
online.

### Common service controls (5.3.0)

Every supported file type accepts `ServiceName` to choose the generated service name and
`DefaultDependencies` to opt out of the implicit `network-online.target` dependency.

### Rootless network ordering (5.3.0)

User units wait for usable networking with `podman-user-wait-network-online.service` instead of
the ineffective user-session `network-online.target`.

### Build-unit lifecycle (5.3.0)

Generated build units no longer set `RemainAfterExit=yes` by default, so systemd state after the
build command exits differs from older generators.

### Dependencies (5.5.0)

`UpheldBy` in `[Install]` is the counterpart of systemd's `Upholds`. Dependency values naming
Quadlet units are translated automatically, so `Wants=my.container` is valid.

### Generator diagnostics (5.8.6-6.1.0)

Generator errors are written to standard error as well as `/dev/kmsg`, allowing tools such as
`systemd-analyze --generators verify` to display them directly.

## Container and pod units

### Logging, stop signals, and network aliases (5.2.0)

`.container` units add `LogOpt=` and `StopSignal=`. Both `.container` and `.pod` units add
`NetworkAlias=`; container keys belong in `[Container]`.

```ini
[Container]
LogOpt=max-size=10mb
StopSignal=SIGTERM
NetworkAlias=web
```

### Container composition (5.3.0)

`PublishPort` accepts variables in `.container` and `.pod` units. A `.container` adds
`StartWithPod` and can share another Quadlet container's network by naming its `.container` file
in `Network`.

### Pod infra names (5.3.0)

A Quadlet pod's infra container uses the pod name with `-infra`, such as `web-infra`. Observability
tools must expect that name.

### Pod shared memory (5.4.0)

`.pod` files accept `ShmSize` in `[Pod]`.

```ini
[Pod]
ShmSize=1g
```

### Container and pull controls (5.5.0)

`.container` units add `Memory`, `ReloadCmd`, and `ReloadSignal`. `.container`, `.image`, and
`.build` units add `Retry` and `RetryDelay` for failed pulls. `.pod` units add `HostName=`.

### Inputs and compatibility warnings (5.6.0)

A value-less `Environment=NAME` in `.container` imports the host variable when the container
starts. `.pod` adds `Label=` and `ExitPolicy=`, `.image` adds `Policy=`, and `.network` adds
`InterfaceName=`. Generation warns about potentially incompatible `[Service]` settings including
`User=`, `Group=`, and `DynamicUser=`.

```ini
[Container]
Environment=REGISTRY_AUTH_FILE
```

### Expanded inputs (5.7.0)

`.container` adds `HttpProxy`, `.pod` adds `StopTimeout`, and `.build` adds `BuildArg` and
`IgnoreFile`. Volume and network dependencies can be templated.

### AppArmor profiles (5.8.0)

Use `AppArmor` in `[Container]` to select a profile.

```ini
[Container]
AppArmor=my-profile
```

### Corrected parsing and restart semantics (5.8.0)

From 5.8.2, Quadlet treats `Entrypoint=""` as clearing the image entrypoint and permits double
quotes in `HealthCmd`. With `podman-restart.service` enabled, containers using `unless-stopped`
restart after reboot.

### Volume controls (6.0.0)

`.volume` units add `UID=`, `GID=`, and generic `Options=`. A `.container` can declare an anonymous
volume by using `Mount=` without a source.

### Image-volume policy (5.8.6-6.1.0)

`.container` units accept `ImageVolume=` to control volumes declared by the image.

```ini
[Container]
ImageVolume=ignore
```

## Image and network units

### Image mounts and tags (5.3.0)

A `.container` can mount an image managed by an `.image` unit with `Mount=type=image` and the
`.image` target. Repeated `ImageTag` entries give the managed image several tags.

### Network teardown (5.5.0)

Stopping a `.network` unit deletes its network when no containers are using it.

## Syntax rules

### Comment markers (5.4.0)

Use systemd-compatible `#` or `;` comments. `:` is no longer a comment marker and is parsed as
content.
