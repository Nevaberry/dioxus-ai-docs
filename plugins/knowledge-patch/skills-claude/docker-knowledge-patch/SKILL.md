---
name: docker-knowledge-patch
description: Docker
version: 29.3
license: MIT
metadata:
  author: Nevaberry
---


# Docker Knowledge Patch

Use this patch when work touches Docker Engine runtime, networking, images,
the Engine API, Go integrations, Buildx, BuildKit, Dockerfile, or Compose.

## How to use this patch

1. Identify the component and read its complete topic reference before changing
   configuration, API calls, parsers, or automation.
2. Check the installed daemon, CLI, API, Buildx, BuildKit, Dockerfile frontend,
   and Compose versions that matter to the task. They do not share one version.
3. For Engine work, distinguish a fresh installation from an upgrade and check
   both the daemon version and negotiated API version.
4. Treat output formats as interfaces: request an explicit CLI format and parse
   event, progress, and Compose streams according to their record framing.
5. Prefer the project's manifests, configuration, code, tests, and observed
   behavior whenever they disagree with compatibility guidance.

## Reference index

| Reference | Topics |
| --- | --- |
| [runtime.md](references/runtime.md) | Daemon lifecycle, storage, resources, security, rootless, Swarm, Windows, and platform support |
| [networking.md](references/networking.md) | Attachments, DNS, IPv4/IPv6, IPAM, gateways, firewalls, and routing |
| [images-registry.md](references/images-registry.md) | Image stores, inspection, archives, platforms, registries, identity, and trust |
| [engine-api.md](references/engine-api.md) | API floors, version-gated schemas, event framing, updates, and deprecations |
| [go-sdk-cli.md](references/go-sdk-cli.md) | Go module, client, type, and call migrations; CLI integration changes |
| [buildx.md](references/buildx.md) | Buildx, Bake, Imagetools, builders, exporters, policies, and resources |
| [buildkit-dockerfile.md](references/buildkit-dockerfile.md) | BuildKit sources, provenance, verification, deployment, Dockerfile, and linting |
| [compose.md](references/compose.md) | Compose SDK, builds, reconciliation, lifecycle, providers, publish, Watch, and output |

## Breaking changes and migration priorities

### Separate fresh Engine installs from upgrades

Fresh Engine 29 installations use the containerd image store by default;
upgrades keep their current store, and `userns-remap` prevents the switch.
The bundled static containerd also inherits systemd's `nofile` default of
1024 instead of the former 1048576. Set `--ulimit` or `default-ulimits` for
descriptor-heavy workloads.

```json
{
  "default-ulimits": {
    "nofile": {"Name": "nofile", "Soft": 1048576, "Hard": 1048576}
  }
}
```

Before an upgrade, identify the image store, validate daemon configuration and
host requirements, and test the firewall. Before downgrading from Engine 28 or
later, remove the newer iptables/ip6tables rules; a reboot is the documented
simplest cleanup.

### Audit firewall reachability

Engine 28 requires kernel `ipset`, redesigns bridge rules, blocks remote direct
routing to unpublished ports, and prevents neighboring hosts from reaching
ports published to host loopback. Publish required ports or intentionally use
`nat-unprotected` when broad direct routing is wanted.

Engine 29 removes the two `DOCKER-ISOLATION-STAGE-*` chains. Cross-network
access through host-published ports and `nat-unprotected` networks can expand,
and its experimental nftables backend does not enable host forwarding.
Configure forwarding explicitly.

IPv6 `ip6tables` filtering is stable and enabled by default. When the host,
rather than Docker, enables IPv6 forwarding, the administrator owns the
`FORWARD` policy.

### Negotiate Engine API behavior

Do not infer response shape from the daemon's marketing version. Important
transitions include:

- Engine 26 removes APIs below v1.24 and the image `Container` and
  `ContainerConfig` fields.
- Engine 29.0 through 29.2 require daemon API v1.44 or newer; Engine 29.3 lowers
  the daemon floor to v1.40.
- API v1.52 removes many top-level container network fields, makes inspect
  responses sparse, declares NDJSON events, and supports RFC 7464 JSON text
  sequences. Read endpoint data from `NetworkSettings.Networks`.
- API v1.53 removes legacy disk-usage arrays and accepts `application/jsonl`;
  it also deprecates `/grpc` and `/session`.
- API v1.55 adds image attestations and makes per-device block-I/O fields live
  during container update. Omitted or `null` fields preserve rules; empty
  arrays clear them.

### Make CLI parsing explicit

`docker image ls` now defaults to a collapsed tree, hides untagged images
without `--all`, keeps full image names, and omits `VirtualSize`. Use an
explicit `--format` rather than parsing its default table.

`docker compose ps --format json` produces one JSON object per line, not one
JSON array. Parse it as JSON Lines. Likewise, negotiate Engine event media
types deliberately and do not treat RFC 7464 records as ordinary NDJSON.

