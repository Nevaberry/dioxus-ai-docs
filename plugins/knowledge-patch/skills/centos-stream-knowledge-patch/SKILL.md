---
name: centos-stream-knowledge-patch
description: CentOS Stream
license: MIT
version: "10.0"
metadata:
  author: Nevaberry
---

# CentOS Stream knowledge patch

Baseline: CentOS Stream 9. Covered range: CentOS Stream 10.0 and Enterprise Linux 9.8 through 10.2, including major-version adoption guidance.

## Reference index

| Reference | Topics |
| --- | --- |
| [Platform, installation, and upgrades](references/platform-installation-upgrades.md) | Hardware baseline, lifecycle, Leapp, Anaconda, Kickstart, Image Builder, bootc, Secure Boot, UKIs, EUS, ReaR |
| [Packages, runtimes, and development](references/packages-runtimes-development.md) | Default versions, modules, databases, compilers, libraries, DNF, repositories, RPM specs and signing |
| [Security, identity, and cryptography](references/security-identity-crypto.md) | AIDE, SSH, crypto policies, LUKS policy, PKCS #11, SELinux, IdM, SSSD, Directory Server, OpenSCAP |
| [Networking](references/networking.md) | NetworkManager, Nmstate, IPsec, nftables, firewalld, DHCP, routing, DNS, VSOCK, interface migration |
| [Storage, kernel, and hardware](references/storage-kernel-hardware.md) | Kernel controls, kdump, live patching, multipath, LVM, Stratis, VDO, XFS, drivers, scheduler changes |
| [Containers and image mode](references/containers-image-mode.md) | Podman, Quadlet, bootc, runtime and cgroup migration, registry images, disconnected updates, microVM isolation |
| [Virtualization](references/virtualization.md) | libvirt, QEMU, Hyper-V, migration, SCSI reservations, passt, VSOCK, secrets, machine-type removals |
| [Services, HA, observability, and desktop](references/services-ha-observability-desktop.md) | Cockpit, system roles, Pacemaker, pcs, PCP, web and mail services, printing, GNOME, Flatpak, editors |
| [Project ecosystem](references/project-ecosystem.md) | Repository hosting and RDO delivery changes |

## Use this patch

1. Identify the target major and minor release before changing configuration.
2. Read the reference matching the subsystem being changed.
3. Treat removal, deprecation, hardware-baseline, and upgrade-path notes as migration gates.
4. Check preview status before relying on a feature in production.
5. Test crypto-policy, identity, storage, boot, and network changes on a representative host.

## Breaking changes and migration gates

### Hardware and boot

- CentOS Stream 10 x86_64 requires x86-64-v3. Other targets begin at ARMv8.0-A, POWER9, and IBM z14.
- A 9.8-to-10.2 Leapp upgrade requires x86-64-v3, ARMv8.0-A, POWER10 or newer, or IBM z15 or newer. Enterprise Linux 8 must pass through 9 before 10.
- Before a Secure Boot upgrade, update the Stream 9-era host to a shim that trusts the signing CAs used by the 10.2 shim and confirm that firmware has a suitable certificate enrolled.
- CentOS Stream 10 cannot mount XFS V4. Back up, recreate as XFS V5, and restore before migration.
- GFS2 and the Resilient Storage Add-On are unavailable. Keep those workloads on an earlier supported major release or redesign storage.

### Containers and host configuration

- `runc` is removed. Convert existing Podman containers with `podman system migrate --new-runtime=crun`.
- Only cgroup v2 can boot. Convert workloads that require cgroup v1.
- CNI networking is unsupported; use Netavark. Rootless `slirp4netns` is deprecated in favor of `pasta`.
- RHEL 7-era containers are unsupported on a Stream 10-era host.
- The packaged `storage.conf` moves from `/etc/containers` to `/usr/share/containers`.
- Podman 6 removes BoltDB. Podman 5.8 attempts migration to SQLite; retry with `podman system migrate --migrate-db`.

### Network configuration

