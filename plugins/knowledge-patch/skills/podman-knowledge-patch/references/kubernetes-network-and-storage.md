# Kubernetes, network, and storage

Use this reference for Kubernetes YAML replay and generation, CDI devices, network behavior,
volume semantics, secrets, host-file generation, and local storage integrity.

## Kubernetes YAML workflows

### Jobs, namespaces, and image volumes

Since 5.3.0, `podman kube generate` and `podman kube play` can generate and run Kubernetes Job
YAML. Generated YAML preserves pod and container user-namespace configuration for later replay,
and `kube play` understands Kubernetes image volumes.

### Volume subpaths and PID limits

Since 5.5.0, generated Kubernetes YAML correctly represents volume mounts that use subpaths.
Generate and replay per-container PID limits with this annotation:

```text
io.podman.annotation.pids-limit/$containername
```

### CPU and memory placement

Since 5.6.0, `podman kube play` accepts per-container CPU-set and memory-node annotations and
honors `lifecycle.stopSignal`:

- `io.podman.annotations.cpuset/$ctrname` selects CPUs;
- `io.podman.annotations.memory-nodes/$ctrname` selects NUMA memory nodes.

```yaml
metadata:
  annotations:
    io.podman.annotations.cpuset/web: "0-3"
    io.podman.annotations.memory-nodes/web: "0"
spec:
  containers:
    - name: web
      lifecycle:
        stopSignal: SIGTERM
```

The PID-limit annotation uses singular `annotation`; the CPU and memory keys use plural
`annotations`. Preserve the exact spellings.

### CDI devices

Since 5.4.0, `podman kube play` accepts Container Device Interface devices. The Compat Container
Create API also honors CDI requests, allowing clients such as Compose front ends to request GPUs
and other CDI-described devices.

Since 5.5.0, add global CDI specification search paths with `--cdi-spec-dir`. Since 6.0.0,
`podman info` reports both CDI specification directories and discovered CDI devices.

### Multiple YAML files and naming

Since 5.7.0, `podman kube play` and `podman kube down` accept several YAML files in one command;
Quadlet `.kube` units can also reference several files:

```console
podman kube play app.yaml worker.yaml
podman kube down app.yaml worker.yaml
```

`podman kube play --no-pod-prefix` suppresses pod-name prefixes on container names. Creation can
fail when the resulting pod and container names collide.

### Play API build contexts

Since 5.3.0, the Kubernetes YAML Play API accepts a compressed context directory with content
type `application/x-tar`.

### Untrusted YAML

Use Podman 5.6.1 or later when processing untrusted YAML. CVE-2025-9566 allowed crafted symlinks
inside `ConfigMap` or `Secret` volumes to overwrite host content.

## Volume mounts and lifecycle

### Subpaths

Since 5.4.0, volume mounts for `podman run`, `podman create`, and `podman volume create` accept
`subpath=` to expose only a directory within a volume:

```console
podman run --mount type=volume,source=data,target=/data,subpath=logs IMAGE
```

Container creation through the 6.0.0 API also honors volume `subpath`.

### Require existing named volumes

Since 6.0.0, add `nocreate` to a container or pod volume mount to fail rather than implicitly
create a missing named volume:

```console
podman run --mount type=volume,src=myvol,dst=/mnt,nocreate IMAGE
```

### Ownership at creation

Since 5.6.0, `podman volume create --uid` and `--gid` set volume ownership when the volume is
created.

### Mount defaults and tmpfs access time

Since 5.6.0:

- tmpfs mounts accept `noatime`;
- `--mount` defaults to `type=volume` when `type=` is omitted.

```console
podman run --tmpfs /run:noatime IMAGE
podman run --mount source=data,destination=/data IMAGE
```

### Export safety and remote support

Since 5.6.0, `podman volume export` refuses to write an export to standard output when stdout is
attached to a TTY. The remote client supports both `podman volume import` and
`podman volume export`.

### Pruning and filter conjunction

Since 6.0.0, `podman volume prune` removes only unused anonymous volumes. Pass `--all` for the
former scope or `--dry-run` to preview:

```console
podman volume prune --dry-run
podman volume prune --all
```

