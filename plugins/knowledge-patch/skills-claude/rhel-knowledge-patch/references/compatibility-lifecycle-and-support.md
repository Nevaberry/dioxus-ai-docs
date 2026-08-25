# Compatibility, Lifecycle, and Support

Consult this reference when selecting an upgrade path, checking support status, planning replacements, or managing minor-release repositories and lifecycle dates.

## Contents

- [Platform requirements and in-place upgrades](#platform-requirements-and-in-place-upgrades)
- [Technology Preview and support boundaries](#technology-preview-and-support-boundaries)
- [Deprecation and replacement planning](#deprecation-and-replacement-planning)
- [Repositories and lifecycle dates](#repositories-and-lifecycle-dates)

## Platform requirements and in-place upgrades

### Platform and in-place-upgrade baseline (10.0)

RHEL 10.0 uses kernel 6.12 and raises the AMD/Intel baseline to x86-64-v3; the other architecture baselines are ARMv8.0-A, little-endian IBM Power, and 64-bit IBM Z. The supported direct upgrade is RHEL 9.6 to 10.0; RHEL 8 must first be upgraded to RHEL 9.

### Upgrade and architecture baseline (10.1)

The supported direct upgrade is RHEL 9.7 to 10.1; on ARM64 it requires the 4-KB-page kernel, while Leapp rejects systems booted with the 64-KB-page kernel. LiveMode upgrades are a Technology Preview, PAYG systems on AWS, Azure, and Google Cloud can use RHUI upgrades, and the distribution's minimum IBM Power baseline is POWER10 even though the upgrade matrix also lists POWER9.

### Upgrade and platform baseline (10.2)

The supported direct in-place upgrade is RHEL 9.8 to 10.2 on x86-64-v3, ARMv8.0-A, POWER10-or-later, and IBM z15-or-later systems. RHEL 8 still requires a two-step upgrade through RHEL 9.


## Technology Preview and support boundaries

### Storage and network Technology Preview boundaries (10.0)

Preview storage interfaces include `ublk_drv`, TLS-PSK for NVMe/TCP, NBFT NVMe/TCP boot, online `xfs_scrub` without repair, limited last-allocation-group XFS shrinking, and XFS blocks larger than the system page. WireGuard, general kTLS, and NetworkManager-managed HSR/PRP are also Technology Previews.

### Identity, virtualization, and container previews (10.0)

IdM DNSSEC, DoT (`ipa-*-encrypted-dns` and `--dns-over-tls`), and `ipa-migrate` are previews; the default IdM DoT policy is `relaxed`, while `--dns-policy=enforced` forbids fallback. Nested KVM, SEV/SEV-ES/SEV-SNP, Trustee guest attestation, Podman VRF networks, and container partial pulls are likewise not fully supported.


## Deprecation and replacement planning

### Newly deprecated administration interfaces (10.0)

Use `cockpit-image-builder` instead of `cockpit-composer`, EROFS instead of SquashFS, `inst.disklabel=` instead of `inst.gpt`, nftables sets instead of ipset, and `sshd_config` instead of the system-role `sshd` variable. FTP clients/servers, glibc `utmp[x]`, `virt-manager`, monolithic `libvirtd`, i440fx/legacy vCPU models, and qcow2-v2 are deprecated.

### Newly deprecated packages and interfaces (10.1)

Additional package deprecations include `wget`, `daxio`, the `libpmem*`/NVML/pmempool tools, `gvisor-tap-vsock-gvforwarder`, `libslirp`, and `sdl2-compat`. Replace the MSSQL role's deprecated versioned EULA variable with `mssql_accept_microsoft_odbc_driver_for_sql_server_eula`; SHA-1 Secure Boot signatures, the `isa-fdc` virtual floppy, and IBM z16 `te`/`cte` VM features are also deprecated.

### New deprecations (10.2)

`bootc-image-builder` is deprecated in favor of RHEL image builder but remains supported through RHEL 10. Corosync deprecates SCTP for knet, the `vmac.ko` hash implementation is deprecated without a replacement, and the MySQL 8.0 and Python 3.11 container images should move to MySQL 8.4 and Python 3.12.


## Repositories and lifecycle dates

### EUS repository caveat (10.2)

Container and image workflows do not enable EUS repositories automatically and major-only `releasever` produces invalid EUS URLs. Set `/etc/dnf/vars/releasever` to the intended minor release, disable standard repositories, and enable their EUS counterparts.

### Errata-date cutoffs for Satellite cloning (release-lifecycle)

The `redhat-release` errata date is the cutoff for cloning a minor-release channel plus all errata issued before the next minor release with `spacewalk-clone-by-date` or the Satellite web UI. Keep it distinct from general availability: RHEL 10.1 became generally available on 2025-11-11, but its release-package erratum is dated 2025-11-10.

