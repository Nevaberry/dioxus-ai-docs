---
name: podman-knowledge-patch
description: Podman
license: MIT
version: 6.0.0
metadata:
  author: Nevaberry
---

# Podman knowledge patch

Use this patch before changing Podman commands, configuration, Quadlets, machine workflows,
Kubernetes replay, networking, storage, build automation, or REST clients. Treat defaults and
output contracts as version-sensitive. Read the topic reference that matches the work instead of
assuming Docker behavior or older Podman behavior.

## Reference index

| Reference | Read for |
| --- | --- |
| [APIs, bindings, and observability](references/apis-bindings-and-observability.md) | Libpod and Compat endpoints, Go bindings, remote connections, inspect/list output, events, and TLS |
| [Containers and runtime](references/containers-and-runtime.md) | Create/run/update/exec, health checks, pods, signals, filters, checkpoint/restore, devices, and runtime defaults |
| [Images, builds, and artifacts](references/images-builds-and-artifacts.md) | Builds, image operations, signing, OCI artifacts, SBOMs, and artifact APIs |
| [Kubernetes, network, and storage](references/kubernetes-network-and-storage.md) | `kube play/generate/down`, CDI, networks, volumes, secrets, host files, and storage checks |
| [Machines and platforms](references/machines-and-platforms.md) | Machine providers, VM provisioning, host mounts, Windows/macOS support, TLS trust, and machine OS management |
| [Migration and configuration](references/migration-and-configuration.md) | Upgrade prerequisites, removed stacks, unified config lookup and precedence, database migration, packaging, and security fixes |
| [Quadlet](references/quadlet.md) | Unit types, installation, discovery, drop-ins, dependencies, resource keys, and generated-service behavior |

## Breaking changes and migration hazards

### Migrate BoltDB safely

- Prefer a reboot so database migration runs without competing Podman processes.
- Use Podman 5.8.1 or later for migration when persistent Quadlets exist; the 5.8.0 path can
  leave a partial SQLite database and has no automatic recovery.
- Before `podman system migrate --migrate-db`, stop every other Podman process, including
  socket-activated services and Quadlets.
- Preserve the legacy database. Podman retains it when migration fails.
- Only move `db.sql` aside and retry on 5.8.1 or later when no persistent containers, pods, or
  volumes need to be preserved.

```console
podman system migrate --migrate-db
```

### Remove unsupported platform and network assumptions

For Podman 6 deployments, require Linux kernel 5.2 or newer and migrate away from:

- Intel macOS hosts and Windows 10;
- cgroups v1;
- iptables networking and CNI;
- `slirp4netns` and its removed global `--network-cmd-path` option.

Use cgroups v2, nftables, Netavark, and Pasta as applicable. Pair Podman 6 with Buildah 1.44.0,
Skopeo 1.23, Netavark and Aardvark 2.0.0, and containers/common configuration 0.68.0.

### Apply unified configuration precedence

Do not merge every main file. For each supported config, Podman selects only the highest-priority
existing main file: user, then administrator, then vendor. Even an empty user main file suppresses
the lower-tier main files.

Then apply drop-ins from all applicable tiers:

1. Mask earlier same-named files with later-location files.
2. Sort the survivors globally by filename.
3. Let lexicographically later filenames win, regardless of tier; a vendor `99-*.conf` can
   override a user `33-*.conf`.

Use `CONTAINERS_<NAME>_CONF` to select one file and disable normal loading. Use
`CONTAINERS_<NAME>_CONF_OVERRIDE` to load one final override after the normal stack. Restart the
Podman service process after configuration changes; in-process reload is gone.

### Update configuration and Go consumers

- Stop using `/etc/containers/containers.rootless.conf`; put root-mode customization in drop-ins.
- Replace storage `rootless_storage_path` with `graphroot` in a rootless drop-in.
- Replace registries.conf V1 and `REGISTRIES_CONFIG_PATH` with V2 and
  `CONTAINERS_REGISTRIES_CONF`.
- Cache `DefaultStoreOptions()` in storage-library code; `ReloadConfigurationFile()`,
  `UpdateStoreOptions()`, and `Save()` are removed.
- Move Go imports from `github.com/containers/podman/v5` to `go.podman.io/podman/v6`.
- Remove the redundant `nameOrID` argument from binding calls to `artifacts.Remove()`.

### Account for changed defaults and output

- Network isolation is enabled by default.
- `podman volume prune` removes only unused anonymous volumes; use `--all` for the former scope
  and `--dry-run` to preview.
- `podman commit` pauses the container by default; use `--pause=false` only when inconsistent
  concurrent changes are acceptable.
- Repeated volume-list filters and repeated supported `label!=` filters now combine with AND.
- An unset inspected `MemorySwappiness` is `nil`, not `-1`.
- `{{json .Labels}}` in container, pod, and volume list templates produces comma-separated
  `key=value` text, not a JSON object.
