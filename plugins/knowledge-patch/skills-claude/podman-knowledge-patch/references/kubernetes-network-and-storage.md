# Kubernetes, network, and storage

## Kubernetes YAML workflows

### Workload kinds and round trips

`podman kube generate` and `podman kube play` support Kubernetes Jobs (since 5.3.0). Generated YAML
preserves pod and container user-namespace configuration, and `kube play` understands Kubernetes
image volumes.

PID limits round-trip through
`io.podman.annotation.pids-limit/$containername`, and generated YAML correctly represents
volume-mount subpaths (since 5.5.0).

`podman generate kube` emits container health checks as Kubernetes `livenessProbe` definitions
(5.8.6-6.1.0).

### Multiple files and naming

`podman kube play` and `podman kube down` accept multiple YAML files in one invocation, as do
Quadlet `.kube` units (since 5.7.0):

```console
podman kube play app.yaml worker.yaml
podman kube down app.yaml worker.yaml
```

`kube play --no-pod-prefix` disables the prefix on generated container names. Avoid a resulting
pod/container name collision because creation will fail.

### CPU, memory, devices, and signals

`kube play` supports CDI devices (since 5.4.0); Compat Container Create honors CDI devices too.
Add CDI search paths with the global `--cdi-spec-dir` option (since 5.5.0).

Per-container CPU and NUMA placement use annotations, while `lifecycle.stopSignal` supplies the
stop signal (since 5.6.0):

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

### Treat untrusted YAML as hostile

Podman 5.6.1 fixes CVE-2025-9566, where crafted symlinks in `ConfigMap` or `Secret` volumes could
overwrite host content during `kube play`. Require that maintenance release or newer before
processing untrusted YAML.

## Network creation and attachment

### Bridges and host-side interface behavior

`podman network create --opt mode=unmanaged` adopts an existing host bridge without changing it
(since 5.4.0). On bridge attachments, the per-container `--network` option accepts
`host_interface_name` to select the interface name outside the container. Podman passes a
container hostname to Netavark so DHCP requests include it.

Network isolation is enabled by default (6.0.0). Explicitly configure communication that depended
on the earlier non-isolated default.

### Addresses, routes, order, and aliases

Repeat `ip=` in one `--net` attachment to assign several static addresses (6.0.0):

```console
podman run --net mynet:ip=10.0.0.2,ip=10.0.0.3 IMAGE
```

When a container joins several networks, Podman configures them in command-line order. For
`--net=host`, `host.containers.internal` resolves to `127.0.0.1`, not a public host address.

With Netavark 2.0 or newer, `podman network create --route` accepts `blackhole`, `unreachable`, and
`prohibit` route types (6.0.0):

```console
podman network create --route 10.20.30.0/24,blackhole isolated
```

`containers.conf` field `default_host_ips` selects the host address used for port forwarding when
the command omits one.

### Pasta and Pesto forwarding

Pasta maps a guest address for `host.containers.internal` by default, allowing containers to reach
the host through that name (since 5.3.0).

Experimental `rootless_port_forwarder="pasta"` makes rootless bridge networks use Pesto while
preserving the client's original source address (6.0.0); `rootlessport` remains the default. Use
6.0.1 or later because the original implementation could leave forwarding rules after container
restarts or network reloads. Pesto forwarding supports IPv6 as well as IPv4
(5.8.6-6.1.0).

On WSL, `containers.conf` field `force_port_listen` must be enabled to forward ports from the
Windows host. New WSL machines set it automatically (5.8.6-6.1.0):

```toml
[network]
force_port_listen = true
```

### Idempotent cleanup and DNS behavior

`podman network rm --ignore` succeeds when a named network does not exist
(5.8.6-6.1.0):

```console
podman network rm --ignore NETWORK
```

With Netavark 1.15 or newer, non-default networks no longer receive the `dns.podman` search domain,
although names in that domain still resolve (since 5.5.0). Stopping an unused Quadlet `.network`
unit deletes its network.

## Volumes and mounts

### Subpaths, creation, and ownership

Volume mounts for `podman run`, `create`, and `volume create` accept `subpath=` to expose one
directory within the volume (since 5.4.0):

```console
podman run --mount type=volume,source=data,target=/data,subpath=logs IMAGE
```

Use `nocreate` to require an existing named volume instead of creating one implicitly (6.0.0).
Use `podman volume create --uid` and `--gid` to set ownership at creation (since 5.6.0).

`podman volume rename` renames an eligible volume (5.8.6-6.1.0). Driver-backed volumes and volumes
currently used by a container cannot be renamed.

### Import and export

Volume import/export is available through the remote client (since 5.6.0). `podman volume export`
refuses to write an export to standard output when stdout is attached to a TTY, preventing binary
output from being sent to an interactive terminal.

### Pruning semantics

`podman volume prune` removes only unused anonymous volumes by default (6.0.0). Pass `--all` for
the former scope, and preview with `--dry-run`:

```console
podman volume prune --dry-run
podman volume prune --all
```

Repeated volume-list filters combine with logical AND. Before the 6.1 fix, `volume prune --all`
could discard a label filter and prune every eligible volume; do not rely on that combination on
earlier releases. The corrected form is:

```console
podman volume prune --all --filter label=foo
```

## Secrets, host files, and storage health

`podman secret create --ignore` makes repeated creation idempotent (since 5.6.0). With
`podman secret create NAME -`, a user can type a secret directly at an interactive terminal rather
than piping it (since 5.8.0):

```console
podman secret create db-password -
```

`podman system check` inspects local container storage for corruption and can correct detected
damage where possible (since 5.2.0). `--quick` skips layer-digest verification (since 5.6.0), so
run the full check when digest integrity is required.

Parent directories above Podman's root and runroot do not all need world-execute permission
(since 5.2.0); do not weaken private ancestor permissions merely to enable storage access.