### Replace removed image and trust behavior

Deprecated image formats are disabled by default. Inventory repositories that
still depend on those formats before upgrading.

Docker Content Trust commands are removed from the CLI. If the legacy command
workflow is still required, provide it as a separate CLI plugin; prefer
explicit provenance and signature policy for new automation.

### Migrate Go integrations

Use `github.com/moby/moby/client` and `github.com/moby/moby/api`; do not import
the deprecated `github.com/docker/docker` module or the internal root
`github.com/moby/moby` module. Engine release tags use `docker-v...`, and the
current SDK requires Go 1.24 or later.

Replace removed `NewClient` and `NewEnvClient`, and replace `ImageCreate` with
`ImagePull` or `ImageImport`. Expect option structs, dedicated result structs,
`Exec...` method names, and pull/push results exposing `JSONMessages` iterators.
Move IPs and subnets to `netip`, MAC values to byte slices compatible with
`net.HardwareAddr`, and container `Port` to `PortSummary`.

Most exported stock CLI command constructors and formatter helpers are gone.
Use the supported client modules and own the command layer instead of embedding
Docker CLI internals.

### Treat Compose 5 as a migration

Compose intentionally jumps from v2 to v5; v3 and v4 were skipped to avoid
confusion with obsolete Compose file-format labels. It removes the internal
BuildKit builder and delegates builds to Bake.

Compose later introduces new workload and image-digest reconciliation. Test
convergence against existing projects after upgrades: the first `up` can
recreate containers once while stored digest state is re-evaluated.

## High-use Engine operations

### Mount image, volume, and bind content

Use `type=image` and optionally `image-subpath` to expose image content without
copying it into another image or volume:

```console
docker run --mount type=image,source=alpine:latest,target=/mnt,image-subpath=etc alpine
```

Use `volume-subpath` for one directory within a volume. Anonymous volumes can
be read-only. Use `bind-create-src` when a missing bind source should be
created. The deprecated `bind-nonrecursive` option is removed.

### Select image platforms

With the containerd store, `docker image push --platform` selects one locally
stored platform manifest. `load`, `save`, and `history` also support platform
selection; newer Engine releases accept comma-separated platform lists for
load/save, while the API uses repeated `platform` parameters.

```console
docker image save --platform linux/amd64,linux/arm64 -o app.tar app:tag
```

### Configure network attachments

Supply multiple long-form `--network` flags at create time, including MAC,
link-local address, endpoint driver options, interface name, and gateway
priority. The highest `gw-priority` becomes the default route.

```console
docker run --network=name=frontend \
  --network=name=egress,gw-priority=100 IMAGE
```

Use `gateway_mode_ipv4` or `gateway_mode_ipv6` values `nat`, `routed`,
`nat-unprotected`, or, on an internal network, `isolated`. Create an IPv6-only
network with `--ipv6 --ipv4=false` where the driver supports it.

## High-use build operations

### Enforce source policy

Buildx policies cover local, Git, HTTP, image, and attestation inputs. Policies
can verify Sigstore or PGP evidence and, with a compatible BuildKit, proxy
build-step HTTP traffic into policy evaluation.

```console
docker buildx build --policy ./policy.rego .
docker buildx bake --policy ./policy.rego
```

### Produce deterministic outputs

Use Imagetools `--metadata-file` to capture the created descriptor and digest.
Use local exporter `mode=delete` to replace rather than merge a destination;
outside the working directory this requires explicit `buildx.local.delete`
permission. Bound remote-builder waits with `--timeout` where supported.

Build and Bake can apply per-build CPU and memory limits through `--resource`
or `resource`, subject to the BuildKit and Dockerfile frontend requirements in
the Buildx reference.

## High-use Compose operations

- `build.no_cache_filter` bypasses cache only for selected build stages.
- `docker compose start --wait` waits for services after starting them.
- Restart and one-off-container paths run their supported lifecycle hooks;
  providers can receive stop hooks.
- Mounted-image digest changes participate in reconciliation.
- OCI and Git remote resources are supported, including OCI overrides.
- `publish` honors optional missing environment files and checks literal inline
  environment values for sensitive data.
- Watch does not rebuild a service merely because it appears in `depends_on`,
  and it limits image cleanup to its own work.
- Pre-start init containers are native and their images are resolved and pinned
  with service and image-mount sources.

## Preflight checklist

- Run `dockerd --validate --config-file ...` and inspect `docker info`.
- Verify image store, firewall backend, cgroup generation, and API negotiation.
- Request explicit formats for CLI output and explicit media types for streams.
- Exercise published, unpublished, loopback, cross-network, routed, and IPv6
  reachability after firewall-affecting upgrades.
- Validate saved-image and registry formats before removing compatibility paths.
- Regression-test SDK compilation and API response parsers during upgrades.
- Test Compose convergence, hashing, Watch, and publish behavior on an existing
  project before rolling out a new Compose release.
