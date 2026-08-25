# Engine Runtime, Daemon, and Platform

Use this reference for daemon configuration and lifecycle, container security
and health behavior, resource limits, logging, and platform-specific changes.

## Daemon startup, reload, and lifecycle

### Atomic daemon configuration reloads (25.0.0)

A failed daemon configuration reload no longer applies a partial set of changes;
if any reload step errors, none of the new configuration is applied.

### Early `userland-proxy-path` validation (25.0.0)

An invalid `userland-proxy-path` is rejected during daemon startup instead of
only failing later when a container with a port mapping starts.

### Proxy upgrade compatibility (28.0.0)

Engine 28's `dockerd` requires the matching updated `docker-proxy`; older proxy
binaries are incompatible. `rootlesskit-docker-proxy` is no longer used and is
removed from the distribution.

### Daemon validation and systemd reload protocol (engine-release-history)

`dockerd --validate` now checks host system requirements as well as
configuration. Engine 29.3 supports systemd 253's `Type=notify-reload` protocol
and sends synchronous `RELOADING`, `READY`, and `STOPPING` notifications.

### Default container stop timeout (29.7.0)

The daemon adds `default-stop-timeout`, which sets the stop timeout inherited by
containers that do not specify their own.

## Container lifecycle and health

### Live-restore lifecycle behavior (25.0.0)

After an Engine restart, live-restored `--rm` containers are no longer forcibly
deleted, and live-restored containers receive a new health-check start period.

### Health-check and lifecycle timing (27.0.1)

The default health-check `StartInterval` is corrected to 5 seconds. Swarm
service updates made with API versions below v1.44 ignore
`Healthcheck.StartInterval`, and container `StartedAt` is now recorded before
startup so it is guaranteed to precede `FinishedAt`.

### OCI hook and network setup order (28.0.0)

The deprecated OCI `prestart` hook remains in use only for build containers. For
other containers, Engine creates the task first, adds network interfaces to its
namespace, and then starts the task; hooks that depended on the old ordering
must adapt.

## Security and resource controls

### Seccomp profiles on privileged containers (27.0.1)

An explicitly selected custom seccomp profile is now honored together with
`--privileged`; earlier engines silently ignored that profile.

```console
docker run --privileged --security-opt seccomp=profile.json IMAGE
```

### Lower default container file-descriptor limit (engine-release-history)

With the bundled static containerd 2.1.5, the container `nofile` limit changes
from 1048576 to systemd's default of 1024. Workloads needing the former limit
must request it with `--ulimit` or a daemon default.

```json
{
  "default-ulimits": {
    "nofile": {"Name": "nofile", "Soft": 1048576, "Hard": 1048576}
  }
}
```

### Swarm swap controls (engine-release-history)

`docker service create` and `docker service update` accept `--memory-swap` and
`--memory-swappiness`; the service and task APIs expose the corresponding
`SwapBytes` and `MemorySwappiness` resource fields.

### Experimental NRI and CDI device handling (engine-release-history)

Engine 29.2 adds experimental NRI support and reports it in `docker info`. GPU
requests use CDI for NVIDIA devices when possible and, from 29.3, for AMD
devices; builder configuration also accepts the `device` entitlement. Rootless
mode searches `$XDG_CONFIG_HOME/cdi` and `$XDG_RUNTIME_DIR/cdi` and falls back to
pasta when slirp4netns is unavailable.

## Observability and logging

### Engine OpenTelemetry tracing (25.0.0)

Docker Engine now supports OpenTelemetry tracing, allowing daemon activity to
participate in an OpenTelemetry observability pipeline.

### Containerd image-store metrics (26.0.0)

The containerd image store now sends Prometheus metrics, making that backend
visible to Prometheus-based monitoring.

### Fluentd acknowledgement timeout (engine-release-history)

The Fluentd logging driver adds `fluentd-read-timeout`, allowing deployments to
bound how long the daemon waits while reading acknowledgements from Fluentd.

## Windows and containerd process layout

### Windows daemon behavior (27.0.1)

Windows containers' internal DNS resolver now forwards to external DNS servers
by default, enabling tools such as `nslookup` to resolve external names. The
temporary opt-out is `"features": {"windows-dns-proxy": false}` in
`daemon.json`; Windows daemons may also use BuildKit when they advertise support
for it.

### Windows-managed containerd (28.0.0)

On Windows, the daemon can run containerd as its own child process instead of
requiring a separately installed system containerd.

### Embedded containerd (29.7.0)

Engine can experimentally run containerd inside the daemon process instead of
as a separate managed process. This provides a new process-layout option but
remains experimental.

## Platform and packaging compatibility

### ARM packaging and cgroup v1 deprecation (engine-release-history)

Debian `armhf` packages now require ARMv7 and no longer run on ARMv6, and
official 32-bit Raspbian packages are removed. Cgroup v1 is deprecated; support
continues until at least May 2029, so hosts should migrate to cgroup v2.

## Removed and deprecated daemon or CLI behavior

### Removed daemon option and logging driver (25.0.0)

Engine 25 removes the `--oom-score-adjust` daemon option and the `logentries`
logging driver; deployments using either must remove or replace that
configuration before upgrading.

### Deprecated daemon extension points (27.0.1)

Experimental GraphDriver plugins are deprecated. The `--api-cors-header` daemon
flag and matching `daemon.json` option are also deprecated and scheduled for
removal in the next major release.

### CLI, daemon, and extension removals (28.0.0)

The Fluentd `fluentd-async-connect` option is removed, and `docker stop` and
`docker restart` rename `--time` to `--timeout`. The daemon's API CORS option,
external graph-driver plugins, and the temporary Windows `windows-dns-proxy`
feature flag are also removed.

### Removed legacy CLI and image behavior (engine-release-history)

Docker Content Trust commands are removed from the CLI and are available only
by building a separate plugin. Engine 29 also stops loading pre-Docker-1.10
images, hides the unsupported `--kernel-memory` option, and deprecates
`docker commit --pause` in favor of `--no-pause`.
