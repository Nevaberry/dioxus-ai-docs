---
name: docker-knowledge-patch
description: Docker
version: "29.3"
license: MIT
metadata:
  author: Nevaberry
---


# Docker Compatibility Guidance

Use this skill when upgrading Docker Engine, integrating with the Engine API or
Go client, operating BuildKit or Buildx, or adopting Docker Compose 5 behavior.
Start with the quick reference for migration blockers, then load only the topic
reference needed for the task.

## Reference index

| Reference | Topics |
| --- | --- |
| [BuildKit and Dockerfile frontend](references/buildkit-dockerfile.md) | Dockerfile behavior, LLB sources, provenance, security fixes, cgroups |
| [Buildx, Bake, imagetools, and builders](references/buildx.md) | Source policies, Bake variables, exporters, builder drivers, attestations |
| [Docker Compose 5](references/compose.md) | Reconciliation, lifecycle hooks, remote resources, Watch, config and publish behavior |
| [Engine API compatibility and deprecations](references/engine-api.md) | API floors, schemas, event streams, inspection, deprecations |
| [Go SDK and CLI integration](references/go-sdk-cli.md) | Module paths, call shapes, type moves, removed symbols, CLI plugins |
| [Images, manifests, archives, and registries](references/images-registry.md) | Image stores, platform selection, mounts, metadata, registry behavior |
| [Networking, DNS, IPAM, and firewalls](references/networking.md) | Attachments, IPv6, gateway modes, DNS, routing, firewall backends |
| [Engine runtime, daemon, and platform](references/runtime.md) | Daemon lifecycle, security, logging, container lifecycle, Windows and rootless behavior |

## Upgrade blockers and removals

### Engine configuration and extensions

- Remove the `--oom-score-adjust` daemon option and replace the `logentries`
  logging driver before moving to Engine 25.0.0.
- Engine 28 removes the daemon API CORS option, external graph-driver plugins,
  the temporary Windows `windows-dns-proxy` flag, and Fluentd
  `fluentd-async-connect`.
- Engine 28 requires a matching updated `docker-proxy`; older proxy binaries are
  incompatible. `rootlesskit-docker-proxy` is removed from the distribution.
- `--allow-nondistributable-artifacts` no longer has any effect and emits a
  deprecation warning.
- Docker Content Trust commands are removed from the Engine 29 CLI and are
  available only by building a separate plugin.

### API and client compatibility

- Engine 26 removes API versions older than v1.24.
- Engine 29.0 through 29.2 requires API v1.44 or later; Engine 29.3 lowers the
  minimum to v1.40. Clients that target earlier 29.x daemons must still
  negotiate v1.44 or newer.
- API v1.52 removes legacy top-level network fields from container inspection;
  read endpoint data from `NetworkSettings.Networks`.
- API v1.53 removes the legacy disk-usage fields `LayersSize`, `Images`,
  `Containers`, `Volumes`, and `BuildCache`.
- API v1.53 deprecates `POST /grpc` and `POST /session`.
- The Go SDK removes deprecated constructors, old image-client interfaces, and
  numerous packages in Engine 29. Use the supported
  `github.com/moby/moby/client` and `github.com/moby/moby/api` modules; the SDK
  requires Go 1.24 or later.

### CLI and output migrations

- Engine 28 renames `docker stop --time` and `docker restart --time` to
  `--timeout`.
- Engine 29 changes `docker image ls` to a collapsed tree-style view, hides
  untagged images unless `--all` is used, stops truncating image names, and
  removes `VirtualSize` from JSON and formatting output.
- `docker compose ps --format json` emits JSON Lines rather than one JSON
  array.
- `docker buildx install` and `docker buildx uninstall` are deprecated; invoke
  `docker buildx` directly.
- Buildx policy evaluation renames `--filename` to `--file`; the old long flag
  remains deprecated.

## Networking quick reference

### Firewall behavior

- `ip6tables` is enabled by default for Linux bridge networks. On IPv6-enabled
  bridges it restricts external access to published ports and enables outbound
  masquerading.
- Engine 28 blocks remote direct access to unpublished container ports. Publish
  required ports or deliberately use `nat-unprotected` when that exposure is
  intended.
- Engine 28 changes bridge iptables and ip6tables rules and requires kernel
  `ipset` support. Before downgrading, remove the new rules; rebooting is the
  documented simplest cleanup.
- The experimental Engine 29 `nftables` backend does not enable host IP
  forwarding. If a bridge needs forwarding while it is disabled, daemon startup
  or network creation fails.
