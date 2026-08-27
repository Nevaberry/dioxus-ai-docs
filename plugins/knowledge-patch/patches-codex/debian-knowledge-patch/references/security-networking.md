# Security and networking

Use this reference before a remote upgrade, an encrypted-storage reboot, or a
network-policy migration.

## Remote upgrade access

### Install the fixed OpenSSH server first

An interrupted SSH-supervised upgrade can leave a system unreachable. Before a
remote upgrade from Bookworm, install `openssh-server`
`1:9.2p1-2+deb12u7` or later from `stable-updates`; this version is included in
Debian 12.12 and later.

Keep an independent recovery route whenever possible. Confirm that the upgraded
daemon starts and that authentication still works before ending the existing
session.

### Migrate OpenSSH compatibility settings

New SSH sessions no longer read `~/.pam_environment` by default. Move required
variables to shell startup files or another mechanism appropriate to the
account and service.

OpenSSH 9.8p1 and later cannot re-enable DSA keys. Replace them. Use the `ssh1`
command from `openssh-client-ssh1` only for a device that offers no other key
type.

### Preserve GSS-API support explicitly

The main OpenSSH packages are expected to drop GSS-API authentication and key
exchange in the next release. Systems that rely on `GSSAPI*` settings should
install the currently transitional `openssh-client-gssapi` or
`openssh-server-gssapi` package, as applicable, so the separately built
implementation remains installed later.

## Encrypted storage

### Require systemd-cryptsetup

Automatic discovery and mounting of encrypted filesystems moved to
`systemd-cryptsetup`. Systemd normally pulls it in through Recommends, but
verify the package is installed before rebooting an upgraded encrypted host.

### Pin legacy plain-mode dm-crypt parameters

Plain-mode dm-crypt does not store its cipher and hash parameters. New defaults
are:

```text
cipher=aes-xts-plain64
hash=sha256
```

For a device created with the previous defaults, record the complete old
parameters in `/etc/crypttab`:

```text
cipher=aes-cbc-essiv:sha256,size=256,hash=ripemd160
```

A parameter mismatch makes valid old data appear random. Verify the original
settings before opening, repairing, or reinitializing the device.

## Kernel and network policy

### Move sysctl configuration

`systemd-sysctl` no longer reads `/etc/sysctl.conf`. Move local settings into
files under `/etc/sysctl.d/` and review
`/usr/lib/sysctl.d/50-default.conf`, supplied by `linux-sysctl-defaults`, for
interactions with distribution defaults.

### Recheck unprivileged ping

`iputils-ping` uses ICMP datagram sockets instead of `CAP_NET_RAW`.
Unprivileged access therefore depends on `net.ipv4.ping_group_range`, normally
set by `linux-sysctl-defaults`. Test the exact service accounts and containers
that need ping rather than assuming prior capabilities still apply.

## Network interface identity

### Test names before reboot

Interface names can change for hardware using the `i40e` driver or firmware
that exposes an ACPI `_SUN` object newly honored by systemd 257. After
`apt full-upgrade` and before reboot, test every required interface:

```bash
udevadm test-builtin net_setup_link /sys/class/net/<interface>
```

If the predicted name changes, pin the old name with a `systemd.link` file and
verify that firewall, bridge, bond, and service configuration agrees.

### Do not depend on incomplete sg3-utils properties

Because of a known `sg3-utils` issue, SCSI devices do not receive every udev
property normally injected by `sg3-utils-udev`. Migrate consumers away from
those properties or prepare for dependent services to fail after reboot.

## TLS and IPsec

### Revalidate OpenLDAP TLS

`libldap2` and `slapd` use OpenSSL rather than GnuTLS. Available TLS options and
their behavior differ. If no CA certificates are configured, the system trust
store loads automatically; configure trusted CAs explicitly where that broader
trust is inappropriate.

### Move strongSwan toward charon-systemd

The replacement stack uses `charon-systemd`, `swanctl`, and
`/etc/swanctl/conf.d` instead of the legacy `ipsec` command and
`/etc/ipsec.conf`. Existing installations continue to work while
`charon-daemon` remains installed, but the `strongswan` metapackage selects the
new dependencies. Port and test custom configuration before removing the
legacy daemon.

## Secure Boot database maintenance

In Debian 12.15, `fwupd` 2.0.20 can update the UEFI Secure Boot CA, KEK, and DBX
databases. Use that support to replace or update trust databases affected by
the expiration of the 2013 UEFI Secure Boot CA that signed bootloaders.

The remote-upgrade, storage, network, and service hazards in this reference are
drawn from batch `13-known-issues` unless a different batch is named.
