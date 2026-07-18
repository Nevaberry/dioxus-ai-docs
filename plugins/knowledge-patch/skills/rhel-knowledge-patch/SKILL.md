---
name: rhel-knowledge-patch
description: RHEL
license: MIT
version: "10.2"
metadata:
  author: Nevaberry
---

# RHEL Knowledge Patch

Identify the exact minor release, architecture, installation mode, repositories, and support level before changing a RHEL host. Many interfaces evolved across adjacent minor releases, and later entries explicitly correct earlier caveats.

Start with the breaking changes and corrections below. Then load every reference relevant to the task; cross-cutting work commonly needs installation, security, networking, packages, storage, and virtualization guidance together.

## Reference index

| Reference | Topics |
| --- | --- |
| [compatibility-lifecycle-and-support.md](references/compatibility-lifecycle-and-support.md) | Hardware and upgrade eligibility, support boundaries, deprecations, EUS, and errata dates |
| [installation-and-image-mode.md](references/installation-and-image-mode.md) | Anaconda, Kickstart, Image Builder, bootc, image mode, recovery, and installer caveats |
| [security-and-compliance.md](references/security-and-compliance.md) | Crypto policies, SSH, FIPS, PKCS #11, Keylime, Clevis, SELinux, Audit, and fapolicyd |
| [networking.md](references/networking.md) | DNS, DHCP, NetworkManager, Nmstate, nftables, routing, transport, and device controls |
| [kernel-storage-and-hardware.md](references/kernel-storage-and-hardware.md) | Kernel controls, Secure Boot, kpatch, BPF, filesystems, LVM, multipath, VDO, and NVMe |
| [packages-runtimes-and-development.md](references/packages-runtimes-and-development.md) | DNF, RPM, repositories, runtimes, databases, toolchains, libraries, and debugging |
| [identity-and-directory-services.md](references/identity-and-directory-services.md) | Authselect, SSSD, IdM, Directory Server, Samba, AD, passkeys, and migration |
| [clustering-and-system-roles.md](references/clustering-and-system-roles.md) | pcs, Pacemaker, fencing, resource agents, cluster exports, and RHEL system roles |
| [system-services-and-operations.md](references/system-services-and-operations.md) | systemd, polkit, reboot, ReaR, Sos, Cockpit, desktop, printing, time, and metrics |
| [virtualization-and-cloud.md](references/virtualization-and-cloud.md) | VM hardware, firmware, migration, cloud images, confidential computing, and caveats |
| [containers.md](references/containers.md) | Podman, Netavark, pasta, Quadlet, artifacts, signatures, builds, and image lifecycle |

## Apply the guidance safely

1. Determine the target minor release and architecture before choosing an upgrade path or feature.
2. Distinguish supported, Technology Preview, and Developer Preview interfaces; do not design production dependencies around previews.
3. Treat image-mode and package-mode hosts as different deployment models, especially for writes to `/usr`, package transactions, service initialization, and rollback.
4. Check later corrected-behavior entries before applying an earlier workaround.
5. Preserve system-wide crypto policy unless the task explicitly requires a scoped exception and the support consequences are understood.
6. Validate generated Kickstart, NetworkManager, Nmstate, Quadlet, libvirt XML, and Ansible role data on the exact target release.

## Breaking changes and removals

### Upgrade and architecture gates

- Verify the source-to-target pair exactly. A direct upgrade to 10.2 starts from 9.8; older major releases require an intermediate major-version upgrade.
- Require x86-64-v3 on AMD64/Intel hosts. Use ARMv8.0-A, POWER10 or later, or IBM z15 or later for the corresponding 10.2 targets.
- On ARM64 upgrades to 10.1, boot the 4-KB-page kernel; Leapp rejects a system running the 64-KB-page kernel.
- Do not assume that a platform listed in an upgrade matrix is the distribution-wide minimum for a fresh deployment.

### Installation and image mode

- Replace removed VNC installer boot options with RDP. Use `inst.rdp*` boot options or the Kickstart `rdp` command supported by the target release.
- Replace removed Kickstart `auth`/`authconfig` with `authselect`, team options with bonds, and camel-case `%packages` options with their current dashed forms.
- Use `fips=1` during installation; `fips-mode-setup` and `/etc/system-fips` are gone.
- Keep an EFI System Partition and a separate `/boot` for the new UEFI `bootc` installation path. The old `ostreecontainer` separate-`/boot` defect is fixed in 10.2.
- Prefer RHEL image builder over deprecated `bootc-image-builder`; the latter remains supported through RHEL 10.
- Treat writes and package transactions on image-mode hosts deliberately. Use transient DNF transactions only for ephemeral changes.

### Packages, services, and development

