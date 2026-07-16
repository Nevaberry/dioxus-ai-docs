# Upgrade foundations

## Check boot-partition capacity

Systems installed with Debian 10 or earlier are especially likely to have undersized
boot partitions. Before upgrading, ensure a separate `/boot` is at least 768 MB with
roughly 300 MB free.

An LVM-backed `/boot` can be enlarged with `lvextend`.

## Interpret usrmerge warnings correctly

During the upgrade, warnings that `dpkg` cannot delete old nonempty directories under
paths such as `/lib/firmware` are a consequence of usrmerge finalization and can be
ignored.

Do not generalize this exception to unrelated `dpkg` errors.

## Sequence high-risk work

Before the operating system upgrade:

1. Prepare OpenSSH for remote access and verify boot-partition space.
2. Record plain-mode dm-crypt parameters and ensure encrypted mounts have their needed
   package.
3. Convert RabbitMQ queues, cleanly stop MariaDB, port Dovecot configuration, and
   reserve Bacula migration space where applicable.
4. Port custom network, WirePlumber, strongSwan, OpenLDAP, Samba, and libvirt setup.

After `apt full-upgrade` but before reboot:

1. Predict important interface names with `udevadm test-builtin net_setup_link`.
2. Review the installed libvirt and Samba feature packages.
3. Verify `systemd-cryptsetup` on systems with encrypted filesystems.

Use the topic references for the exact requirements; this sequence does not replace
their service-specific recovery planning.

## Complete migrations before Forky

### Container and build tooling

- `libnss-docker` depends on a Docker API removed after Engine 26. Migrate away from
  that dependency.
- Replace `sbuild-debian-developer-setup` with `sbuild --chroot-mode=unshare`.
- Move Debian LXD users to Incus with tools in `incus-extra`.

### Input methods

Replace fcitx 4 with `fcitx5`.

### DHCP software

- NetworkManager and systemd-networkd need no ISC DHCP client.
- `ifupdown` can use `dhcpcd-base`.
- Servers should move from ISC DHCP to Kea.

Also complete the sudo LDAP and OpenSSH GSS-API package migrations described in
[security-networking.md](security-networking.md).
