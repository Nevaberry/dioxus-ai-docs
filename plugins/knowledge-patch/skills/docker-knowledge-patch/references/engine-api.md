# Engine API Compatibility and Deprecations

Use this reference before generating requests, negotiating versions, decoding responses, or maintaining long-lived event and progress parsers.

## Version floors and negotiation

- API v1.44 deprecates versions older than v1.24 (Engine 25.0.0). Engine 26.0.0 removes versions below v1.24.
- For clients below API v1.44, Engine 26.0.0 preserves the earlier non-recursive behavior of read-only mounts.
- Engine 29.0 through 29.2 require daemon API v1.44 or newer. Engine 29.3 lowers the daemon minimum to v1.40.
- The v29 CLI and Go client removed compatibility and negotiation below v1.44. A raw older client can therefore reach a 29.3 daemon at versions that the current v29 client cannot negotiate.

## Image list and inspection

- API v1.44 removes `VirtualSize` from `GET /images/json` and `GET /images/{id}/json`.
- API v1.44 deprecates image-inspect `Container` and `ContainerConfig`; Engine 26.0.0 removes them from `GET /images/{name}/json`.
- When image config has no `Created`, newer APIs omit the field. Through v1.43 it remains `0001-01-01T00:00:00Z`.
- Image-search results always return `is_automated=false` starting with Engine 26.0.0. The deprecated `is-automated=true` filter matches nothing and `is-automated=false` is a no-op; `IsAutomated` and the filter were deprecated in v1.44.
- Image inspect's always-empty, non-spec `Config` fields are deprecated starting in 27.0.1: `Hostname`, `Domainname`, `AttachStdin`, `AttachStdout`, `AttachStderr`, `Tty`, `OpenStdin`, `StdinOnce`, `Image`, `NetworkDisabled`, `MacAddress`, and `StopTimeout`.
- API v1.48 adds `Manifests` for platform manifests and build attestations. On a multi-platform containerd image store it also adds image `Descriptor`, while container list and inspect add `ImageManifestDescriptor`.
- API v1.49 lets `GET /images/{name}/json` select one variant using JSON-encoded OCI `platform`; this is mutually exclusive with `manifests`.
- API v1.50 adds a JSON-encoded `platforms` array to `DELETE /images/{name}`, allowing selected platform content to be deleted without removing every variant.
- API v1.52 omits unset image `Parent`, `Comment`, `DockerVersion`, `Author`, and `Config`. It omits `GraphDriver` with the containerd backend and omits empty `OnBuild`.
- Starting in Engine 29.3, `GET /images/json?identity=1` returns manifest summaries and can include per-manifest identity information.

## Image attestations

API v1.55 adds `GET /images/{name}/attestations` for in-toto statements:

- Pass `platform` to select one image variant.
- Repeat `type` to filter by predicate-type URI.
- Pass `statement=true` to include statement bodies.
- Without `statement=true`, the endpoint returns descriptors and predicate types without reading statement blobs.

```http
GET /v1.55/images/example:latest/attestations?statement=true
```

## Container create, update, and inspect

- Container list responses include annotations starting in 27.0.1.
- Container and service create requests accept mount tmpfs options through `HostConfig.Mounts.TmpfsOptions.Options` starting in 27.0.1.
- Container create accepts `writable-cgroups=true` in `HostConfig.SecurityOpt` starting in 28.0.0:

```json
{"HostConfig":{"SecurityOpt":["writable-cgroups=true"]}}
```

- Container `StartedAt` is recorded before startup and is guaranteed to precede `FinishedAt` starting in 27.0.1.
- API v1.52 adds health-check status as `Health` in `GET /containers/json` and adds storage information to container inspection.
- Top-level `Config.MacAddress` is obsolete in v1.52 and later. Use per-endpoint settings; `POST /networks/{id}/connect` correctly applies them as of Engine 29.3.
- API v1.52 removes deprecated top-level bridge, endpoint, IP, gateway, MAC, hairpin, link-local, and secondary-address fields from container `NetworkSettings`. Read per-network values from `NetworkSettings.Networks`.
- `KernelMemoryTCP` is removed from `GET /info` and container inspection at v1.52; values sent to container update are ignored.
- API v1.52 deprecates start-time backfill that turns an empty `PortBindings` list into one empty binding. Build the desired binding explicitly before v1.53 removes the behavior.

