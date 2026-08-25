# Machines and platforms

## Provider selection and lifecycle

### macOS providers

`libkrun` became available as a macOS machine backend in 5.2.0 and can expose GPUs inside its VM;
`applehv` remained the default at that point. `libkrun` is Arm-only, and macOS cannot run
`libkrun` and `applehv` machines simultaneously (since 5.4.0). The 5.3.0 implementation cannot be
used on Macs with 64 GB of memory or more.

For Podman 6, Intel macOS hosts are unsupported and macOS defaults to `libkrun`. Existing Intel Mac
artifacts from the earlier best-effort support period do not imply continued support.

Rosetta is disabled by default in machine VMs (since 5.6.0). On M3-or-newer Macs running macOS 15
or later, `libkrun` machines enable nested virtualization by default.

### Provider-independent commands

Every `podman machine` command can address VMs from every provider (6.0.0). The configured provider
chooses only the provider for a newly created VM; override it with `machine init --provider`. The
old `machine list --all-providers` option is removed.

```console
podman machine init --provider libkrun dev
```

`podman machine reset` resets every provider present on the host rather than only one provider
(since 5.2.0); on Windows this can remove both Hyper-V and WSL VMs.

The `podman machine init --volume-driver` option is deprecated (since 5.2.0).

## Provisioning and initial configuration

### Playbooks, swap, and host mounts

`podman machine init --playbook` runs an Ansible playbook inside the new VM at first boot
(since 5.4.0):

```console
podman machine init --playbook bootstrap.yml
```

`podman machine init --swap` enables swap and takes its size in megabytes (since 5.6.0):

```console
podman machine init --swap 2048
```

Machine creation rejects a host mount that would cover the VM's `/tmp` directory (since 5.5.0).

New machine VMs mount the host user's container configuration into `/etc/containers` (6.0.0).
Linux machine host-volume mounts now use systemd; this is incompatible with mounts in existing
VMs, so recreate those VMs.

Earlier Linux machines moved host mounts from `9p` to VirtioFS (since 5.2.0), converting existing
mounts on restart or recreation; hosts on that path need `virtiofsd` installed.

### Connections and host trust

Starting a non-default VM, including `machine init --now`, can prompt to make its connection the
default (6.0.0). Set `--update-connection` explicitly in automation.

`podman machine init` and `set` accept `--import-native-ca`, importing host trusted CAs whenever the
VM boots. `machine init --tls-verify` controls machine-image TLS verification and defaults to true
(since 5.7.0).

## Windows providers and installation

The Windows installer can select WSLv2 or Hyper-V (since 5.3.0). The 5.3.1 upgrade path no longer
installs WSLv2 unexpectedly over an existing Hyper-V installation. From 5.5.0, the installer does
not automatically install either virtualization provider.

The single-MSI installer introduced with 5.7.0 supports per-user installation without
administrator privileges and machine-wide installation. Uninstall an existing Podman application
before switching installers; containers, images, machines, and related data remain.

Windows 10 is unsupported by Podman 6. `podman system hyperv-prep` prepares a Hyper-V host
(6.0.0). Creating a new Hyper-V VM still requires elevation, but starting and stopping it afterward
does not. Use a maintenance release containing the fix for crafted Hyper-V machine image paths
before accepting untrusted `machine init --image` values.

New WSLv2 machines fetch their VM image as an artifact from `quay.io/podman/machine-os`
(since 5.6.0). They also set `force_port_listen` automatically for Windows-to-guest port
forwarding (5.8.6-6.1.0).

## Machine OS operations

`podman machine os update` updates the guest OS but is unavailable for WSL (6.0.0).
`machine os apply` uses `bootc switch` and accepts transports supported by that command.

Remote Podman clients can run on cgroups v1 Linux hosts again from 6.0.2, but this is a client-only
compatibility path. A Podman 6 engine still requires cgroups v2.