- Network teams, `teamd`, and `libteam` are removed. Convert teams to kernel bonds.
- NetworkManager no longer reads ifcfg profiles from `/etc/sysconfig/network-scripts`; migrate them to keyfiles in `/etc/NetworkManager/system-connections`.
- External `dhclient` is removed. Use NetworkManager's internal DHCP client.
- Native NVMe multipath is always enabled; `nvme_core.multipath` and DM Multipath for NVMe over RDMA or Fibre Channel are unavailable.
- Firewalld lockdown is removed. Replace it with explicit privilege and service isolation.

### Authentication and cryptography

- `authselect-libs` owns `/etc/nsswitch.conf` and selected PAM files. Put changes in a custom profile or run `authselect opt-out`.
- SSSD's `files` provider and its authselect profile options are removed; use the proxy provider when SSSD must expose local identities.
- `nscd` is removed. Use `systemd-resolved` for DNS caching and SSSD for other name services.
- `compat-openssl11`, the OpenSSL ENGINE API, `engine.h`, and engine-based PKCS #11 integration are gone or deprecated. Build for OpenSSL 3 providers and use `pkcs11-provider`.
- The `DEFAULT:SHA1` subpolicy is removed. RSA key-exchange TLS suites require `LEGACY` or a custom policy; TLS 1.0/1.1 also needs application security level 0.
- A FIPS-mode 10 replica cannot join an older IdM deployment whose Kerberos master key still uses AES HMAC-SHA1.

### Packages, compilers, and filesystems

- GCC 14 diagnoses implicit `int`, implicit function declarations, and pointer-to-integer misuse as C errors.
- On IBM Power, `long double` uses the IEEE128 ABI and is incompatible with the older IBM double-double ABI.
- Berkeley DB 5 and `libdb` are absent. Migrate applications, Directory Server databases, and Postfix maps.
- Traditional zlib is provided through `zlib-ng` compatibility packages; TBB 2021.11 consumers must be rebuilt.
- `%patch` in RPM specs must name patch numbers. `%patchN` is deprecated, and an unnumbered `%patch` fails.
- DNF does not fetch filelists by default. Enable `optional_metadata_types=filelists` for path dependency resolution.

### Installer and image workflows

- RDP replaces VNC for remote graphical installation.
- The installer GUI cannot add repositories; use Kickstart or `inst.addrepo`.
- Removed Kickstart interfaces include `pwpolicy`, `%anaconda`, `auth`, `authconfig`, `%addon com_redhat_oscap`, the deprecated `module` command, and several old option spellings.
- Image-mode UEFI installation needs separate EFI System, `/boot`, and root partitions; the default `/boot` size is 2 GiB.
- `bootc-image-builder` is deprecated; use the AppStream `image-builder` command.

## Platform quick reference

### CentOS Stream 10 baseline

- Kernel 6.12; Python 3.12; GCC 14; Go 1.23; Rust 1.82; LLVM 19.
- Ruby 3.3; Node.js 22; PHP 8.3; OpenJDK 21.
- Apache HTTP Server 2.4.62; nginx 1.26.
- PostgreSQL 16; MariaDB 10.11; MySQL 8.4; Valkey 7.2.
- GNOME 47; Qt 6.7; DNF 4.20; RPM 4.19.
- Alternative application versions are ordinary AppStream RPMs, not modular streams.
- Wayland is the display server; Xwayland supports legacy X11 clients. The Xorg server package is absent.

### Upgrade paths

```text
Enterprise Linux 7 -> 8 -> 9
Enterprise Linux 8.10 -> 9.8
Enterprise Linux 9.8 -> 10.2
```

Direct 7-to-9 and 8-to-10 upgrades are unsupported. Read the platform reference for architecture and SAP HANA conditions.

### Image mode and bootc

- `bootc upgrade --download-only` downloads without selecting the image for the next boot.
- `bootc upgrade --from-downloaded` deploys exactly the staged image without checking the registry.
- Image Builder can create network-installer ISOs, stateless PXE artifacts, bootable containers, and disk images.
- `bcvk` launches boot containers as ephemeral VMs or converts them to persistent disk images.
- Boot Loader Specification entries can use `efi` to point to a UKI under `/boot/efi/EFI/Linux`.

## Security quick reference

### OpenSSH 9.9

