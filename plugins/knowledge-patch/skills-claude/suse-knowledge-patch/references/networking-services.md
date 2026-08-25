# Networking and Network Services

## Network configuration

### NetworkManager and interface names (`leap-16.0-guide`)

NetworkManager is the only supported Leap network configuration stack. systemd
predictable names replace Leap 15's persistent naming scheme; use `systemd.link`
files for complex naming instead of relying on legacy interface names.

### Bonding replaces teaming

SLES 16 removes and does not support `teamd`, `libteam-tools`, or
`NetworkManager-team`. Convert teaming configurations, including LACP, to
NetworkManager's built-in bonding support.

### Literal hostnames

SLES 16 applies `/etc/hostname` exactly as written instead of silently removing
the domain from an FQDN. Prefer an unqualified hostname to avoid
application-specific FQDN handling.

## Firewall behavior

### Docker and libvirt on Leap 16 (`leap-16.0-guide`)

When Docker breaks guest networking, select libvirt's iptables backend in
`/etc/libvirt/network.conf`, persist `virbr0` in the `libvirt` zone, and restart
libvirt:

```conf
firewall_backend = "iptables"
```

```sh
firewall-cmd --add-interface=virbr0 --zone=libvirt --permanent
firewall-cmd --reload
systemctl restart libvirtd
```

### Maintained legacy firewalld on SLES 15 SP6

firewalld 2.x remains preferred. Deployments affected by slow 2.x reloads may
use maintained 1.3.4 temporarily. The transaction preserves the live firewall
and configuration, so restart afterward:

```sh
zypper refresh
zypper install --oldpackage --allow-downgrade 'firewalld < 2'
zypper addlock 'firewalld >= 2'
systemctl restart firewalld.service
```

Return to the current series with:

```sh
zypper removelock 'firewalld >= 2'
zypper refresh
zypper update
systemctl restart firewalld.service
```

### Many-interface restart timeout

On SLES 16, restarting firewalld after assigning many interfaces can be slow or
time out with `org.freedesktop.DBus.Error.NoReply`. Recognize this as a known
interface-scaling limitation rather than generic D-Bus failure.

### Minimal-image firewall tools (`16.0-rev-2026-08-04`)

SLES Minimal images include both `iptables` and `nftables`; automation need not
install these packages first.

## Routing, DNS, DHCP, and mail

### FRRouting replaces Quagga

SLES 15 SP6 supplies `frr` as the maintained routing-daemon path. Configuration,
including `vtysh`, is mostly backward compatible with Quagga, but migrations
must be reviewed for FRR changes and additions.

### BIND migration and repository reality

SLES 15 SP6 moves BIND from 9.16 to 9.18. It removes configuration options and
adds DNS-over-TLS, DNS-over-HTTPS, and OpenSSL 3 support; validate `named`
configuration against 9.18 before upgrade.

SLES 15 SP7 records disagree: the GA comparison names BIND 9.20.3, while
release-note prose names 9.18. Query enabled repositories or installed RPMs
before using version-specific guidance. The same evidence conflict exists for
MariaDB 11.4.5 versus 11.8 LTS; see [packages-runtimes.md](packages-runtimes.md).

### Kea replaces ISC DHCP

SLES 15 SP7 supplies Kea 2.6.1 as the successor to end-of-life ISC `dhcpd`.
Migrate DHCP configuration and service automation; a package rename is not a
complete migration.

### Dovecot 2.4 configuration (`leap-16.0-guide`)

Dovecot 2.4 configuration is incompatible with 2.3. Convert it manually during
the Leap 16 upgrade and do not start 2.4 with an unreviewed 2.3 configuration.

## NFS boundaries

### NFS over TLS (`leap-16.0-guide`)

NFS can protect storage traffic with TLS; transport encryption need not be
provided entirely outside NFS.

### IPv6 and protocol versions on SLE 15 SP6

NFSv4 over IPv6 is supported for clients only, not servers. NFSv2 remains
enabled but deprecated on SLE 15 and is disabled and removed on SLE 16.

## Protocol deprecations (`16.0-rev-2026-08-04`)

DCCP and UDP-Lite are deprecated on SLES 16.0. Plan to migrate deployments that
depend on either protocol.
