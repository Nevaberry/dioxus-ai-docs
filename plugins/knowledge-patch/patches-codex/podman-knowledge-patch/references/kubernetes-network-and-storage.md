# Kubernetes, network, and storage

## Kubernetes generation and replay

### Jobs and richer round-trips (5.3.0)

`podman kube generate` and `podman kube play` create and run Kubernetes Job YAML. Generated YAML
preserves pod and container user-namespace settings for replay, and `kube play` understands
Kubernetes image volumes.

### Tar contexts in the Play API (5.3.0)

The Kubernetes YAML Play API accepts compressed context directories with content type
`application/x-tar`.

### CDI devices (5.4.0)

`podman kube play` supports Container Device Interface devices. Compat Container Create also
honors CDI devices, allowing clients such as Compose to request GPUs and other CDI resources.

### PID limits and volume subpaths (5.5.0)

`kube generate` and `kube play` preserve per-container PID limits with
`io.podman.annotation.pids-limit/$containername`. Generated YAML correctly represents volume
mounts that use subpaths.

### CPU placement and stop signals (5.6.0)

`kube play` accepts per-container `io.podman.annotations.cpuset/$ctrname` and
`io.podman.annotations.memory-nodes/$ctrname`. It also honors `lifecycle.stopSignal`.

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

### Multi-file workflows and names (5.7.0)

`podman kube play` and `podman kube down` accept several YAML files in one invocation; Quadlet
`.kube` units do too. `podman kube play --no-pod-prefix` removes the pod prefix from container
names, but fails if a pod and container then have the same name.

```console
podman kube play app.yaml worker.yaml
podman kube down app.yaml worker.yaml
```

### Generated health checks (5.8.6-6.1.0)

`podman generate kube` emits a container health check as a Kubernetes `livenessProbe`.

### Untrusted YAML security floor (5.6.0)

Use 5.6.1 or later for YAML from untrusted sources. CVE-2025-9566 allowed crafted symlinks in
`ConfigMap` or `Secret` volumes processed by `kube play` to overwrite host content.

## Volumes and mounts

### Volume subpaths (5.4.0)

Volume mounts for `podman run`, `create`, and `volume create` accept `subpath=` to expose only a
directory within a volume.

```console
podman run --mount type=volume,source=data,target=/data,subpath=logs IMAGE
```

### Ownership at creation (5.6.0)

`podman volume create --uid` and `--gid` set ownership when creating a volume.

### Remote import and export (5.6.0)

The remote client supports `podman volume import` and `podman volume export`. Export refuses to
write to standard output when standard output is a TTY.

### Existing-only named volumes (6.0.0)

Container and pod volume mounts accept `nocreate`, causing creation to fail if the named volume
does not exist.

```console
podman run --mount type=volume,src=myvol,dst=/mnt,nocreate IMAGE
```

### Volume pruning scope and conjunction (6.0.0)

`podman volume prune` removes only unused anonymous volumes. Use `--all` for the former scope and
`--dry-run` to preview. Repeated `podman volume list` filters combine with logical AND, as do
repeated supported `label!=` filters.

```console
podman volume prune --all
podman volume prune --dry-run
```

### Label-safe all-volume pruning (5.8.6-6.1.0)

Podman 6.1 makes `podman volume prune --all` honor label filters. Earlier versions can discard the
filter and prune every eligible volume; do not rely on this combination before 6.1.

```console
podman volume prune --all --filter label=foo
```

### Volume renaming (5.8.6-6.1.0)

Podman 6.1 adds `podman volume rename`. A driver-backed volume or one currently used by a
container cannot be renamed.

```console
podman volume rename OLD NEW
```

## Secrets and CDI discovery

### CDI paths and secret events (5.5.0)

The global `--cdi-spec-dir` option adds CDI specification search paths. Events include secret
creation and removal.

### Idempotent secret creation (5.6.0)

`podman secret create --ignore` makes repeated creation succeed.

### Interactive secret input (5.8.0)

`podman secret create NAME -` can read directly from a terminal as well as from piped input.

```console
podman secret create db-password -
```

## Network creation and addressing

### Existing bridges and interface names (5.4.0)

`podman network create --opt mode=unmanaged` adopts an existing host bridge without changing it.
For bridge networking, per-container `--network` accepts `host_interface_name` to choose the host
interface name.

### DHCP hostnames (5.4.0)

Podman passes a container hostname to Netavark, which includes it in DHCP requests.

### Network isolation default (6.0.0)

Network isolation is enabled by default. Make previously implicit cross-network communication
explicit.

### Static addresses and host binding (6.0.0)

Repeat `ip=` within one `--net` attachment to assign several static addresses. The containers.conf
field `default_host_ips` selects the host address for port forwarding when a command omits one.

```console
podman run --net mynet:ip=10.0.0.2,ip=10.0.0.3 IMAGE
```

### Typed routes (6.0.0)

With Netavark 2.0 or newer, `podman network create --route` accepts `blackhole`, `unreachable`,
and `prohibit` route types.

```console
podman network create --route 10.20.30.0/24,blackhole isolated
```

### Host aliases and deterministic network order (6.0.0)

For `--net=host`, `host.containers.internal` resolves to `127.0.0.1`, not a public host address.
When joining several networks, Podman configures them in command-line order.

### Idempotent network removal (5.8.6-6.1.0)

`podman network rm --ignore` suppresses errors for missing networks.

```console
podman network rm --ignore NETWORK
```

## Rootless forwarding and host reachability

### Pasta host reachability (5.3.0)

Podman enables Pasta `--map-guest-addr` by default and uses it for
`host.containers.internal`, allowing containers to reach the host through that name.

### Experimental Pasta bridge forwarding (6.0.0)

Setting `rootless_port_forwarder="pasta"` makes rootless bridge networks use Pasta's Pesto
forwarder and preserves the original client source address. `rootlessport` remains the default.
Use 6.0.1 or later because 6.0.0 can leave stale rules after restart or network reload.

### IPv6 through Pesto (5.8.6-6.1.0)

Pesto-based rootless port forwarding supports IPv6 while preserving the original source address.

## Events and network lifecycle

### Network events (5.4.0)

`podman events` reports network creation and removal.

### Reset and DNS lifecycle (5.5.0)

`podman system reset` preserves the user's `podman.sock`. With Netavark 1.15 or later,
non-default networks no longer receive the `dns.podman` search domain, though names in that domain
still resolve. Stopping a Quadlet `.network` deletes the network when unused.

### Expanded labels and OOM data (6.0.0)

Container `died` events include `OOMKilled`; artifact events cover create, pull, push, and remove;
pod and volume events include labels as attributes.

## Storage integrity

### Full checks (5.2.0)

`podman system check` inspects local container storage for corruption and can repair detected
damage when possible.

```console
podman system check
```

Parent directories of Podman's root and runroot no longer all need world-execute permission, so
private ancestor permissions need not be relaxed for storage access. (5.2.0)

### Quick checks (5.6.0)

`podman system check --quick` skips layer-digest verification. Run the full check when digest
validation is required.
