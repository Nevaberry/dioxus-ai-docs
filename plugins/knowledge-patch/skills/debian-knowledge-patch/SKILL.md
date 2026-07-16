---
name: debian-knowledge-patch
description: Debian 13.0 compatibility. Use for Debian work.
license: MIT
version: "13.0"
metadata:
  author: Nevaberry
---

# Debian knowledge patch

## Navigate the references

Choose references by the task at hand. Read every relevant file before changing an
upgrade plan, package set, boot configuration, network configuration, or stateful
service.

| Reference | Topics |
| --- | --- |
| [packages-toolchains-desktops.md](references/packages-toolchains-desktops.md) | Core package versions, desktop stacks, compatibility packages, package splits, removals, and replacements |
| [release-platform.md](references/release-platform.md) | Architecture support, ABI changes, filesystem and accounting defaults, boot media, hardware hardening, virtual machines, and support dates |
| [security-networking.md](references/security-networking.md) | Remote upgrade access, OpenSSH, encrypted storage, sysctl, ping, interface naming, TLS, IPsec, sudo, and udev properties |
| [services-data.md](references/services-data.md) | RabbitMQ, MariaDB, Dovecot, Bacula, WirePlumber, and legacy timezone data |
| [upgrade-foundations.md](references/upgrade-foundations.md) | Boot-space checks, usrmerge warnings, upgrade sequencing, and migrations to complete before the next release |

## Triage breaking upgrade risks first

Before approving an in-place upgrade, identify whether the host is:

- reached only through SSH;
- using a separate `/boot`;
- mounting encrypted filesystems, especially plain-mode dm-crypt;
- running RabbitMQ, MariaDB, Dovecot, or Bacula;
- dependent on stable network-interface names or `/etc/sysctl.conf`;
- using a retired architecture or third-party `armel`/`armhf` binaries;
- relying on custom WirePlumber, strongSwan, OpenLDAP, Samba, or libvirt setup;
- carrying packages or commands that no longer exist.

Treat any matching condition as a required migration, verification, or rollback-planning
step. Do not reduce it to a post-upgrade cleanup item.

## Protect remote access and bootability

### Prepare SSH before a remote upgrade

- Install `openssh-server` version `1:9.2p1-2+deb12u7` or later from
  `stable-updates` before starting an SSH-supervised upgrade.
- Do not expect a new SSH session to read `~/.pam_environment`; relocate required
  variables to shell startup files or another suitable mechanism.
- Replace DSA keys. OpenSSH 9.8p1 and later cannot re-enable them.
- Reserve the `ssh1` command from `openssh-client-ssh1` for devices that offer no
  other key type.

### Check `/boot`

- Require a separate `/boot` to be at least 768 MB with about 300 MB free.
- Pay particular attention to systems originally installed with Debian 10 or earlier.
- Enlarge an LVM-backed `/boot` with `lvextend` when necessary.

Read [security-networking.md](references/security-networking.md) and
[upgrade-foundations.md](references/upgrade-foundations.md) before finalizing the
remote-upgrade procedure.

## Preserve encrypted storage

- Verify that `systemd-cryptsetup` is installed before rebooting an upgraded encrypted
  system; automatic discovery and mounting moved into that package.
- Never let new plain-mode dm-crypt defaults silently replace the parameters that
  created existing data.
- For a device made with the previous defaults, pin
  `cipher=aes-cbc-essiv:sha256,size=256,hash=ripemd160` in `/etc/crypttab`.
- Recognize the new plain-mode defaults as `cipher=aes-xts-plain64` and `hash=sha256`.

Plain mode stores no parameters. A mismatch can make valid old data appear random, so
verify the configuration before attempting repair or reinitialization.

## Stage stateful-service migrations

### RabbitMQ

- Convert classic HA queues to quorum queues before upgrading.
- Do not plan a direct broker upgrade from the preceding stable release.
- Preserve or recreate required state before applying Debian's reset procedure, which
  removes `/var/lib/rabbitmq/mnesia` after the OS upgrade and restarts the service.

### MariaDB

- Stop MariaDB cleanly before its major upgrade and confirm `Shutdown complete` in the
  logs.
- If the stop was unclean, recover with 10.11, then stop it cleanly again before moving
  to 11.8. MariaDB 11.8 cannot crash-recover a crashed 10.11 data directory.

### Dovecot and Bacula

- Port and test the incompatible Dovecot 2.4 configuration before the OS upgrade; the
  `replicator` feature is gone.
