# Quadlet

## Unit types and resource composition

### Build, image, and artifact units

`.build` units build images under systemd management for later use by Quadlet containers
(since 5.2.0). Build units no longer set `RemainAfterExit=yes` by default (since 5.3.0), so their
systemd state after the build process exits differs from early behavior.

A `.container` unit can mount an image managed by an `.image` unit with `Mount=type=image` and an
`.image` target (since 5.3.0). Repeat `ImageTag` in the `.image` unit to assign several tags.

`.artifact` units manage OCI artifacts as systemd-backed resources (since 5.7.0), alongside
container, image, build, pod, network, and volume units.

### Pods, containers, and networks

`PublishPort` accepts variables in `.container` and `.pod` units (since 5.3.0). A `.container` unit
can use `StartWithPod` and can share another Quadlet container's network by naming that
`.container` file in `Network`.

The infra container of a Quadlet pod is named from the pod with an `-infra` suffix (since 5.3.0),
so observability and cleanup code should expect names such as `web-infra`.

Stopping a `.network` unit deletes its network when no containers use it (since 5.5.0).

## Discovery, installation, and listing

### Search locations and drop-ins

Quadlet reads transient system-level units from `/run/containers/systemd` (since 5.3.0). It also
searches top-level type drop-ins such as `container.d` and `pod.d`, plus truncated-name drop-ins such
as `unit-.container.d` (since 5.2.0).

Packaged user-unit lookup includes `/usr/share/containers/systemd/users` and
`/usr/share/containers/systemd/users/${UID}` (6.0.0), allowing distribution-wide and per-UID units.

### Local management commands

`podman quadlet install`, `list`, `print`, and `rm` manage current-user units (since 5.6.0). These
commands were local-only when introduced, so check transport coverage before depending on remote
operation.

`podman quadlet install` accepts a bundle containing several units (since 5.8.0). Put `---` on its
own line between sections and start every section with `# FileName=<name>`:

```ini
# FileName=app.container
[Container]
Image=docker.io/library/alpine:latest
---
# FileName=data.volume
[Volume]
```

The installation layout uses subdirectories rather than a tracked `.app` file (6.0.0). Removal and
manual tooling must understand the new layout and its auxiliary files.

`podman quadlet list --noheading` suppresses headings; `--format` does so automatically. Listing
also exposes a container unit's pod in `Pod` and supports `--filter status=...` (6.0.0).

Use 5.8.6 or later for `podman quadlet install --replace`: CVE-2026-19730 allowed a shorter
replacement to leave trailing content in the destination before the truncation fix
(5.8.6-6.1.0).

## Service generation and dependencies

### Common service controls

Every supported Quadlet type accepts `ServiceName` to choose the generated systemd service name
and `DefaultDependencies` to disable the implicit `network-online.target` dependency
(since 5.3.0).

Generated `.image` units depend on `network-online.target` (since 5.2.0). Rootless user units wait
for usable networking through `podman-user-wait-network-online.service`, not the user session's
ineffective `network-online.target` (since 5.3.0).

### Unit-to-unit dependency translation

`UpheldBy` is available in `[Install]` as systemd's counterpart to `Upholds` (since 5.5.0).
Dependency fields automatically translate values that name Quadlet units, so `Wants=my.container`
is valid. Volume and network dependencies can be templated (since 5.7.0).

### Service compatibility warnings

Generation warns about potentially incompatible `[Service]` settings such as `User=`, `Group=`,
and `DynamicUser=` (since 5.6.0). Generator errors also go to standard error in addition to
`/dev/kmsg`, so `systemd-analyze --generators verify` can display them (5.8.6-6.1.0).

Quadlet uses systemd comment syntax: `#` and `;` begin comments, but `:` does not (since 5.4.0).

## Container unit keys

### Runtime, logging, and reload controls

`.container` units accept these controls:

- `LogOpt=`, `StopSignal=`, and `NetworkAlias=` (since 5.2.0).
- `Memory=`, `ReloadCmd=`, and `ReloadSignal=` (since 5.5.0).
- `HttpProxy=` to control automatic host proxy forwarding (since 5.7.0).
- `AppArmor=` to select the AppArmor profile (since 5.8.0).

```ini
[Container]
LogOpt=max-size=10mb
StopSignal=SIGTERM
NetworkAlias=web
AppArmor=my-profile
```

A valueless `Environment=NAME` imports that host environment variable when the container starts
(since 5.6.0):

```ini
[Container]
Environment=REGISTRY_AUTH_FILE
```

From 5.8.2, `Entrypoint=""` correctly clears the image entrypoint and `HealthCmd` accepts double
quotes in its command.

### Volumes declared by units and images

A `.container` unit can declare an anonymous volume by writing `Mount=` without a source (6.0.0).
`ImageVolume=` controls how volumes declared by the container image are handled
(5.8.6-6.1.0):

```ini
[Container]
ImageVolume=ignore
```

## Pod, image, build, network, and volume keys

- `.container` and `.pod` accept `NetworkAlias=` (since 5.2.0).
- `.pod` accepts `ShmSize=` (since 5.4.0), `HostName=` (since 5.5.0), and `Label=` plus
  `ExitPolicy=` (since 5.6.0).
- `.pod` accepts `StopTimeout=` (since 5.7.0).
- `.image` accepts `Policy=` (since 5.6.0).
- `.container`, `.image`, and `.build` accept `Retry=` and `RetryDelay=` for failed image pulls
  (since 5.5.0).
- `.build` accepts `BuildArg=` and `IgnoreFile=` (since 5.7.0).
- `.network` accepts `InterfaceName=` (since 5.6.0).
- `.volume` accepts `UID=`, `GID=`, and generic `Options=` (6.0.0).

Example pod shared memory:

```ini
[Pod]
ShmSize=1g
```

## Kubernetes units

Quadlet `.kube` units accept multiple YAML files in the same workload (since 5.7.0), matching the
multi-file `podman kube play` and `kube down` commands.

## API discovery and management

Libpod exposes `GET /libpod/quadlets/json` for listing units (since 5.7.0). From 5.8.0 it also
provides file retrieval and existence checks for a named unit, bulk install and removal, and
single-unit removal. See the API reference for exact routes and request semantics.
