# Security and networking

Unless noted otherwise, the upgrade behavior in this reference comes from
`13-known-issues`.

## Preserve remote access

### Upgrade OpenSSH before a remote OS upgrade

An interrupted SSH-supervised upgrade can leave a Bookworm host unreachable. Install
`openssh-server` version `1:9.2p1-2+deb12u7` or later from `stable-updates` before
starting; that fix is included in Debian 12.12 and later.

Keep another recovery path available when possible, and validate a second SSH session
before changing packages.

### Replace removed compatibility mechanisms

New SSH sessions no longer read `~/.pam_environment` by default. Move required
variables to shell startup files or another suitable mechanism.

DSA keys cannot be re-enabled as of OpenSSH 9.8p1. Replace them. Reserve the `ssh1`
command from `openssh-client-ssh1` for devices offering no other key type.

## Preserve encrypted storage

### Install systemd-cryptsetup

Automatic discovery and mounting of encrypted filesystems moved to
`systemd-cryptsetup`. It is normally pulled in by systemd's Recommends, but verify the
package is installed before rebooting an upgraded encrypted host.

### Pin plain-mode dm-crypt parameters

Plain dm-crypt does not store the parameters used to create a device. Trixie's new
defaults are `cipher=aes-xts-plain64` and `hash=sha256`; using them on old data can
make that data look random.

For a device created with Bookworm defaults, put the following parameters in
`/etc/crypttab` before rebooting:

```text
cipher=aes-cbc-essiv:sha256,size=256,hash=ripemd160
```

Verify the existing configuration rather than attempting repair or reinitialization
when data becomes unreadable after an upgrade.

## Move sysctl policy and verify ping

`systemd-sysctl` no longer reads `/etc/sysctl.conf`. Move local settings into
`/etc/sysctl.d/*.conf`, and review `/usr/lib/sysctl.d/50-default.conf` supplied by
`linux-sysctl-defaults`.

`iputils-ping` uses ICMP datagram sockets instead of `CAP_NET_RAW`. Unprivileged ping
therefore depends on `net.ipv4.ping_group_range`, which is normally supplied by the
defaults package. Test the intended service users and containers explicitly.

## Keep network interfaces addressable

Systemd 257 can rename interfaces using the `i40e` driver or firmware whose ACPI
`_SUN` object is newly honored. After `apt full-upgrade` and before reboot, test each
critical interface:

```bash
udevadm test-builtin net_setup_link /sys/class/net/<interface>
```

If a name would change, pin the old name with a `systemd.link` file and verify the
network configuration refers to it.

## Migrate TLS and IPsec configuration

### OpenLDAP

`libldap2` and `slapd` use OpenSSL rather than GnuTLS. Available TLS options and their
behavior differ. If no CA certificates are configured, the system trust store loads
automatically; configure trusted CAs explicitly when that broad trust is unwanted.

### strongSwan

The replacement stack uses `charon-systemd`, `swanctl`, and
`/etc/swanctl/conf.d` rather than the legacy `ipsec` command and `/etc/ipsec.conf`.
Existing installations continue to work while `charon-daemon` remains installed, but
the `strongswan` metapackage now selects the new dependencies. Port custom deployment
and management scripts deliberately.

## Refresh Secure Boot databases

This Bookworm maintenance change is from `12.15`.

Bookworm's `fwupd` 2.0.20 can update the UEFI Secure Boot CA, KEK, and DBX databases.
Apply the needed database updates because the 2013 UEFI Secure Boot CA used to sign
bootloaders has expired.
