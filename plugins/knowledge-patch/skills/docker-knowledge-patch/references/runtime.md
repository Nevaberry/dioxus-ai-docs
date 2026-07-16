# Engine Runtime, Daemon, and Platform

Use this reference for daemon installation and configuration, container lifecycle, mounts, resource controls, rootless mode, Windows, and platform support.

## Daemon startup, validation, and reload

- Configuration reload is atomic (since 25.0.0): if any proposed setting is invalid, none of the reload changes take effect.
- The daemon validates `userland-proxy-path` during startup rather than waiting for the first published port (since 25.0.0).
- A proxy executable whose name begins with `docker-` is also searched for in `/usr/local/libexec` and `/usr/libexec` (since 27.0.1).
- Engine 28.0.0 requires the updated `docker-proxy`; an older binary is incompatible. `rootlesskit-docker-proxy` was removed from builds and packages.
- `dockerd --validate` now checks host requirements as well as daemon configuration:

```console
dockerd --validate --config-file /etc/docker/daemon.json
```

- Reloads now emit systemd `RELOADING` notifications and support systemd 253's `Type=notify-reload` protocol.
- The Engine API socket can serve gRPC natively, so a gRPC integration does not need a second listener. API v1.53 nevertheless deprecates the older `POST /grpc` tunnel; see [engine-api.md](engine-api.md).

## Installation and image-store behavior

- The containerd image store is the default for fresh Engine 29 installations. Upgrades retain their existing store. Daemons using `userns-remap` cannot temporarily use the containerd store.
- On Windows, Engine 28.0.0 can manage containerd as a daemon child instead of requiring a system-installed containerd.
- The `devicemapper` storage driver, Debian Upstart integration, daemon `--oom-score-adjust`, and `logentries` logging driver were removed in 25.0.0.
- External graph-driver plugins and daemon/API CORS configuration were removed in 28.0.0. The in-tree image-spec package was replaced by `github.com/moby/docker-image-spec`.

## Container lifecycle and OCI behavior

- After a daemon restart, live-restored `--rm` containers are no longer forcibly removed, and every restored container receives another health-check start period (since 25.0.0).
- `Healthcheck.StartInterval` now defaults to the documented five seconds (since 27.0.1).
- Container `StartedAt` is recorded before startup and therefore precedes `FinishedAt` (since 27.0.1).
- The deprecated OCI `prestart` hook is used only for build containers (since 28.0.0). For other containers, Engine adds network interfaces after task creation completes and before the task starts; account for that order in hooks that inspect the network namespace.
- Restarting a container no longer overwrites a user-edited `/etc/resolv.conf` starting with Engine 29.1.
- Legacy-link environment variables are no longer injected automatically. Set `DOCKER_KEEP_DEPRECATED_LEGACY_LINKS_ENV_VARS=1` only as temporary compatibility; that switch is also scheduled for removal.

## Filesystems and mounts

- Layer extraction fails rather than silently dropping extended attributes when the target filesystem cannot store them (since 25.0.0). Dockerfile `ADD` has separate behavior for archives; see [buildkit-dockerfile.md](buildkit-dockerfile.md).
- Containers can mount content from an image with `type=image` (since 28.0.0). `image-subpath` selects a path inside the source image:

```console
docker run --mount type=image,source=alpine:latest,target=/mnt,image-subpath=etc alpine:latest
```

- `--mount` accepts `bind-create-src` when Docker should create a missing bind source:

```console
docker run --mount type=bind,src=/host/data,dst=/data,bind-create-src IMAGE
```

- The deprecated `bind-nonrecursive` spelling is removed. Engine 29 treats it as an error; use `bind-recursive=disabled`:

```console
docker run --mount type=bind,src=/host/data,dst=/data,bind-recursive=disabled IMAGE
```

- Anonymous volume mounts can now be read-only; a named volume source is no longer required:

```console
docker run --mount type=volume,dst=/data,readonly IMAGE
```

## Resource limits, cgroups, and security

- Bundled containerd 2.1.5 adopts systemd's default `LimitNOFILE`, changing a container's default `ulimit -n` from `1048576` to `1024`. Set a per-container `--ulimit` or a daemon default:

