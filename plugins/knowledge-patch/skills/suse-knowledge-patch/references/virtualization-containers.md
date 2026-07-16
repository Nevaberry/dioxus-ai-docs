# Virtualization, Containers, and High Availability

Use this reference for libvirt, QEMU, Xen, KubeVirt, confidential computing, container images, and cluster-stack transitions.

## Containers and images

### Registry defaults and RPM databases

SLES 15 SP6 no longer preconfigures Docker Hub or the openSUSE Registry. Add required registries explicitly to `/etc/containers/registries.conf`. A WSL image's free `SLE_BCI` repository is disabled after base-product registration.

The `suse/sle15` image uses RPM's NDB database backend. Host-side scanners, diff tools, and image builders need an RPM implementation that can read NDB, such as SLE 15 SP2 or later.

### STIG BCI

A STIG-compliant SLE Base Container Image is available from the US Department of Defense Iron Bank repository for deployments that require Iron Bank content.

### Runtime changes

SLES 15 SP6 removes `docker-runc` in favor of `runc`. Leap 16 removes `criu` and requires former `crun` users to switch to `runc`.

Leap 16 cannot run 32-bit container images. Do not assume x86-64 `ia32_emulation` makes a 32-bit container image a supported workload.

### Kiwi KubeVirt output

SLES 16 Kiwi can combine an OEM disk build with OCI packaging using `containerdisk`. It stores the disk at `/disk` and adds KubeVirt metadata. Select both container transport and inner disk format in the format string:

```xml
format="oci:qcow2:docker://registry.example.com/kubevirt-disk:latest"
```

## libvirt and QEMU

### Modular daemons and bridge setup

Leap 16 libvirt uses modular daemons. `virt-bridge-setup` replaces YaST's automatic virtualization bridge setup, but it is IPv4-only, must run locally before custom network configuration, and is unsuitable for VLAN or bonding configurations.

When Docker disrupts libvirt guest networking, configure libvirt's iptables firewall backend and persist `virbr0` in the libvirt firewalld zone; see [networking-services.md](networking-services.md).

### QEMU capabilities

SLES 15 SP6 QEMU 8.2 adds virtio-sound, Hyper-V `hv-balloon`, UFS emulation, 64-bit NBD offsets, standard-kdump output from `dump-guest-memory`, Granite Rapids and Sapphire Rapids CPU models, and supported rather than experimental VFIO live migration. Audit removed and deprecated QEMU features before updating guests or management automation.

SLES 15 SP7 moves to Xen 4.20, QEMU 9.2.2, libvirt 11.0.0, and virt-manager 5.0.0. It removes `sanlock` and adds NVIDIA vGPU 16.10 support; migration is supported only in some scenarios.

### Guest CPU exposure

A SLES 16 guest can crash during kernel startup if QEMU exposes a virtual CPU below the required instruction level. Use `-cpu host` or an equivalent virtual CPU model.

### Disk conversion and guestfs

Leap 16 `virt-v2v` adds `--parallel=N` for concurrent disk copies.

SLES 15 SP6 libguestfs 1.52 adds LZMA and Zstandard compression to tar APIs, lets `guestfish --key` recognize LVM mapper names and the `all:` selector, and adds `--chown` and `--tar-in` to `virt-customize`. Remove workflows that depend on the deleted `virt-dib` tool.

### SR-IOV through Cockpit

An SLES 16 SR-IOV virtual function attached to a VM through Cockpit direct mode may fail to obtain IPv4. Use passthrough or a `hostdev` device definition instead.

## Confidential computing

### AMD SEV-SNP and Intel TDX

Leap 16 integrates AMD SEV-SNP across kernel, QEMU, libvirt, and OVMF for KVM guests on enabled third-generation EPYC or newer hosts. Intel TDX has kernel patches only; complete QEMU and libvirt integration is deferred.

### SLES 15 SP6 SEV

Use unified `ovmf-x86_64-sev.bin`. The split `ovmf-x86_64-sev-{code,vars}.bin` images remain only for compatibility, have an unmeasured variable store, and are deprecated for removal.

`virt-install --cdrom` cannot install an ISO into an SEV guest. Use `--location`, PXE, or an existing disk image, or install without SEV and enable it afterward.

The SLES 15 SP6 Confidential Computing Module is disabled by default and is a technical preview; its host, secure-VM, and remote-attestation tooling is unsupported.

### IBM Z Secure Execution

For SLES 16 host-key hashes, `genprotimg`, `pvimg`, retrievable secrets, and boot ordering, see [platforms.md](platforms.md).

## KubeVirt support

SLES 15 SP6 provides L3 support for KubeVirt only while running the latest packaged version N or N+1 during the normal SP6 lifecycle. KubeVirt is not covered by LTSS or Extended Support.

## Xen and firmware boundaries

Leap 16 cannot host Xen or run as a Xen paravirtualized guest. It can still run as a Xen HVM or PVH guest.

Leap 16 OVMF images disable iSCSI boot. SLES 15 SP7 deprecates its 2 MB OVMF image for removal in SLES 16.1; update VM definitions before that release.

## Arm and POWER virtualization

KVM with the SLES 15 SP6 Arm 64 KiB kernel is only a technology preview; use the default kernel for supported virtualization.

Leap 16 can host KVM inside a dedicated-core, KVM-enabled PowerVM LPAR on firmware 1060.10. See [platforms.md](platforms.md) for console and hardware constraints.

## High Availability

SLE HA 16 moves Pacemaker and Corosync from major version 2 to 3 and splits fence agents into separate packages. Plan cluster configuration and package automation migrations for both changes.

SLES 16 removes OCFS2; use HA-provided read/write GFS2 for migrated clustered storage. Filesystem-based HA for SAP ENSA1/2 central services is not supported.
