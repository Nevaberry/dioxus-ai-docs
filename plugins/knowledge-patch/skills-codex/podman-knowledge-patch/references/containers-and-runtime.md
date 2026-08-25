# Containers and runtime

## Creation and runtime defaults

### Devices in privileged containers (5.2.0)

`podman create` and `podman run` apply `--device` even with `--privileged`; requested device
mappings are no longer ignored.

### Systemd stop timeouts (5.2.0)

When Podman creates a systemd cgroup, it passes the container stop timeout to systemd so the scope
honors the configured timeout and does not hang during shutdown.

### Multiple hostnames for one address (5.3.0)

`podman create`, `run`, and `pod create` accept semicolon-separated hostnames in `--add-host`.

```console
podman run --add-host 'test1;test2:192.168.1.1' IMAGE
```

### Rlimit inheritance (5.3.0)

Podman no longer reapplies default rlimits explicitly, avoiding a reduction when an inherited
limit is higher than the Podman default.

### Sized keep-id namespaces (5.4.0)

`podman run`, `create`, and `pod create` accept `size` with `--userns=keep-id`.

```console
podman run --userns=keep-id:size=65536 IMAGE
```

### Minimal pod service containers and masks (5.5.0)

Pod infra and service containers no longer use a pause image by default; their root filesystem
contains only `catatonit`. Containers mask `/proc/interrupts` and
`/sys/devices/system/cpu/$CPU/thermal_throttle` by default.

### Restored namespace path mode (5.7.0)

`podman run` and `podman create` support `--userns=ns:/path` with runc 1.1.11 and newer.

### AMD GPUs (6.0.0)

`--gpus` on `podman create` and `podman run` supports AMD GPUs as well as previously supported
devices.

## Updating and selecting containers

### Health checks and resource updates (5.4.0)

`podman update` can add, change, disable, or remove health checks with options such as
`--health-cmd` and `--no-healthcheck`. Resource limits remain unchanged unless explicitly updated.

```console
podman update --no-healthcheck CONTAINER
```

### Command filtering and live environment (5.5.0)

The `command` filter works with `pause`, `ps`, `restart`, `rm`, `start`, `stop`, and `unpause`; it
matches the first command element (`argv[0]`). `podman exec --cidfile` reads its target container
ID from a file. `podman update --env` and `--unsetenv` change the live container environment.

### Latest-container updates (5.6.0)

`podman update --latest` targets the newest container.

### Live ulimit updates (5.8.0)

`podman update --ulimit` changes ulimits without recreating the container.

```console
podman update --ulimit nofile=4096:8192 web
```

## Exec, wait, checkpoint, and restore

### First-match waits (5.7.0)

`podman wait --return-on-first` returns when any selected container satisfies the condition.

```console
podman wait --return-on-first ctr1 ctr2
```

### Repeat restore with TCP state (5.7.0)

`podman container restore --tcp-close` permits repeated restores of containers checkpointed with
active TCP connections.

### Untracked exec sessions (5.8.0)

`podman exec --no-session` disables session tracking to reduce startup overhead where tracking is
unnecessary.

```console
podman exec --no-session web true
```

### Checkpoint diff completion (6.0.0)

`podman container checkpoint --leave-running` keeps the container paused until root-filesystem and
named-volume diffs finish. Account for this brief pause even though the final state is running.

## Health checks and shutdown

### Health log controls (5.3.0)

`podman create` and `podman run` add `--health-log-destination`, `--health-max-log-count`, and
`--health-max-log-size` to choose storage and bound retained health logs.

### Stopped status and pod shutdown order (5.5.0)

Health checks interrupted by container shutdown report `stopped`. Image health settings can be
overridden without also passing `--health-cmd`. Pod containers stop in dependency order, with the
infra container last so application networking remains available during shutdown.

### Timeout signaling (5.6.0)

A health check exceeding its timeout receives SIGTERM and then SIGKILL after a delay.

## Signals and command output

### Pod start and stop identifiers (5.2.0)

Pod start/stop echoes the identifier supplied by the caller instead of expanding it to a full ID.
For example, `podman pod start b` prints `b`; scripts must not assume a full ID.

### SIGTERM process status (5.3.0)

Podman no longer exits successfully by default after receiving SIGTERM. Callers must not treat
that termination as status 0.

### Signal proxy exclusions (5.6.0)

Signal proxying for `podman run` and `podman attach` no longer forwards SIGSTOP.

## Logging and filtering

### Runtime and log defaults (5.7.0)

`containers.conf` adds `log_path` for the default `k8s-file` log location and `runtimes_flags` for
default OCI-runtime flags.

### Docker-compatible filters (5.7.0)

`podman ps --filter ancestor=...` accepts substring ancestor matches. `podman events --filter
label=KEY` accepts key-only label matches.

### Journald message labels (6.0.0)

With the journald driver, `podman run` and `create` accept `--log-opt label=...` to attach labels
to messages. Do not use the option with other log drivers.

### Annotation filters (6.0.0)

`podman ps` and `podman container prune` accept `--filter annotation=...`.

## Mount and host-file controls

### Host-file selection (5.4.0)

`podman run`, `create`, and `pod create` add `--hosts-file` to choose base `/etc/hosts` content and
`--no-hostname` to prevent `/etc/hostname` creation.

```console
podman run --hosts-file /etc/containers/custom-hosts --no-hostname IMAGE
```

### Mount defaults and security unmasking (5.6.0)

Tmpfs mounts accept `noatime`. `--mount` again defaults to a volume when `type=` is omitted.
`--security-opt unmask=` accepts comma-separated paths.

```console
podman run --tmpfs /run:noatime IMAGE
podman run --mount source=data,destination=/data IMAGE
```

## Inspection privacy and security

### Secret omission (5.3.0)

Environment-variable secrets used by a container are omitted from `podman inspect`.

### Container-escape floor (5.7.0)

Use 5.7.0 or later to address CVE-2025-52881, where runc arbitrary-write gadgets and procfs write
redirects could permit container escape or denial of service.
