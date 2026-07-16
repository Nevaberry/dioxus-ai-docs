# Containers and runtime

Use this reference for container lifecycle commands, live updates, health checks, pods, user
namespaces, runtime defaults, filtering, logging, and checkpoint/restore behavior.

## Create and run behavior

### Privileged device mappings

Since 5.2.0, `podman create` and `podman run` apply explicit `--device` mappings even when
`--privileged` is also set. Do not assume privileged mode causes the mapping to be ignored.

### Sized `keep-id` namespaces

Since 5.4.0, `podman run`, `podman create`, and `podman pod create` accept `size` with
`keep-id` user namespaces:

```console
podman run --userns=keep-id:size=65536 IMAGE
```

### Explicit user-namespace paths

Podman 5.7.0 restores `--userns=ns:/path` for `podman run` and `podman create` when using runc
1.1.11 or newer.

### Resource-limit inheritance

Since 5.3.0, Podman does not explicitly reapply its default rlimits. A container can retain a
higher inherited limit instead of being lowered to Podman's default.

### GPU selection

Since 6.0.0, `--gpus` on `podman create` and `podman run` supports AMD GPUs as well as previously
supported devices.

### Pod infrastructure root filesystem

Since 5.5.0, pod infra and service containers do not use a pause image by default. Their root
filesystem contains only `catatonit`.

### Default masks

Since 5.5.0, containers mask these paths by default:

- `/proc/interrupts`;
- `/sys/devices/system/cpu/$CPU/thermal_throttle`.

Since 5.6.0, `--security-opt unmask=` accepts a comma-separated path list.

## Live container updates

### Health checks

Since 5.4.0, `podman update` can add, change, disable, or remove an existing container's health
check with options such as `--health-cmd` and `--no-healthcheck`. Resource limits remain unchanged
unless the update explicitly modifies them.

```console
podman update --no-healthcheck CONTAINER
```

Since 5.5.0, inherited image health-check settings can be overridden without also providing
`--health-cmd`.

### Environment

Since 5.5.0, update environment variables in place with `podman update --env` and
`--unsetenv`.

### Target the newest container

Since 5.6.0, `podman update --latest` targets the most recently created container where that
selection is appropriate.

### Ulimits

Since 5.8.0, update an existing container's ulimits without recreation:

```console
podman update --ulimit nofile=4096:8192 web
```

## Health-check execution and logs

### Retention controls

Since 5.3.0, `podman create` and `podman run` accept:

- `--health-log-destination` to select health-log storage;
- `--health-max-log-count` to cap retained entries;
- `--health-max-log-size` to cap entry size.

### Interrupted and timed-out checks

- Since 5.5.0, a check interrupted because its container stopped has status `stopped`.
- Since 5.6.0, a check that exceeds its timeout receives SIGTERM, followed by SIGKILL after a
  delay.

## Exec, wait, and signal handling

### Exec target files

Since 5.5.0, `podman exec --cidfile` reads the target container ID from a file.

### Untracked exec sessions

Since 5.8.0, use `--no-session` to skip exec-session tracking and reduce startup overhead when
session tracking is unnecessary:

```console
podman exec --no-session web true
```

### Wait for the first match

Since 5.7.0, `podman wait --return-on-first` returns when any selected container meets the wait
condition instead of waiting for all selected containers:

```console
podman wait --return-on-first ctr1 ctr2
```

### Signal behavior

- Since 5.3.0, Podman does not return success by default after receiving SIGTERM. Do not interpret
  that termination as exit code 0.
- Since 5.6.0, signal proxying for `podman run` and `podman attach` does not forward SIGSTOP.

### systemd stop timeouts

Since 5.2.0, when Podman creates a systemd cgroup it passes the container's stop timeout to
systemd. The scope therefore honors the configured timeout instead of risking a shutdown hang.

## Pod start and shutdown

### Printed identifiers

Since 5.2.0, pod start/stop output echoes the identifier supplied by the caller rather than
expanding it to a full pod ID. For example, `podman pod start b` prints `b`. Scripts must not
assume a full ID.

### Dependency-ordered shutdown

Since 5.5.0, containers in a pod stop in dependency order. The infra container stops last so
application containers retain networking while shutting down.

## Restart behavior

Since 5.8.2, containers with restart policy `unless-stopped` restart after reboot when
`podman-restart.service` is enabled.

## Checkpoint and restore

### Repeated restores with TCP connections

Since 5.7.0, `podman container restore --tcp-close` allows repeated restores of a checkpoint that
had active TCP connections.

### `--leave-running` completion

Since 6.0.0, `podman container checkpoint --leave-running` keeps the container paused until
root-filesystem and named-volume diffs finish. The container resumes and remains running after
checkpoint creation, but callers must tolerate that temporary pause.

## Container selection and filters

### Command filter

Since 5.5.0, the `command` filter is available to `pause`, `ps`, `restart`, `rm`, `start`, `stop`,
and `unpause`. It matches only the first command element, `argv[0]`.

### Ancestor substring matching

Since 5.7.0, `podman ps --filter ancestor=...` accepts substring matches instead of requiring a
complete ancestor match.

### Annotation filters

Since 6.0.0, `podman ps` and `podman container prune` accept `--filter annotation=...`.

## Logging and runtime defaults

### Configuration defaults

Since 5.7.0, `containers.conf` supports:

- `log_path`, the default log location for the `k8s-file` driver;
- `runtimes_flags`, default flags passed to OCI runtimes.

### Journald labels

Since 6.0.0, `podman run` and `podman create` accept `--log-opt label=...` with the `journald`
driver to attach extra labels to log messages. Do not use this option with another log driver.

## Container inspection caveat

Environment-variable secrets used by a container have been omitted from `podman inspect` output
since 5.3.0. Do not build automation that expects secret material there.
