# Quadlet

## Management commands (5.6+)

New CLI commands for managing Quadlet units directly (not available with remote client):

```bash
podman quadlet install myapp.container # install for current user
podman quadlet list                    # list installed Quadlets
podman quadlet print myapp.container   # print file contents
podman quadlet rm myapp.container      # remove a Quadlet
```

## Multi-file install (5.8+)

A single file can contain multiple Quadlet units separated by `---`, each named with a `# FileName=<name>` header:
```ini
# FileName=app.container
[Container]
Image=myapp:latest

---
# FileName=db.container
[Container]
Image=postgres:16
```
```bash
podman quadlet install combined.quadlet
```

## `.artifact` file type (5.7+)

New Quadlet file type for managing OCI artifacts via systemd units.

## New Quadlet keys

| Version | File type | Key | Purpose |
|---|---|---|---|
| 5.7 | `.container` | `HttpProxy` | Control HTTP proxy forwarding into container |
| 5.7 | `.pod` | `StopTimeout` | Configure pod stop timeout |
| 5.7 | `.build` | `BuildArg` | Specify build arguments |
| 5.7 | `.build` | `IgnoreFile` | Specify ignore file |
| 5.7 | `.kube` | *(multi-YAML)* | Multiple YAML files in single `.kube` file |
| 5.8 | `.container` | `AppArmor` | Set container's AppArmor profile |

## REST API (5.8+)

Endpoints for managing Quadlets via API:

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/libpod/quadlets` | Install Quadlets |
| `GET` | `/libpod/quadlets/{name}/file` | Print Quadlet file contents |
| `GET` | `/libpod/quadlets/{name}/exists` | Check if Quadlet exists |
| `DELETE` | `/libpod/quadlets` | Remove multiple Quadlets |
| `DELETE` | `/libpod/quadlets/{name}` | Remove a single Quadlet |