- `ssh-keygen` defaults to Ed25519, or RSA under FIPS.
- Review `ChannelTimeout`, `PerSourcePenalties`, `CanonicalMatchUser`, `PAMServiceName`, `EnableEscapeCommandline`, and `GSSAPIDelegatedCredentials`.
- The server is split into `sshd` and `sshd-session`; disabling privilege separation or daemon re-execution is unsupported.

### Post-quantum policies

- The `PQ` subpolicy enables hybrid ML-KEM and ML-DSA in GnuTLS and `mlkem768x25519-sha256` in OpenSSH.
- The 10.2 `FUTURE` policy permits only hybrid ML-KEM key exchange and intentionally breaks many CDN, Java, and legacy-peer connections.
- OpenSSL 3.5 standardizes ML-KEM and ML-DSA private-key formats; convert old unencrypted keys with:

```bash
openssl pkcs8 -in old-key -nocrypt -topk8 -out standard-key
```

### LUKS and key handling

- `clevis-pin-trustee` releases LUKS keys through Trustee KBS remote attestation and supports combination with Tang or TPM2 policy.
- `link-volume-key=` in `/etc/crypttab` can place a LUKS2 key in a kernel keyring for crash-kernel reuse.
- `cryptsetup reencrypt` supports token-bound LUKS2 devices.

## Networking quick reference

- Set `ipv4.forwarding` per NetworkManager or Nmstate connection; `auto` follows shared-connection state and otherwise the kernel default.
- Set `rd.net.dhcp.client-id=<id>` when early-boot DHCP must present a stable client ID.
- Nmstate's `alt-names` adds or removes interface alternative names.
- NetworkManager Libreswan supports multiple left/right subnets and `nm-connect-mode=ondemand`.
- Dynamic nftables netdev hooks may bind future interfaces and wildcard suffixes; inspect them with `nft list hooks`.
- Firewalld policy sets provide reusable collections such as the `gateway` router baseline.
- Use `tcp_rto_max_ms` or per-socket `TCP_RTO_MAX_MS` to lower the 120000 ms retransmission ceiling.

## Storage, kernel, and hardware quick reference

- Kernel 9.8 enables `io_uring`; HSR and PRP are fully supported.
- `purge_disconnected yes` lets `multipathd` remove disconnected SCSI LUNs instead of queueing indefinitely.
- Snapm 0.7 can mount, inspect, execute within, and boot snapshot sets.
- LVM supports volume-group-scope persistent reservations; Stratis retains unlocked encrypted-pool keys in the daemon keyring for automatic extension.
- EEVDF replaces CFS. Rename `sched_min_granularity` tuning to `sched_base_slice`; `sched_wakeup_granularity` is removed.
- Audit removed and unmaintained hardware with `lspci -nn` before a major-version upgrade.

## Package and runtime quick reference

- Valkey replaces Redis.
- PostgreSQL 18 enables data-page checksums by default and deprecates MD5 authentication.
- MariaDB 11.8 defaults to `utf8mb4`; remove `innodb_defragment` and migrate from deprecated `mysql*` command symlinks.
- Newer runtime choices include Node.js 24, Ruby 4.0, Python 3.14, OpenJDK 25, PostgreSQL 18, and MariaDB 11.8.
- `createrepo_c` defaults to Zstandard metadata and omits SQLite metadata unless `--database` is passed.
- RPM supports multiple, RFC 9580, and post-quantum signatures; `rpmsign --addsign` preserves existing signatures.

## Operations quick reference

- PCP can ingest and export OpenTelemetry data with `pmdaopentelemetry` and `pcp2opentelemetry`.
- Pacemaker's `portblock` agent uses nftables by default.
- Cockpit delegates TLS to `cockpit-tls`; remove obsolete `pam_cockpit_cert` configuration.
- System Roles add upgrade analysis, remediation, and execution roles, plus broader storage, immutable-host, HA, SSH, firewall, and metrics support.
- The standalone `pcsd` web UI is gone; install the `cockpit-ha-cluster` add-on.

## Preview and deprecation discipline

- Do not treat Developer Preview or Technology Preview interfaces as production support commitments.
- Before adopting a preview, read its limitations in the matching reference and provide a rollback path.
- For every deprecated package, interface, command, image, or machine type, migrate to the documented replacement before the next major release.
