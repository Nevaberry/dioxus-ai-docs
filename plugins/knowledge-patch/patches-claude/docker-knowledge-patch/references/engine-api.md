# Engine API Compatibility and Deprecations

## Version negotiation and floors

- Engine 26.0.0 removes APIs older than v1.24.
- Engine 29.0 through 29.2 require v1.44 or later and introduce v1.52.
- Engine 29.3 lowers the daemon floor to v1.40. A client that must also talk to
  Engine 29.0–29.2 still needs v1.44 or newer.
- Do not assume the CLI or Go client's supported floor equals the raw daemon's
  floor; negotiate and test the actual client/daemon pair.

Daemon debug and pprof endpoints are available under `/v<API-version>/` since
28.0.0, so a consistently version-prefixed client need not switch to
unversioned paths.

## Events and streamed JSON

Engine 25.0.0 adds containerd-store push, pull, and save image events. Engine
27.0.1 emits image `create` for build results whether or not they are tagged.

Engine 29 labels its newline-delimited event stream `application/x-ndjson`.
API v1.52 omits legacy event fields `status`, `id`, and `from`, and can negotiate
RFC 7464 `application/json-seq`. API v1.53 also accepts `application/jsonl`.
JSON text sequences have record separators; do not feed them to an ordinary
NDJSON parser.

JSON progress streams deprecate `error` and `progress` in favor of
`errorDetail` and `progressDetail` since 28.0.0.

## Image responses and operations

Engine 26.0.0 removes `Container` and `ContainerConfig` from image inspect and
omits missing `Created`; APIs v1.43 and earlier receive
`0001-01-01T00:00:00Z` instead.

API v1.48 adds image `Manifests`; with the containerd store, it adds target OCI
`Descriptor`, while container inspect/list add `ImageManifestDescriptor`.
These descriptors require a multi-platform store.

API v1.49 lets `GET /images/{name}/json` select a JSON-encoded `platform`,
mutually exclusive with `manifests`. API v1.50 adds `platforms` to
`DELETE /images/{name}`. Engine 29's load and export endpoints accept repeated
`platform` query parameters.

Engine 29 makes image inspect sparse: empty `Parent`, `Comment`,
`DockerVersion`, `Author`, and unset `Config` are omitted; `GraphDriver` is
omitted under the containerd backend. Engine 29.2 adds trusted-origin
`Identity`; Engine 29.3 adds the image-list `identity` query option.

### Attestations in API v1.55

`GET /images/{name}/attestations` returns attestation descriptors and predicate
metadata. `platform` selects a variant and defaults to the host platform;
repeated `type` values filter in-toto predicate URIs; `statement=true` includes
statement bodies.

## Container inspection and lists

Engine 27.0.1 container-list responses add annotations. Engine 29
`GET /containers/json` adds `Health`.

API v1.52 removes these top-level container-inspection network fields:
bridge, hairpin mode, link-local addresses, secondary addresses, endpoint ID,
gateway, IP address/prefix length, IPv6 gateway/address/prefix, and MAC address.
Read per-endpoint data from `NetworkSettings.Networks`.

API v1.52 also makes container-level `Config.MacAddress` obsolete in favor of
endpoint settings. Network inspect gains per-subnet IPAM allocation statistics.
Engine 29.3 makes `POST /networks/{id}/connect` apply
`EndpointSettings.MacAddress` as requested.

## Container create and update

### Mount fields

Engine 26.0.0 exposes volume subpaths through `VolumeOptions.Subpath`. Clients
using API versions below v1.44 retain legacy non-recursive read-only behavior;
they must not assume nested mounts are read-only.

API v1.48 warns when `Config.VolumeDriver` is combined with
`HostConfig.Mounts`; the container-wide volume driver does not configure those
mount entries.

### Empty port bindings

API v1.52 deprecates turning an empty `PortBindings` list into one binding with
empty `HostIP` and `HostPort` at start. Creation warns. Omit an unused mapping
or send the exact binding instead of relying on future backfill.

### Live block-I/O changes

