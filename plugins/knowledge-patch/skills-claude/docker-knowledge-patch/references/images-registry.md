# Images, Manifests, Archives, and Registries

## Listing and inspection

### Timestamp filtering

Since 25.0.0, image listings accept `--filter=until=<timestamp>` for inventory
and age-based cleanup.

```console
docker image ls --filter 'until=2024-01-01T00:00:00Z'
```

### Default listing format

Engine 29 changes `docker image ls` to a collapsed tree view, hides untagged
images unless `--all` is set, stops truncating names, and removes `VirtualSize`
from JSON and formatting output. Automation should use an explicit `--format`
and should not infer completeness from the default table.

### Sparse image inspection

Engine 26.0.0 removes image-inspect `Container` and `ContainerConfig`. It omits
missing `Created`; API v1.43 and older still receive a zero timestamp. API
consumers must tolerate the missing optional timestamp.

Engine 28.0.0 inspection adds `Manifests`, including platform manifests and
attestations. With the containerd store it adds target OCI `Descriptor`;
container inspect/list add platform `ImageManifestDescriptor`. Descriptor data
requires a multi-platform store.

Engine 29 omits empty `Parent`, `Comment`, `DockerVersion`, `Author`, and unset
`Config`; it also omits `GraphDriver` with the containerd backend. Parsers must
tolerate absent optional fields.

Engine 29.2 adds image `Identity`, describing trusted origin such as local build,
pulled repository, or verified signed provenance. Engine 29.3 adds `identity`
to `GET /images/json` to request manifest summaries and available identity.

The nonstandard, always-default image `Config` fields `Hostname`, `Domainname`,
`AttachStdin`, `AttachStdout`, `AttachStderr`, `Tty`, `OpenStdin`, `StdinOnce`,
`Image`, `NetworkDisabled`, `MacAddress`, and `StopTimeout` are deprecated since
27.0.1. Do not treat them as meaningful image configuration.

## Containerd image store

Engine 25.0.0 adds push, pull, and save image events; legacy schema-1 pulls;
pull/push of all tags; registry tokens; `sha256:`-prefixed truncated IDs; and a
container-use count to the containerd image store.

Fresh Engine 29 installations default to that store, while upgrades keep their
existing store and `userns-remap` prevents use of it. Engine 29.7.0 makes
daemon-wide concurrent download and upload limits actually cap transfers on
the containerd store. Set both to zero to retain prior unlimited behavior.

```json
{
  "max-concurrent-downloads": 0,
  "max-concurrent-uploads": 0
}
```

## Archives and platform selection

### OCI image-save archives

Since 25.0.0, `docker image save` emits OCI-compliant tar archives. External
consumers should handle them as OCI rather than assuming older Docker-specific
archive details.

### Push one platform

With the containerd store, Engine 27.0.1 supports `docker image push
--platform` to select one local manifest. The experimental API push parameter
contains a JSON-encoded OCI Platform.

```console
docker image push --platform linux/amd64 registry.example/app:tag
```

### Load, save, and history platforms

Engine 28.0.0 adds single-platform selection to `docker load`, `docker save`,
and `docker history`. Engine 29 accepts comma-separated lists for image load and
save; the load/export APIs use repeated `platform` query parameters.

```console
docker image load --platform linux/amd64,linux/arm64 -i image.tar
```

API v1.49 lets image inspect select one JSON-encoded OCI `platform`, mutually
exclusive with `manifests`. API v1.50 adds `platforms` to image deletion for
selected OCI platforms.

## Image formats and registry behavior

Engine 26.0.0 disables deprecated image formats by default. Inventory and
migrate repositories that still require them before upgrading.

Engine 29 stops loading pre-Docker-1.10 images.

IPv6 loopback counts as an insecure registry address since 28.0.0. Registry
credentials and special Desktop/Compose behavior are covered in their component
references rather than inferred from this address rule.

## Attestations, provenance, and trust

### Attestation retrieval

API v1.55 adds `GET /images/{name}/attestations`. `platform` selects a variant
and defaults to the daemon host platform. Repeated `type` filters by in-toto
predicate URI. `statement=true` reads and includes statement bodies; without it,
the response carries descriptor and predicate metadata.

### Supply-chain metadata during image assembly

Buildx 0.30.0 Imagetools preserves attestation manifests and Cosign manifest
signatures when creating a new image. Buildx 0.32.0 can write the created
descriptor and digest to a metadata file, and Engine 29 inspection can expose
trusted `Identity`. Keep each layer of evidence distinct: preserved manifests,
creation metadata, and daemon-verified origin are not interchangeable.

### Docker Content Trust removal

Engine 29 removes Docker Content Trust commands from the CLI. The command can
be built as a separate plugin when legacy workflows require it. New automation
should use explicit signing, provenance, and source-policy verification.

## Search metadata deprecation

Since 25.0.0, API field `IsAutomated` and `docker search` filter `is-automated`
are deprecated. Stop using automated-build state from Docker Hub search as a
selection signal.

## Mounting images

Engine 28.0.0 introduces image-backed mounts and `image-subpath`; Engine 29.7.0
makes `type=image` non-experimental. Compose later pins image mount sources as
part of reconciliation. See the runtime and Compose references for mount and
convergence details.

## Registry and archive checks

1. Detect the image store and install history.
2. Select platforms explicitly for push, inspect, delete, load, save, and
   history where the operation supports it.
3. Accept sparse inspection fields and new descriptor/identity data.
4. Verify archive and registry media types before dropping old compatibility.
5. Preserve attestation and signature manifests when assembling indexes.
