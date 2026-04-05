# Docker Engine 29.x

Engine 29.0 released November 2025, API v1.52. This is the current latest major version.

## Breaking Changes

### containerd image store is now the default

Fresh installs use the containerd image store by default. Existing installations are not migrated. Not enabled when `userns-remap` is configured.

### Docker Content Trust (DCT/Notary) removed from CLI

DCT is no longer built into the Docker CLI. It is available only as a separate plugin.

### cgroup v1 deprecated

Support continues until at least May 2029, but users should migrate to cgroup v2. Deprecation warnings are shown.

### Container file descriptor limit changed

Default fd limit changed from 1048576 to 1024 (matches systemd default), via containerd v2.1.5. This can break applications expecting the previous high default.

### Minimum API version is v1.44

Docker Engine 29 requires API v1.44+ (Docker 25.0+). Older API clients will be rejected.

Note: 29.3 lowered the minimum back to v1.40 (Docker 19.03) for client connections.

### Go module renamed

`github.com/docker/docker` Go module deprecated in favor of:
- `github.com/moby/moby/client`
- `github.com/moby/moby/api`

Release tags now use `docker-` prefix.

### iptables isolation chains removed

`DOCKER-ISOLATION-STAGE-1` and `DOCKER-ISOLATION-STAGE-2` chains removed. Network isolation uses an updated model.

### Legacy links environment variables removed

Legacy links env vars no longer added automatically. To restore temporarily:
```bash
DOCKER_KEEP_DEPRECATED_LEGACY_LINKS_ENV_VARS=1
```

### Debian armhf requires ARMv7

ARMv6 devices (original Raspberry Pi) no longer supported for Debian armhf packages.

### `docker image ls` collapsed tree view by default

The image list now uses a collapsed tree view by default (previously required `--tree` flag with containerd image store).

---

## New Features (29.0)

### Experimental nftables firewall backend

```json
// daemon.json
{
  "firewall-backend": "nftables"
}
```

`docker info` reports the active firewall backend.

### Multi-platform load/save

`docker image load/save` with `--platform` now supports multiple platforms:
```bash
docker image save --platform linux/amd64,linux/arm64 myimage >multi.tar
docker image load --platform linux/amd64 <multi.tar
```

### Health field in container list API

`GET /containers/json` now includes a `Health` field with healthcheck status, without needing to inspect each container.

### Device entitlement in builder

Builder configuration supports `device` entitlement for hardware access during builds.

### Swarm memory-swap flags

`--memory-swap` and `--memory-swappiness` flags added to `docker service create/update`.

### Network prefix size specification

Request subnets by prefix size from default address pools:
```bash
docker network create --subnet 0.0.0.0/24 --subnet ::/96 mynet
```

### macvlan/IPvlan-l2 gateway behavior

No default gateway is configured unless `--gateway` is explicitly specified.

### Other 29.0 features

- Native gRPC support on daemon listening socket
- `--bind-accept-fwmark` daemon option for firewall mark bypass
- `docker run --runtime` supported on Windows
- `sd_notify` support for systemd `Type=notify-reload` service reload

---

## New Features (29.2)

### NRI (Node Resource Interface) support (experimental)

Node Resource Interface support for container resource management. Shown in `docker info`.

### Image Identity field

`docker image inspect` includes a new `Identity` field showing trusted origin information:
- Build reference
- Registry source
- Signed provenance

---

## New Features (29.3)

### `bind-create-src` mount option

Creates the source directory if it doesn't exist when using bind mounts:
```bash
docker run --mount type=bind,src=/path/new,dst=/data,bind-create-src myimage
```

### CLI plugin error hooks

CLI plugin hooks now fire on command failure. Plugins can register `error-hooks` for failure-only handling.

### Image identity query parameter

`GET /images/json` supports `identity` query parameter to filter by trusted identity/manifest summaries.

### CDI-based GPU injection

`--gpus` uses CDI-based injection for both AMD and NVIDIA GPUs:
```bash
docker run --gpus all myimage  # works for AMD and NVIDIA via CDI
```
