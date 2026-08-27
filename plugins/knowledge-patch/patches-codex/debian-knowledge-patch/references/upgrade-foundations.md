# Upgrade foundations

Use this checklist to establish a recoverable upgrade path and complete
migrations that will otherwise become breaking changes in the next release.

## Preflight

### Preserve remote access

For an SSH-supervised upgrade, install `openssh-server`
`1:9.2p1-2+deb12u7` or later from Bookworm `stable-updates` before changing the
system. Keep the existing session open until the upgraded daemon and a new
login have been tested. Read
[security-networking.md](security-networking.md) for OpenSSH key, environment,
and GSS-API compatibility changes.

### Size a separate boot filesystem

A separate `/boot` must be at least 768 MB with about 300 MB free. Systems
originally installed with Debian 10 or earlier are especially likely to be
undersized. Enlarge an LVM-backed `/boot` with `lvextend` where necessary and
verify the filesystem has grown before continuing.

### Inventory hard blockers

Before `apt full-upgrade`, identify:

- encrypted filesystems and their exact dm-crypt parameters;
- RabbitMQ, MariaDB, Dovecot, and Bacula instances;
- local settings still stored in `/etc/sysctl.conf`;
- network configuration bound to current interface names;
- third-party packages and packages no longer supplied;
- custom libvirt, Samba, WirePlumber, strongSwan, and OpenLDAP configuration;
- legacy timezone identifiers used inside applications or databases.

Write a rollback or recovery procedure for each matching item. The detailed
requirements are in the other topic references.

## Upgrade sequence

1. Back up system configuration and stateful application data, then verify the
   restore path.
2. Complete service prerequisites such as RabbitMQ queue conversion, a clean
   MariaDB shutdown, and Dovecot configuration porting.
3. Correct SSH, `/boot`, encrypted-storage, sysctl, and package prerequisites.
4. Run the package upgrade while retaining recovery access.
5. After `apt full-upgrade` and before reboot, test predicted network-interface
   names with `udevadm test-builtin net_setup_link`.
6. Confirm `systemd-cryptsetup`, required split packages, and all boot-critical
   packages are installed.
7. Reboot only after validating the boot, storage, and network configuration
   and preserving an alternate recovery path.

## usrmerge warnings

During the upgrade, `dpkg` can warn that it cannot delete old nonempty
directories under paths such as `/lib/firmware`. These warnings result from
usrmerge finalization and can be ignored when they match this known pattern.
Do not generalize that exception to unrelated `dpkg` errors.

The system assumes a fully merged `/usr`; `usrmerge` and `usr-is-merged` are
removable dummy packages.

## Migrations to finish before the next release

### sudo and privilege policy

Move LDAP-backed sudo rules from `sudo-ldap` to `libsss-sudo`; otherwise the
rules may disappear when `sudo-ldap` is removed. The `sudo_logsrvd` I/O logging
service may also be removed if it does not gain a maintainer, so do not make a
new long-term dependency on it without a contingency.

### OpenSSH GSS-API

If configuration relies on `GSSAPI*` authentication or key-exchange options,
install `openssh-client-gssapi` or `openssh-server-gssapi` as appropriate. The
main OpenSSH packages are expected to drop those features, while the
transitional packages retain the separately built implementation.

### Input methods, containers, and build environments

- Replace fcitx 4 with `fcitx5`.
- Move Debian LXD deployments to Incus using the migration tools in
  `incus-extra`.
- Replace `sbuild-debian-developer-setup` with
  `sbuild --chroot-mode=unshare`.
- Remove dependencies on `libnss-docker`; its required Docker API disappears
  after Engine 26.

### DHCP clients and servers

Choose DHCP software by network stack:

- NetworkManager and systemd-networkd need no ISC DHCP client.
- `ifupdown` can use `dhcpcd-base`.
- Servers should move from ISC DHCP to Kea.

Do not install an ISC client merely because an older host had one; first
identify which component actually manages each interface.

The breaking risks, sequence constraints, warnings, and future migrations in
this reference are derived from batch `13-known-issues`.
