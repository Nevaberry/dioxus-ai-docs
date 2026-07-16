---
name: rocky-knowledge-patch
description: Rocky Linux 10.2 compatibility. Use for Rocky Linux work.
license: MIT
version: "10.2"
metadata:
  author: Nevaberry
---

# Rocky Linux knowledge patch

Baseline: Rocky Linux 9.3. Covers Rocky Linux 9.4, 9.5, 9.6, 9.7, 9.8, 10.0, 10.1, and 10.2.

Use this skill before planning installs, upgrades, package selection, networking,
security configuration, container workloads, or build environments on the covered
Rocky Linux releases. Read the reference matching the task before changing a host.

## Reference index

| Reference | Topics |
|---|---|
| [installation-and-images.md](references/installation-and-images.md) | Architecture requirements, installer behavior, cloud and WSL images, Image Builder, desktop and remote access |
| [system-administration.md](references/system-administration.md) | NetworkManager migration, DHCP, storage, kernel, DNF/RPM, Cockpit, infrastructure services |
| [security-and-cryptography.md](references/security-and-cryptography.md) | SELinux, crypto policies, PQC, OpenSSL/OpenSSH, attestation, signing, logging security |
| [containers-and-virtualization.md](references/containers-and-virtualization.md) | Podman 4.9/5, Quadlet, runtimes, networking, databases, libvirt changes |
| [runtimes-and-toolchains.md](references/runtimes-and-toolchains.md) | Application streams, language runtimes, compilers, debugging tools, retired streams |
| [upgrade-and-known-issues.md](references/upgrade-and-known-issues.md) | OpenZFS, `passt`, GStreamer upgrade conflicts, installer recovery |

## Breaking platform changes

### Check Rocky Linux 10 hardware before deployment

- Require x86-64-v3 for `x86_64`; Rocky Linux 10 has no 32-bit compatibility.
- Run 32-bit dependencies with 64-bit replacements or in a container.
- Limit RISC-V targets to StarFive VisionFive 2, QEMU, or SiFive HiFive
  Premier P550.
- Use Rocky Pi images only on Raspberry Pi 4 or 5; Pi 3 and Pi Zero 2W are
  no longer supported.
- For Rocky Linux 10.1, require ARMv8.0-A or later for `aarch64`, POWER10 or
  later for `ppc64le`, and IBM z15 or later for `s390x`.

### Replace legacy network configuration on Rocky Linux 10

The `ifcfg-rh` format, `/etc/sysconfig/network-scripts/ifcfg-*`, `ifup`,
`ifdown`, and hooks such as `ifup-local` are removed. Use `nmcli`, `nmtui`,
or `nmstate`; persistent profiles live in
`/etc/NetworkManager/system-connections/`.

Also migrate:

- ISC DHCP server configurations to Kea.
- DHCP client assumptions to NetworkManager's internal client; the
  `dhcp-client` package is removed.
- NIC teams to bonds; teaming is removed.

### Update package-management assumptions

Rocky Linux 10 phases out AppStream modules and `dnf module`. Query ordinary
packages and operate on versioned RPM names:

```console
$ dnf repoquery nginx
$ sudo dnf install nginx-1.26.3
$ sudo dnf remove nginx-1.26.3
```

DNF no longer downloads repository file-list metadata by default. Commands
that need it generally fetch it on demand, so do not assume it is always local.

### Replace removed desktop and remote-access components

- Treat Rocky Linux 10 as Wayland-only at the server level; Xwayland remains
  for compatible X11 clients.
- Do not install `xrdp`, `x11vnc`, or TigerVNC server packages; Rocky Linux 10
  does not ship the required X11-dependent packages or a VNC server.
- Use GNOME Remote Desktop over RDP for sharing, remote login, or headless
  sessions, and Connections when only a VNC client is needed.
- Replace gedit with GNOME Text Editor, Eye of GNOME with Loupe, GNOME Terminal
  with Ptyxis, Cheese with Snapshot, Festival with Espeak NG, and the
  PulseAudio daemon with PipeWire while retaining PulseAudio client interfaces.
