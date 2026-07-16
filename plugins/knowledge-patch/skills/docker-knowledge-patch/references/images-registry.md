# Images, Manifests, Archives, and Registries

Use this reference for image listing, image-store differences, platform-specific operations, archive behavior, image identity, and removed registry formats.

## List and inspect images

- `docker image ls` accepts `--filter=until=<timestamp>` to exclude images newer than a timestamp (since 25.0.0):

```console
docker image ls --filter=until=2024-01-01
```

- Engine 29 changes the default image-list presentation to a collapsed tree and omits untagged images unless `--all` is supplied. Use an explicit `--format` in scripts instead of parsing the human view.
- Image inspection now includes `Identity`: a local build reference, the repository origin for a pull, or verified-signature information from valid signed provenance.
- Starting with 29.3, `GET /images/json?identity=1` can return manifest summaries and optional per-manifest identity. See [engine-api.md](engine-api.md) for API omission rules.

## OCI archives and platform selection

- `docker image save` produces OCI-compliant tar archives (since 25.0.0).
- With the containerd image store, `docker image push --platform` selects one platform manifest from a multi-platform image (since 27.0.1):

```console
docker image push --platform linux/amd64 registry.example/app:tag
```

- The experimental API equivalent accepts `platform` as a JSON-encoded OCI Platform value.
- `docker load`, `docker save`, and `docker history` accept single-platform selection starting in 28.0.0. With the containerd image store, `docker load --platform` fails when the requested platform is absent instead of loading another variant:

```console
docker save --platform=linux/amd64 -o app.tar app:tag
docker load --platform=linux/amd64 -i app.tar
docker history --platform=linux/amd64 app:tag
```

- Engine 29 extends `docker image load` and `docker image save` to comma-separated platform lists. Their API endpoints accept repeated `platform` query parameters:

```console
docker image save --platform linux/amd64,linux/arm64 -o app.tar app:tag
```

- API v1.49 can inspect one selected image platform, and v1.50 can delete selected platforms. See [engine-api.md](engine-api.md).

## Containerd image store

- Engine 25.0.0 adds image push, pull, and save events; legacy schema1 pulls; push-all-tags and `docker pull -a`; registry-token support; image-use container counts; and registry authentication keyed by the domain in the image reference.
- Engine 26.0.0 exports Prometheus metrics for the store and, with `--userns-remap`, isolates images into distinct containerd namespaces.
- Fresh Engine 29 installations use the containerd image store by default, but upgrades retain their current store. The default does not yet apply with `userns-remap`.
- API responses differ by backend. Image and container responses can expose manifest descriptors, while `GraphDriver` can be absent with containerd; see [engine-api.md](engine-api.md).

## Manifests, attestations, and provenance

- API v1.48 image inspect adds `Manifests` for platform manifests and build attestations.
- With a multi-platform containerd store, v1.48 image responses also add `Descriptor`; container list and inspect add `ImageManifestDescriptor` for the manifest used to create a container.
- API v1.55 adds an image-attestation endpoint that can return descriptors, predicate types, and optionally in-toto statements. See [engine-api.md](engine-api.md).
- Buildx Imagetools preserves attestations and signatures and can write image metadata. See [buildx.md](buildx.md).

## Legacy formats and registry compliance

- Pulling deprecated image formats is disabled by default in 26.0.0.
- Engine 28.2 removes pull and push support for Docker Image v1 and manifest v2 schema 1. Republish images as OCI or manifest v2 schema 2.
- Engine 28.2 removes the tag fallback previously used when a registry failed to pull a manifest by its resolved digest. A non-compliant registry can now fail; conform to the OCI Distribution Specification.
- Engine 29 stops loading image formats older than Docker 1.10.

## Non-distributable artifact configuration

- `--allow-nondistributable-artifacts` and its `daemon.json` counterpart are inert and warn starting in 28.0.0.
- Related registry fields in `GET /info` are always `null` through API v1.48 and are scheduled to disappear in v1.49. Do not gate behavior on them.

## Image-backed mounts

Mount image content directly with `--mount type=image` (since 28.0.0); use `image-subpath` to select content within the source image. See [runtime.md](runtime.md) for syntax and mount migration details.
