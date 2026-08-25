# Machines and platforms

## Providers and lifecycle

### macOS libkrun backend (5.2.0)

On macOS, `libkrun` can back a Podman machine and can mount GPUs into the VM. `applehv` remained
the default in this release.

### Reset every provider (5.2.0)

`podman machine reset` resets every provider available on the host. On Windows, for example, it
removes both Hyper-V and WSL machines.

### Volume-driver deprecation (5.2.0)

Do not build new automation around `podman machine init --volume-driver`; the option is
deprecated.

### Provider-independent management (6.0.0)

Every `podman machine` command can address VMs from every provider. The configured provider is
only the default for new VMs. Use `machine init --provider` for a per-VM choice. The old
`machine list --all-providers` option is removed, and macOS now defaults to `libkrun`.

```console
podman machine init --provider libkrun dev
```

### Connections and host trust (6.0.0)

Starting a non-default VM, including `machine init --now`, may prompt to make its connection the
default. Use `--update-connection` to make automation explicit. `machine init` and `machine set`
accept `--import-native-ca`, which imports host-trusted CA certificates whenever the VM boots.

## VM provisioning and filesystems

### VirtioFS host mounts (5.2.0)

New and restarted Linux machines use `virtiofs` rather than `9p`; existing mounts are converted
on restart or recreation. Install `virtiofsd` on the host.

### First-boot playbooks (5.4.0)

`podman machine init --playbook` runs an Ansible playbook in a new VM on first boot.

```console
podman machine init --playbook bootstrap.yml
```

### Provisioning constraints (5.5.0)

The Windows installer no longer installs WSLv2 or Hyper-V automatically. Machine creation also
rejects a host mount that would cover the VM's `/tmp` directory.

### Swap allocation (5.6.0)

`podman machine init --swap` enables VM swap and takes the size in megabytes.

```console
podman machine init --swap 2048
```

### Machine configuration mounts (6.0.0)

New VMs mount the host user's container configuration at `/etc/containers`. Linux machine host
volumes now use systemd; this is incompatible with mounts in existing VMs, so recreate those VMs
after upgrading.

## macOS behavior

### Provider constraints (5.4.0)

Intel Mac binaries and images were best-effort only in this release. `libkrun` is Arm-only, and
macOS cannot run `libkrun` and `applehv` machines simultaneously.

### libkrun high-memory limitation (5.3.0)

The 5.3.0 `libkrun` provider is unusable on Macs with 64 GB of RAM or more.

### Virtualization defaults (5.6.0)

Rosetta is disabled by default inside machine VMs. On M3-or-newer Macs with macOS 15 or later,
`libkrun` enables nested virtualization by default.

Podman 6 removes Intel Mac support; do not treat the earlier best-effort binaries as a continuing
platform contract.

## Windows and WSL

### Host API socket (5.3.0)

Windows machine VMs expose a Unix socket on the host filesystem that forwards API access into the
VM.

### Virtualization-provider selection (5.3.0)

The Windows installer can select WSLv2 or Hyper-V. The accompanying 5.3.1 maintenance release
stops an existing Hyper-V installation from unexpectedly gaining WSLv2 during upgrade.

### WSL image source (5.6.0)

New WSLv2 machines obtain their VM image as an artifact from `quay.io/podman/machine-os`.

### Single-MSI installer (5.7.0)

The single Windows MSI supports both non-administrator per-user installation and machine-wide
installation. Uninstall an older Podman package before switching; containers, images, machines,
and other data are preserved.

### Machine image verification (5.7.0)

`podman machine init --tls-verify` controls verification while pulling a machine image and
defaults to `true`.

### Hyper-V image-path security (5.8.0)

Use 5.8.2 or later to fix CVE-2026-33414, where commands embedded in a
`podman machine init --image` path could execute in the Hyper-V host's PowerShell session.

### OS and Hyper-V management (6.0.0)

`podman machine os update` updates the VM OS but is unavailable for WSL. `machine os apply` uses
`bootc switch` and accepts its supported transports. Prepare a Windows Hyper-V host with
`podman system hyperv-prep`. Creating a new Hyper-V VM still requires elevation, but starting and
stopping it afterward does not.

### WSL host port forwarding (5.8.6-6.1.0)

Set `force_port_listen = true` under `[network]` in containers.conf to forward ports from the
Windows host into Podman on WSL. Newly created WSL-backed machines set it automatically.

```toml
[network]
force_port_listen = true
```

## Remote-client host compatibility

### cgroups v1 Linux clients (5.8.6-6.1.0)

Podman 6.0.2 restores remote-client operation on Linux hosts without cgroups v2. This affects the
client only and does not restore cgroups v1 support to the Podman 6 engine.
