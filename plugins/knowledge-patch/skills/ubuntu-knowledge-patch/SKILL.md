---
name: ubuntu-knowledge-patch
description: Ubuntu 26.04 compatibility. Use for Ubuntu work.
license: MIT
version: "26.04"
metadata:
  author: Nevaberry
---

# Ubuntu Knowledge Patch

Use this skill when installing, upgrading, configuring, securing, or operating
Ubuntu systems and images. Start with the breaking-change checks, then read the
topic reference that matches the machine, service, or deployment being changed.

## Reference index

| Reference | Topics |
| --- | --- |
| [cloud-containers.md](references/cloud-containers.md) | Cloud-init, cloud images, Azure, Google Cloud, WSL, LXD, containerd, runc, Docker, Buildx, and Compose |
| [desktop-experience.md](references/desktop-experience.md) | Desktop defaults, GNOME, Wayland, graphics, application replacements, permissions, Insights, and desktop-image behavior |
| [installation-boot.md](references/installation-boot.md) | Installer and autoinstall, systemd boot, crash dumps, initramfs, GRUB, iPXE, encryption, and installation constraints |
| [networking-security.md](references/networking-security.md) | Netplan, DNS readiness, OpenSSL, OpenSSH, SSSD, authd, AppArmor, Chrony, OVS TLS, VPN, and network services |
| [services-data.md](references/services-data.md) | Web and mail services, Redis and Valkey, Samba, databases, Bacula, monitoring, diagnostics, and high availability |
| [upgrades-packaging.md](references/upgrades-packaging.md) | Release upgrades, APT, package transitions, command providers, toolchains, lifecycle, and package snapshots |
| [virtualization-platforms.md](references/virtualization-platforms.md) | Libvirt, QEMU, OVN, kernel facilities, Arm, IBM Z, POWER, RISC-V, Raspberry Pi, and confidential computing |

## Breaking changes and upgrade gates

### Check the direct upgrade path

Do not assume every installed release can upgrade directly. For the latest LTS,
only the immediately preceding interim release and the prior LTS are direct
sources. LTS users receive the automatic offer at the first point release rather
than on the initial release date. Read the lifecycle section before automating a
fleet upgrade.

### Revalidate privileged commands and core utilities

Ubuntu 25.10 changes two foundational command providers:

- `sudo-rs` provides `sudo` by default. Classic sudo binaries use a `.ws`
  suffix, and `sudo-ldap` is removed; integrate LDAP authentication through PAM.
- `rust-coreutils` provides the core operating-system utilities. GNU coreutils
  remain selectable through managed diversions, but scripts that rely on edge
  behavior need compatibility tests.

Also stop assuming a server image directly contains `screen`, `wget`, `byobu`,
`cloud-guest-utils`, or `dirmngr`. Use the seeded `wcurl` for simple downloads or
install the package a workload actually requires.

### Migrate APT keys and solver assumptions

`apt-key` is removed. Store repository keys as files and configure verification
according to `apt-secure(8)` instead of scripting the deleted command.

APT 3.0 tries the new solver only after the classic solver fails; APT 3.1 makes
the new solver the default. Use these commands to explain its choices:

```sh
apt why PACKAGE
apt why-not PACKAGE
```

Deb822 repository definitions can use `Include` and `Exclude` to constrain which
packages a repository supplies. Account for the automatic pager used by
`apt show` and `apt list` in scripts and captured output.

### Convert removed service configuration

Treat these as migrations, not restart-only upgrades:

- Dovecot 2.4 substantially changes and renames 2.3 configuration syntax.
- QEMU 9.2 removes old block-migration, compression, and 9pfs proxy interfaces;
  QEMU 10.1 also removes old x86 and s390x machine types.
- Samba 4.22 removes `nmbd proxy logon`, `cldap port`, and
  `fruit:posix_rename`.
- OpenSSH 10 removes DSA support, and strongSwan 6.0 removes NTRU.
- HAProxy 3.0 rejects several previously tolerated forms and renames
  `tune.ssl.ocsp-update` to `tune.ocsp-update`.
- Containerd 2.0 removes 1.x-deprecated functionality, while runc 1.2 changes
  mount validation and flag handling.

Complete any guarded Redis-to-Valkey migration before installing a release that
removes `valkey-redis-compat`. Never delete `/etc/valkey/REDIS_MIGRATION` until
the migrated configuration and data have been reviewed.

### Declare cloud-init datasources on non-x86 images

Cloud-init 25.3 disables itself on non-x86 systems unless a known datasource is
declared during early boot through DMI, kernel parameters, filesystem
configuration, or environment files. Image builders must make the declaration;
otherwise a newly launched machine may be unreachable over SSH.

Invoke cloud-init boot stages through their systemd units. The four stages share
one Python process through `cloud-init-main.service`, and direct post-production
stage invocation produces warnings and bypasses the intended lifecycle.

### Account for boot-stack changes

Systemd 256.5 refuses cgroup v1 unless the kernel command line contains:

```text
SYSTEMD_CGROUP_ENABLE_LEGACY_FORCE=1
```

