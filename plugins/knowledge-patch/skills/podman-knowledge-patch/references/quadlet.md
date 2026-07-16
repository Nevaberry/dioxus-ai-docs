# Quadlet

Use this reference for source-unit discovery, installation, generated systemd behavior, and keys
specific to container, pod, image, build, artifact, network, volume, and Kubernetes units.

## Install and manage source units

### Local management commands

Podman 5.6.0 added:

```console
podman quadlet install
podman quadlet list
podman quadlet print
podman quadlet rm
```

Installation targets the current user. These commands were not available through the remote
client when introduced.

### Bundled installation files

Since 5.8.0, one input file can install several units. Separate units with `---` on its own line
and begin each section with `# FileName=<name>`:

```ini
# FileName=app.container
[Container]
Image=docker.io/library/alpine:latest
---
# FileName=data.volume
[Volume]
```

### Podman 6 installation layout

Since 6.0.0, `podman quadlet install` no longer tracks an installation and its auxiliary files in
a `.app` file. It places them in subdirectories. Update manual cleanup and management tools for
the new layout.

### Scriptable listing

Since 6.0.0, `podman quadlet list`:

- accepts `--noheading`;
- applies no-heading mode automatically with `--format`;
- reports a container unit's pod in the `Pod` field;
- accepts `--filter status=...`.

## Discover source units and drop-ins

### Runtime system units

Since 5.3.0, Quadlet reads `/run/containers/systemd`, enabling transient system-level units in
addition to persistent unit directories.

### Packaged user units

Since 6.0.0, Quadlet also searches:

- `/usr/share/containers/systemd/users`;
- `/usr/share/containers/systemd/users/${UID}`.

Distributions can use these paths for system-wide or per-UID user Quadlets.

### Broader drop-in lookup

Since 5.2.0, Quadlet searches top-level type drop-ins such as `container.d` and `pod.d`, plus
truncated unit-name drop-ins such as `unit-.container.d`.

## Generated service names and dependencies

### Common service controls

Since 5.3.0, all supported Quadlet file types accept:

- `ServiceName=` to choose the generated systemd service name;
- `DefaultDependencies=` to opt out of the implicit network-online dependency.

### Network-online ordering

Generated `.image` units have depended on `network-online.target` since 5.2.0. For rootless user
units, 5.3.0 replaced the ineffective user-session `network-online.target` wait with
`podman-user-wait-network-online.service`. Use `DefaultDependencies=` when the implicit dependency
is undesirable.

### Quadlet-aware dependency translation

Since 5.5.0, dependency values naming Quadlet source units are translated to their generated
systemd names, so declarations such as this are valid:

```ini
[Unit]
Wants=my.container
```

Quadlet also supports `UpheldBy=` in `[Install]`, the counterpart to systemd's `Upholds=`.

### Service-setting compatibility warnings

Since 5.6.0, generation warns about `[Service]` settings that can conflict with Quadlet's model,
including `User=`, `Group=`, and `DynamicUser=`.

## Container units

### Build and image composition

`.build` units have existed since 5.2.0, allowing systemd-managed image builds that feed Quadlet
containers. Since 5.3.0, a `.container` unit can mount an image managed by an `.image` unit using
`Mount=type=image` with the `.image` target.

### Pod and network composition

Since 5.3.0:

- `PublishPort=` in `.container` and `.pod` files accepts variables;
- `StartWithPod=` starts a container with its referenced pod;
- `Network=` in a `.container` file can name another `.container` file to share that container's
  network namespace.

### Logging, stopping, aliases, and memory

Container keys include:

| Key | Behavior |
| --- | --- |
| `LogOpt=` | Add container logging options (since 5.2.0) |
| `StopSignal=` | Select the container stop signal (since 5.2.0) |
| `NetworkAlias=` | Add a network alias; also accepted by `.pod` units (since 5.2.0) |
| `Memory=` | Set the memory limit (since 5.5.0) |
| `ReloadCmd=` | Select the command run on systemd reload (since 5.5.0) |
| `ReloadSignal=` | Select the reload signal (since 5.5.0) |
| `HttpProxy=` | Control automatic host proxy forwarding (since 5.7.0) |
| `AppArmor=` | Select an AppArmor profile (since 5.8.0) |

```ini
[Container]
LogOpt=max-size=10mb
StopSignal=SIGTERM
NetworkAlias=web
AppArmor=my-profile
```

### Host environment imports

Since 5.6.0, a value-less `Environment=NAME` imports that environment variable from the host when
the container starts:

```ini
[Container]
Environment=REGISTRY_AUTH_FILE
```

### Entrypoint and health-command parsing

Since 5.8.2, `Entrypoint=""` clears the image entrypoint and `HealthCmd=` accepts double quotes in
the command.

### Anonymous volumes

Since 6.0.0, a `.container` unit can declare an anonymous volume by using `Mount=` without a
source.

## Pod units

Pod-specific additions include:

| Key | Behavior |
| --- | --- |
| `ShmSize=` | Set pod shared-memory size (since 5.4.0) |
| `HostName=` | Set the pod hostname (since 5.5.0) |
| `Label=` | Add pod labels (since 5.6.0) |
| `ExitPolicy=` | Set pod exit policy (since 5.6.0) |
| `StopTimeout=` | Set the stop timeout (since 5.7.0) |

```ini
[Pod]
ShmSize=1g
```

The infra container created for a Quadlet pod has used the pod-derived `-infra` suffix since
5.3.0, such as `web-infra`. Do not hard-code an older infra naming convention in tooling.

## Image and build units

### Image tags and pull policy

Since 5.3.0, repeat `ImageTag=` in an `.image` file to assign several tags to the managed image.
Since 5.6.0, `.image` units accept `Policy=`.

### Pull retry controls

Since 5.5.0, `.container`, `.image`, and `.build` units accept `Retry=` and `RetryDelay=` for
failed image pulls.

### Build-unit lifecycle

Since 5.3.0, generated `.build` units no longer set `RemainAfterExit=yes` by default. The unit's
systemd state after its build command exits therefore differs from earlier behavior.

### Build inputs

Since 5.7.0, `.build` units accept `BuildArg=` and `IgnoreFile=`.

## Artifact units

Podman 5.7.0 added the `.artifact` unit type for systemd-managed OCI artifacts. Use it alongside
container, image, build, pod, network, and volume resources. See the image and artifact reference
for artifact CLI, mount, and API semantics.

## Network and volume units

### Network inputs and lifecycle

- `.network` units accept `InterfaceName=` since 5.6.0.
- Stopping a `.network` unit deletes its network when no containers are using it since 5.5.0.
- Volume and network dependencies can be templated since 5.7.0.

### Volume ownership and options

Since 6.0.0, `.volume` units accept `UID=`, `GID=`, and generic `Options=` keys.

## Kubernetes units

Since 5.7.0, a `.kube` unit can reference multiple YAML files. Keep naming collision behavior and
the other multi-file replay details in mind; see the Kubernetes, network, and storage reference.

## Parsing rules

Since 5.4.0, `:` is not a Quadlet comment marker. Use systemd-compatible `#` or `;`. A colon that
previously appeared to begin a comment is parsed as unit content.