- Remove dependencies on modular Application Streams and the deprecated DNF and Kickstart `module` commands. Initial streams are ordinary RPMs; fast-moving tools use Rolling Streams without parallel versions.
- Expect DNF filelists metadata to load only when needed. Enable `optional_metadata_types=filelists` for filepath-dependency workflows that require it.
- Find the RPM database under `/usr/lib/sysimage/rpm`; expect `createrepo_c` to use zstd and omit SQLite metadata unless `--database` is requested.
- Put vendor systemd defaults under `/usr/lib/systemd` and local overrides under `/etc/systemd`; cgroup v2 is mandatory and SysV scripts are deprecated.
- Spell RPM patch application as `%patch 0` or `%patch -P 0`; numberless `%patch` no longer means patch zero.
- Replace Redis with Valkey, ISC DHCP with Kea, Sendmail with Postfix, and removed Berkeley DB mail maps with LMDB equivalents.
- Rebuild software affected by the x86-64-v3 baseline, the IBM Power IEEE128 `long double` ABI, or the TBB 2021.11 incompatibility.

### Security and identity

- Replace the removed OpenSSL PKCS #11 engine with `pkcs11-provider`; use provider-aware applications and PKCS #11 URIs.
- Do not rely on DSA SSH keys, `pam-ssh-agent`, Kerberos RSA PKINIT, the IdM NIS emulator, or SSSD's files provider and AD/IdM enumeration.
- Expect Ed25519 SSH keys by default outside FIPS and RSA in FIPS. Keep host private keys at mode `0600`.
- Move custom SELinux equivalence paths from `/var/run` to `/run`, and place EPEL-related policy in the current CRB extra-policy packages.
- Use authselect profiles or `authselect opt-out`; authselect owns core PAM files and `/etc/nsswitch.conf` and overwrites unmanaged edits.
- Migrate new Directory Server deployments to LMDB. Export/import or replicate BDB instances into a new instance before removing the old backend.
- Account for FIPS TLS 1.2 EMS requirements when interoperating with legacy peers.
- Do not use the 10.2 `FUTURE` crypto policy where non-PQ key exchange is required; it permits only hybrid ML-KEM key exchange.

### Networking, storage, and virtualization

- Replace network teams with bonds and `dhclient` with NetworkManager's internal DHCP client.
- Use nftables sets instead of deprecated ipset workflows. Native NVMe multipath is permanently enabled; DM multipath for NVMe is unsupported.
- Do not plan to mount XFS V4, use GFS2/Resilient Storage, or use removed `md-faulty` and `md-multipath` personalities.
- Replace `kexec_load` integrations with `kexec_file_load` and VDO sysfs tooling with `dmsetup` interfaces.
- Replace Pacemaker legacy master/slave terms, old CIB forms, and removed `show`/`list` commands before moving to the `pacemaker-4.0` schema.
- Do not use removed RHEL 5 Xen or RHV `virt-v2v` paths, RDMA migration, persistent-memory passthrough, or bundled iPXE ROMs.
- Prefer modular libvirt daemons and supported machine models; `virt-manager`, monolithic `libvirtd`, i440fx, legacy vCPU models, and qcow2-v2 are deprecated.

### Containers and desktop

- Migrate existing containers to `crun` with `podman system migrate --new-runtime=crun` and replace CNI with Netavark.
- Replace supported rootless `slirp4netns` workflows with `pasta`; cgroup v1 and `runc` are not the RHEL 10 runtime path.
- Move connection and farm state out of `containers.conf`; Podman persists it in `podman.connections.json`.
- Treat Podman 6 preparation explicitly: use `podman system migrate --migrate-db` to move BoltDB state to SQLite.
- Replace Xorg-server assumptions with Wayland/Xwayland, TigerVNC with GNOME Remote Desktop RDP, PulseAudio with PipeWire, and Qt 5 with Qt 6.
- Install `tzdata` rather than attempting to reinstall it in `ubi10-minimal`, where it is omitted.

## Corrected behavior and high-risk caveats

- Do not carry forward the 10.0 SR-IOV warning: reducing VF counts no longer panics IOMMU/page-pool hosts as of 10.1.
- Keep `discard_granularity` aligned when possible, although misaligned guest discards no longer pause a VM under `werror=stop` as of 10.1.
- Expect `virtiofsd` to survive open-file-limit errors in 10.1 and to use inode handles by default in 10.2, avoiding large-tree descriptor exhaustion.
- Treat IBM Z live dumps and snapshots as fixed in 10.2; the earlier guest-hang caveat no longer applies.
- Let Kickstart resolve iSCSI and zFCP devices regardless of `ignoredisk` ordering in 10.2, and expect `inst.dd` console input to be visible again.
- In 10.2 image mode, PostgreSQL initializes and BIND installs after its state move; MySQL still cannot initialize and has no workaround.
- Treat `io_uring` as a regular 10.2 feature. Earlier releases exposed it as a restricted preview controlled by `kernel.io_uring_disabled` and `kernel.io_uring_group`.
- Re-provision preview NVMe/TLS PSKs after target upgrades when `--compat` cannot bridge pre-2.16 `nvme-cli` or pre-1.16 `libnvme` derivation.
- Do not expect DNF versionlock to block a local RPM path. Create a repository and install the locked package by name.
- On ARM64, disable Secure Boot if kdump is required; no other workaround is documented.
- Do not relax SELinux to work around MariaDB 11.8 Galera replication after upgrade; no secure enforcing-mode workaround is documented.
- Export IdM user and ID-override SSH keys separately before `ipa-migrate`; restore them after migration.

