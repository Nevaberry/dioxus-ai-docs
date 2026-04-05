# OCI Artifacts

## `podman artifact` commands (stable since 5.6)

The `podman artifact` commands are stable (no longer experimental) and available via remote client:

```bash
podman artifact pull oci-registry.example/myartifact:v1
podman artifact ls
podman artifact inspect myartifact
podman artifact push myartifact docker://registry/repo:tag
podman artifact rm myartifact
podman artifact add myartifact file1.tar file2.tar
podman artifact extract myartifact
```

## `podman inspect` artifacts (5.7+)

`podman inspect` can now inspect artifacts (not just containers/images).

## REST API (5.6+)

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/libpod/artifacts/json` | List artifacts |
| `GET` | `/libpod/artifacts/{name}/json` | Inspect artifact |
| `POST` | `/libpod/artifacts/pull` | Pull artifact |
| `DELETE` | `/libpod/artifacts/{name}` | Remove artifact |
| `POST` | `/libpod/artifacts/add` | Add artifact from tar |
| `POST` | `/libpod/artifacts/{name}/push` | Push to registry |
| `GET` | `/libpod/artifacts/{name}/extract` | Get artifact contents |
