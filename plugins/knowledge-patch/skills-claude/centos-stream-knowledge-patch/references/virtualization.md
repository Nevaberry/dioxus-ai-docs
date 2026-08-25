# Virtualization

## Guest configuration and devices

### Automatic Hyper-V enlightenments

Use `<hyperv mode='host-model'/>` in libvirt domain XML to enable every Hyper-V enlightenment supported by the host, avoiding separate Intel and AMD templates. (9.8)

### Guest SCSI passthrough and persistent reservations

Single-path and multipathed virtual disks support direct SCSI passthrough and fully supported SCSI3 Persistent Reservations. This enables tape or SAN access and shared-storage clustering from guests. (9.8)

### Older NVIDIA vGPU guests need `drm_client_lib`

Some older vGPU guest drivers fail with `Module drm_client_lib not found` because the function is now a separate kernel module. Run `modprobe drm_client_lib` before loading the driver, or update to a driver that loads the dependency. (9.8)

### Host identity with passt networking

For interfaces using the `passt` backend, libvirt XML can pass DHCP and DHCPv6 identity with `<backend type='passt' hostname='vm1' fqdn='vm1.example.'/>`. Both identity attributes are optional. (10.2)

### VSOCK for Windows guests

The `virtio-win` media includes the `viosock` driver and automatically installs `VsockTcpBridge`. Windows applications can communicate with the KVM host over VSOCK or bridge existing TCP services without application changes. (10.2)

### Encryption of libvirt secrets

`virt-secrets-init-encryption` encrypts libvirt secrets such as vTPM keys with systemd credential sealing by default. Select a custom key or disable automatic encryption in `/etc/libvirt/secret.conf`. (10.2)

## Live migration

### Live-migration modes and reservations

Live migration can begin with parallel `multifd` precopy and switch to postcopy without restarting; postcopy itself does not use `multifd`. As a Technology Preview, S3-PR state can survive migration with `<reservations managed="no" migration="yes">`. Migration to a host with an older QEMU then fails. (9.8)

## Deprecations and removals

### Virtualization deprecation migrations

Avoid `rtl8139`, i440fx machine types, legacy Nehalem, Ivy Bridge, and Opteron CPU types, `virt-manager`, monolithic `libvirtd`, virtual floppy devices, and SHA-1 Secure Boot signatures in new deployments. Convert qcow2-v2 disks to qcow2-v3 with `qemu-img amend`; 10.2 Image Builder cannot create qcow2-v2. (10.2)

### Removed i440fx machine version

Guests using `pc-i440fx-rhel7.6` cannot boot or live-migrate to a release 10 host. Inspect with `virsh dumpxml <vm>`, then change to `pc-i440fx-rhel10.0` with `virsh edit`. The entire i440fx family remains deprecated for new deployments.

### Virtualization conversion and migration removals

`virt-v2v` cannot import from release 5 Xen or export through `-o rhv-upload`, `-o rhv`, or `-o vdsm`. `virt-p2v` cannot target a release 10 host. VM migration over an `rdma` URI is unsupported.
