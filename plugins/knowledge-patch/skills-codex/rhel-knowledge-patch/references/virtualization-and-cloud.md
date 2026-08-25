# Virtualization and Cloud

Consult this reference for guest hardware and firmware, VM migration and conversion, cloud images, confidential computing, virtualization caveats, removals, and preview support.

## Contents

- [Guest hardware, firmware, storage, and networking](#guest-hardware-firmware-storage-and-networking)
- [Migration, conversion, and operating caveats](#migration-conversion-and-operating-caveats)
- [Cloud images and confidential computing](#cloud-images-and-confidential-computing)
- [Removed and preview virtualization interfaces](#removed-and-preview-virtualization-interfaces)

## Guest hardware, firmware, storage, and networking

### Virtualization support additions (10.0)

ARM64 hosts gain same-CPU/page-size migration, TPM TIS, NVDIMM, and virtio-iommu support; Mellanox CX-7 VFs with the required firmware and shared writable virtiofs directories can live-migrate. `virt-install --launchSecurity sev-snp,policy=0x30000` creates SEV-SNP guests, but SEV-SNP remains a Technology Preview.

### VM memory and conversion additions (10.1)

`virtio-mem` is supported on IBM Z and Windows guests, and `virsh hypervisor-cpu-models` lists models known to an IBM Z hypervisor; IBM Z guests currently need `memhp_default_state=online` for hot-added memory to become available automatically. `virt-v2v` can convert VMware VMs with NVMe disks, and the Windows NetKVM `FastInit` setting is enabled by default.

### VM firmware and shutdown controls (10.1)

VM XML can inject an MSDM license table with `<acpi><table type="msdm">PATH</table></acpi>`, and QEMU `-fw_cfg name=opt/HOST/FirmwareSetupSupport,string=no` blocks UEFI setup access. New deployments should use `auto_shutdown` in `/etc/libvirt/virtqemud.conf` instead of `libvirt-guests.service`; the two mechanisms cannot be active together.

### VM boot and storage interfaces (10.1)

Secure Boot VMs can direct-boot a kernel by adding `<shim>PATH-TO-EFI</shim>` under `<os firmware="efi">`. A single `virtio-scsi` device can use multiple `<iothreads>`, and supported hosts can expose single- or multipath SCSI devices with passthrough and SCSI-3 persistent reservations for guest clustering.

### Passt and Windows guest networking (10.2)

Libvirt domain XML can pass DHCP identity to `passt` with `<backend type='passt' hostname='vm1' fqdn='vm1.example.'/>`. Virtio-win adds a `viosock` driver and automatically configured `VsockTcpBridge` service for host-to-Windows communication without modifying TCP applications.

### Hyper-V and libvirt secret controls (10.2)

`<hyperv mode='host-model'/>` enables every Hyper-V enlightenment supported by the host without separate Intel and AMD templates. `virt-secrets-init-encryption` now seals libvirt secrets such as vTPM keys with systemd credentials by default; `/etc/libvirt/secret.conf` selects a custom key or disables encryption.

### VM backup, statistics, and IBM Z behavior (10.2)

`virsh backup-begin` keeps the QEMU process alive if the guest shuts down so the backup can finish, and `virsh domstats --block` reports request-size, vector-count, and alignment limits. IBM Z gains multiple network boot entries, optional CPI for guests, and the `s390-ccw-virtio-rhel10.2.0` machine type with CPI and enhanced PCI translation enabled.


## Migration, conversion, and operating caveats

### Virtualization, cloud-upgrade, and bootc caveats (10.0)

Set a VM disk's `discard_granularity` to the host value before using `werror=stop`, and raise virtiofsd file limits or use `--inode-file-handles=mandatory`/`--cache=never` for large shared trees. Before a 9.6-to-10.0 cloud upgrade, migrate ifcfg files to NetworkManager keyfiles; Podman login does not authenticate bootc, and FIPS-enabled hosts cannot build FIPS bootc disk images.

### VM migration controls (10.1)

`virsh migrate --live --available-switchover-bandwidth VALUE` can override measured pre-copy switchover bandwidth, multifd pre-copy can lead into post-copy migration, and `/etc/libvirt/qemu.conf` adds the support-directed `migrate_tls_priority` workaround. ARM64 hosts add live snapshots plus substantially broader encrypted, compressed, zero-copy, recovery, preemption, and virtiofs live-migration combinations.

### Virtualization caveats (10.1)

SEV-SNP guests must disable `arch-capabilities`, large Genoa SEV-SNP guests can panic, Windows VBS cannot hot-plug CPU or memory without a reboot, and VMs above 1 TB with five-level paging and SMM must keep `host-phys-bits-limit` at 48 or lower. Before cloning or snapshotting an LVM-based RHEL 9 guest on Nutanix AHV, disable the LVM devices file or be prepared to remove `system.devices` and run `vgimportdevices -a` in emergency mode.

### Cloud and IBM Z crash-dump caveats (10.1)

Azure DCv5/ECv5 confidential VMs can leave only `vmcore-incomplete` after kdump, VMware vSphere PVRDMA is unavailable, and live dumps or live snapshots can hang IBM Z guests. Windows Server 2016 Hyper-V guests on AMD EPYC may need `xsavec=off`.

### Corrected virtualization caveats (10.2)

Virtiofsd now uses inode handles by default instead of retaining one file descriptor per cached file, resolving large-tree descriptor exhaustion. Live VM dumps and snapshots on IBM Z no longer hang guests.


## Cloud images and confidential computing

### Cloud, UKI, and WSL behavior (10.0)

Cloud-init uses NetworkManager keyfiles as its default renderer, and supported UKIs come from `kernel-uki-virt`. Portal WSL images are self-supported and lack enforcing SELinux and FIPS; Podman needs `firewall_driver="iptables"`, while cloud-init needs the WSL data source with networking disabled.

### Cloud registration and confidential VMs (10.1)

Eligible marketplace images auto-register against the Red Hat CDN and disable RHUI repositories by default. Azure adds confidential-VM images with Confidential OS disk encryption and an `azure-vm-utils` package of guest utilities and udev rules.

### Offline TDX attestation (10.2)

The new Provisioning Caching Certification Service caches Intel PCS data locally, enabling scalable TDX attestation on hosts without public-internet access.


## Removed and preview virtualization interfaces

### Removed virtualization and container interfaces (10.0)

`virt-v2v` no longer converts RHEL 5 Xen guests or exports to RHV, RDMA migration and persistent-memory passthrough are unsupported, and iPXE relies on firmware NIC drivers rather than its removed ROM bundle. RHEL's OCI runtime is `crun`, and cgroup v1 is unavailable.

### New virtualization and container previews (10.1)

New virtualization previews include Intel TDX hosts, VDUSE devices, a vsock-to-TCP bridge, ARM guest CCA, and SEV-SNP host configuration through `snphost`. Podman's compatibility with Docker API 1.41 and 1.43 is a Technology Preview.

### Virtualization and container previews (10.2)

ARM64 VM Secure Boot is a Technology Preview, as is S3 persistent-reservation live migration using `<reservations managed="no" migration="yes">`, which cannot migrate back to an older QEMU. The preview `krun` runtime runs containers inside lightweight microVMs through a krun-capable crun.

