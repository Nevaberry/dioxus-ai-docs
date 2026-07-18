---
name: suse-knowledge-patch
description: SUSE / openSUSE
license: MIT
version: null
metadata:
  author: Nevaberry
---

# SUSE Linux and openSUSE Knowledge Patch

Identify the exact product, service pack, architecture, enabled modules, and installation or migration path before applying guidance. Leap and SLES can intentionally differ even when they share packages or workload compatibility.

Read the reference file for every affected subsystem. Treat support boundaries, technology previews, removals, and migration-only compatibility behavior as operational constraints rather than feature suggestions.

## Reference index

| Reference | Topics |
| --- | --- |
| [administration-desktop.md](references/administration-desktop.md) | systemd, Cockpit, desktop sessions, audio, tuning, cgroups, Kdump |
| [installation-migration.md](references/installation-migration.md) | Agama, upgrades, lifecycle, repositories, boot parameters, recovery |
| [kernel-hardware.md](references/kernel-hardware.md) | kernel behavior, NVIDIA, BPF, scheduling, CPU limits and errata |
| [networking-services.md](references/networking-services.md) | NetworkManager, firewalld, NFS, BIND, DHCP, Dovecot, hostnames |
| [packages-runtimes.md](references/packages-runtimes.md) | package removals, repositories, language runtimes, databases, compatibility libraries |
| [platforms.md](references/platforms.md) | IBM Z, POWER, Arm, x86-64, firmware, boot and cryptography |
| [security-identity.md](references/security-identity.md) | SELinux, AppArmor, SSH, sudo, SSSD, FIPS, LDAP, identity |
| [storage-filesystems.md](references/storage-filesystems.md) | Btrfs, mount semantics, LUKS2, unsupported features, removed file systems |
| [virtualization-containers.md](references/virtualization-containers.md) | QEMU, libvirt, KubeVirt, Xen, SEV, container images, HA |

## Breaking migrations and removals

### Choose the supported migration mechanism

- Patch an SLES source fully before a service-pack upgrade.
- Do not skip service packs without the required LTSS entitlement.
- Use `opensuse-migration-tool` for the supported Leap migration path.
- Use the offline Distribution Migration System for SLES migration; do not migrate while the source system continues running.
- Treat SLE 15 SP7 as the only accepted SLES 16.0 source and expect incomplete 16.0 migration coverage.
- Do not treat AutoYaST input as a drop-in Agama configuration even where schema conversion exists.
- Plan recovery from an Agama console or runlevel 3 because its images have no separate rescue system.
- Keep an RMT server on SLE 15 when serving SLES 16.0 clients.
- See [installation-migration.md](references/installation-migration.md) before changing repositories, boot parameters, or deployment automation.

### Replace removed administration and compatibility stacks

- Replace YaST manual administration with Cockpit where a supported Cockpit module exists.
- Replace SysV `init.d` and `rc<service>` controls with native systemd units.
- Replace network teaming with NetworkManager bonding.
- Replace `sapconf` with `saptune` and migrate selected SAP tuning assumptions.
- Replace SLE HA Pacemaker 2 and Corosync 2 assumptions with their version 3 interfaces.
- Replace combined fence-agent packaging with the individually packaged agents.
- Replace NIS identity service with LDAP.
- Replace WBEM/SBLIM integrations; no direct replacement is supplied.
- Replace Redis with Valkey and ISC `dhcpd` with Kea; migrate configuration rather than only renaming packages.
- Replace `docker-runc` or `crun` assumptions with `runc` where indicated.

### Account for removed platform capabilities

- Do not plan SLES 16 transactional updates; use SLE Micro for that update model.
- Migrate OCFS2 to HA-provided GFS2 and retire ReiserFS, HFS+, UFS, and quota-v1 dependencies.
- Port GTK2, Qt5, and wxWidgets desktop dependencies; use RDP instead of the removed VNC server.
- Do not require cgroup v1 or hybrid mode on Leap 16.
- Do not require 32-bit binaries unless x86-64 32-bit syscalls are enabled via `ia32_emulation`; 32-bit container images cannot run regardless.
- Do not append to `/etc/services` on the assumption that the file already exists.
- Audit removed cloud agents, Terraform providers, Python RPMs, MPI lines, drivers, and legacy tools before upgrading images.
- Read [packages-runtimes.md](references/packages-runtimes.md) for the complete removal and replacement inventory.

## Security and identity defaults

- Expect SLES 16 to use SELinux enforcing mode and to remove AppArmor.
- Distinguish Leap behavior: new installations do not offer AppArmor during setup, but post-install enablement and migration preservation remain possible.
- Expect the first installer-created SLES user to join `wheel` and authenticate to `sudo -i` with their own password.
- Expect non-wheel users to supply the root password for privileged actions.
- Audit policy that assumes every user belongs to a shared `users` primary group.
- Expect new remote root SSH access to be key-only unless the root-login compatibility package is deliberately installed.
- Treat OpenSSH keys below 2048-bit RSA as rejected by the system crypto policy.
- Do not enable the `LEGACY` crypto policy permanently during SSH recovery.
- Treat FIPS availability separately from FIPS 140-3 certification status.
- Enable the OpenSSL legacy provider only when MD2, MD4, or MD5 compatibility is explicitly required.
- Read [security-identity.md](references/security-identity.md) before changing PAM, SSSD, LDAP, Entra ID, or cryptographic policy.

## Service and configuration breaks

