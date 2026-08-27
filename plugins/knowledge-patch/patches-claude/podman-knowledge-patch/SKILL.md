---
name: podman-knowledge-patch
description: Podman
version: "6.0.0"
license: MIT
metadata:
  author: Nevaberry
---


# Podman knowledge patch

Use this patch before changing Podman commands, configuration, Quadlets, machine workflows,
Kubernetes replay, networking, storage, builds, or REST clients. Treat defaults, platform support,
and machine-readable output as version-sensitive. Read the topic reference that matches the task
instead of assuming Docker behavior or older Podman behavior.

## Reference index

| Reference | Read for |
| --- | --- |
| [APIs, bindings, and observability](references/apis-bindings-and-observability.md) | Libpod and Compat endpoints, Go bindings, remote connections, inspect/list output, events, and TLS |
| [Containers and runtime](references/containers-and-runtime.md) | Create/run/update/exec, health checks, pods, signals, filters, checkpoint/restore, and runtime defaults |
| [Images, builds, and artifacts](references/images-builds-and-artifacts.md) | Builds, image operations, signing, OCI artifacts, SBOMs, and artifact APIs |
| [Kubernetes, network, and storage](references/kubernetes-network-and-storage.md) | `kube play/generate/down`, CDI, networks, volumes, secrets, host files, and storage checks |
| [Machines and platforms](references/machines-and-platforms.md) | Machine providers, VM provisioning, host mounts, Windows/macOS support, TLS trust, and machine OS management |
| [Migration and configuration](references/migration-and-configuration.md) | Upgrade prerequisites, removed stacks, unified config lookup and precedence, database migration, packaging, and security fixes |
| [Quadlet](references/quadlet.md) | Unit types, installation, discovery, drop-ins, dependencies, resource keys, and generated-service behavior |

## Breaking changes and migration hazards

### Migrate BoltDB without competing processes

Prefer a reboot so migration runs without other Podman processes. If manual migration is required,
use Podman 5.8.1 or later when persistent Quadlets exist, then stop every Podman process—including
socket-activated services and Quadlets—before running:

```console
podman system migrate --migrate-db
```

The legacy database is retained on failure. The 5.8.0 path can leave a partial SQLite database and
has no automatic recovery. Only move `db.sql` aside and retry on a fixed release when no persistent
containers, pods, or volumes need to survive.

### Remove unsupported platform and network assumptions

For Podman 6 engine deployments, require Linux kernel 5.2 or newer and migrate away from Intel
macOS hosts, Windows 10, cgroups v1, iptables networking, CNI, and `slirp4netns`. Use cgroups v2,
nftables, Netavark, and Pasta as applicable. The removed slirp-only global
`--network-cmd-path` option has no replacement requirement under Pasta.

A Podman 6 engine does not regain cgroups v1 support merely because remote-client operation on a
cgroups v1 Linux host was restored in 6.0.2; that fix is client-side only.

### Apply unified configuration precedence exactly

For each supported main configuration file, load only the highest-priority existing file: user,
then administrator, then vendor. An empty user file still suppresses lower-tier main files.

Then process drop-ins from all applicable tiers:

1. Let later locations mask earlier same-named files.
2. Sort the surviving files globally by filename.
3. Let lexicographically later filenames win, regardless of tier.

Use `CONTAINERS_<NAME>_CONF` to select one file and disable normal loading. Use
`CONTAINERS_<NAME>_CONF_OVERRIDE` to load one final override after the normal stack. Restart the
Podman service after configuration changes; in-process configuration reload is gone.

### Update configuration and Go consumers

- Stop using `/etc/containers/containers.rootless.conf`; use rootful/rootless drop-ins.
- Replace storage `rootless_storage_path` with `graphroot` in a rootless drop-in.
- Replace registries.conf V1 and `REGISTRIES_CONFIG_PATH` with V2 and
  `CONTAINERS_REGISTRIES_CONF`.
- Cache `DefaultStoreOptions()` in storage-library code; configuration reload/update/save APIs
  were removed.
- Move Go imports from `github.com/containers/podman/v5` to `go.podman.io/podman/v6`.
- Remove the redundant `nameOrID` argument from binding calls to `artifacts.Remove()`.

### Recheck changed defaults and output contracts

- Network isolation is enabled by default.
- `podman volume prune` removes only unused anonymous volumes; use `--all` for the former scope and
  `--dry-run` to preview.
- Do not combine `volume prune --all` with label filters before the release that fixes filter loss.
- `podman commit` pauses its container by default.
- Repeated volume-list filters and supported repeated `label!=` filters combine with AND.
- An unset inspected `MemorySwappiness` is `nil`, not `-1`.
- `{{json .Labels}}` in container, pod, and volume list templates produces comma-separated
  `key=value` text, not a JSON object.