- The daemon no longer appends permissive host `INPUT` rules for encrypted
  overlays. Restrictive hosts may need an explicit rule for incoming encrypted
  overlay traffic.

### Addressing and routes

- Extended `--network` syntax supports multiple attachments, per-attachment MAC
  and link-local addresses, endpoint driver options, gateway priority, and
  container-side interface names.
- The highest `gw-priority` selects the default gateway; equal priorities are
  resolved by network-name order.
- `docker network create --ipv4=false` disables IPv4 assignment, subject to the
  driver and platform limits in the networking reference.
- A routed bridge installs no NAT or masquerading for published ports. The
  surrounding network must route container addresses to the host.
- Macvlan and IPvlan L2 networks in Engine 29 receive no default gateway unless
  IPAM explicitly supplies `--gateway`.

## Images and registries quick reference

### Platform selection and stores

- The containerd image store supports `docker image push --platform` for one
  locally stored platform manifest.
- Engine 28 adds single-platform selection to `docker load`, `docker save`, and
  `docker history`.
- Engine 29 accepts comma-separated platform lists for `docker image load` and
  `docker image save`; the APIs accept repeated `platform` parameters.
- Fresh Engine 29 installations use the containerd image store by default, but
  existing installations are not switched automatically and `userns-remap`
  installations are excluded.
- Engine 29.7.0 graduates the `image` mount type from experimental status.

### Metadata and compatibility

- Engine 26 image inspection removes `Container` and `ContainerConfig`.
- Engine API v1.48 adds image `Manifests`; containerd-backed responses also add
  OCI descriptor fields.
- Engine 29.2 adds trusted image `Identity` data, and 29.3 adds an `identity`
  query parameter to `GET /images/json`.
- API v1.55 adds `GET /images/{name}/attestations` with platform, predicate-type,
  and statement-body controls.
- Saved image tar archives are OCI compliant from Engine 25.0.0.

## Build quick reference

### Provenance and policies

- BuildKit provenance defaults to SLSA v1.0. Set the provenance `version`
  attribute when v0.2 output is required.
- Buildx can enforce Rego source policies, evaluate and test them, and apply them
  to local, remote Git, and HTTP sources.
- Attestation-aware policy builtins can validate signed Sigstore bundles, fetch
  attestations from the GitHub API, and inspect image provenance. Provenance
  policy inputs require BuildKit 0.28 or later.
- Default verification of Docker pipeline images is opt-in through
  `BUILDX_DEFAULT_POLICY`; Buildx 0.36.0 extends default-policy checks to the
  BuildKit release image used by a `docker-container` builder.

### Exports and resources

- A local export with `mode=delete` replaces the destination instead of merging
  into it. The destination must be below the working directory unless
  `--allow=buildx.local.delete` is supplied or the TUI confirms the action.
- Registry-oriented exports initialized with `--push` or `-o type=registry` do
  not unpack images created in the Docker image store.
- Build requests can set CPU and memory limits through `--resource` or a Bake
  target `resource` key when the stated BuildKit and Dockerfile requirements are
  met.
- `imagetools create --metadata-file` writes properties such as the created
  descriptor and digest for automation.

## Compose quick reference

### Build and reconciliation

- Compose 5 delegates builds to Docker Bake and removes its internal BuildKit
  builder. Integrations that depended on the internal builder must migrate to
  the delegated path.
- Compose recreates a container when the digest of an image mounted into it
  changes.
- The first `docker compose up` after the image-digest reconciliation upgrade
  may recreate existing containers once.
- Compose 5.2 introduces a new workload reconciliation algorithm, so existing
  workloads can behave differently after upgrading even when their files have
  not changed.
- Compose 5.4 includes volume recreation and network lifecycle in reconciliation
  plans.

### Lifecycle and configuration

- Service hooks run on restart; `docker compose run` executes the target
  service's `post_start` hooks; external providers gain a stop hook.
- Compose supports native init containers that run before the main workload.
- `docker compose config --variables` extracts variables without first
  requiring full model validation.
- `docker compose config --hash` accounts for zero-replica services and, in
  Compose 5.5, resolves service environments before computing the hash.
- `docker compose pull` honors `pull_policy` refresh windows such as `daily`,
  `weekly`, and `every_N`.

## Apply guidance conservatively

Preserve every stated condition when using these references: API negotiation,
image-store backend, operating system, network driver, experimental status, and
minimum component versions all affect whether an item applies. Do not infer a
replacement or outcome where a reference only records a behavior change.
