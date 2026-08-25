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
SLES intentionally differ in several defaults, hardware floors, support
boundaries, and migration mechanisms.

Read the reference file for every affected subsystem. Treat removals,
deprecations, technology previews, lifecycle limits, and compatibility shims as
operational constraints. Confirm enabled repositories and installed RPMs when
package records disagree or advice is version-specific.

## Reference index

| Reference | Topics |
| --- | --- |
| [administration-desktop.md](references/administration-desktop.md) | systemd, Cockpit, desktop sessions, audio, tuning, cgroups, Kdump |
| [installation-migration.md](references/installation-migration.md) | Agama, upgrades, lifecycle, repositories, boot parameters, recovery |
| [kernel-hardware.md](references/kernel-hardware.md) | kernel behavior, BPF, scheduling, CPU limits, drivers, hardening |
| [networking-services.md](references/networking-services.md) | NetworkManager, firewalld, NFS, BIND, DHCP, Dovecot, protocols |
| [packages-runtimes.md](references/packages-runtimes.md) | package turnover, modules, repositories, language runtimes, databases |
| [platforms.md](references/platforms.md) | NVIDIA, IBM Z, POWER, Arm, firmware, boot, cryptographic hardware |
| [security-identity.md](references/security-identity.md) | SELinux, AppArmor, SSH, sudo, SSSD, FIPS, LDAP, cryptography |
| [storage-filesystems.md](references/storage-filesystems.md) | Btrfs, mount semantics, LUKS2, XFS, unsupported and removed features |
| [virtualization-containers.md](references/virtualization-containers.md) | QEMU, libvirt, KubeVirt, Xen, SEV, TDX, containers, HA |

## Breaking migrations and removals

### Choose the product-specific migration path

- Patch SLES to its latest maintenance level before a service-pack upgrade.
- Do not skip SLES service packs without the required LTSS entitlement.
- Use `opensuse-migration-tool` for supported Leap migrations.
- Use the offline Distribution Migration System for SLES 16 migration; do not
  migrate while the source system remains running.
- Treat SLE 15 SP7 as the only SLES 16.0 source and expect incomplete 16.0
  migration coverage.
- Do not treat AutoYaST input as a drop-in Agama profile even where schema
  conversion exists.
- Plan recovery through an Agama console, installation terminal, or runlevel 3;
  its images have no separate rescue system.
- Keep an RMT server on SLE 15 when serving SLES 16.0 clients.
- Read [installation-migration.md](references/installation-migration.md) before
  changing repositories, boot parameters, deployment profiles, or lifecycle
  automation.

### Replace removed stacks

- Replace YaST manual administration with Cockpit where an appropriate module
  exists.
- Replace SysV `init.d`, `rc<service>`, and `after-local` assumptions with
  native systemd units and drop-ins.
- Replace network teaming, including LACP, with NetworkManager bonding.
- Replace `sapconf` with `saptune` and review migrated SAP tuning.
- Replace Pacemaker 2 and Corosync 2 assumptions with the SLE HA 16 version 3
  interfaces; install fence agents individually.
- Replace NIS identity services with LDAP and migrate existing OpenLDAP servers
  toward 389 Directory Server.
- Replace Redis with Valkey and ISC `dhcpd` with Kea; migrate configuration and
  service automation rather than only renaming packages.
- Replace `docker-runc` or `crun` dependencies with `runc` where required.
- Treat the removal of WBEM/SBLIM management as having no direct replacement.

### Account for removed capabilities

- Do not plan transactional updates on SLES 16; use SLE Micro for that model.
- Migrate OCFS2 workloads to the HA-provided GFS2 and retire ReiserFS, HFS+,
  UFS, and quota-v1 dependencies.
- Port GTK2, Qt5, and wxWidgets applications; use RDP instead of the removed VNC
  server.
- Do not require cgroup v1 or hybrid mode on Leap 16.
- Do not require 32-bit binaries unless x86-64 32-bit syscalls are explicitly
  enabled; 32-bit container images cannot run.
- Do not append to `/etc/services` on the assumption that a real file exists.
- Audit cloud agents, Terraform providers, Python RPMs, MPI families, drivers,
  and legacy tools before upgrading images.
- Read [packages-runtimes.md](references/packages-runtimes.md) for the package
  and compatibility inventory.

## Security and identity defaults

- Expect SLES 16 to remove AppArmor and enable SELinux enforcing mode.
- Distinguish Leap: a new installation cannot select AppArmor, but it can be
  enabled later and migration can preserve it.
- Expect the first installer-created SLES user to join `wheel` and use their own
  password for `sudo -i`; non-wheel users supply the root password.
- Audit policies that assume all users share the `users` primary group.
- Expect new remote root SSH access to be key-only unless the compatibility
  package is deliberately installed.
- Replace RSA SSH keys shorter than 2048 bits before crypto-policy enforcement;
  never leave the `LEGACY` policy enabled after recovery.
- Distinguish FIPS mode availability from FIPS 140-3 certification.
- Activate the OpenSSL legacy provider only when MD2, MD4, or MD5 compatibility
  is explicitly required.