```json
{
  "default-ulimits": {
    "nofile": { "Name": "nofile", "Soft": 1048576, "Hard": 1048576 }
  }
}
```

- A custom seccomp profile supplied with `--privileged` is honored instead of ignored (since 27.0.1).
- API `HostConfig.SecurityOpt` accepts `writable-cgroups=true`, allowing writable cgroup mounts without full privileged mode (since 28.0.0):

```json
{"HostConfig":{"SecurityOpt":["writable-cgroups=true"]}}
```

- Cgroup v1 is deprecated. Support is promised only until at least May 2029; migrate deployments to cgroup v2.
- `--kernel-memory` is hidden and warns because neither the daemon nor the kernel supports it.

## Swarm resources and security

- Service create and update accept `OomScoreAdj` through the API (since 27.0.1). `docker service create` and Compose stack deployment expose it starting with 28.0.0.
- Swarm service create and update now accept memory-swap and memory-swappiness controls. Service and task resources expose `SwapBytes` and `MemorySwappiness` in list, inspect, create, and update operations.
- API v1.44 service create and update requests accept `Seccomp` and `AppArmor` under `ContainerSpec.Privileges`.
- `Healthcheck.StartInterval` is correctly ignored when a Swarm service is updated through API versions earlier than v1.44 (since 27.0.1).

## NRI, CDI, and device access

- Engine 29.2 adds experimental NRI support; inspect its state in the `NRI` section of `docker info`.
- Engine 29.2 uses CDI for NVIDIA `--gpus` requests when possible, and 29.3 uses CDI injection for AMD GPUs.
- Rootless CDI discovery searches `$XDG_CONFIG_HOME/cdi` and `$XDG_RUNTIME_DIR/cdi`.
- API v1.44 exposes configured CDI directories as `CDISpecDirs`; v1.50 adds discovered devices. See [engine-api.md](engine-api.md).
- Engine builder configuration adds a `device` entitlement for builds that need device access.

## Rootless mode and user namespaces

- Rootless containers can opt into host access at `10.0.2.2` by setting `DOCKERD_ROOTLESS_ROOTLESSKIT_DISABLE_HOST_LOOPBACK=false` (since 26.0.0). Host loopback remains disabled by default.
- With `--userns-remap`, the containerd image store separates images into distinct containerd namespaces and publishes metrics (since 26.0.0). Engine 29's fresh-install default still excludes `userns-remap` temporarily.
- If `slirp4netns` is unavailable, `dockerd-rootless.sh` now tries pasta from passt instead of failing immediately.

## Remote daemon security

- The CLI and daemon deprecate unauthenticated TCP connections starting in 26.0.0.
- On Engine 27 and later, a non-local remote TCP listener combined with explicit `--tls=false` or `--tlsverify=false`—including equivalent `daemon.json` settings—prevents daemon startup. `tcp://localhost` is exempt. Use verified TLS, a Unix socket, or SSH.

## Logging

- The `fluentd-async-connect` logging option was removed in 28.0.0.
- The fluentd driver accepts `fluentd-read-timeout` to bound waits for Fluentd acknowledgement reads.

## Windows behavior

- Windows containers' internal DNS forwards to external DNS by default (since 27.0.1), allowing tools such as `nslookup` to resolve external names. The temporary daemon switch below disables it but is planned for removal:

```json
{"features":{"windows-dns-proxy":false}}
```

- A CLI can use BuildKit when a Windows daemon advertises support (since 27.0.1).
- Windows now supports `docker run --runtime <name>`.
- The Windows overlay driver accepts `--dns`.
- Install Windows CLI plugins under `%ProgramFiles%\Docker\cli-plugins`; the old `%PROGRAMDATA%\Docker\cli-plugins` compatibility location is no longer searched.

## Host and package compatibility

- Debian `armhf` packages now require ARMv7 and do not run on ARMv6.
- Official Raspbian packages were removed. Use Debian arm64 for 64-bit systems or Debian armhf for 32-bit ARMv7.
- Engine no longer loads image formats predating Docker 1.10.
- Values passed to `--tlscacert`, `--tlscert`, and `--tlskey` are no longer specially unquoted.
