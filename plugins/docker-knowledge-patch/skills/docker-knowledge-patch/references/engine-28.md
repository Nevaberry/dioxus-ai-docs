# Docker Engine 28.x

Engine 28.0 released February 2025, API v1.49–v1.51.

## Networking Security Overhaul (28.0) — Potentially Breaking

Engine 28.0 significantly restructured networking and iptables rules.

### ipset kernel support required

`ip_set` and `ip_set_hash_net` kernel modules are required. This requirement was softened in 28.0.1.

### iptables restructuring

Major changes to port publishing and network isolation rules:
- Remote hosts could previously connect directly to containers on published ports — now fixed
- Neighbor hosts could connect to ports mapped on a loopback address — now fixed
- Direct routed access to unpublished container ports now blocked in `DOCKER` iptables chain

### docker-proxy incompatibility

`docker-proxy` was updated; old versions are incompatible with new `dockerd`. `rootlesskit-docker-proxy` binary was removed.

### MAC address changes

Container interfaces now use randomly-generated MAC addresses with gratuitous ARP on start. IPv6 addresses in the default bridge network are now IPAM-assigned (not MAC-derived).

### DNS resolution changes

DNS nameservers from host `resolv.conf` are now accessed from the host network namespace.

### New gateway modes

```bash
# NAT without protection from external access
docker network create --opt com.docker.network.bridge.gateway_mode=nat-unprotected mynet

# Isolated mode for internal networks
docker network create --internal --opt com.docker.network.bridge.gateway_mode=isolated mynet
```

### Gateway priority

New `gw-priority` option controls which network provides the default gateway for multi-network containers.

### Custom interface names

```bash
docker network connect --driver-opt com.docker.network.endpoint.ifname=myeth0 mynet mycontainer
```

---

## New Features (28.0)

### Image mounts

Mount an image directly inside a container:
```bash
docker run --mount type=image,source=alpine:latest,dst=/alpine myimage
docker run --mount type=image,source=tools:v1,dst=/tools,image-subpath=bin myimage
```

### Platform flags for load/save/history

```bash
docker load --platform linux/amd64 <image.tar
docker save --platform linux/arm64 myimage >arm.tar
docker history --platform linux/amd64 myimage
```

### Build cache prune filters

```bash
docker buildx prune --filter reserved-space=10GB
docker buildx prune --filter max-used-space=50GB
docker buildx prune --filter min-free-space=20GB
docker buildx prune --filter keep-bytes=5GB
```

---

## New Features (28.1)

### `docker bake` top-level alias

`docker bake` works as a top-level alias for `docker buildx bake`.

### `--use-api-socket` (experimental)

Expose Docker socket inside containers:
```bash
docker run --use-api-socket myimage
docker create --use-api-socket myimage
```

### Platform-specific image inspect

```bash
docker image inspect --platform linux/arm64 myimage
```

---

## New Features (28.2)

### CDI enabled by default

Container Device Interface is enabled by default. Discovered CDI devices shown in `docker info`.

### AMD GPU support

AMD GPUs supported via `--gpus` using CDI:
```bash
docker run --gpus all amd-workload
```

### Platform-specific image removal

```bash
docker image rm --platform linux/arm64 myimage
```

### Platform format in `docker ps`

```bash
docker ps --format '{{.Names}} {{.Platform}}'
```

### Relative parent paths in bind mounts

```bash
docker run -v ../data:/data myimage
docker run --mount type=bind,src=../data,dst=/data myimage
```

### `DOCKER_AUTH_CONFIG` credential store

`DOCKER_AUTH_CONFIG` environment variable can now be used as a credential store.

### Trusted host interfaces

```bash
docker network create --opt com.docker.network.bridge.trusted_host_interfaces=eth0 mynet
```

### `allow-direct-routing` daemon option

New daemon option to allow direct routed access to container ports.

### Other 28.2 changes

- Windows: Initial BuildKit support for Windows container images
- Schema 1 image pulling fully removed
- `fluentd-write-timeout` log option added
- API v1.50: `BridgeNfIptables`/`BridgeNfIp6tables` omitted from `GET /info`

---

## Deprecations in 28.x

- Legacy links environment variables deprecated (removal in v30)
- `KernelMemoryTCP` deprecated
- Raspberry Pi OS 32-bit (armhf) packages deprecated starting in v28
- `AllowNondistributableArtifacts*` fields removed from `GET /info` in API v1.49
- `ContainerdCommit.Expected`, `RuncCommit.Expected`, `InitCommit.Expected` removed from `GET /info` in API v1.49
- Massive Go SDK deprecation sweep (hundreds of functions marked for removal in v29)