- Pod start/stop prints the identifier supplied by the caller, not necessarily a full ID.
- SIGTERM no longer implies a successful Podman exit.

## Security-critical patch floors

Use patched maintenance releases when the affected path is present:

| Minimum | Reason |
| --- | --- |
| 5.6.1 | Prevent crafted `ConfigMap` or `Secret` symlinks in `kube play` YAML from overwriting host content; restore runc 1.3 startup compatibility |
| 5.6.2 | Restore non-root Containerfile builds that use cache mounts |
| 5.7.0 | Address the runc arbitrary-write/procfs container-escape and denial-of-service path |
| 5.7.1 | Restore rootless user-namespace recreation after both Conmon and the pause process die |
| 5.8.1 | Avoid the Quadlet-related partial-database migration path |
| 5.8.2 | Prevent command execution from a crafted Hyper-V machine image path; fix `unless-stopped` reboot behavior and Quadlet parsing |
| 5.8.3 | Prevent malicious Git or tar build contexts from escaping `ADD`/`COPY` boundaries |
| 5.8.4 | Prevent malformed image `Env` entries from exposing host environment variables |
| 6.0.1 | Avoid stale Pasta/Pesto forwarding rules during experimental rootless bridge forwarding |

## High-value command and configuration patterns

### Manage Quadlets locally

Use `podman quadlet install`, `list`, `print`, and `rm` for current-user units. These commands were
local-only when introduced. A bundled install file may contain several units; separate sections
with `---` and start each with `# FileName=<name>`.

```ini
# FileName=app.container
[Container]
Image=docker.io/library/alpine:latest
---
# FileName=data.volume
[Volume]
```

On Podman 6, expect installed units and auxiliary files in subdirectories rather than a tracked
`.app` file. Use `podman quadlet list --format ...` for scriptable output; it suppresses headings,
can filter by status, and exposes a container unit's pod.

### Use current container controls

```console
podman update --ulimit nofile=4096:8192 web
podman update --no-healthcheck web
podman exec --no-session web true
podman wait --return-on-first ctr1 ctr2
podman run --userns=keep-id:size=65536 IMAGE
podman run --mount type=volume,src=myvol,dst=/mnt,nocreate IMAGE
```

- Update environment with `podman update --env` and `--unsetenv`; target the newest container
  with `--latest`.
- Use `--health-log-destination`, `--health-max-log-count`, and `--health-max-log-size` to bound
  health logs.
- Expect timed-out health checks to receive SIGTERM and then SIGKILL after a delay.
- Use `--gpus` for AMD GPUs as well as other supported GPU devices.
- Use `--log-opt label=...` only with the journald log driver.

### Use current volume, network, and Kubernetes features

```console
podman volume prune --dry-run
podman run --net mynet:ip=10.0.0.2,ip=10.0.0.3 IMAGE
podman network create --route 10.20.30.0/24,blackhole isolated
podman kube play app.yaml worker.yaml
```

- Use `subpath=` to mount only a volume subdirectory and `nocreate` to require an existing named
  volume.
- Use `podman volume create --uid ... --gid ...` to set ownership at creation.
- Repeat `ip=` to assign several addresses on one network; network attachment order follows the
  command line.
- Use `--no-pod-prefix` cautiously: a pod and container with the same resulting name conflict.
- Treat untrusted Kubernetes YAML as hostile and enforce the security floor above.

### Use stable OCI artifacts

Manage artifacts with `podman artifact add`, `inspect`, `ls`, `pull`, `push`, and `rm`. Mount them
with `type=artifact`; use `name=` to choose the exposed filename. A single-blob artifact mounts as
a file when the destination does not already exist in the image.

```console
podman run --mount type=artifact,src=example.com/acme/data:latest,dst=/data,name=payload IMAGE
```

Use `.artifact` Quadlet units for systemd-managed artifacts. For service-local content, use the
local artifact API; for remote uploads, use the tar-body endpoint described in the API reference.

### Work across machine providers

Treat the configured machine provider as the default for new VMs only. Every machine command can
address VMs from every provider. Select a provider at creation and suppress default-connection
prompts explicitly in automation:

```console
podman machine init --provider libkrun --update-connection=false dev
```

Recreate existing Linux machine VMs after adopting Podman 6 because systemd-based host volume
mounting is incompatible with their old mounts. Use `--import-native-ca` when the VM must trust
host CAs, and remember that `machine os update` is unavailable with WSL.

## Verification checklist

- Inspect the relevant topic reference before editing commands or parsing output.
- Confirm the installed Podman maintenance release before relying on a security or compatibility
  fix.
- Preview destructive storage work with `--dry-run` where supported and stop background services
  before database migration.
- Restart the system service after configuration changes.
- Test remote and local clients separately when a feature has transport-specific coverage.
- Recheck scripts that parse IDs, labels, statuses, image fields, or Compat API responses.