- Budget hours or days and roughly twice the current database space for a Bacula schema
  migration, plus dump space under `/var/cache/dbconfig-common/backups`.
- Prevent Bacula from exhausting disk space because that can corrupt its database.

Read [services-data.md](references/services-data.md) for the complete service-specific
requirements.

## Reconcile system and network behavior

- Move local sysctl settings from `/etc/sysctl.conf` to `/etc/sysctl.d/*.conf`;
  `systemd-sysctl` no longer reads the former file.
- Review `/usr/lib/sysctl.d/50-default.conf` from `linux-sysctl-defaults`.
- Account for `iputils-ping` using ICMP datagram sockets instead of `CAP_NET_RAW`.
  Unprivileged ping now depends on `net.ipv4.ping_group_range`.
- After `apt full-upgrade` and before reboot, test interface naming with:

```bash
udevadm test-builtin net_setup_link /sys/class/net/<interface>
```

- Pin an old interface name with a `systemd.link` file if `i40e` behavior or newly
  honored ACPI `_SUN` data would rename it.
- Rework custom strongSwan deployment toward `charon-systemd`, `swanctl`, and
  `/etc/swanctl/conf.d`.
- Review OpenLDAP TLS settings because `libldap2` and `slapd` now use OpenSSL and may
  load the system trust store when no CA certificates are configured.

## Reconcile package and configuration splits

- Review libvirt drivers and storage backends after upgrade; each is now a separate
  binary package.
- Install `samba-ad-dc` for Active Directory domain-controller support.
- Install `samba-vfs-ceph` or `samba-vfs-glusterfs` for those backends; most other VFS
  modules are included in `samba`.
- Keep `tzdata-legacy` where a database or service still uses names such as `US/*`.
- Port custom WirePlumber setup to its new configuration system; defaults require no
  action.

Consult [packages-toolchains-desktops.md](references/packages-toolchains-desktops.md)
before substituting a removed package or command. Some removals have targeted
replacements, while others do not.

## Account for architecture and ABI boundaries

- Do not plan an upgrade of an existing `i386` installation. Use `i386` only for
  legacy roles such as chroots and multiarch on `amd64`.
- Treat `mipsel` and `mips64el` as removed.
- Treat `armel` as installer-less and limited to Raspberry Pi 1, Zero, and Zero W with
  Debian kernels, while allowing supported existing systems to upgrade.
- Rebuild and audit third-party software for `armel` and `armhf`: the 64-bit `time_t`
  transition changes many library ABIs without changing sonames and can cause silent
  data loss.
- Keep the legacy time ABI expectation only for `i386`.
- Match ppc64el guest page-size needs to the host kernel and QEMU machine setting.

Read [release-platform.md](references/release-platform.md) for exact platform and
virtual-machine constraints.

## Use the new platform capabilities deliberately

- Expect systemd to mount `/tmp` as tmpfs by default.
- Distinguish fresh installations, which enable cleanup of `/tmp` and `/var/tmp`, from
  upgraded systems, which must opt in.
- Use firmware HTTP Boot to start installer or live media directly from a full ISO URL
  on supported UEFI and U-Boot systems.
- Expect automatic Pointer Authentication and Branch Target Identification hardening
  on supported arm64 hardware.
- Expect Hunspell language packages to provide compiled `.bdic` dictionaries for
  supporting Qt WebEngine browsers.
- Allow Plasma 6 applications to coexist with the retained Qt 5 and KDE Frameworks 5
  compatibility stack, while treating Frameworks 5 as deprecated.

## Prepare migrations that become urgent next

- Move `sudo-ldap` rules to `libsss-sudo` so privilege policy survives its removal.
- Install the transitional OpenSSH GSS-API client or server package now when relying on
  `GSSAPI*` options.
- Replace fcitx 4 with `fcitx5` and move Debian LXD deployments to Incus with tools from
  `incus-extra`.
- Replace `sbuild-debian-developer-setup` with `sbuild --chroot-mode=unshare`.
- Remove dependency on `libnss-docker`, whose required Docker API disappears after
  Engine 26.
- Select DHCP software by network stack: NetworkManager and systemd-networkd need no
  ISC client, `ifupdown` can use `dhcpcd-base`, and servers should move to Kea.

Use [upgrade-foundations.md](references/upgrade-foundations.md) as the final migration
checklist rather than assuming a successful reboot completes the work.
