---
name: docker-knowledge-patch
description: Docker
license: MIT
version: "29.3"
metadata:
  author: Nevaberry
---

# Docker Knowledge Patch

Baseline: Docker Engine 24.x and Compose 2.x. Covered range: Engine 25.0.0 through 29.3, Engine API v1.44 through v1.55, Compose 5.0.0 through 5.3.0, Buildx 0.30.0 through 0.35.0, BuildKit 0.28.0, and Dockerfile 1.22.0.

Included versioned batches: 25.0.0, 26.0.0, 27.0.1, 28.0.0, 0.30.0, 5.0.0, 0.31.0, 5.1.0, 0.28.0, 1.22.0, 0.32.0, 0.33.0, 0.34.0, 0.35.0, 5.2.0, and 5.3.0.

## Use this patch

1. Identify whether the task targets Engine runtime, networking, images, the Engine API, Go integration, Buildx, BuildKit/Dockerfile, or Compose.
2. Read the matching reference before changing configuration, client calls, parsers, or automation.
3. Check both the daemon version and negotiated API version; several defaults and response shapes are API-gated.
4. Treat fresh installations, upgrades, and downgrades separately. Engine 28 and 29 include stateful storage and firewall transitions.
5. Make output parsing explicit. Several human-oriented CLI defaults changed, while event and Compose JSON streams use record framing.

## Reference index

| Reference | Topics |
| --- | --- |
| [runtime.md](references/runtime.md) | Daemon startup and reload, storage, mounts, resources, security, rootless, Windows, Swarm, platform support |
| [networking.md](references/networking.md) | Attachments, DNS, IPv4/IPv6, IPAM, gateway modes, firewall backends, routing |
| [images-registry.md](references/images-registry.md) | Image store, archives, platform selection, manifests, formats, registry behavior, provenance |
| [engine-api.md](references/engine-api.md) | API compatibility, schema changes, event framing, inspection, updates, deprecations |
| [go-sdk-cli.md](references/go-sdk-cli.md) | Go modules and client migrations, removed APIs, CLI behavior and embedding |
| [buildx.md](references/buildx.md) | Bake, exporters, Imagetools, source policies, builders, provenance, resources |
| [buildkit-dockerfile.md](references/buildkit-dockerfile.md) | BuildKit sources and verification, provenance, deployment, Dockerfile frontend and linting |
| [compose.md](references/compose.md) | Compose 5 migration, builds, lifecycle, providers, publish, watch, output, init containers |

## Breaking changes and migration priorities

### Engine 29 fresh installations

- Fresh Engine 29 installations use the containerd image store by default; upgrades keep their existing store. `userns-remap` temporarily prevents use of the containerd store.
- Bundled containerd 2.1.5 follows systemd's `LimitNOFILE`, changing the container default from `1048576` to `1024`. Set `--ulimit` or `default-ulimits` for workloads that require more descriptors.

```json
{
  "default-ulimits": {
    "nofile": { "Name": "nofile", "Soft": 1048576, "Hard": 1048576 }
  }
}
```

- Do not assume the old image-list table: `docker image ls` now uses a collapsed tree and hides untagged images unless `--all` is set. Give scripts an explicit `--format`.
- Legacy-link environment variables are no longer injected by default. `DOCKER_KEEP_DEPRECATED_LEGACY_LINKS_ENV_VARS=1` is only a temporary compatibility switch.

### Firewall and network transitions

- Engine 28.0.0 requires kernel `ipset` support and installs redesigned iptables/ip6tables rules. Before downgrading, remove those rules; rebooting is the simplest documented cleanup.
- Engine 28.0.0 blocks remote direct routing to unpublished ports and prevents neighboring hosts from reaching ports published to host loopback. Publish required ports or deliberately choose a `nat-unprotected` gateway mode.
- Engine 29 removes the `DOCKER-ISOLATION-STAGE-1` and `DOCKER-ISOLATION-STAGE-2` chains. Without the userland proxy, cross-network reachability through host-published ports and `nat-unprotected` networks can increase.
- The nftables backend is experimental. Docker does not enable host forwarding in this mode; configure forwarding and non-Docker interface policy yourself.
- IPv6 `ip6tables` filtering became stable and default-enabled in 27.0.1. A host that enables IPv6 forwarding independently owns its `FORWARD` policy.

### API compatibility and response parsing

- Engine 25.0.0 API v1.44 removes image `VirtualSize`; Engine 26.0.0 removes API versions below v1.24 and image `Container`/`ContainerConfig` fields.
- Engine 29.0 through 29.2 require daemon API v1.44 or newer; 29.3 lowers the raw daemon floor to v1.40. The v29 CLI and Go client still do not negotiate below v1.44.
- API v1.52 removes many top-level container network fields, omits unset image fields, and can omit `GraphDriver` with the containerd backend. Read per-network data from `NetworkSettings.Networks` and tolerate absent optional fields.
- API v1.53 removes the legacy `/system/df` arrays in favor of usage summaries and deprecates `/grpc` and `/session`.
- API v1.55 adds image attestations and makes per-device block-I/O update fields live. Distinguish omitted or `null` update fields from empty arrays, which clear rules.
- Negotiate event framing explicitly: NDJSON is declared in v1.52, RFC 7464 `application/json-seq` is accepted in v1.52, and `application/jsonl` is accepted in v1.53.

### Image and registry removals

