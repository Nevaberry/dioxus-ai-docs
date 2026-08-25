# Engine API Compatibility and Deprecations

Use this reference when negotiating API versions, parsing Engine responses,
building API requests, or migrating deprecated endpoints and fields.

## Version negotiation and endpoint transport

### Minimum Engine API version (26.0.0)

Engine API versions older than v1.24 are removed, so clients must negotiate
v1.24 or newer.

### Engine API compatibility floor (engine-release-history)

Engine 29.0 through 29.2 requires API v1.44 or later and introduces API v1.52.
Engine 29.3 lowers the minimum again to v1.40, so clients targeting earlier 29.x
daemons must still negotiate v1.44 or newer.

### Versioned debug endpoints (28.0.0)

Daemon debug and pprof endpoints are now also reachable below
`/v<API-version>/`, so clients that consistently prefix Engine requests with a
negotiated API version can use them without switching to unversioned paths.

### Native gRPC on the daemon socket (engine-release-history)

Engine 29.2 can serve gRPC natively on its listening socket, allowing
integrations to use gRPC without a separate listener or translation layer.

### Deprecated session transport endpoints (engine-api-and-deprecations)

API v1.53 deprecates `POST /grpc` and `POST /session`; integrations using either
endpoint must migrate before their future removal.

## Events and streaming responses

### API event and container-list responses (engine-release-history)

The events endpoint now identifies its newline-delimited stream as
`application/x-ndjson`; with API v1.52 it also omits the legacy `status`, `id`,
and `from` fields. `GET /containers/json` adds a `Health` field for health-check
state.

### Event stream media types (engine-api-and-deprecations)

API v1.52 adds RFC 7464 `application/json-seq` negotiation for `GET /events`,
and v1.53 also accepts `application/jsonl`. Consumers selecting JSON text
sequences must handle their record separators rather than parsing them as
ordinary newline-delimited JSON.

### API response deprecations (28.0.0)

`GET /info` now always reports `BridgeNfIptables` and
`BridgeNfIp6tables` as false; API v1.49 will omit them. JSON progress streams
deprecate `error` and `progress` in favor of `errorDetail` and
`progressDetail`, and the `Expected` commit fields in `GET /info` are also
scheduled for omission in v1.49.

## Image API requests and responses

### Image-inspect response changes (26.0.0)

`GET /images/{name}/json` removes the `Container` and `ContainerConfig` fields.
It also omits a missing `Created` field instead of returning a zero timestamp,
while API v1.43 and older still receive `0001-01-01T00:00:00Z`.

### Engine API v1.48 image metadata (28.0.0)

Image inspection adds `Manifests`, including platform manifests and
attestations. With the containerd image store, image responses add the target
OCI `Descriptor`, while container inspection and listing add the
platform-specific `ImageManifestDescriptor`; these descriptor fields are
populated only by a multi-platform image store.

### Sparse inspect responses and network metadata (engine-release-history)

Image inspection omits empty `Parent`, `Comment`, `DockerVersion`, `Author`, and
unset `Config` fields; `GraphDriver` is absent with the containerd image
backend. API v1.52 makes container-level `Config.MacAddress` obsolete in favor
of endpoint settings, while network inspection adds per-subnet IPAM allocation
statistics; from 29.3, `POST /networks/{id}/connect` actually applies
`EndpointSettings.MacAddress`.

### Image attestation retrieval (engine-api-and-deprecations)

Engine API v1.55 adds `GET /images/{name}/attestations`. `platform` selects one
image variant and defaults to the daemon host platform, repeated `type`
parameters filter by in-toto predicate URI, and `statement=true` includes
statement bodies instead of returning descriptor and predicate metadata without
reading the blobs.

### Platform-scoped image API operations (engine-api-and-deprecations)

API v1.49 lets `GET /images/{name}/json` select a JSON-encoded OCI `platform`,
mutually exclusive with `manifests`. API v1.50 adds a `platforms` query
parameter to `DELETE /images/{name}` so clients can delete content for selected
OCI platforms.

## Container create, update, and inspect

### API-gated recursive read-only mounts (26.0.0)

For clients using Engine API versions below v1.44, read-only mounts remain
non-recursive by default for compatibility; nested mounts must not be assumed to
become read-only.

### Engine API additions (27.0.1)

Service create and update accept `OomScoreAdj`; container-list responses include
annotations; and container or service creation accepts
`HostConfig.Mounts.TmpfsOptions.Options`. Image builds emit an image `create`
event whether or not the result is tagged, while `GET /info` adds `Containerd`
socket and namespace details.

