# Containers and runtime

## Create and run behavior

### Devices, namespaces, and mounts

`podman create` and `podman run` apply an explicitly requested `--device` even with
`--privileged`; the mapping is no longer ignored (since 5.2.0).

Bound a `keep-id` namespace with a `size` parameter (since 5.4.0):

```console
podman run --userns=keep-id:size=65536 IMAGE
```

The `--userns=ns:/path` form works with runc 1.1.11 and newer after its regression was corrected
(since 5.7.0). `--security-opt unmask=` accepts comma-separated paths, and a tmpfs mount accepts
`noatime` (since 5.6.0). When `type=` is omitted, `--mount` again defaults to a volume.

`--gpus` supports AMD GPUs as well as previously supported device types (6.0.0).

### Host-file and logging controls

`podman run`, `create`, and `pod create` accept `--hosts-file` to select base `/etc/hosts` content
and `--no-hostname` to suppress `/etc/hostname` creation (since 5.4.0). One `--add-host` mapping can
associate semicolon-separated names with an address (since 5.3.0):

```console
podman run --add-host 'test1;test2:192.168.1.1' IMAGE
```

`containers.conf` provides `log_path` as the default path for the `k8s-file` driver and
`runtimes_flags` for default OCI-runtime flags (since 5.7.0). With journald only,
`--log-opt label=...` attaches extra labels to messages (6.0.0); reject that option with other log
drivers.

### Runtime defaults and limits

Podman no longer reapplies default rlimits when an inherited limit is higher (since 5.3.0).
Containers mask `/proc/interrupts` and `/sys/devices/system/cpu/$CPU/thermal_throttle` by default
(since 5.5.0). Pod infra and service containers use a minimal root filesystem containing
`catatonit` rather than a pause image.

When Podman creates a systemd cgroup, it passes the container stop timeout to systemd so scope
shutdown honors the configured timeout (since 5.2.0).

## Live updates and selection

### Update health, resources, environment, and ulimits

`podman update` can add, change, disable, or remove health checks with controls such as
`--health-cmd` and `--no-healthcheck`; unspecified resource limits remain unchanged (since 5.4.0).
Inherited image health settings can be overridden without also supplying `--health-cmd`
(since 5.5.0).

Use `--env` and `--unsetenv` to update environment variables, and `--latest` to target the newest
container (since 5.5.0 and 5.6.0). Use `--ulimit` for live rlimit changes (since 5.8.0):

```console
podman update --ulimit nofile=4096:8192 web
```

### Filters and target selection

The `command` filter works with `pause`, `ps`, `restart`, `rm`, `start`, `stop`, and `unpause`; it
matches command element `argv[0]` (since 5.5.0). `podman exec --cidfile` reads the target container
ID from a file.

`podman ps --filter ancestor=...` accepts substring matching rather than requiring a complete
ancestor value (since 5.7.0). `podman ps` and `podman container prune` accept
`--filter annotation=...` (6.0.0).

Repeated supported `label!=` filters combine with logical AND (6.0.0). Do not write clients that
assume repeated negative filters are alternatives.

## Health checks and signals

### Health log bounds and timeout behavior

`podman create` and `run` accept `--health-log-destination`, `--health-max-log-count`, and
`--health-max-log-size` to select and bound health-log retention (since 5.3.0).

A health check interrupted because its container stopped has status `stopped` (since 5.5.0). A
check that exceeds its timeout receives SIGTERM, then SIGKILL after a delay (since 5.6.0).

### Signal and process-exit behavior

Signal proxying for `podman run` and `attach` does not forward SIGSTOP (since 5.6.0). Podman no
longer treats its own SIGTERM receipt as a successful process exit by default (since 5.3.0), so
supervisors must not assume status 0.

## Exec, wait, checkpoint, and restore

`podman exec --no-session` disables exec-session tracking when its overhead and session record are
unnecessary (since 5.8.0):

```console
podman exec --no-session web true
```

`podman wait --return-on-first` returns when any selected container meets the condition instead of
waiting for all targets (since 5.7.0). `podman container restore --tcp-close` permits repeated
restores of checkpoints that had active TCP connections.

During `podman container checkpoint --leave-running`, the container remains paused until root
filesystem and named-volume diffs finish, then continues running (6.0.0). Account for this brief
pause in availability-sensitive workflows.

## Pods, start/stop, and restart behavior

Pod start and stop output echoes the identifier supplied by the caller instead of expanding it to
a full ID (since 5.2.0). Scripts should accept a name, partial ID, or other supplied identifier.

Containers in a pod stop in dependency order, with the infra container last so application
containers retain networking during shutdown (since 5.5.0).

From 5.8.2, a container with `unless-stopped` restarts after reboot when
`podman-restart.service` is enabled. Do not rely on the corrected behavior in earlier releases.

## Commit, deletion, and recovery

`podman commit` pauses the source container by default for a consistent snapshot (6.0.0). Use
`--pause=false` only when concurrent changes and a potentially inconsistent result are acceptable.

Forced deletion through the Compat path removes only stopped containers (since 5.6.0).

Podman 5.7.1 restores rootless user-namespace recreation when both Conmon and the rootless pause
process die unexpectedly. Require that maintenance level where this recovery path matters.
