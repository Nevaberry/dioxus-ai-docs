# Docker Compose New Features

Covers Compose v2.30 through v2.38 (October 2024 – June 2025).

## Service Lifecycle Hooks (v2.30)

Run commands after container start and before stop:

```yaml
services:
  web:
    image: myapp
    post_start:
      - command: /app/warmup.sh
    pre_stop:
      - command: /app/drain.sh
```

## Watch Enhancements (v2.32–v2.34)

### Restart action (v2.32)

Trigger a container restart on file changes:
```yaml
services:
  web:
    develop:
      watch:
        - action: restart
          path: ./config
```

### Sync+exec action (v2.32)

Sync files then run a command in the container:
```yaml
services:
  web:
    develop:
      watch:
        - action: sync+exec
          path: ./src
          target: /app/src
          exec:
            command: npm run build
```

### Include filter (v2.34)

Specify which files the watch action should consider:
```yaml
services:
  web:
    develop:
      watch:
        - action: sync
          path: ./src
          target: /app/src
          include:
            - "**/*.ts"
            - "**/*.tsx"
```

## Build with Bake (v2.32)

Route `docker compose build` through `docker buildx bake` for faster builds:
```bash
COMPOSE_BAKE=1 docker compose build
```

## Refresh Pull Policy (v2.34)

Always re-pull images even if they exist locally:
```yaml
services:
  web:
    image: myapp:latest
    pull_policy: refresh
```

## `docker compose publish` (v2.34)

Promoted from alpha. Publishes Compose applications as OCI artifacts. Includes Defang secret detector integration to identify leaks before publishing.

```bash
docker compose publish myregistry/myapp:v1
```

## `--env-from-file` flag (v2.34)

```bash
docker compose run --env-from-file .env.test web pytest
```

## CDI Device Requests (v2.30)

```yaml
services:
  gpu-worker:
    image: myworkload
    devices:
      - nvidia.com/gpu=all
```

## Bind Recursive Mounts (v2.30)

```yaml
services:
  web:
    volumes:
      - type: bind
        source: ./data
        target: /data
        bind:
          recursive: true
```

## OCI Compose Artifacts (v2.30)

Use published OCI artifacts directly with `-f`:
```bash
docker compose -f oci://registry/myapp:v1 up
```

## Raw `env_file` Format (v2.30)

Support for raw (unprocessed) environment file format.

## `docker compose generate` (v2.30, alpha)

Generate Compose files from existing resources.

## `docker compose export` (v2.30)

Export service filesystem as a tarball:
```bash
docker compose export web > web-fs.tar
```

---

## Service Provider Plugins (v2.36)

External binaries can implement the `service.provider` key to extend Compose with custom service types:

```yaml
services:
  myservice:
    provider:
      type: my-custom-provider
      options:
        key: value
```

The provider binary is discovered from PATH and implements a defined interface.

## Network Interface Name (v2.36)

Set custom interface name for a network endpoint:
```yaml
services:
  web:
    networks:
      frontend:
        interface_name: eth-frontend
```

## `COMPOSE_PROGRESS` Environment Variable (v2.36)

Control progress display output format.

## Build Check (v2.36)

Validate build configuration without actually building:
```bash
docker compose build --check
```

---

## `models:` Top-Level Key (v2.38)

Docker AI Models integration via Compose:
```yaml
models:
  my-model:
    model: ai/my-model:latest
    context_length: 8192

services:
  app:
    image: myapp
    depends_on:
      - my-model
```

## `docker compose volumes` Command (v2.38)

List volumes associated with the Compose project:
```bash
docker compose volumes
```

## `--use-api-socket` Support (v2.38)

Mount Docker socket for services declaring API socket access:
```yaml
services:
  manager:
    image: portainer/portainer
    # --use-api-socket mounts /var/run/docker.sock
```

## Containers Recreated on Volume Change (v2.32)

Containers are now automatically recreated when their volume configuration changes in the Compose file.
