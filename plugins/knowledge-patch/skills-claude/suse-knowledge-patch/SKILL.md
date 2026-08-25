---
name: suse-knowledge-patch
description: SUSE / openSUSE
version: null
license: MIT
metadata:
  author: Nevaberry
---


# SUSE Linux and openSUSE Knowledge Patch

Identify the exact product, release or service pack, architecture, enabled
modules, and installation or migration path before applying guidance. Leap and
SLES can intentionally differ even when packages or workloads are compatible.

Read the reference file for every affected subsystem. Treat support boundaries,
technology previews, removals, and migration-only compatibility behavior as
operational constraints.

## Reference index

| Reference | Topics |
| --- | --- |
| [administration-desktop.md](references/administration-desktop.md) | systemd, Cockpit, desktop sessions, audio, tuning, cgroups, Kdump |
| [installation-migration.md](references/installation-migration.md) | Agama, upgrades, lifecycle, repositories, boot parameters, recovery |
| [kernel-hardware.md](references/kernel-hardware.md) | kernel behavior, BPF, scheduling, limits, drivers, errata |
| [networking-services.md](references/networking-services.md) | NetworkManager, firewalld, NFS, BIND, DHCP, Dovecot, hostnames |
| [packages-runtimes.md](references/packages-runtimes.md) | package removals, repositories, runtimes, databases, compatibility libraries |
| [platforms.md](references/platforms.md) | IBM Z, POWER, Arm, x86-64, firmware, boot, cryptography |
| [security-identity.md](references/security-identity.md) | SELinux, AppArmor, SSH, sudo, SSSD, FIPS, LDAP, identity |
| [storage-filesystems.md](references/storage-filesystems.md) | Btrfs, mount semantics, LUKS2, XFS, unsupported and removed file systems |
| [virtualization-containers.md](references/virtualization-containers.md) | QEMU, libvirt, KubeVirt, Xen, SEV, TDX, containers, HA |

## Breaking migrations and removals

### Choose the supported migration mechanism

- Patch an SLES source fully before a service-pack upgrade.
- Do not skip service packs without the required LTSS entitlement.
- Use `opensuse-migration-tool` for the supported Leap migration path.
- Use the offline Distribution Migration System for SLES 16 migration; do not
  migrate while the source system continues running.
- Treat SLE 15 SP7 as the only accepted SLES 16.0 source and expect incomplete
  16.0 migration coverage.
- Do not treat AutoYaST input as a drop-in Agama configuration.
- Plan recovery from an Agama console or runlevel 3 because its images have no
  separate rescue system.
- Keep an RMT server on SLE 15 when serving SLES 16.0 clients.
- Read [installation-migration.md](references/installation-migration.md) before
  changing repositories, boot parameters, or deployment automation.

### Replace removed administration and compatibility stacks

- Replace YaST manual administration with Cockpit where a supported Cockpit
  module exists.
- Replace SysV `init.d` and `rc<service>` controls with native systemd units.
- Replace network teaming with NetworkManager bonding.
- Replace `sapconf` with `saptune` and migrate selected SAP tuning assumptions.
- Replace SLE HA Pacemaker 2 and Corosync 2 assumptions with their version 3
  interfaces and install fence agents as individual packages.
- Replace NIS identity service with LDAP.
- Retire WBEM/SBLIM integrations; no direct replacement is supplied.
- Replace Redis with Valkey and ISC `dhcpd` with Kea; migrate configuration and
  automation rather than only renaming packages.
- Replace `docker-runc` or `crun` assumptions with `runc` where applicable.

### Account for removed platform capabilities

- Do not plan transactional updates on SLES 16; use SLE Micro for that model.
- Migrate OCFS2 to HA-provided GFS2 and retire ReiserFS, HFS+, UFS, quota-v1,
  and unsupported Btrfs-feature dependencies.
- Port GTK2, Qt5, and wxWidgets desktop dependencies; use RDP instead of the
  removed VNC server.
- Do not require cgroup v1 or hybrid mode on Leap 16.
- Do not require 32-bit binaries unless x86-64 32-bit syscalls are enabled with
  `ia32_emulation`; 32-bit container images cannot run regardless.
- Do not append to `/etc/services` on the assumption that it already exists.
- Audit removed cloud agents, Terraform providers, Python RPMs, MPI lines,
  drivers, and legacy tools before upgrading images.
- Read [packages-runtimes.md](references/packages-runtimes.md) for the detailed
  removal, replacement, and module inventory.

## Security and identity defaults

- Expect SLES 16 to use SELinux enforcing mode and to remove AppArmor.
- Distinguish Leap: new installations cannot select AppArmor, but post-install
  enablement and migration preservation remain possible.
- Expect the first installer-created SLES user to join `wheel` and authenticate
  to `sudo -i` with their own password; non-wheel users supply the root password.
- Audit policy that assumes every user belongs to a shared `users` primary group.
- Expect new remote root SSH access to be key-only unless the root-login
  compatibility package is deliberately installed.
- Treat OpenSSH RSA keys below 2048 bits as rejected by system crypto policy.
- Do not leave the `LEGACY` crypto policy enabled after SSH recovery.
- Distinguish FIPS availability from FIPS 140-3 certification status.
- Enable the OpenSSL legacy provider only when MD2, MD4, or MD5 compatibility is
  explicitly required.
