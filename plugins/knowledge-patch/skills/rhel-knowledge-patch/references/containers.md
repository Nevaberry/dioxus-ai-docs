# Containers

Consult this reference for Podman runtime and network migration, managed state, rootless behavior, Quadlet, OCI artifacts and signatures, image builds, and container-image deprecations.

## Contents

- [Runtime, networking, state, and restart behavior](#runtime-networking-state-and-restart-behavior)
- [Quadlet, artifacts, and signatures](#quadlet-artifacts-and-signatures)
- [Build layers and container-image lifecycle](#build-layers-and-container-image-lifecycle)

## Runtime, networking, state, and restart behavior

### Podman 5 runtime and network migration (10.0)

RHEL 10 uses cgroup v2, `crun`, Netavark, and rootless `pasta`; cgroup v1, `runc`, CNI, and the supported `slirp4netns` path are gone or deprecated. Upgrade existing containers with `podman system migrate --new-runtime=crun` and replace `network_backend="cni"` with `netavark`.

### Podman state, Quadlet, and health controls (10.0)

Connection and farm state moves from read-only `containers.conf` entries to Podman-managed `podman.connections.json`, `storage.conf` moves to `/usr/share/containers`, and `podman pod inspect` always returns a JSON array. Pod Quadlets are supported, `podman update` persists runtime changes, `[engine] healthcheck_events=false` suppresses health events, and `--compat-volumes` restores the old rule that only `ADD` and `COPY` changes survive under Dockerfile `VOLUME` paths.

### Podman and minimal-image deprecations (10.0)

The CNI stack is no longer supported and `slirp4netns` is deprecated, in favor of Netavark and pasta respectively; connection/farm state in `containers.conf` is legacy read-only input. `ubi10-minimal` omits `tzdata`, so migrations must run `microdnf install tzdata` rather than `reinstall`.

### Rootless and restart behavior (10.2)

Rootless Podman gains inheritable system-wide defaults while preserving per-user overrides and existing configurations. Containers with `unless-stopped` restart after reboot only when `podman-restart.service` is enabled.


## Quadlet, artifacts, and signatures

### Container artifacts, compression, and signatures (10.0)

Buildah can create and annotate OCI artifact manifests in image indexes, and `podman artifact` is a Technology Preview CLI for artifacts. Container tools use Sigstore rather than simple GPG signatures, while `zstd:chunked` push/pull is supported and changed-chunk-only partial pulls require the Technology Preview `enable_partial_images="true"`.

### Podman 5.6 and Quadlet management (10.1)

Podman adds `quadlet install|list|print|rm`, remote volume import/export, volume `--uid`/`--gid`, `secret create --ignore`, `pull --policy`, and `update --latest`. Quadlet gains memory/reload, retry, pod hostname, and `UpheldBy` keys; artifact APIs, `artifact extract`, `--mount type=artifact`, and artifact append/file-type controls make OCI artifacts usable from scripts and containers.

### Sequoia container signatures (10.2)

Podman and Skopeo use Sequoia-PGP rather than GnuPG for OpenPGP verification, while GnuPG signing remains available. `--sign-by-sq-fingerprint` selects Sequoia keys and enables modern composite schemes such as ML-DSA-87+Ed448.

### Podman 5.8 and Quadlet interfaces (10.2)

`podman quadlet install` accepts multiple documents separated by `---` when each starts with `# FileName=NAME`, and `.container` units add `AppArmor` plus `Entrypoint=""` clearing. New controls include `podman system migrate --migrate-db` for explicit BoltDB-to-SQLite migration ahead of Podman 6, `podman update --ulimit`, `podman exec --no-session`, and REST endpoints to install, remove, inspect, and test Quadlets.


## Build layers and container-image lifecycle

### Reproducible builds and linked layers (10.1)

Buildah's source-date-epoch and rewrite-timestamp controls improve, but do not guarantee, reproducibility. Containerfile `ADD` and `COPY` accept `--link` to place new content in an independent layer.

### Container-image deprecations (10.1)

The `nodejs-18`, `nodejs-18-minimal`, and `gcc-toolset-13-toolchain` images are deprecated, and `podman-tests` moves from AppStream to CRB. Use the Node.js 22 images for supported Node 18 replacements.