## Frequently used new interfaces

### Installation, image building, and bootc

- Stage without deploying with `bootc upgrade --download-only`; deploy that exact image later with `bootc upgrade --from-downloaded`.
- Use `bcvk` to run a boot-container image as an ephemeral VM or convert it to a persistent disk image.
- Use RHEL image builder for first-boot subscription images, stateless PXE artifacts, and network-installer ISOs with embedded activation keys.
- Use Anaconda Flatpak preinstallation controls when choosing between default Firefox/Thunderbird Flatpaks and supported RPMs.
- Use rescue mode for image-based systems at `/mnt/sysroot`; meaningful manual changes are limited to `/etc` and `/var`.

### Cryptography and secure access

- Expect post-quantum algorithms under `LEGACY`, `DEFAULT`, `FUTURE`, and `FIPS`; apply `NO-PQ` only when interoperability requires disabling them.
- Convert private ML-KEM or ML-DSA keys created by the older provider with `openssl pkcs8 -in OLD -nocrypt -topk8 -out NEW`.
- Use `GSSAPIDelegatedCredentials no` to reject forwarded Kerberos credentials and `CanonicalMatchUser` to match the canonical account name.
- Use `clevis-pin-trustee` for attestation-gated LUKS unlocking, and validate TPM2 pin JSON because unknown fields are now rejected.
- Use Keylime push attestation for agents behind NAT or inbound firewalls.
- Restrict NetworkManager's system-profile polkit permission when non-wheel console users must not create root-read certificate paths.

### Packages, runtimes, and databases

- Query whole-package digests with `rpm -q --qf "[%{packagedigestalgos:hashalgo} %{packagedigests}\n]" PACKAGE`.
- Use spec-local dependency generators through `%_local_file_attrs` and matching `%__NAME_*` macros.
- Plan PostgreSQL 18 upgrades around default data-page checksums; enable them first or explicitly disable them during upgrade.
- Remove MariaDB's unsupported `innodb_defragment`; prefer the `mariadb-*` commands over deprecated MySQL-named symlinks.
- Use `gcc-toolset-15-env COMMAND`, not `scl enable`, for GCC Toolset 15.
- Account for LLVM 21 IR changes, including `captures(none)` and `callbr`, before rebuilding generated IR.

### Networking and storage

- Use NetworkManager and Nmstate `ipv4.forwarding`; `auto` enables forwarding for shared connections and otherwise follows the kernel default.
- Use Nmstate PCI or MAC-bound selection instead of volatile interface names, and configure route `mtu`, `quickack`, FEC, bond, VLAN priority, and delegated-prefix settings as needed.
- Bind nftables hooks and flowtables to absent interfaces by exact name or suffix wildcard; inspect activation with `nft list hooks`.
- Use `TCP_RTO_MAX_MS` or `tcp_rto_max_ms` to lower the 120000-ms retransmission ceiling.
- Use `kdumpctl setup-crypttab` on x86_64 to write crash dumps to encrypted storage.
- Use `snapset mount|umount|exec|shell`, `lvmpersist`, and `vdocalculatesize` for snapshot, shared-LVM, and VDO workflows.

### Identity, containers, virtualization, and operations

- Refresh Directory Server certificates online with `dsconf INSTANCE config refresh-certs`; new connections use the replacement without a restart.
- Scope dynamic groups and MemberOf processing explicitly, and pass a backend to `dsctl db2index --attr`.
- Use passkey authentication in supported IdM Ansible modules and control user verification with `ipapasskeyconfig`.
- Use `podman quadlet install|list|print|rm`; multi-document installs require `---` separators and `# FileName=NAME` at the start of each document.
- Enable `podman-restart.service` when rootless or rootful containers using `unless-stopped` must restart after reboot.
- Use `virt-secrets-init-encryption` and `/etc/libvirt/secret.conf` to seal or configure libvirt secrets.
- Use `<hyperv mode='host-model'/>` for host-supported Hyper-V enlightenments and passt backend identity attributes for guest DHCP naming.
- Prefer `auto_shutdown` in `virtqemud.conf`; do not enable it together with `libvirt-guests.service`.
- Use `pcs` JSON or replayable `cmd` output for automation, and retain the last fencing mechanism unless an explicit safety override is justified.
- Quote YAML-looking string values such as `on`, `off`, `yes`, and `no` in bootloader role data.
- Use PCP/OpenTelemetry bridges for OTLP ingestion, export, and JSON `resourceMetrics`; use the push archive model when local retention is undesirable.
