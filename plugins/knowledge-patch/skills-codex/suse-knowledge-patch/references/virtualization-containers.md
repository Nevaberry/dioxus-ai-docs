# Virtualization, Containers, and High Availability

## Confidential computing

Leap 16 integrates AMD SEV-SNP across kernel, QEMU, libvirt, and OVMF for KVM
guests on enabled third-generation EPYC or newer hardware. Its initial Intel TDX
support is kernel-only; complete management initially lacks QEMU and libvirt.
(leap-16.0-guide)

The later SLES 16.0 revision adds QEMU and libvirt integration for Intel TDX, so
TDX guests can be managed through the distribution stack.
(16.0-rev-2026-08-04)

For SEV, use unified `ovmf-x86_64-sev.bin`. Split
`ovmf-x86_64-sev-{code,vars}.bin` images remain only for compatibility, have an
unmeasured variable store, and are scheduled for removal. `virt-install
--cdrom` cannot install an ISO into an SEV guest; use `--location`, PXE, an
existing disk, or enable SEV after installation.

## libvirt, QEMU, and guest setup

Leap 16 disables iSCSI boot in OVMF and uses modular libvirt daemons.
`virt-bridge-setup` replaces YaST's automatic bridge setup, but is IPv4-only,
must run locally before custom networking, and is unsuitable for VLAN or
bonding. `virt-v2v --parallel=N` enables parallel disk copies.

Leap can no longer host Xen or run as a paravirtualized Xen guest, but it can
still run as an HVM or PVH guest.

SLES 15 SP6 QEMU 8.2 adds virtio-sound, Hyper-V `hv-balloon`, UFS emulation,
64-bit NBD offsets, standard-kdump output from `dump-guest-memory`, Granite
Rapids and Sapphire Rapids CPU models, and supported VFIO live migration. Audit
removed and deprecated QEMU features when upgrading management automation.

libguestfs 1.52 adds LZMA/Zstandard tar APIs, LVM mapper names and `all:` for
`guestfish --key`, and `virt-customize --chown`/`--tar-in`; `virt-dib` is
removed.

SLES 15 SP7 moves to Xen 4.20, QEMU 9.2.2, libvirt 11.0.0, and virt-manager
5.0.0. It removes `sanlock` and adds NVIDIA vGPU 16.10, with migration support
only in some scenarios. The 2 MiB OVMF image is deprecated for SLES 16.1
removal; update VM definitions.

A SLES 16 guest can crash at kernel startup if its QEMU CPU lacks the required
instruction level. Use `-cpu host` or an equivalent virtual CPU model.

Cockpit direct attachment of an SR-IOV VF can fail to obtain IPv4. Use
passthrough or a `hostdev` definition. SLES 16.0 also documents a startup
failure for UEFI KVM guests; account for it when validating UEFI deployments.

## KubeVirt and image formats

SLES 15 SP6 KubeVirt receives L3 support only on packaged N or N+1 during the
normal lifecycle. It has no LTSS or Extended support.

Kiwi can combine an OEM disk with OCI packaging using `containerdisk`; the
image is at `/disk` with KubeVirt metadata. The format selects the transport and
inner disk type:

```xml
format="oci:qcow2:docker://registry.example.com/kubevirt-disk:latest"
```

## Containers and High Availability

SLES 15 SP7 provides a STIG-compliant SLE Base Container Image through the US
Department of Defense Iron Bank repository.

SLE HA 16 moves Pacemaker and Corosync from major 2 to 3 and splits fence agents
into individual packages. SLES 16 does not support filesystem-based HA for SAP
ENSA1/2 central services.