It also ships `tmp.mount`, making `/tmp` a tmpfs, and places cryptsetup-related
helpers in the separately installed `systemd-cryptsetup` package.

Ubuntu Desktop 25.10 uses Dracut and systemd for initramfs generation. Server and
Raspberry Pi desktop installations retain `initramfs-tools`; choose hooks and
recovery procedures for the stack actually installed.

## Installation quick reference

### Make offline behavior explicit

For an autoinstall that may have no reachable package mirror, configure:

```yaml
apt:
  fallback: offline-install
```

Selecting NVIDIA drivers while offline installs Nouveau instead. Complete that
installation with network access or change the graphics driver afterward.

### Avoid known storage and firmware traps

- TPM-backed full-disk encryption cannot boot while Absolute/Computrace is
  enabled and can omit hardware-specific modules such as `vmd`, hiding NVMe RAID.
- ZFS encryption can fail to activate cryptoswap. OEM installation is not
  supported in the affected desktop installer generation.
- NVMe-over-TCP firmware installation can leave the target unbootable; apply the
  dedicated autoinstall workaround or repair it before the first reboot.
- U-Boot targets must have the matching newer U-Boot before installation because
  Subiquity does not run `flash-kernel` or `update-grub` there.
- Physical GRUB-to-iPXE boot needs `grub-ipxe` and the correct `ipxe.efi` or
  `ipxe.lkrn`; QEMU's driver-only UEFI ROM still has to chainload full iPXE.

### Prevent installer network hangs

The installer treats otherwise-unconfigured interfaces as DHCPv4. Remove
disconnected interfaces from `/etc/netplan/50-cloud-init.conf` or mark them
`optional: true`. A Raspberry Pi server that needs network-provided cloud-init
data must instead leave at least one interface `optional: false`.

## Networking and security quick reference

### Make DNS and search-domain policy explicit

General systemd-networkd installations no longer add DHCP search domains unless
`UseDomains=true` is configured. Ubuntu cloud images deliberately restore that
behavior in `/etc/systemd/networkd.conf.d/50-cloudimg-settings.conf`.

Netplan wait-online semantics also evolved: link-local and a routable interface
matter, and configured DNS servers must be reachable before an interface is
online. Mark interfaces and DNS dependencies deliberately.

### Update time synchronization rules

Ubuntu's Chrony pool definitions live in
`/etc/chrony/sources.d/ubuntu-ntp-pools.sources`. Avoid keeping duplicate pool
entries in `chrony.conf` after an upgrade.

Ubuntu NTS uses TCP 4460 for key exchange and UDP 123 for time. Networks that
cannot reach both need ordinary NTP sources. Chrony later becomes the seeded
default; migrate an existing system with:

```sh
apt-mark auto systemd-timesyncd
apt install chrony
```

### Rehome SSH environment configuration

SSH sessions no longer read `~/.pam_environment`. Move required values to a
supported mechanism such as server `AcceptEnv` plus client `SendEnv`. Review
post-quantum key exchange defaults and OpenSSH 10 match conditions before using
strict allowlists or banner-based compatibility checks.

## Cloud and virtualization quick reference

### Validate container host compatibility

Ubuntu 24.10 containers require cgroup v2 and an LXD build with
systemd-credential support. Older hosts and affected LXD 5.0 installations need
the documented kernel, channel, or nesting workaround; very old containers
cannot run on that cgroup-v2 host.

Docker inspection consumers must use `DNSNames`, not `Aliases`, to find the short
container ID. IPv6 iptables is enabled by default for Linux bridge networks.

### Preserve virtual-machine compatibility

Before a QEMU upgrade, inventory machine types, serial arguments, 9pfs backends,
block migration, compression, host bitness, and confidential-guest firmware.
Before a libvirt upgrade, inventory split driver packages, default URI overrides,
NVRAM format, migration storage, IOMMU scale, and CPU-model versioning.

## Desktop quick reference

Ubuntu Desktop 25.10 is Wayland-only. Its default image viewer and terminal are
Loupe and Ptyxis, and Ubuntu Insights replaces Ubuntu Report without carrying
forward prior consent. Test extensions against GNOME 50 on Ubuntu Desktop 26.04.

For graphics, distinguish hardware enablement from installation conditions:
VA-API may need `va-driver-all`, supported NVIDIA laptops enable Dynamic Boost
only on AC power under load, and offline NVIDIA selection installs Nouveau.
GTK4 rendering can regress under VirtualBox or VMware with 3D acceleration.

## Working method

1. Identify the exact Ubuntu release, architecture, image type, and upgrade path.
2. Inventory package providers, removed options, custom service configuration,
   initramfs tooling, network readiness rules, and cloud-init datasource setup.
3. Read every matching topic reference before editing automation or images.
4. Test boot, networking, authentication, storage, and service migrations on a
   disposable instance that matches the target architecture and image seed.
5. After an upgrade, review snap channels, time sources, package transitions,
   crash-dump capacity, cloud-init state, and services intentionally left stopped.
