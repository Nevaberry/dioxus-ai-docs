# Security and networking

## Preserve SSH access during remote upgrades

An interrupted SSH-supervised upgrade can leave the host unreachable. Before upgrading
remotely, install `openssh-server` version `1:9.2p1-2+deb12u7` or later from
`stable-updates`. That version is included in Debian 12.12 and later.

## OpenSSH compatibility removals

New SSH sessions no longer read `~/.pam_environment` by default. Move required
variables to shell startup files or another mechanism.

DSA keys cannot be re-enabled as of OpenSSH 9.8p1. Replace them. For a device that
offers no other key type, use the `ssh1` command from `openssh-client-ssh1` only as a
last-resort compatibility path.

## OpenSSH GSS-API packaging

Debian's main OpenSSH packages will drop GSS-API authentication and key exchange in
Forky. A Trixie system that relies on `GSSAPI*` options should install the currently
transitional `openssh-client-gssapi` or `openssh-server-gssapi` package so the
separately built implementation is retained later.

## Encrypted filesystem discovery

Automatic discovery and mounting of encrypted filesystems moved to the new
`systemd-cryptsetup` package. Systemd normally installs it through Recommends, but
verify that it is present before rebooting an upgraded encrypted system.

## Plain-mode dm-crypt parameters

Trixie changes plain-mode defaults to `cipher=aes-xts-plain64` and `hash=sha256`.
Unlike LUKS, plain mode does not store these parameters. Applying different parameters
can make existing data appear random.

For a device created with Bookworm defaults, record the following in `/etc/crypttab`:

```text
cipher=aes-cbc-essiv:sha256,size=256,hash=ripemd160
```

## sysctl and unprivileged ping

`systemd-sysctl` no longer reads `/etc/sysctl.conf`. Put local settings in
`/etc/sysctl.d/*.conf` and review `/usr/lib/sysctl.d/50-default.conf` from
`linux-sysctl-defaults`.

`iputils-ping` now uses ICMP datagram sockets instead of `CAP_NET_RAW`. Unprivileged
access depends on `net.ipv4.ping_group_range`, normally supplied by
`linux-sysctl-defaults`.

## Network-interface names

Interface names can change on systems using the `i40e` driver or firmware that exposes
the ACPI `_SUN` object newly honored by systemd 257.

After `apt full-upgrade` and before reboot, test each important interface:

```bash
udevadm test-builtin net_setup_link /sys/class/net/<interface>
```

Pin the old name with a `systemd.link` file when required.

## OpenLDAP TLS provider

`libldap2` and `slapd` now use OpenSSL rather than GnuTLS. This changes available TLS
options and their behavior. When no CA certificates are configured, the system trust
store is loaded automatically; explicitly configure trusted CAs to avoid that default.

## strongSwan service transition

The replacement stack uses `charon-systemd`, `swanctl`, and `/etc/swanctl/conf.d`
instead of the legacy `ipsec` command and `/etc/ipsec.conf`.

Existing installations keep working while `charon-daemon` remains installed, but the
`strongswan` metapackage now selects the new dependencies.

## Incomplete `sg3-utils` udev properties

Because of a Trixie `sg3-utils` bug, SCSI devices do not receive all properties normally
injected by `sg3-utils-udev`. Migrate away from dependencies on those properties or be
prepared for failures after reboot.

## sudo features scheduled for removal

Forky will remove `sudo-ldap`. Migrate to `libsss-sudo` before that upgrade or privilege
escalation rules may disappear. The `sudo_logsrvd` input/output logging service may also
be removed unless it gains a maintainer.
