# Engine Runtime, Daemon, and Platform

## Daemon startup, reload, and process model

### Transactional reload and early validation

Since 25.0.0, a failed daemon configuration reload is atomic: none of the new
settings apply if any reload step fails. An invalid `userland-proxy-path` is
also rejected at daemon startup rather than on the first published port.

Engine 29 extends `dockerd --validate` to check host requirements as well as
configuration. Engine 29.3 implements systemd 253 `Type=notify-reload` with
synchronous `RELOADING`, `READY`, and `STOPPING` notifications. Validate first,
then let systemd's completion notification delimit a reload.

### Live restore

Since 25.0.0, live-restored `--rm` containers survive an Engine restart instead
of being forcibly deleted. They also begin a new health-check start period.
Automation must not infer either removal or immediate health failure after a
live-restore restart.

### Containerd layouts and installation state

Windows Engine 28.0.0 can manage containerd as a daemon child rather than
requiring a separately installed system service. Fresh Engine 29 installations
default to the containerd image store; upgrades preserve their existing store,
and `userns-remap` prevents use of that store. Detect the store rather than
inferring it from the Engine version.

Engine 29.7.0 adds an experimental mode that embeds containerd inside the
daemon process. Monitoring and process supervision must account for the chosen
layout.

### Proxy compatibility

Engine 28.0.0 requires its matching `docker-proxy`; older proxy binaries are
incompatible. `rootlesskit-docker-proxy` is removed from the distribution.

### OpenTelemetry

Engine 25.0.0 adds daemon OpenTelemetry tracing. Configure it when daemon
activity needs to join an existing OpenTelemetry trace pipeline.

### Containerd store metrics

Since 26.0.0, the containerd image store exposes Prometheus metrics. Include
that backend in Prometheus collection and alerting instead of assuming only the
classic store contributes daemon image metrics.

## Resource controls and host integration

### File-descriptor defaults

Engine 29's bundled static containerd 2.1.5 follows systemd's default
`LimitNOFILE`, reducing a container's default `nofile` limit from 1048576 to
1024. Request a limit per container or configure a daemon default:

```json
{
  "default-ulimits": {
    "nofile": {"Name": "nofile", "Soft": 1048576, "Hard": 1048576}
  }
}
```

### Writable cgroups and cgroup generations

Engine 28.0.0 accepts `writable-cgroups=true` in `HostConfig.SecurityOpt`,
providing writable cgroup mounts without full privileged mode.

```json
{"HostConfig": {"SecurityOpt": ["writable-cgroups=true"]}}
```

Cgroup v1 is deprecated in Engine 29, though support is promised until at least
May 2029. Plan host migration to cgroup v2.

### Stop and swap controls

Engine 29.7.0 adds daemon option `default-stop-timeout`, inherited by containers
that do not set their own timeout. Engine 28.0.0 renamed the CLI flags on
`docker stop` and `docker restart` from `--time` to `--timeout`.

Engine 29 adds `--memory-swap` and `--memory-swappiness` to `docker service
create` and `docker service update`; service and task resources expose
`SwapBytes` and `MemorySwappiness`.

### Build-cache storage policy

Since 28.0.0, `docker buildx prune` supports `reserved-space`,
`max-used-space`, and `min-free-space` in addition to `keep-bytes`. The prune
API renames `keep-bytes` to `reserved-space` and exposes the other limits.

## Mount and filesystem behavior

### Image mounts

Engine 28.0.0 introduces `type=image` mounts and `image-subpath`. The mount type
graduates from experimental in Engine 29.7.0.

```console
docker run --rm --mount type=image,source=alpine:latest,target=/mnt,image-subpath=etc alpine ls /mnt
```

### Volume and bind subpaths

Engine 26.0.0 adds `VolumeOptions.Subpath`, exposed as `volume-subpath`. Engine
28.0.0 extends it to Swarm services.

```console
docker run --mount type=volume,src=data,dst=/mnt,volume-subpath=logs IMAGE
```

Engine 29.2 allows anonymous read-only volumes. Engine 29.3 adds
`bind-create-src` and removes `bind-nonrecursive`.

### Extended attributes