- Read [security-identity.md](references/security-identity.md) before changing
  PAM, SSSD, LDAP, Entra ID, or cryptographic policy.

## Service and configuration breaks

- Convert Dovecot 2.3 configuration manually before starting Dovecot 2.4.
- Validate BIND configuration against the installed major version.
- Review Quagga-to-FRouting configuration compatibility explicitly.
- Migrate ISC DHCP configuration and automation to Kea.
- Put local systemd overrides under `/etc`; packaged defaults now live under
  `/usr`.
- Treat `/tmp` as volatile and move persistent work state elsewhere.
- Expect `/etc/hostname` to be applied literally; prefer an unqualified name.
- Check the active `tuned` profile because dynamic tuning is installed by
  default and kernel hardening may be centralized there.
- Read [administration-desktop.md](references/administration-desktop.md) and
  [networking-services.md](references/networking-services.md) for exact
  behavior and commands.

## Kernel, storage, and resource behavior

- Enable `kernel.task_delayacct=1` or boot with `delayacct` when `iotop` must
  report SWAPIN and IO percentages.
- Use `none` or `no` to disable Btrfs compression; an empty value restores the
  default.
- Never bypass a filesystem driver's `allow_unsupported` gate on a supported
  production system.
- Use `mount -oro=vfs` when a physical mount must later become read-write under
  the `mountfd` API.
- Reinitialize swap with `swapon --fixpgsz` after changing Arm page size and
  discard any suspend image first.
- Pair BPF tools and development headers with a kernel from the same product.
- Query systemd's `EffectiveMemoryMax`, `EffectiveMemoryHigh`, and
  `EffectiveTasksMax` for inherited effective limits.
- Replace custom POWER Kdump `maxcpus` settings with `nr_cpus` and update Kdump
  parsers for hyphenated output-directory times.
- Read [kernel-hardware.md](references/kernel-hardware.md) and
  [storage-filesystems.md](references/storage-filesystems.md) before tuning
  these subsystems.

## Networking and installation operations

- Use NetworkManager as the supported Leap network configuration stack and
  `systemd.link` for complex predictable interface naming.
- Account for NFSv4-over-IPv6 being client-only on SLE 15 and NFSv2 being
  removed in SLE 16.
- Prefer current firewalld; use the maintained 1.3.4 fallback only for affected
  SLES 15 SP6 deployments.
- Recognize long firewalld restarts with many interfaces as a known scaling
  limitation.
- For Docker/libvirt firewall conflicts, select libvirt's iptables backend and
  persist `virbr0` in the `libvirt` zone.
- Permit `installer-updates.suse.com` through installation allowlists.
- Use `root=live:` and `inst.install_url=` for SLES 16 netboot; do not use
  `install=`.
- Use `rd.ntp=<server>` when time must be correct before Agama starts.
- Create new NetworkManager connections through Agama CLI or configuration,
  because its UI only edits existing connections.
- Use `zypper lifecycle` with `lifecycle-data-openSUSE` for deprecated Leap
  packages and `zypper search-packages` across SLE modules.

## Desktop, architecture, and virtualization checks

- Expect Wayland-only desktop choices during Leap installation and use XWayland
  for X11 applications.
- Start IBus explicitly under KDE Plasma with `ibus-daemon -x`.
- Expect PipeWire in place of PulseAudio and inspect WirePlumber profile policy
  when migration leaves audio unavailable.
- Remove `opensuse-welcome-launcher` from images that must suppress welcome
  applications.
- Install Steam as Flatpak and satisfy its IA32 and SELinux prerequisites;
  packaged Wine is WoW64-only.
- Verify architecture floors separately for Leap and SLES, especially IBM Z.
- Use GCC 13 and `gcc-13` for matching external kernel and module builds.
- Verify Arm UEFI/SBBR or EBBR conformance and choose ACPI with `acpi=force`
  when both ACPI and a device tree exist.
- Use the unified SEV OVMF image and avoid `virt-install --cdrom` for SEV guest
  installation.
- Pass through the host CPU or select an equivalent QEMU model when a guest
  lacks the required instruction level.
- Treat Arm KVM with the 64 KiB kernel as a technology preview.
- Distinguish full AMD SEV-SNP integration from Intel TDX support, whose QEMU
  and libvirt integration arrives in the later SLES 16.0 revision.
- Read [platforms.md](references/platforms.md) and
  [virtualization-containers.md](references/virtualization-containers.md) before
  changing firmware, guest CPUs, secure execution, containers, or HA.

## Support-boundary discipline

- Treat technology previews as unsupported even when packages and interfaces
  are present.
- Confirm support for the intended workload rather than inferring it from
  package inclusion.
- Keep KubeVirt on packaged N or N+1 during its normal support window; do not
  assume LTSS or Extended support.
- Do not infer external-kernel-module presence from a kernel taint bit.
- Revalidate CPU mitigation behavior after service-pack upgrades because
  `Auto` is not a fixed parameter set.
- Prefer repository and installed-package reality whenever release prose and
  package-comparison records diverge.