Multiple `podman volume list` filters combine with logical AND. Repeated `label!=` filters also
combine with AND on commands that support them.

## Secrets

### Idempotent creation

Since 5.6.0, `podman secret create --ignore` makes repeated creation succeed when the secret
already exists.

### Interactive input

Since 5.8.0, `podman secret create NAME -` can read a secret typed directly into a terminal as
well as piped standard input:

```console
podman secret create db-password -
```

Secret creation and removal have appeared in the event stream since 5.5.0. Environment-variable
secrets are omitted from container inspection output.

## Hostname and host-file handling

### Several aliases for one address

Since 5.3.0, `podman create`, `podman run`, and `podman pod create` accept semicolon-separated
hostnames in one `--add-host` entry:

```console
podman run --add-host 'test1;test2:192.168.1.1' IMAGE
```

### Select or suppress generated files

Since 5.4.0, those same create commands accept:

- `--hosts-file` to select the base content for `/etc/hosts`;
- `--no-hostname` to prevent creation of `/etc/hostname`.

```console
podman run --hosts-file /etc/containers/custom-hosts --no-hostname IMAGE
```

The Compat and Libpod Images Build APIs also accept boolean `nohosts` since 5.4.0; use
`nohosts=true` to suppress `/etc/hosts` creation during a build.

### DHCP hostnames

Since 5.4.0, Podman passes the container hostname to Netavark for inclusion in DHCP requests.

## Host reachability and DNS

### Pasta guest-to-host mapping

Since 5.3.0, Podman enables Pasta's `--map-guest-addr` by default and uses it for
`host.containers.internal`, allowing a container to reach the host through that name.

### Host-network alias

Since 6.0.0, `host.containers.internal` resolves to `127.0.0.1` inside `--net=host` containers,
not to a public host address.

### Non-default network search domains

With Netavark 1.15 or newer and Podman 5.5.0 or newer, non-default networks no longer receive the
`dns.podman` search domain. Names ending in that domain still resolve.

## Bridge networks and interfaces

### Adopt an existing bridge

Since 5.4.0, create an unmanaged network over an existing host bridge without Podman altering the
bridge:

```console
podman network create --opt mode=unmanaged NAME
```

For bridge networks, per-container `--network` options also accept `host_interface_name` to set
the interface name outside the container.

### Network isolation default

Since 6.0.0, network isolation is enabled by default. Explicitly model communication that relied
on the former non-isolated behavior.

### Several static addresses and default binding address

Since 6.0.0, repeat `ip=` in one network attachment to give a container several static addresses:

```console
podman run --net mynet:ip=10.0.0.2,ip=10.0.0.3 IMAGE
```

Set `default_host_ips` in `containers.conf` to choose the host address for port forwarding when a
command does not specify one.

### Deterministic attachment order

Since 6.0.0, Podman configures several joined networks in command-line order.

## Routes and rootless forwarding

### Typed routes

With Netavark 2.0 or newer and Podman 6.0.0, `podman network create --route` accepts `blackhole`,
`unreachable`, and `prohibit` route types:

```console
podman network create --route 10.20.30.0/24,blackhole isolated
```

### Experimental Pasta/Pesto bridge forwarding

Set this in `containers.conf` to make rootless bridge networks use Pasta's Pesto forwarding and
preserve the original client source address:

```toml
rootless_port_forwarder="pasta"
```

`rootlessport` remains the default. Use 6.0.1 or later for this experimental mode; 6.0.0 can
leave forwarding rules behind after container restarts or network reloads.

## Storage integrity and reset behavior

### Full and quick checks

Since 5.2.0, `podman system check` inspects local container storage for corruption and can repair
detected damage where possible:

```console
podman system check
```

Since 5.6.0, `podman system check --quick` skips layer-digest verification. Run the full check
when digest validation is required.

### Private root and runroot ancestors

Since 5.2.0, ancestor directories of Podman's root and runroot do not all need world-executable
permissions. Do not relax private ancestor permissions merely to make storage accessible.

### System reset socket preservation

Since 5.5.0, `podman system reset` preserves the user's `podman.sock`.
