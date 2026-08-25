# Networking and Network Services

## NetworkManager and interface configuration

NetworkManager is the only supported Leap 16 network configuration stack.
systemd predictable names replace the Leap 15 persistent naming scheme; use
`systemd.link` files for complex requirements rather than relying on legacy
names. (leap-16.0-guide)

SLES 16 removes `teamd`, `libteam-tools`, and `NetworkManager-team`. Convert
teaming, including LACP, to NetworkManager's built-in bonding support.

DCCP and UDP-Lite are deprecated in the later SLES 16.0 revision. Plan to
migrate any dependent workloads. SLES Minimal images now contain both
`iptables` and `nftables`, so minimal-image automation can use them without an
extra package installation. (16.0-rev-2026-08-04)

## firewalld and virtualization networking

When Docker disrupts networking for libvirt guests, choose libvirt's iptables
backend in `/etc/libvirt/network.conf`, assign `virbr0` permanently to the
`libvirt` zone, and restart libvirt:

```conf
firewall_backend = "iptables"
```

```sh
firewall-cmd --add-interface=virbr0 --zone=libvirt --permanent
firewall-cmd --reload
systemctl restart libvirtd
```

On affected SLES 15 SP6 systems with slow firewalld 2.x reloads, maintained
1.3.4 is available as a legacy fallback, although 2.x remains preferred. The
transaction leaves the live firewall and configuration in place, so restart
after downgrading and locking:

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

On SLES 16, a restart after assigning many interfaces can take a long time or
time out with `org.freedesktop.DBus.Error.NoReply`. Recognize that signature as
the known interface-scaling limitation rather than generic D-Bus failure.

## NFS

Leap 16 supports NFS traffic encryption with TLS, so transport encryption need
not be supplied outside NFS.

On SLE 15, NFSv4 over IPv6 is supported for clients only; serving NFSv4 over
IPv6 is unsupported. NFSv2 is enabled but deprecated in SLE 15 and disabled and
removed in SLE 16.

## Routing, DNS, DHCP, and mail

FRRouting (`frr`) replaces unmaintained Quagga. Its configuration, including
`vtysh`, is mostly backward compatible, but review migrations for FRR changes
and additions.

SLES 15 SP6 moves BIND from 9.16 to 9.18, removing some options while adding
DNS-over-TLS, DNS-over-HTTPS, and OpenSSL 3 support. Validate `named`
configuration against the installed major version before upgrade. SLES 15 SP7
records disagree between package comparison (`bind` 9.20.3) and release prose
(BIND 9.18), so query the enabled repository or installed RPM rather than
assuming either record.

Leap 16 Dovecot 2.4 configuration is incompatible with 2.3. Convert it manually
before starting the upgraded service.

SLES 15 SP7 supplies Kea 2.6.1 as the successor to end-of-life ISC `dhcpd`.
Migrate DHCP configuration and service automation rather than merely replacing
the package name.