- Obtain LibreOffice, Evolution, Inkscape, Totem, and Motif from upstream or
  Flatpak where available; Thunderbird is the packaged mail replacement for
  Evolution.

### Account for installer changes

- Create an administrative user with full `sudo` access; Anaconda disables the
  root account by default on Rocky Linux 10.
- Use RDP rather than VNC for remote graphical installation.
- Supply third-party repositories with `inst.addrepo` or Kickstart; the GUI can
  no longer add them.

### Migrate removed or deprecated system components

- Replace GFS2; it is unsupported on Rocky Linux 10.
- Do not enable Device Mapper Multipath for NVMe devices.
- Move from monolithic `libvirtd` to modular daemons and sockets.
- Replace the deprecated i440fx machine type and Virtual Machine Manager;
  Cockpit is the intended management replacement.
- Replace Redis with Valkey. Use `valkey-compat-redis` from the Plus repository
  when compatibility is required.
- Replace Sendmail with Postfix; obtain SpamAssassin from EPEL.
- Use `tuned-ppd` where applications expect the `power-profiles-daemon`
  interface.

## Upgrade hazards

Before upgrading to Rocky Linux 9.6:

1. Verify that the fixed OpenZFS 2.2.8-branch module is available. The module
   shipped at release does not load, and the 2.3 branch had no compatible update.
2. Expect a `passt`-backed interface to fail under SELinux on workstation,
   server, or virtual-host installations with that back end installed.
3. Swap older third-party GStreamer ugly/freeworld packages to the 9.6 free
   builds before retrying a failed DNF transaction test. Use the exact commands
   in [upgrade-and-known-issues.md](references/upgrade-and-known-issues.md).

## High-use new workflows

### Install a Rocky Linux 9.6 WSL image

Rocky Linux publishes `.wsl` images for `x86_64` and `aarch64`. First launch
prompts for a username.

```powershell
wsl --install --from-file path/to/Rocky-9-WSL-Base.latest.x86_64.wsl rocky-wsl-base
```

Image Builder can also create WSL2 and libvirt-provider Vagrant images on Rocky
Linux 10.1. Since 9.4 it supports custom mount points outside reserved OS paths,
`auto-lvm`, `lvm`, and `raw` partitioning, plus per-blueprint security-profile
rule selection.

### Use Podman 5 defaults deliberately

- Expect `crun` and cgroup v2 by default on Rocky Linux 10.
- Prefer Quadlet for automatic systemd service generation.
- Use fully supported multi-architecture image builds and manifest management.
- Configure retry counts and delays for image pushes and pulls when needed.
- Migrate away from deprecated `slirp4netns`; on Rocky Linux 9.4 also migrate
  from the deprecated `pasta` network name, BoltDB, `container-tools:4.0`, and
  CNI network stack.

### Enable post-quantum cryptography at the right scope

- On Rocky Linux 9.7, opt in with the system crypto policy's `PQ` subpolicy.
- Rocky Linux 10 enables post-quantum cryptography in OpenSSL and OpenSSH system
  policy by default.
- Rocky Linux 9.8 supplies ML-KEM hybrid exchange and ML-DSA through GnuTLS
  3.8.10 and PQC definitions through `p11-kit` 0.26.1.
- Rocky Linux 10.2 adds FIPS-mode OpenSSH hybrid exchange, PQ/T hybrid methods
  in `libssh`, and composite post-quantum signatures through `podman-sequoia`.

### Sort RPM versions correctly

Use RPM 4.19's `rpmsort` instead of lexical `sort` when comparing kernel or RPM
versions:

```console
$ rpm -q kernel | rpmsort
```

Lexical ordering can place `6.12.0-130` before `6.12.0-13`.

### Match PHP dependencies on Rocky Linux 10.2

Both PHP 8.3 and 8.4 packages can be present in the repositories. Resolve an
unqualified dependency, then select the provider matching the installed PHP:

```console
$ dnf provides php-json
```