API v1.55 makes `BlkioWeightDevice`, `BlkioDeviceReadBps`,
`BlkioDeviceWriteBps`, `BlkioDeviceReadIOps`, and `BlkioDeviceWriteIOps`
effective in `POST /containers/{id}/update`. They were formerly ignored.
Omitted or `null` values preserve rules; empty arrays clear them.

### Removed resource fields

API v1.52 removes `KernelMemoryTCP` from update, inspect, and `GET /info`.
Older APIs may accept it without applying it.

## Network schema

API v1.45 endpoint `Aliases` contains only aliases explicitly supplied at
creation and no longer includes the container short ID. Use `DNSNames`, added
in v1.44, when the name, hostname, explicit aliases, and short ID are needed.

Create and connect support endpoint driver options and per-interface sysctls;
use `IFNAME`. Service network attachments accept driver options as well.

## Swarm API

API v1.44 service create/update can set `Seccomp` and `AppArmor` in
`ContainerSpec.Privileges`. It deprecates request-level `Networks` in favor of
`TaskTemplate.Networks`.

Engine 27.0.1 service create/update adds `OomScoreAdj`. It also accepts
`HostConfig.Mounts.TmpfsOptions.Options` during container or service creation.

Engine 29 adds service/task `SwapBytes` and `MemorySwappiness` corresponding to
the CLI's swap controls.

## Disk usage redesign

API v1.52 adds `ImagesUsage`, `ContainersUsage`, `VolumesUsage`, and
`BuildCacheUsage` to `GET /system/df`; `?verbose=1` requests detail. In v1.52,
legacy fields coexist except they are unpopulated in verbose mode. API v1.53
removes `LayersSize`, `Images`, `Containers`, `Volumes`, and `BuildCache`.

## Daemon information and capabilities

`GET /info` additions:

- v1.44: `CDISpecDirs`, empty unless experimental support is active.
- v1.49: `FirewallBackend`.
- v1.50: `DiscoveredDevices`, currently CDI-discovered devices.

Engine 27.0.1 also adds containerd socket and namespace details to `GET /info`.

Since 28.0.0, `BridgeNfIptables` and `BridgeNfIp6tables` always report false;
API v1.49 omits them. The `Expected` commit fields are also scheduled for
omission in v1.49.

Engine 29.2 adds experimental NRI reporting in `docker info` and can serve gRPC
natively on its daemon socket.

## Session transports

API v1.53 deprecates `POST /grpc` and `POST /session`. Migrate integrations off
those transport endpoints before removal; native daemon-socket gRPC is a
separate Engine 29.2 capability and should be discovered rather than assumed.

## Remote daemon TLS and CLI quoting

From Engine 27.0.1, a non-local TCP listener with explicit `--tls=false` or
`--tlsverify=false` prevents startup. Use verified TLS, Unix socket, or SSH;
`tcp://localhost` is exempt.

Special quote stripping for equals-form `--tlscacert=...`, `--tlscert=...`, and
`--tlskey=...` is deprecated in 28.4 and removed in 29. Pass a path containing
spaces as a separate shell argument:

```console
docker --tlscert "/path with spaces/cert.pem" info
```

## Deprecated and removed API surface

- Since 25.0.0, search `IsAutomated` and filter `is-automated` are deprecated.
- The image-inspect `Config` fields that model container runtime defaults rather
  than image configuration are deprecated since 27.0.1.
- Since 28.0.0, non-distributable-artifact registry fields remain `null`
  through v1.48 and disappear in v1.49.
- Engine 28.0.0 removes API CORS and external graph-driver extensions.
- Engine 29 removes legacy event fields in v1.52 and old disk-usage fields in
  v1.53; build clients around explicit versioned response models.

## Parser checklist

1. Negotiate the API and branch on its schema, not only Engine version.
2. Model optional fields as optional and distinguish absent, `null`, and empty.
3. Read endpoint network data from `NetworkSettings.Networks`.
4. Choose and correctly frame one event media type.
5. Do not parse human CLI output as a substitute for a stable API contract.
