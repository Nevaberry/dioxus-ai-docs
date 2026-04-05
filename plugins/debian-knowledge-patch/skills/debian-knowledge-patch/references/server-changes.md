# Debian 13 (Trixie) Server Changes

## RabbitMQ

### HA Queues Removed

High-availability (HA) queues no longer supported. Must switch to **quorum queues** before upgrading.

OpenStack users: beginning with "Caracal" release in trixie, only quorum queues supported.

### No Direct Upgrade Path

No easy upgrade from bookworm's RabbitMQ to trixie's. See [bug 1100165](https://bugs.debian.org/1100165).

Recommended path: completely wipe database and restart:

```bash
# After trixie upgrade:
rm -rf /var/lib/rabbitmq/mnesia
systemctl restart rabbitmq-server
```

## MariaDB 10.11 -> 11.8

### Clean Shutdown Required

MariaDB does not support crash recovery across major versions. If 10.11 crashed, you must restart with 10.11 binaries for recovery before upgrading to 11.8.

```bash
# Before upgrading:
systemctl stop mariadb
# Verify clean shutdown in logs
# Then proceed with apt upgrade
```

## Key Package Version Changes

| Package | Bookworm (12) | Trixie (13) |
|---------|--------------|-------------|
| Kernel | 6.1 | 6.12 |
| Python 3 | 3.11 | 3.13 |
| GCC | 12.2 | 14.2 |
| OpenSSH | 9.2p1 | 10.0p1 |
| OpenSSL | 3.0 | 3.5 |
| systemd | 252 | 257 |
| PostgreSQL | 15 | 17 |
| MariaDB | 10.11 | 11.8 |
| PHP | 8.2 | 8.4 |
| Perl | 5.36 | 5.40 |
| Rustc | 1.63 | 1.85 |
| LLVM/Clang | 14 (default) | 19 (default) |
| Samba | 4.17 | 4.22 |
| GIMP | 2.10 | 3.0 |
| curl/libcurl | 7.88 | 8.14 |
| GnuPG | 2.2.40 | 2.4.7 |
| Emacs | 28.2 | 30.1 |
| OpenJDK | 17 | 21 |
| OpenLDAP | 2.5.13 | 2.6.10 |
| Postfix | 3.7 | 3.10 |
| Nginx | 1.22 | 1.26 |
| Apache | 2.4.62 | 2.4.65 |
| Cryptsetup | 2.6 | 2.7 |
| Vim | 9.0 | 9.1 |
| BIND | 9.18 | 9.20 |
| Exim | 4.96 | 4.98 |
| LibreOffice | 7.x | 25 |
| Inkscape | 1.2 | 1.4 |
| glibc | 2.36 | 2.41 |

## curl HTTP/3 and wcurl

curl and libcurl support HTTP/3:

```bash
curl --http3 https://example.com
curl --http3-only https://example.com
```

New `wcurl` command (wget alternative using curl):

```bash
wcurl https://example.com/file.tar.gz
```

## Desktop Environment Versions

- GNOME 48
- KDE Plasma 6.3 (first Debian release with Plasma 6)
- LXQt 2.1.0
- Xfce 4.20
- LXDE 13

### Plasma 6 Details

- Qt 6.8.2 (up from 6.4.2)
- KDE Frameworks 6.13
- Plasma 6.3.6 (replaces 5.27.5)
- KDE PIM 24.12.3
- Qt 5.15.15 and KF5 5.116 for compatibility (deprecated)
- Krita still on KF5; KF5 removal planned for forky cycle

GNUcash updated to 5.10.
