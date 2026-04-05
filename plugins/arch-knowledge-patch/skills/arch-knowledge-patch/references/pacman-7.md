# pacman 7.0.0 (2024-09-14)

## Privilege-separated downloads via `alpm` user

pacman now downloads packages as a dedicated unprivileged user instead of as root. A new `alpm` system user/group is created during upgrade.

**Breaking for local repos**: The download user needs read access to local repo files. Fix:

```bash
chown :alpm -R /path/to/local/repo
# Ensure +x on directories so alpm user can traverse
```

After upgrading, merge `.pacnew` files (`/etc/pacman.conf`, `/etc/makepkg.conf`) to pick up new defaults.

## Git source checksum change

Repos using `.gitattributes` may produce different checksums due to improved checksum stability. One-time `PKGBUILD` checksum update may be needed for git sources.
