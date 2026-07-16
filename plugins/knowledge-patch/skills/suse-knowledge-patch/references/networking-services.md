# Networking and Network Services

Use this reference for interface configuration, firewalls, remote services, DNS, DHCP, mail, NFS, and hostname behavior.

## Interface configuration

### NetworkManager and names

Leap 16 supports only NetworkManager for network configuration. systemd predictable interface names replace Leap 15's persistent naming scheme; use `systemd.link` files for complex naming requirements instead of relying on legacy names.

### Bonding replaces teaming

SLES 16 removes and does not support `teamd`, `libteam-tools`, or `NetworkManager-team`. Migrate teaming configurations, including LACP, to NetworkManager's built-in bonding support.

### Literal hostname handling

SLES 16 applies `/etc/hostname` literally instead of silently stripping the domain from an FQDN. Prefer an unqualified hostname because an FQDN can cause application-specific surprises.

## Firewall behavior

### Docker and libvirt

When Docker breaks networking for Leap 16 libvirt guests, select the iptables backend in `/etc/libvirt/network.conf`:

```conf
firewall_backend = "iptables"
```

Persist `virbr0` in the libvirt zone and restart libvirt:

```sh
firewall-cmd --add-interface=virbr0 --zone=libvirt --permanent
firewall-cmd --reload
systemctl restart libvirtd
```

### SLES 15 SP6 legacy firewalld

Prefer `firewalld` 2.x. If slow reloads require the maintained 1.3.4 fallback, downgrade and lock it, then restart because package replacement leaves the live firewall and configuration in place:

```sh
zypper refresh
zypper install --oldpackage --allow-downgrade 'firewalld < 2'
zypper addlock 'firewalld >= 2'
systemctl restart firewalld.service
```

Return to the current series by removing the lock, updating, and restarting:

```sh
zypper removelock 'firewalld >= 2'
zypper refresh
zypper update
systemctl restart firewalld.service
```

### Many-interface limitation

On SLES 16, restarting firewalld after assigning many interfaces can be slow or time out with `org.freedesktop.DBus.Error.NoReply`. Recognize that signature as a known interface-scaling limitation rather than generic D-Bus failure.

## Routing, DNS, DHCP, and mail

### FRRouting

Use SLES 15 SP6 `frr` as the maintained successor to unmaintained Quagga. Configuration, including `vtysh`, is mostly backward compatible, but review FRR changes and additions during migration.

### BIND

SLES 15 SP6 moves BIND from 9.16 to 9.18, removes configuration options, and adds DNS-over-TLS, DNS-over-HTTPS, and OpenSSL 3 support. Validate `named` configuration against 9.18 before upgrading.

For SLES 15 SP7, the release documentation disagrees with itself: the GA package comparison records BIND 9.20.3 and MariaDB 11.4.5, while the release-note prose describes BIND 9.18 and MariaDB 11.8 LTS. The conflict is unresolved in the documentation, so query enabled repositories or installed RPMs before version-specific work.

### Kea DHCP

SLES 15 SP7 supplies `kea` 2.6.1 as the successor to end-of-life ISC `dhcpd`. Migrate server configuration and service automation; changing only the package name is insufficient.

### Dovecot

Leap 16 Dovecot 2.4 configuration is incompatible with 2.3. Convert it manually during upgrade and do not start the new service with an unreviewed 2.3 configuration.

### NFS protocol boundaries and encryption

On SLES 15 SP6, NFSv4 over IPv6 is supported only for clients; an NFSv4 server over IPv6 is unsupported. NFSv2 remains enabled but deprecated in SLE 15 and is disabled and removed in SLE 16.

Leap 16 supports NFS over TLS, allowing NFS storage traffic to use native transport encryption instead of requiring an external encryption layer.

## Installer networking

Agama's UI can edit only existing NetworkManager connections. Use its CLI or a configuration file to create a connection for an unconfigured device. See [installation-migration.md](installation-migration.md) for early-boot NTP and netboot parameters.

## Compatibility files

Leap 16 provides `/etc/services` only as a dummy file. Do not assume the file already exists when software attempts to append service entries.
