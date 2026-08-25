# Virtualization, Containers, and High Availability

## Leap 16 virtualization changes

### Xen and compatibility removals (`leap-16.0-guide`)

Leap can no longer be a Xen host or a paravirtualized Xen guest. It can still
run as a Xen HVM or PVH guest. `criu` is removed, and `crun` users must move to
`runc`.

### Confidential-computing state (`leap-16.0-guide`)

AMD SEV-SNP is integrated across kernel, QEMU, libvirt, and OVMF for KVM guests
on SEV-SNP-enabled third-generation EPYC or newer systems. The initial Leap 16
state had Intel TDX kernel patches but no QEMU/libvirt integration. The newer
SLES 16 state is described under [Intel TDX](#intel-tdx-integration).

### OVMF, libvirt, and bridge setup (`leap-16.0-guide`)

iSCSI boot is disabled in OVMF images, and libvirt uses modular daemons.
`virt-bridge-setup` replaces YaST's automatic virtualization bridge setup. It is
IPv4-only, must run locally before custom networking, and is unsuitable for
VLAN or bonding configurations. `virt-v2v --parallel=N` permits parallel disk
copies.

### Docker/libvirt firewall interaction (`leap-16.0-guide`)

When Docker breaks libvirt guest networking, configure libvirt's iptables
backend and persist `virbr0` in the `libvirt` firewalld zone. Exact commands are
in [networking-services.md](networking-services.md).

## SLES 15 SP6 virtualization

### SEV firmware and installation

The split `ovmf-x86_64-sev-{code,vars}.bin` images remain for compatibility but
have an unmeasured variable store and are deprecated for removal. Use unified
`ovmf-x86_64-sev.bin`.

`virt-install --cdrom` cannot install an ISO into an SEV guest. Use `--location`,
PXE, or an existing disk image, or install without SEV and enable it afterward.

### QEMU 8.2

QEMU 8.2 adds virtio-sound, Hyper-V `hv-balloon`, UFS emulation, 64-bit NBD
offsets, standard-kdump output from `dump-guest-memory`, Granite Rapids and
Sapphire Rapids CPU models, and supported rather than experimental VFIO live
migration. Audit removed and deprecated QEMU features before changing guests or
management automation.

### libguestfs 1.52

Tar APIs add LZMA and Zstandard compression. `guestfish --key` accepts LVM
mapper names and the `all:` selector. `virt-customize` adds `--chown` and
`--tar-in`. `virt-dib` is removed.

### KubeVirt support window

KubeVirt has L3 support only on the packaged N or N+1 versions during the normal
SP6 lifecycle. It is not covered by LTSS or Extended support.

### Container registries and RPM database

Docker Hub and the openSUSE Registry are no longer preconfigured. Add required
registries to `/etc/containers/registries.conf`. `suse/sle15` uses RPM NDB, so
host scanners and builders require NDB-aware RPM tooling such as SLE 15 SP2 or
newer.

## SLES 15 SP7 virtualization

### Stack transition and vGPU

The stack moves to Xen 4.20, QEMU 9.2.2, libvirt 11.0.0, and virt-manager 5.0.0.
`sanlock` is removed. NVIDIA vGPU 16.10 support is added, but migration is
supported only in some scenarios.

### OVMF deprecation

The 2 MB OVMF image is deprecated for removal in SLES 16.1; update VM
definitions before that release.

### STIG-compliant base container

A STIG-compliant SLE Base Container Image is available from the US Department
of Defense Iron Bank. Deployments requiring Iron Bank content can use it rather
than hardening the ordinary BCI from scratch.

## SLES 16 virtualization and HA

### High Availability stack

SLE HA 16 moves Pacemaker and Corosync from major 2 to 3 and splits fence agents
from one combined package into separately packaged agents. Filesystem-based HA
for SAP ENSA1/2 central services is unsupported.

### Cockpit SR-IOV attachment

An SR-IOV VF attached through Cockpit direct mode can fail to obtain IPv4. Use
passthrough or a `hostdev` device definition.

### Guest CPU exposure

A SLES 16 guest can crash during kernel startup if QEMU exposes too old an
instruction level. Use `-cpu host` or an equivalent virtual CPU model.

### Kiwi KubeVirt `containerdisk`

Kiwi can combine an OEM disk with OCI packaging. The image is stored at `/disk`
with KubeVirt metadata, and the format selects container transport plus disk
format:

```xml
format="oci:qcow2:docker://registry.example.com/kubevirt-disk:latest"
```

### UEFI KVM startup limitation (`16.0-rev-2026-08-04`)

SLES 16.0 documents a startup failure affecting UEFI KVM guests. Treat it as a
known limitation when validating UEFI deployments.

### Intel TDX integration

The `16.0-rev-2026-08-04` revision supplies both libvirt and QEMU integration
for Intel TDX, so TDX guests can be managed with the distribution virtualization
stack. This supersedes the earlier Leap 16 kernel-only integration state.

## Architecture-specific virtualization

KVM in a PowerVM LPAR, Arm 64 KiB kernel preview status, IBM Z Secure Execution,
and architecture firmware requirements are detailed in
[platforms.md](platforms.md).