- Pod start/stop prints the caller-supplied identifier rather than necessarily printing a full ID.
- SIGTERM no longer implies a successful Podman process exit.
- A one-element inspected command can leave `Args` empty because the command appears only in
  `Path`.

## Security-sensitive maintenance guidance

- Use 5.6.1 or later when replaying untrusted Kubernetes YAML; crafted `ConfigMap` or `Secret`
  symlinks could otherwise overwrite host content. The same maintenance release restores startup
  with runc 1.3.
- Use 5.6.2 or later for non-root Containerfile builds that use cache mounts.
- Use a release containing the runc arbitrary-write/procfs fix before exposing workloads to the
  affected container-escape and denial-of-service path.
- Use 5.8.2 or later for machine images on Windows Hyper-V, `unless-stopped` reboot behavior, and
  corrected Quadlet entrypoint and health-command parsing.
- Use 5.8.3 or later for untrusted Git or tar build contexts, and 5.8.4 or later when malformed image
  environment entries may be present.
- Use 5.8.6 or later for `podman quadlet install --replace`; older behavior can leave trailing
  destination content.
- Use 6.0.1 or later when testing experimental Pasta/Pesto rootless bridge forwarding so restarts
  and reloads do not leave stale forwarding rules.

## High-value current patterns

### Manage Quadlets locally

Use `podman quadlet install`, `list`, `print`, and `rm` for current-user units. A bundled install
file may contain several units; separate sections with `---` and start each with
`# FileName=<name>`.

```ini
# FileName=app.container
[Container]
Image=docker.io/library/alpine:latest
---
# FileName=data.volume
[Volume]
```

Installed units and auxiliary files use subdirectories rather than a tracked `.app` file. For
scripts, `podman quadlet list --format ...` suppresses headings, supports status filtering, and can
report a container unit's pod. Quadlet management began as local-only; check transport coverage
before using it through a remote client or API.

### Update and run containers with explicit controls

```console
podman update --ulimit nofile=4096:8192 web
podman update --no-healthcheck web
podman exec --no-session web true
podman wait --return-on-first ctr1 ctr2
podman run --userns=keep-id:size=65536 IMAGE
podman run --mount type=volume,src=myvol,dst=/mnt,nocreate IMAGE
```

Update environment with `podman update --env` and `--unsetenv`; target the newest container with
`--latest`. Bound health logs with the destination, maximum-count, and maximum-size options. A
timed-out health check receives SIGTERM and then SIGKILL after a delay. Use `--gpus` for supported
AMD GPU devices as well as other supported devices, and use `--log-opt label=...` only with the
journald log driver.

### Use volume, network, and Kubernetes controls deliberately

```console
podman volume prune --dry-run
podman run --net mynet:ip=10.0.0.2,ip=10.0.0.3 IMAGE
podman network create --route 10.20.30.0/24,blackhole isolated
podman kube play app.yaml worker.yaml
```

Use `subpath=` to expose one volume subdirectory and `nocreate` to require an existing named
volume. Use `podman volume create --uid ... --gid ...` to set initial ownership. Repeat `ip=` to
assign several addresses on one network; attachment order follows the command line. Use
`--no-pod-prefix` carefully because a pod and container with the same resulting name conflict.

### Consume stable OCI artifacts

Manage artifacts with `podman artifact add`, `inspect`, `ls`, `pull`, `push`, and `rm`. Mount them
with `type=artifact`; `name=` selects the exposed filename. A single-blob artifact mounts as a file
when the destination does not already exist in the image.

```console
podman run --mount type=artifact,src=example.com/acme/data:latest,dst=/data,name=payload IMAGE
```

Use `.artifact` Quadlet units for systemd-managed artifacts. Distinguish service-local artifact
loading from tar-body remote uploads when selecting an API endpoint.

### Address machines by provider

Treat the configured machine provider as the default for newly created VMs only. Every machine
command can address VMs from every provider. Select the provider at creation and suppress
default-connection prompts explicitly in automation:

```console
podman machine init --provider libkrun --update-connection=false dev
```

Recreate existing Linux machine VMs after adopting systemd-based host volume mounts. Use
`--import-native-ca` when a VM must trust host CAs. Remember that `machine os update` is unavailable
with WSL, and that WSL host port forwarding depends on `force_port_listen`.

## Verification checklist

- Read the relevant topic reference before editing commands or parsing output.
- Confirm the installed maintenance release before relying on a security or compatibility fix.
- Preview destructive storage work where supported and stop background services before database
  migration.
- Restart the system service after configuration changes.
- Test remote and local clients separately when transport coverage differs.
- Recheck scripts that parse identifiers, labels, statuses, image fields, or Compat responses.
