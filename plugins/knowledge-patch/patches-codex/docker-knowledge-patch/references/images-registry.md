# Images, Manifests, Archives, and Registries

Use this reference for image-store behavior, platform-scoped operations, image
mounts, archive compatibility, registry access, and image-list output.

## Listing and inspection behavior

### Timestamp-filtered image listings (25.0.0)

`docker image ls` accepts `--filter=until=<timestamp>`, so image inventory and
cleanup automation can select images older than a cutoff.

```console
docker image ls --filter 'until=2024-01-01T00:00:00Z'
```

### Changed `docker image ls` output (engine-release-history)

`docker image ls` defaults to a collapsed tree-style view and hides untagged
images unless `--all` is used. Engine 29 also stops truncating image names and
removes `VirtualSize` from JSON and formatting output, so parsers must tolerate
the new shape.

### Image-config fields slated for removal (27.0.1)

The always-default, nonstandard image-inspect `Config` fields `Hostname`,
`Domainname`, `AttachStdin`, `AttachStdout`, `AttachStderr`, `Tty`, `OpenStdin`,
`StdinOnce`, `Image`, `NetworkDisabled`, `MacAddress`, and `StopTimeout` are
deprecated. API consumers should neither interpret them as image configuration
nor require them to remain present.

### Trusted image identity metadata (engine-release-history)

Engine 29.2 image inspection adds `Identity`, reporting trusted origin data such
as a local build reference, pulled repository, or verified signed-provenance
information. Engine 29.3 adds an `identity` query parameter to
`GET /images/json`, which requests manifest summaries and available identity
data.

## Platform-scoped operations

### Platform-specific pushes from the containerd image store (27.0.1)

With the containerd image store, `docker image push --platform` can select one
platform manifest from a locally stored multi-platform image.
`POST /images/{name}/push` gains an experimental `platform` parameter containing
a JSON-encoded OCI Platform value.

```console
docker image push --platform linux/amd64 registry.example/app:tag
```

### Platform-selective image operations (28.0.0)

`docker load`, `docker save`, and `docker history` accept `--platform`, allowing
one platform to be selected when working with a multi-platform image.

```console
docker image save --platform linux/amd64 -o app.tar app:tag
```

### Multiple platforms in image load and save (engine-release-history)

Unlike Engine 28's single-platform selection, Engine 29 accepts a comma-separated
platform list for `docker image load` and `docker image save`. The matching load
and export API endpoints accept repeated `platform` query parameters.

```console
docker image load --platform linux/amd64,linux/arm64 -i image.tar
```

## Image stores and transfer behavior

### Containerd image-store command parity (25.0.0)

The containerd image store adds push, pull, and save image events; supports
legacy schema-1 pulls, pulling or pushing all tags, registry tokens, and
`sha256:`-prefixed truncated IDs; and reports how many containers use an image.

### Containerd image store by default on fresh installs (engine-release-history)

Engine 29 uses the containerd image store by default for fresh installations.
This does not switch existing installations automatically and does not apply
when `userns-remap` is configured.

### Containerd image-store transfer limits (29.7.0)

With the containerd image store, the daemon-wide concurrent download and upload
limits now actually cap pulls and pushes. To retain the previous unlimited
behavior, set both limits to zero.

```json
{
  "max-concurrent-downloads": 0,
  "max-concurrent-uploads": 0
}
```

## Archives and layer extraction

### OCI-compliant image-save archives (25.0.0)

Tar archives produced by `docker image save` are now OCI compliant, which
matters to tools that consume saved images outside Docker.

### Strict extended-attribute extraction (25.0.0)

Unpacking an image layer with extended attributes onto a filesystem that cannot
store them now fails instead of silently dropping the attributes.

## Image-backed and volume mounts

### Image-backed mounts (28.0.0)

Containers can mount an image directly, and `image-subpath` selects a directory
inside that image. This makes image contents usable without copying them into
the container image or a volume.

```console
docker run --rm --mount type=image,source=alpine:latest,target=/mnt,image-subpath=etc alpine:latest ls /mnt
```

### Image mounts graduate from experimental (29.7.0)

The `image` mount type is no longer experimental in Engine 29.7.0.

### Volume subpath mounts (26.0.0)

`VolumeOptions` adds `Subpath`, exposed by the `volume-subpath` mount option, so
a container can mount one subdirectory from a volume instead of the entire
volume.

```console
docker run --mount type=volume,src=data,dst=/mnt,volume-subpath=logs IMAGE
```

### Swarm volume subpaths (28.0.0)

Swarm now honors `volume.subpath`; stack and service mounts no longer ignore a
requested volume subdirectory.

### Bind and volume mount compatibility (engine-release-history)

Engine 29.3 adds `bind-create-src` to `--mount` bind specifications, while 29.2
permits anonymous read-only volumes. The deprecated `bind-nonrecursive` mount
option is removed.

```console
docker run --mount type=bind,src=/host/data,dst=/data,bind-create-src IMAGE
docker run --mount type=volume,dst=/data,readonly IMAGE
```

## Registry and format compatibility

### Deprecated automated-build search metadata (25.0.0)

The `IsAutomated` API field and the `is-automated` filter for `docker search`
are deprecated, so consumers should stop depending on Docker Hub automated-build
status in search results.

### Deprecated image formats disabled by default (26.0.0)

Pulling deprecated image formats is now disabled by default; repositories that
only provide such formats can no longer be assumed to pull successfully.
