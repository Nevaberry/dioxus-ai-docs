# Infrastructure

## TLS/mTLS for remote connections (5.7+)

The remote client and `podman system service` now support TLS and mTLS encryption, including client certificate authentication. `podman system connection add` can create TLS-encrypted TCP connections.

## BoltDB → SQLite migration

BoltDB removal is planned for Podman 6.0. Migration timeline:

| Version | Behavior |
|---|---|
| 5.6 | Deprecation warning added for BoltDB users |
| 5.7 | BoltDB warnings visible by default |
| 5.8 | Auto-migrates BoltDB databases to SQLite on reboot |

Force manual migration:
```bash
podman system migrate --migrate-db
```

## Rosetta disabled by default (5.6+)

Rosetta support in `podman machine` VMs disabled by default due to issues with newer Linux kernels.

## Breaking: Compat Image Inspect API (5.7+)

The `ContainerConfig` field is removed from the compat image inspect endpoint (matching Docker v1.45 API). Use the `Config` field instead.