- Engine 28.2 cannot pull or push Docker Image v1 or manifest v2 schema 1. Republish content as OCI or manifest v2 schema 2.
- Engine 28.2 also removes pull-by-tag fallback after digest resolution. Registries must conform to the OCI Distribution Specification.
- Engine 27 and later reject a non-local remote TCP listener configured with explicit `--tls=false` or `--tlsverify=false`. Use verified TLS, a Unix socket, or SSH.
- Engine 29 removes Docker Content Trust commands and classic-builder DCT support from the CLI; install the trust command separately as a CLI plugin when needed.

### Go SDK and CLI integration

- Stop importing `github.com/docker/docker`. Use `github.com/moby/moby/client` and `github.com/moby/moby/api`; the parent `github.com/moby/moby` module is internal, release tags use `docker-v29.0.0` form, and the SDK requires Go 1.24 or newer.
- Replace removed `NewClient` and `NewEnvClient`; replace `ImageCreate` with `ImagePull` or `ImageImport`.
- Expect option structs and dedicated result structs instead of positional parameters and raw returns. `ContainerExec...` methods become `Exec...`, while pull/push results expose `JSONMessages` iterators.
- Migrate IP/subnet values to `netip.Addr` and `netip.Prefix`, MAC values to byte slices compatible with `net.HardwareAddr`, and container `Port` to `PortSummary`.
- Docker CLI embedding lost most exported stock-command constructors and many formatter and `Run...` helpers. Build on the supported client modules or provide a separate command layer.

### Compose 5 migration

- Compose intentionally jumps from v2 to v5; v3 and v4 were skipped to avoid confusion with obsolete Compose file format labels.
- Compose 5 removes its internal BuildKit builder and delegates builds to Bake. Remove dependencies on the former internal builder path.
- Compose 5.2.0 introduces a new state-reconciliation algorithm. Regression-test upgrade convergence for existing projects.
- `docker compose ps --format json` emits JSON Lines, not one JSON array. Consume each line as a separate JSON value.
- Compose 5.3.0 supports native pre-start init containers.

## High-use Engine features

### Mount image content

Use `type=image` (since 28.0.0) and optionally select an internal path with `image-subpath`:

```console
docker run --mount type=image,source=alpine:latest,target=/mnt,image-subpath=etc alpine:latest
```

Use `bind-create-src` when a missing bind source should be created. Replace removed `bind-nonrecursive` with `bind-recursive=disabled`:

```console
docker run --mount type=bind,src=/host/data,dst=/data,bind-recursive=disabled IMAGE
```

Anonymous volumes may now be read-only without naming a source.

### Select image platforms

- With the containerd image store, `docker image push --platform` selects one manifest (since 27.0.1).
- `docker load`, `docker save`, and `docker history` gained one-platform selection in 28.0.0.
- Engine 29 accepts comma-separated platform lists for `load` and `save`; the API accepts repeated `platform` parameters.

```console
docker image save --platform linux/amd64,linux/arm64 -o app.tar app:tag
```

### Control network gateways and address families

Choose the default gateway with extended `--network` syntax and `gw-priority`:

```console
docker run --network=name=frontend --network=name=egress,gw-priority=100 IMAGE
```

Use `gateway_mode_ipv4` or `gateway_mode_ipv6` values `nat`, `routed`, `nat-unprotected`, or, for an internal network, `isolated`. Create IPv6-only networks with `--ipv6 --ipv4=false` where supported.

```console
docker network create --ipv6 --ipv4=false v6-only
```

Configure per-endpoint interface sysctls with the `IFNAME` placeholder; API v1.48 no longer migrates container-wide `eth0` sysctls automatically.

## High-use build features

### Enforce source policy

- Buildx 0.31.0 introduces Rego source policy for local contexts; 0.32.0 extends it to Git and HTTP sources and adds Sigstore/provenance inputs.
- Buildx 0.33.0 adds PGP verification and makes the DAP debugger generally available.
- Buildx 0.34.0 adds opt-in `BUILDX_DEFAULT_POLICY` verification for Docker pipeline images and global `bake --policy` options.
- Buildx 0.35.0 can proxy build-step network traffic into policy evaluation with BuildKit 0.31.0 or later.

```console
docker buildx build --policy ./policy.rego .
docker buildx bake --policy ./policy.rego
```

### Make outputs and resources deterministic

- Use local exporter `mode=delete` to replace rather than merge the destination. Outside the working directory, allow `buildx.local.delete` explicitly.
- Use `buildx build --resource` or Bake's `resource` key for CPU and memory limits; this requires BuildKit 0.31.0 or later and Dockerfile v1.25.0 or later.
- Use `imagetools create --metadata-file` to capture the created descriptor and digest.
- Use Buildx command `--timeout` where offered to bound waits for remote builders.

## High-use Compose features

- Use `build.no_cache_filter` to bypass cache only for named build stages.
- Use `docker compose start --wait` to wait for services after starting them.
- Expect lifecycle hooks on restart, `post_start` hooks for `compose run`, and provider stop hooks during shutdown.
- Compose recreates a container when an image-mounted digest changes.
- OCI and Git remote resources are supported, including overrides for OCI projects and corrected Windows/SSH path handling.
- `docker compose publish` honors optional missing environment files and checks literal inline environment values for sensitive data.
- Compose Watch no longer rebuilds `depends_on` services solely because of that relationship.

## Preflight checklist

- Run `dockerd --validate --config-file ...` to validate configuration and host requirements.
- Verify the active image store and firewall backend with `docker info`.
- Pin or inspect the Engine API version before relying on fields or omission behavior.
- Make CLI and stream output formats explicit in automation.
- Test firewall reachability after Engine 28/29 upgrades and before any downgrade.
- Test Compose convergence after moving to 5.2.0 or later.
- Read the complete topic reference before changing SDK integrations or compatibility paths.
