# Service Migrations

Covered batches: `9.8p1`, `3.4.0`, `2025-h1-platform`, `2025-q3-operations`, `2.4`, and `2026-h1-platform`.

## Immediate security upgrades

### Restart OpenSSH after upgrading

After upgrading Arch's `openssh` package to 9.8p1, the still-running daemon cannot accept new connections. Restart it immediately:

```sh
systemctl try-restart sshd
```

For a remote system, retain the current connection until a new connection through the restarted daemon succeeds.

### Upgrade every rsync endpoint

Upgrade all rsync servers and clients to Arch package `3.4.0-1` or newer, then reboot. Give public mirrors particular urgency.

Anonymous read access to a vulnerable server can be sufficient for remote code execution. A compromised server can also read or overwrite arbitrary files on connected vulnerable clients, including SSH keys, OpenPGP keys, and shell startup files.

## Database and monitoring services

### Migrate Redis to Valkey

Valkey replaced `redis` in `[extra]` under batch `2025-h1-platform`. Redis remained in the repository for only about 14 days from 2025-04-17, then moved to the AUR, became deprecated, and stopped receiving Arch updates.

Migrate Arch-managed Redis deployments to Valkey rather than treating the AUR package as a maintained continuation.

### Consolidate Zabbix accounts

Starting with `zabbix>=7.4.1-2`, every Zabbix component uses the shared `zabbix` account supplied by the new `zabbix-common` split package. The shared account replaces accounts previously supplied by `zabbix-server`, `zabbix-proxy`, `zabbix-agent`, and `zabbix-web-service`.

Packaged configuration and systemd units migrate automatically. Manually update ownership and account references for custom:

- PSK files
- metric and report scripts
- sudoers rules
- configuration and other service files

Complete the changes before removing obsolete accounts. Otherwise, services and user parameters may fail.

## Mail services

### Migrate Dovecot 2.3 configuration

Dovecot 2.4 cannot read any configuration from 2.3 or earlier and will not start until the configuration is migrated.

If migration is not yet possible, or the deployment requires replication removed in 2.4, install Arch's `dovecot23` package. Add the applicable `pigeonhole23`, `dovecot23-fts-elastic`, or `dovecot23-fts-xapian` package from `[extra]`. The 2.3 branch continues to receive critical upstream security fixes.

## Firewall services

### Select the intended iptables backend

Under batch `2026-h1-platform`, `iptables` replaces `iptables-nft` and provides the nft backend by default. The legacy backend moves to `iptables-legacy`.

When switching among `iptables-nft`, `iptables`, and `iptables-legacy`:

1. Inspect `/etc/iptables/iptables.rules.pacsave` and `/etc/iptables/ip6tables.rules.pacsave`.
2. Restore saved IPv4 and IPv6 rules when required.
3. Test uncommon xtables extensions and any behavior known to require the legacy backend.
4. Retain `iptables-legacy` only where the nft-backed implementation is incompatible.

## DHCP services

### Move Kea from root to its service account

Starting with `kea>=1:3.0.3-6`, all Kea services run as the dedicated `kea` user instead of root. Update ownership of existing runtime state and restart all Kea services after upgrading:

```sh
chown kea: /var/lib/kea/* /var/log/kea/* /run/lock/kea/logger_lockfile
systemctl try-restart kea-ctrl-agent.service kea-dhcp{4,6,-ddns}.service
```

Add accounts to the `kea` group when they must interact with lease files under `/var/lib/kea`, logs under `/var/log/kea`, or configuration under `/etc/kea`.

## HTTP cache services

### Migrate Varnish to Vinyl Cache

Arch replaces `varnish` with `vinyl-cache`. Every `varnish` reference in binaries and directories is renamed to `vinyl`.

Perform the migration deliberately:

1. Rename `/etc/varnish` to `/etc/vinyl-cache`.
2. Rename `/var/lib/varnish` to `/var/lib/vinyl-cache`.
3. Correct ownership of state files.
4. Replace the `varnish` and `varnishlog` accounts with `vinyl` and `vinyllog`; leave `vcache` unchanged.
5. Disable `varnish.service` and `varnishncsa.service`.
6. Enable `vinyl-cache.service` and `vinylncsa.service`.

The old `varnish` package has left `[extra]`. No Arch package for the now-separate upstream Varnish project is currently planned.