### Writable cgroups without privileged mode (28.0.0)

Container creation accepts `writable-cgroups=true` in
`HostConfig.SecurityOpt`, allowing writable cgroup mounts without granting the
container full privileged mode.

```json
{
  "HostConfig": {
    "SecurityOpt": ["writable-cgroups=true"]
  }
}
```

### Live per-device block-I/O updates (engine-api-and-deprecations)

API v1.55 makes `BlkioWeightDevice`, `BlkioDeviceReadBps`,
`BlkioDeviceWriteBps`, `BlkioDeviceReadIOps`, and `BlkioDeviceWriteIOps`
effective in `POST /containers/{id}/update`; they were previously accepted but
ignored. Omitting a field or sending `null` preserves its current rules, while
an empty array clears them.

### Empty port-binding lists (engine-api-and-deprecations)

API v1.52 deprecates automatically turning an empty `PortBindings` list into a
binding with empty `HostIP` and `HostPort` during container start. Container
creation now warns about this input, and clients should omit an unused mapping
or send an explicit binding before a future API version drops the backfill.

### Container inspection field removals (engine-api-and-deprecations)

API v1.52 removes the top-level `NetworkSettings` bridge, hairpin, link-local,
secondary-address, endpoint, gateway, IP-prefix, IPv6, and MAC fields from
container inspection; read endpoint data from `NetworkSettings.Networks`. It
also removes `KernelMemoryTCP` from container update, container inspection, and
`GET /info`; older APIs may still accept the field without applying it.

### Container-wide volume drivers do not configure mounts (engine-api-and-deprecations)

From API v1.48, container creation warns when `Config.VolumeDriver` is combined
with volumes in `HostConfig.Mounts`, because the container-wide driver has no
effect on those mount entries.

## Disk usage and daemon capability discovery

### Disk-usage response redesign (engine-api-and-deprecations)

API v1.52 adds `ImagesUsage`, `ContainersUsage`, `VolumesUsage`, and
`BuildCacheUsage` to `GET /system/df`, with `?verbose=1` for detailed data.
V1.52 returns the legacy fields alongside the replacements except that they are
unpopulated in verbose mode; v1.53 removes `LayersSize`, `Images`, `Containers`,
`Volumes`, and `BuildCache`.

### Daemon capability discovery (engine-api-and-deprecations)

`GET /info` adds `CDISpecDirs` in v1.44, `FirewallBackend` in v1.49, and
`DiscoveredDevices` in v1.50. `CDISpecDirs` is empty without experimental
daemon support, and the discovered-device list currently describes devices
found through CDI.

## Networking and Swarm schemas

### Network aliases versus DNS names (engine-api-and-deprecations)

From API v1.45, an endpoint's `Aliases` contains only aliases explicitly
supplied at container creation and no longer includes the container short ID.
Use the v1.44 `DNSNames` field when the container name, hostname, aliases, and
short ID are all required.

### Swarm service request schema (engine-api-and-deprecations)

API v1.44 allows service create and update requests to set `Seccomp` and
`AppArmor` in `ContainerSpec.Privileges`. The same version deprecates the
request's top-level `Networks` field in favor of `TaskTemplate.Networks`.

## Remote daemon security and CLI argument handling

### Mandatory TLS for remote daemon TCP (engine-api-and-deprecations)

Unauthenticated daemon TCP listeners were deprecated in Engine 26. From Engine
27, a non-local TCP listener combined with explicit `--tls=false` or
`--tlsverify=false` makes the daemon fail to start; use verified TLS, a Unix
socket, or SSH, while `tcp://localhost` is exempt.

### Standard quoting for TLS path flags (engine-api-and-deprecations)

The CLI's special stripping of quote characters from `--tlscacert=...`,
`--tlscert=...`, and `--tlskey=...` values was deprecated in 28.4 for removal
in 29. Pass a quoted path as a separate shell argument, such as
`--tlscert "/path with spaces/cert.pem"`, rather than depending on the old
equals-sign handling.

### Default-bridge links approaching removal (engine-api-and-deprecations)

`--link` without an explicit network remains deprecated and is targeted for
removal in Engine 30; Engine 29.6 adds a warning when it is used on the default
bridge. Move workloads to custom networks; links on non-default networks remain
supported.

## Deprecated fields and inert settings

### Inert non-distributable-artifact configuration (28.0.0)

`--allow-nondistributable-artifacts` and the matching daemon configuration no
longer have any effect and emit a deprecation warning. Related registry API
fields remain present but `null` through API v1.48 and are omitted from v1.49
onward.