- Convert Dovecot 2.3 configuration manually before starting Dovecot 2.4.
- Validate BIND configuration against the installed major version before upgrade.
- Migrate FRRouting configuration from Quagga with an explicit compatibility review.
- Migrate DHCP configuration and service automation from ISC DHCP to Kea.
- Use drop-ins under `/etc` for systemd defaults now shipped under `/usr`.
- Expect `/tmp` to be volatile and move persistent work state elsewhere.
- Expect `/etc/hostname` to be applied literally; prefer an unqualified hostname.
- Check the active `tuned` profile because the daemon is installed by default.
- Read [administration-desktop.md](references/administration-desktop.md) and [networking-services.md](references/networking-services.md) for exact service behavior.

## Kernel, storage, and resource behavior

- Enable `kernel.task_delayacct=1` or the `delayacct` boot option when `iotop` must show SWAPIN and IO percentages.
- Use `none` or `no` to disable Btrfs compression; an empty value restores the default.
- Do not bypass a file-system driver's `allow_unsupported` gate on a supported production system.
- Use `mount -oro=vfs` when the physical mount must later become read-write under the `mountfd` API.
- Reinitialize swap with `swapon --fixpgsz` after changing Arm page size and discard any suspend image first.
- Pair BPF tools and development headers with a kernel from the same product.
- Query systemd's `EffectiveMemoryMax`, `EffectiveMemoryHigh`, and `EffectiveTasksMax` for inherited effective limits.
- Replace custom POWER Kdump `maxcpus` settings with `nr_cpus`.
- Update Kdump parsers for hyphenated time fields in output directory names.
- Read [kernel-hardware.md](references/kernel-hardware.md) and [storage-filesystems.md](references/storage-filesystems.md) before tuning these subsystems.

## Networking defaults and recovery

- Use NetworkManager as the supported Leap network configuration stack.
- Use `systemd.link` for complex predictable interface naming.
- Convert teaming and LACP configurations to NetworkManager bonding.
- Account for NFSv4-over-IPv6 being client-only on SLE 15 and for NFSv2 removal in SLE 16.
- Prefer current firewalld; use the maintained 1.3.4 fallback only for affected SLES 15 SP6 deployments.
- Recognize a firewalld restart timeout with many interfaces as a known scaling limitation.
- For Docker/libvirt conflicts, select libvirt's iptables backend and persist `virbr0` in the `libvirt` zone.
- Use passthrough or `hostdev` instead of Cockpit direct mode when an SR-IOV VF cannot obtain IPv4.
- Read [networking-services.md](references/networking-services.md) for commands and protocol boundaries.

## Installation and package operations

- Permit `installer-updates.suse.com` through installation firewalls and allowlists.
- Use `root=live:` and `inst.install_url=` for SLES 16 netboot; do not use `install=`.
- Use `rd.ntp=<server>` when time must be correct before Agama starts.
- Create new NetworkManager connections through Agama CLI or configuration, not its UI.
- Use `zypper lifecycle` with `lifecycle-data-openSUSE` to find deprecated Leap packages.
- Use `zypper search-packages` to search enabled and disabled SLE modules through SCC or RMT.
- Expect parallel Zypper package downloads where supported.
- Query enabled repositories or installed RPMs before applying database-version-specific advice.
- Read [installation-migration.md](references/installation-migration.md) and [packages-runtimes.md](references/packages-runtimes.md) for exact commands and module placement.

## Desktop and application behavior

- Expect Wayland-only desktop choices during Leap installation and use XWayland for X11 applications.
- Start IBus explicitly under KDE Plasma with `ibus-daemon -x`.
- Expect PipeWire to replace PulseAudio and inspect WirePlumber profile policy when audio migration fails.
- Remove `opensuse-welcome-launcher` from managed images that must suppress welcome applications.
- Install Steam as Flatpak and satisfy the documented IA32 and SELinux policy prerequisites.
- Treat Wine as WoW64-only where packaged.
- Complete an SP7 upgrade before replacing an unsubscribed `kde` pattern with `kde_minimal`.

## Architecture and virtualization checks

- Verify architecture floors before deployment; Leap and SLES intentionally differ on IBM Z support.
- Use GCC 13 and `gcc-13` for matching external kernel and module builds where required.
- Verify UEFI/SBBR or EBBR conformance on Arm64 and choose ACPI explicitly with `acpi=force` when needed.
- Use the unified SEV OVMF image and avoid `virt-install --cdrom` for SEV guest installation.
- Pass through the host CPU or select an equivalent QEMU CPU model when a guest lacks the required instruction level.
- Treat KVM with the Arm 64 KiB kernel as a technology preview.
- Distinguish complete AMD SEV-SNP integration from kernel-only Intel TDX enablement.
- Read [platforms.md](references/platforms.md) and [virtualization-containers.md](references/virtualization-containers.md) before changing firmware, guest CPU, secure execution, or HA configuration.

## Support-boundary discipline

- Treat technology previews as unsupported even when packages and configuration interfaces are present.
- Confirm that a package is supported for the intended workload rather than inferring support from inclusion.
- Keep KubeVirt on packaged N or N+1 during its normal support window; do not assume LTSS coverage.
- Do not infer external-kernel-module presence from a kernel taint bit.
- Revalidate CPU mitigation behavior after a service-pack upgrade because `Auto` is not a fixed parameter set.
- Confirm repository and installed-package reality whenever release documentation and package comparisons diverge.