## Live block-I/O updates

API v1.55 makes these `POST /containers/{id}/update` fields effective; older implementations ignored them:

- `BlkioWeightDevice`
- `BlkioDeviceReadBps`
- `BlkioDeviceWriteBps`
- `BlkioDeviceReadIOps`
- `BlkioDeviceWriteIOps`

Omit a field or send `null` to preserve its current rules. Send an empty array to clear all rules for that resource type. Per-device weights remain deprecated with cgroup v1.

## Network API

- API v1.44 adds `DNSNames` containing the container name, hostname, network aliases, and short ID.
- Starting with v1.45, per-network `Aliases` contains only aliases explicitly supplied at create time; it no longer automatically contains the short ID. Use `DNSNames` when all DNS identities are needed.
- On daemons supporting API v1.44, `POST /networks/create` rejects duplicate names for every request version. `CheckDuplicate` is deprecated and unnecessary.
- API v1.48 stops migrating container-wide `HostConfig.Sysctls` entries that name `eth0` into endpoint driver options. Send interface sysctls directly in endpoint driver options with the `IFNAME` placeholder.
- API v1.52 exposes per-subnet IPAM allocation statistics in network inspection.

## Swarm and service API

- Service create and update accept `OomScoreAdj` starting in 27.0.1.
- API v1.44 accepts `Seccomp` and `AppArmor` under service `ContainerSpec.Privileges`.
- When a Swarm service is updated through an API earlier than v1.44, `Healthcheck.StartInterval` is correctly ignored starting in 27.0.1.
- Service and task resources expose swap controls as `SwapBytes` and `MemorySwappiness` for list, inspect, create, and update.

## Events, progress, and content negotiation

- Image builds emit an image `create` event even when the image is untagged (since 27.0.1).
- API v1.52 declares the events endpoint as `application/x-ndjson` and omits legacy event fields `status`, `id`, and `from`.
- API v1.52 accepts RFC 7464 `application/json-seq` for `GET /events`; v1.53 also accepts `application/jsonl`. Select framing with `Accept`:

```http
GET /v1.53/events HTTP/1.1
Accept: application/json-seq
```

- Streaming clients must consume structured `errorDetail` and `progressDetail`. Legacy `error` and `progress` are deprecated and can become empty or disappear (since 28.0.0).

## System information and disk usage

- `GET /info` reports the containerd socket and the namespaces used for containers and plugins starting in 27.0.1.
- API v1.44 adds `CDISpecDirs`; it is an empty list when experimental features are disabled.
- API v1.50 adds `DiscoveredDevices`, initially containing CDI `DeviceInfo` records reported by device drivers.
- Engine 29.2 adds an `NRI` section to `docker info`.
- API v1.52 adds `os_type` to `GET /containers/{id}/stats`.
- API v1.52 redesigns `GET /system/df` around `ImagesUsage`, `ContainersUsage`, `VolumesUsage`, and `BuildCacheUsage`; pass `verbose=1` for detail.
- Starting in v1.53, `/system/df` no longer returns legacy `LayersSize`, `Images`, `Containers`, `Volumes`, or `BuildCache` fields.
- `BridgeNfIptables` and `BridgeNfIp6tables` in `GET /info` are always false as of 28.0.0 and scheduled for removal in v1.49.
- Registry fields related to non-distributable artifacts are always `null` through v1.48 and scheduled for removal in v1.49.

## Build prune API

API v1.48 renames `POST /build/prune` parameter `keep-bytes` to `reserved-space` and adds `max-used-space` and `min-free-space`. Match these to the Buildx cache-policy filters described in [buildx.md](buildx.md).

## Deprecated configuration and endpoints

- Daemon `--api-cors-header` and its `daemon.json` setting were deprecated in 27.0.1 and removed in 28.0.0.
- API v1.53 deprecates `POST /grpc` and `POST /session`; do not create new dependencies on them.
- Native gRPC can now be served on the Engine API listener, but it is separate from the deprecated `/grpc` tunnel semantics.
