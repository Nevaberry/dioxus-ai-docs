# Server Packages

## Valkey replacing Redis (2025-04-17)

Redis was dropped from the official repos due to its license change (BSD-3-Clause to RSALv2/SSPLv1). Valkey, the BSD-licensed fork, is the replacement. It's API-compatible and a drop-in replacement.

```bash
# Install
pacman -S valkey

# CLI and server binaries are renamed
valkey-cli ping # was: redis-cli ping
valkey-server   # was: redis-server

# systemd service
systemctl enable --now valkey.service # was: redis.service
```

The old `redis` package is in the AUR only. Scripts and configs referencing `redis-cli`, `redis-server`, or `redis.service` need updating.

## Zabbix 7.4.1-2 — Unified user (2025-08-04)

The separate system users (`zabbix-server`, `zabbix-proxy`, `zabbix-agent`, `zabbix-web-service`) are removed. All Zabbix components now run as a single shared `zabbix` user, provided by the new `zabbix-common` split package.

Main config files and systemd units are migrated automatically. **Manual fix needed** for custom files referencing old users:

```bash
# Update ownership of PSK files, custom scripts, etc.
chown zabbix:zabbix /etc/zabbix/zabbix_agentd.psk
# Update any sudoers rules from old user to 'zabbix'
# e.g., change "zabbix-agent ALL=..." to "zabbix ALL=..."
```

After migrating, remove the obsolete user accounts (`userdel zabbix-server`, etc.).

## Dovecot 2.4 — Breaking config migration (2025-10-31)

Dovecot 2.4 configs are incompatible with 2.3. The service **will not start** until you migrate your config. See [upstream migration guide](https://doc.dovecot.org/latest/installation/upgrade/2.3-to-2.4.html).

The replication feature was **removed** in 2.4.

If you can't migrate yet, legacy packages are available in [extra]:

```bash
# Stay on 2.3 temporarily
pacman -S dovecot23 pigeonhole23
# Also available: dovecot23-fts-elastic, dovecot23-fts-xapian
```

## .NET packages 9.0 to 10.0 (2025-12-11)

The unversioned packages (`dotnet-sdk`, `dotnet-runtime`, `aspnet-runtime`, etc.) jumped to .NET 10.0. pacman may fail with `could not satisfy dependencies` during upgrade.

If you need to keep 9.0 alongside 10.0:

```bash
# Install the versioned 9.0 package, then remove the unversioned one
pacman -Syu aspnet-runtime-9.0
pacman -Rs aspnet-runtime
# Same pattern for dotnet-sdk-9.0, dotnet-runtime-9.0, etc.
```