Since 25.0.0, unpacking an image layer onto a filesystem that cannot store its
extended attributes fails rather than silently losing them. Separately, since
26.0.0 Dockerfile `ADD` archive extraction tolerates an xattr-incapable
destination rather than failing with `lsetxattr ... operation not supported`.
Test the exact extraction path; these behaviors address different operations.

## Container lifecycle and security

### MAC persistence repair

Engine 26.0.0 stops restoring generated MAC addresses across restart while
preserving explicitly configured values. Re-create containers created by
25.0.0 that may have duplicate MACs. Also re-create 25.0.0/25.0.1 containers
with configured MACs if 25.0.2 started them with generated addresses.

### Seccomp with privileged containers

Since 27.0.1, an explicitly supplied custom seccomp profile remains active
with `--privileged`; it is no longer silently ignored.

```console
docker run --privileged --security-opt seccomp=profile.json IMAGE
```

### Health and timestamps

Engine 27.0.1 corrects the default health-check `StartInterval` to five seconds.
Swarm updates through APIs older than v1.44 still ignore that field. Container
`StartedAt` is recorded before startup and therefore precedes `FinishedAt`.

### OCI hook ordering

In 28.0.0, the deprecated OCI `prestart` hook remains only for build
containers. For other containers Engine creates the task, attaches network
interfaces to its namespace, then starts it. Hooks depending on the previous
network/task order must be migrated.

## Rootless and devices

### Rootless host loopback

Since 26.0.0, rootless containers can reach the host at `10.0.2.2` when
`DOCKERD_ROOTLESS_ROOTLESSKIT_DISABLE_HOST_LOOPBACK=false`; the default remains
`true`.

```console
export DOCKERD_ROOTLESS_ROOTLESSKIT_DISABLE_HOST_LOOPBACK=false
```

### NRI, CDI, and networking fallback

Engine 29.2 adds experimental NRI and reports it in `docker info`. NVIDIA GPU
requests use CDI when possible; Engine 29.3 adds AMD CDI handling, and builder
configuration accepts the `device` entitlement. Rootless mode searches
`$XDG_CONFIG_HOME/cdi` and `$XDG_RUNTIME_DIR/cdi`, and falls back to pasta when
slirp4netns is unavailable.

## Logging

Engine 25.0.0 removes the `logentries` driver. Engine 28.0.0 removes Fluentd
option `fluentd-async-connect`. Engine 29 adds `fluentd-read-timeout` so a
daemon can bound its wait for Fluentd acknowledgements.

## Windows and platform support

### Windows behavior

Engine 27.0.1 makes the Windows container DNS resolver forward to external DNS
by default and permits BuildKit when the daemon advertises support. The
temporary `"windows-dns-proxy": false` escape hatch is removed in 28.0.0.

Engine 29 supports `docker run --runtime` for Windows containers and `--dns` on
the Windows overlay driver. The CLI stops discovering plugins under
`%PROGRAMDATA%\Docker\cli-plugins`; use `%ProgramFiles%\Docker\cli-plugins`.

### ARM packages

Engine 29 Debian `armhf` packages require ARMv7, official 32-bit Raspbian
packages are removed, and ARMv6 is unsupported by those packages.

## Removed and inert daemon features

- Engine 25.0.0 removes daemon option `--oom-score-adjust`.
- Engine 27.0.1 deprecates experimental GraphDriver plugins and API CORS.
- Engine 28.0.0 removes external graph-driver plugins and the daemon API CORS
  option.
- Engine 28.0.0 makes `--allow-nondistributable-artifacts` inert and warns;
  related registry fields are `null` through API v1.48 and omitted from v1.49.
- Engine 28.0.0 removes the SCTP checksum mangle rule but temporarily accepts
  daemon environment `DOCKER_IPTABLES_SCTP_CHECKSUM=1`; Engine 29 removes the
  behavior entirely, so the switch then has no effect.
- Engine 29 hides unsupported `--kernel-memory` and deprecates `docker commit
  --pause` in favor of `--no-pause`.

## Operational checks

1. Run `dockerd --validate --config-file ...` before reload or restart.
2. Inspect the image store, containerd layout, firewall backend, cgroups, CDI,
   and resource defaults with host configuration and `docker info`.
3. Re-test hooks, health timing, logging acknowledgements, and live restore.
4. Treat fresh installs, in-place upgrades, and downgrades as different state
   transitions.