- Read [security-identity.md](references/security-identity.md) before changing
  PAM, SSSD, LDAP, Entra ID, or cryptographic policy.

## Service and configuration breaks

- Convert Dovecot 2.3 configuration manually before starting Dovecot 2.4.
- Validate BIND configuration against the installed major version before upgrade.
- Migrate FRRouting configuration from Quagga with an explicit compatibility
  review.
- Migrate DHCP configuration and service automation from ISC DHCP to Kea.
- Use drop-ins under `/etc` for systemd defaults now shipped under `/usr`.
- Expect `/tmp` to be volatile and move persistent work state elsewhere.
- Expect `/etc/hostname` to be applied literally; prefer an unqualified hostname.
- Check the active `tuned` profile because the daemon is installed by default.
- Read [administration-desktop.md](references/administration-desktop.md) and
  [networking-services.md](references/networking-services.md) for exact behavior.

## Kernel, storage, and resource behavior

- Enable `kernel.task_delayacct=1` or the `delayacct` boot option when `iotop`
  must show SWAPIN and IO percentages.
- Use `none` or `no` to disable Btrfs compression; an empty value restores the
  default.
- Do not bypass a file-system driver's `allow_unsupported` gate on a supported
  production system.
- Use `mount -oro=vfs` when the physical mount must later become read-write with
  the `mountfd` API.
- Reinitialize swap with `swapon --fixpgsz` after changing Arm page size and
  discard any suspend image first.
- Pair BPF tools and development headers with a kernel from the same product.
- Query systemd's `EffectiveMemoryMax`, `EffectiveMemoryHigh`, and
  `EffectiveTasksMax` for inherited limits.
- Replace custom POWER Kdump `maxcpus` settings with `nr_cpus`.
- Update Kdump parsers for hyphenated time fields in output directory names.
- Read [kernel-hardware.md](references/kernel-hardware.md) and
  [storage-filesystems.md](references/storage-filesystems.md) before tuning.

## Networking defaults and recovery

- Use NetworkManager as the supported Leap network configuration stack and
  `systemd.link` for complex predictable interface naming.
- Convert teaming and LACP configurations to NetworkManager bonding.
- Account for NFSv4-over-IPv6 being client-only on SLE 15 and NFSv2 removal in
  SLE 16.
- Prefer current firewalld; use the maintained 1.3.4 fallback only for affected
  SLES 15 SP6 deployments.
- Recognize a firewalld restart timeout with many interfaces as a known scaling
  limitation.
- For Docker/libvirt conflicts, use libvirt's iptables backend and persist
  `virbr0` in the `libvirt` zone.
- Use passthrough or `hostdev` when a Cockpit direct-mode SR-IOV VF cannot obtain
  IPv4.
- Read [networking-services.md](references/networking-services.md) for commands
  and protocol boundaries.

## Installation and package operations

- Permit `installer-updates.suse.com` through installation firewalls.
- Use `root=live:` and `inst.install_url=` for SLES 16 netboot; do not use
  `install=`.
- Use `rd.ntp=<server>` when time must be correct before Agama starts.
- Create new NetworkManager connections through Agama CLI or configuration, not
  its UI.
- Use `zypper lifecycle` with `lifecycle-data-openSUSE` to find deprecated Leap
  packages.
- Use `zypper search-packages` to search enabled and disabled SLE modules through
  SCC or RMT.
- Query enabled repositories or installed RPMs before database-version-specific
  advice.
- Read [installation-migration.md](references/installation-migration.md) and
  [packages-runtimes.md](references/packages-runtimes.md) for exact commands.

## Desktop, architecture, and virtualization checks

- Expect Wayland-only desktop choices during Leap installation and use XWayland
  for X11 applications.
- Start IBus explicitly under KDE Plasma with `ibus-daemon -x`.
- Expect PipeWire to replace PulseAudio; inspect WirePlumber profile policy if
  migration fails.
- Install Steam as Flatpak and satisfy IA32 and SELinux policy prerequisites.
- Verify architecture floors before deployment; Leap and SLES intentionally
  differ on IBM Z support.
- Use GCC 13 and `gcc-13` for matching external kernel/module builds where
  required.
- Use the unified SEV OVMF image and avoid `virt-install --cdrom` for SEV guests.
- Pass through the host CPU or select an equivalent QEMU model when a guest lacks
  the required instruction level.
- Treat KVM with the Arm 64 KiB kernel as a technology preview.
- Use the current Intel TDX integration state documented for SLES 16 rather than
  the earlier kernel-only state.
- Read [platforms.md](references/platforms.md) and
  [virtualization-containers.md](references/virtualization-containers.md) before
  changing firmware, guest CPU, secure execution, or HA configuration.

## Support-boundary discipline

- Treat technology previews as unsupported even when packages and interfaces are
  present.
- Confirm that a package is supported for the intended workload rather than
  inferring support from inclusion.
- Keep KubeVirt on packaged N or N+1 during its normal support window; do not
  assume LTSS coverage.
- Do not infer external-kernel-module presence from a kernel taint bit.
- Revalidate CPU mitigation behavior after a service-pack upgrade because
  `Auto` is not a fixed parameter set.
- Confirm repository and installed-package reality whenever release prose and
  package comparisons diverge.
