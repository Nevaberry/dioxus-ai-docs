# Machines and platforms

Use this reference for provider selection, VM creation, mounts, trust, Windows installation, and
macOS virtualization behavior.

## Provider selection and cross-provider management

### Provider-independent commands

Since 6.0.0, every `podman machine` command can access VMs from every installed provider. The
configured provider selects only the provider for newly created VMs. Override it per VM:

```console
podman machine init --provider libkrun dev
```

The former `podman machine list --all-providers` option is removed because cross-provider listing
is now the default. macOS now defaults to `libkrun` rather than `applehv`.

This generalizes earlier reset behavior: since 5.2.0, `podman machine reset` resets every provider
available on the host, such as both Hyper-V and WSL on Windows.

### Default connection updates

Starting a non-default VM can prompt to make that VM's connection the default, including when
using `machine init --now`. Set `--update-connection` explicitly in automation to accept or reject
the update without a prompt.

## macOS virtualization

### `libkrun` evolution

- Podman 5.2.0 made `libkrun` available on macOS with GPU mounting into the VM; `applehv` was
  still the default.
- In 5.3.0, the `libkrun` provider was unusable on Macs with 64 GB of RAM or more.
- In 5.4.0, `libkrun` remained Arm-only, and macOS no longer allowed `libkrun` and `applehv`
  machines to run at the same time. Intel Mac builds and images were only best-effort.
- Since 5.6.0, Rosetta is disabled by default in machine VMs. On M3-or-newer Macs running macOS
  15 or later, `libkrun` machines enable nested virtualization by default.
- Podman 6.0.0 removes Intel Mac support and makes `libkrun` the macOS default.

## Windows providers and installation

### Installer/provider behavior

- The 5.3.0 installer could select WSLv2 or Hyper-V. The 5.3.1 maintenance release stopped an
  upgrade of an existing Hyper-V installation from unexpectedly installing WSLv2.
- Since 5.5.0, the installer does not install WSLv2 or Hyper-V automatically. Provision the
  desired Windows virtualization feature separately.
- The 5.7.0 single-MSI installer supports per-user installation without administrator privileges
  and machine-wide installation. Uninstall an existing Podman installation before switching to
  this MSI; containers, images, machines, and other data remain preserved.
- Podman 6.0.0 no longer supports Windows 10.

### Host API socket

Since 5.3.0, Windows machine VMs expose a Unix socket on the host filesystem that forwards Podman
API access into the VM.

### WSL machine images

Since 5.6.0, new WSLv2 machines obtain the VM image as an artifact from
`quay.io/podman/machine-os`.

### Hyper-V preparation and privileges

Since 6.0.0, run `podman system hyperv-prep` as an administrator to prepare a Hyper-V host. New
Hyper-V VMs still require elevation at creation, but can then be started and stopped without
administrator privileges.

Podman 5.8.2 or later is required to avoid CVE-2026-33414, where commands embedded in a crafted
`podman machine init --image` path could execute in the Hyper-V host's PowerShell session.

## VM provisioning

### First-boot Ansible playbooks

Since 5.4.0, initialize a VM with an Ansible configuration hook by passing `--playbook`; Podman
runs the playbook inside the machine on first boot:

```console
podman machine init --playbook bootstrap.yml
```

### Swap

Since 5.6.0, enable VM swap with `--swap`, whose value is in megabytes:

```console
podman machine init --swap 2048
```

### Machine image verification

Since 5.7.0, `podman machine init --tls-verify` controls TLS verification while pulling the
machine image and defaults to `true`.

### Host certificate authorities

Since 6.0.0, `podman machine init` and `podman machine set` accept `--import-native-ca`. When
enabled, Podman imports the host's trusted CA certificates whenever the VM boots.

### Invalid `/tmp`-covering mounts

Since 5.5.0, Podman rejects a machine whose host mount would cover the VM's `/tmp` directory.

### Deprecated volume driver selection

The `--volume-driver` option to `podman machine init` has been deprecated since 5.2.0. Do not add
new automation around it.

## Machine operating systems

### Update and apply

Since 6.0.0, `podman machine os update` updates a machine VM's operating system, except with the
WSL provider. `podman machine os apply` uses `bootc switch` and accepts transports supported by
that command.

## Host filesystem mounts

### VirtioFS transition

Beginning with 5.2.0, new and restarted Linux Podman machines use VirtioFS instead of 9p for host
filesystem mounts. Existing mounts are converted on restart or recreation, and the host must have
`virtiofsd` installed.

### Podman 6 mount implementation

New 6.0.0 machine VMs mount the host user's container configuration into `/etc/containers`.
Linux machines also move host volume mounting to systemd. This is incompatible with mounts in
existing VMs, so recreate those VMs rather than expecting their old mounts to continue working.
