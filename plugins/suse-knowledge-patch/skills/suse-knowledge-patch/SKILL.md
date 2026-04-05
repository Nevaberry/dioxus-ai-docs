---
name: suse-knowledge-patch
description: This skill should be used when working with SUSE Linux (SLES 16+), openSUSE Leap 15.6+, or openSUSE Tumbleweed — including Agama installer, SELinux, NetworkManager migration from wicked, /usr-merge system defaults, Cockpit administration, or SUSE 16 component removals. Triggers on SUSE, SLES, openSUSE, Leap, Tumbleweed.
license: MIT
metadata:
  author: Nevaberry
  version: "16.0"
---

# SUSE 16+ Knowledge Patch

Claude's baseline covers SLES 15 SP5, openSUSE Leap 15.5, and Tumbleweed through mid-2024. This skill provides changes from openSUSE Leap 15.6 (June 2024) and the SUSE 16.0 release (SLES Nov 2025, Leap Oct 2025).

**Key context**: openSUSE Leap 16.0 and SUSE Linux Enterprise 16.0 share the same codebase (source and binary identical). Nearly all 16.0 changes below apply to both distributions.

**Rebranding**: "SUSE Linux Enterprise Server" is now "SUSE Linux". Minor releases (16.0, 16.1, ...) replace service packs.

## Breaking Changes Quick Reference

| What Changed | Old (15.x) | New (16.0) |
|--------------|------------|------------|
| Installer | YaST / AutoYaST | Agama (web UI + CLI + HTTP API) |
| Security framework | AppArmor | SELinux (enforcing, 400+ modules) |
| Network stack | wicked | NetworkManager only |
| Config locations | Mixed `/etc` | Defaults in `/usr`; `/etc` for overrides only |
| `/tmp` | Persistent on disk | tmpfs (RAM-backed, cleared on reboot) |
| SSH root login | Password allowed | Password disabled; key-only |
| User groups | Shared `users` group | Per-user primary groups |
| Cgroups | v1 + v2 | v2 only |
| Hypervisor | Xen + KVM | KVM only |
| Display server | Xorg + Wayland | Wayland only (XWayland for compat) |
| Init system | systemd + SysV compat | systemd only (no SysV scripts) |
| Python | 3.6/3.11 | 3.13 |
| CPU minimum | x86-64 | x86-64-v2 |
| DHCP server | ISC DHCP | Kea DHCP |
| Name service | NIS available | NIS removed; LDAP |
| sudo behavior | Target user's password | Own password (wheel group) |
| Zypper repos | Modules + pool/update channels | Single repo per minor release |
| Remote desktop | VNC | GNOME Remote Desktop (RDP) |
| GUI toolkits | GTK2, Qt5, wxWidgets | GTK3+/GTK4, Qt6 only |
| Audio (Leap) | PulseAudio | PipeWire |

## Agama Installer (Replaces YaST)

YaST and AutoYaST are fully removed. Agama provides:

- **Web UI** for interactive installs
- **CLI** (`agama`) for scripted installs
- **HTTP API** for automation
- **Profiles** (JSON/Jsonnet) replace AutoYaST XML for unattended installs

```bash
# Unattended install with Agama profile
agama profile import profile.json
agama install

# Profiles are additive — layer multiple profiles
agama profile import base.json
agama profile import site-specific.json
agama install
```

For remote management, use **Cockpit** (replaces YaST remote modules). For configuration management, use **Salt** or **Ansible**.

See [references/installer-and-management.md](references/installer-and-management.md) for details.

## SELinux (Replaces AppArmor)

SELinux is enforcing by default with policies for 400+ modules. AppArmor is no longer the default.

```bash
# Check status
sestatus
getenforce # returns "Enforcing"

# Temporarily set to permissive (for debugging)
setenforce 0

# View/manage booleans
getsebool -a
setsebool -P httpd_can_network_connect on

# Troubleshoot denials
ausearch -m AVC -ts recent
audit2allow -a # generate policy from denials
```

**openSUSE note**: AppArmor cannot be selected during install but can be enabled post-install. AppArmor updated from 3.1 to 4.1 (fine-grained network rules by IP/port in 4.0, `priority=<number>` rule prefix in 4.1).

See [references/security-and-networking.md](references/security-and-networking.md) for details.

## NetworkManager Only (wicked Removed)

`wicked` is removed. NetworkManager is the sole network stack. Interface names use systemd predictable naming.

```bash
# Configure network via CLI
nmcli connection show
nmcli connection add type ethernet con-name eth0 ifname enp0s3 ipv4.method manual ipv4.addresses 192.168.1.10/24

# For complex naming, use systemd.link
# /etc/systemd/network/10-custom.link
```

See [references/security-and-networking.md](references/security-and-networking.md) for networking details.

## System Defaults Moved to /usr

Default configs now live in `/usr`; `/etc` is for admin overrides only.

```bash
# Customize systemd settings — create drop-in snippets
mkdir -p /etc/systemd/system/myservice.service.d/
cat >/etc/systemd/system/myservice.service.d/override.conf <<EOF
[Service]
LimitNOFILE=65536
EOF

# Restore a default: remove the /etc override
rm /etc/systemd/system/myservice.service.d/override.conf
```

See [references/system-defaults.md](references/system-defaults.md) for full details.

## SSH Root Password Login Disabled

New installs disable password-based SSH for root. If no SSH key is provided during install, sshd won't be enabled.

```bash
# Restore password login (not recommended)
zypper install openssh-server-config-rootlogin
```

## /tmp Is Now tmpfs

`/tmp` uses tmpfs (RAM-backed), cleared on every reboot. Applications writing persistent temporary data must use `/var/cache`, `/var/tmp`, or another persistent location.

## sudo: Wheel Group and Auth Changes

The first user created by the installer is added to the `wheel` group. The `sudo-policy-wheel-auth-self` package (installed by default) changes sudo behavior:

- Users in `wheel` group: prompted for **their own** password (not root's)
- Users NOT in `wheel`: prompted for root password

This replaces the 15.x behavior where `sudo` always prompted for the target user's password.

## /etc/hostname No Longer Strips FQDN

Previously, if a FQDN was stored in `/etc/hostname`, the domain part was silently stripped. In 16.0, the name is applied as-is. Storing a FQDN is discouraged (non-RFC-compliant); use DNS or `/etc/hosts` for FQDN resolution.

## No Zypper Modules or Split Repos

The module system (basesystem, server-apps, development, etc.) is gone. No separate `pool`/`update` channels. Minor releases (16.1, 16.2) get separate repositories.

## Key Version Changes

| Component | Version | Notes |
|-----------|---------|-------|
| Python | 3.13 | `/usr/bin/python3` ��� may bump in minor releases |
| Kernel compiler | gcc 13 | Install `gcc13`, invoke as `gcc-13` for module builds |
| CPU requirement | x86-64-v2 | QEMU needs `-cpu host` or v2-capable model |
| Cgroups | v2 only | v1 no longer available |

## mountfd API in util-linux

`mount` uses the new kernel mountfd API. For read-only mounts where you need the physical layer read-write:

```bash
mount -oro=vfs    # instead of: mount -oro
```

## Per-User Primary Groups

`USERGROUPS_ENAB` is enabled: each new user gets their own primary group instead of the shared `users` group. Scripts relying on `@users` in sudoers or similar need updating.

## Major Removals

| Removed | Replacement | Notes |
|---------|-------------|-------|
| YaST / AutoYaST | Agama, Cockpit, Salt/Ansible | Full removal |
| wicked | NetworkManager | Sole network stack |
| AppArmor (default) | SELinux (enforcing) | 400+ policy modules |
| Xen hypervisor | KVM | HVM/PVH guests still work |
| Xorg | Wayland + XWayland | X11 apps via XWayland |
| SysV init scripts | systemd units | `rc<service>` shortcuts removed |
| NIS (`ypserv`) | LDAP | Full removal |
| ISC DHCP server | Kea DHCP | |
| 32-bit support | -- | `ia32_emulation` kernel param on x86_64 |
| `/etc/services` | -- | Dummy file, being phased out |
| `libnsl.so.1` | -- | `libnsl-stub1` temporary workaround |
| `nscd` | -- | Removed |
| `crun` | `runc` | |
| `dovecot` 2.3 | 2.4 | Incompatible config format, manual migration |
| VNC server | GNOME Remote Desktop (RDP) | |
| GTK2, Qt5, wxWidgets | GTK3+/GTK4, Qt6 | Desktop toolkit migration required |
| `sapconf` | `saptune` | SLES only |

See [references/removals-and-migrations.md](references/removals-and-migrations.md) for migration guidance.

## SLES-Specific Notes

- **Kdump**: Configure via `kdumptool` and `/etc/sysconfig/kdump`. NOT enabled by default in 16.0 (fix planned for 16.1). See [references/installer-and-management.md](references/installer-and-management.md).
- **`sapconf` removed**: Use `saptune` for SAP tuning.
- **Rebranding**: "SUSE Linux Enterprise Server" is now "SUSE Linux".

## openSUSE-Specific Notes

### PipeWire Replaces PulseAudio

PipeWire is the default audio stack in Leap 16.0. Upgrades auto-migrate. If issues: ensure not using `wireplumber-video-only-profile`.

### NVIDIA Auto-Setup

On supported GPUs, NVIDIA open driver and graphics repository are installed automatically. User-space drivers also auto-installed for out-of-box graphical acceleration.

### libvirt + Docker nftables Conflict

Docker doesn't support nftables, breaking libvirt VM networking. Fix:

```bash
# /etc/libvirt/network.conf
firewall_backend = "iptables"

firewall-cmd --add-interface=virbr0 --zone=libvirt --permanent
firewall-cmd --reload
systemctl restart libvirtd
```

### 32-bit / Steam on Leap

Steam removed from Non-OSS repo; use Flatpak. For 32-bit: install `grub2-compat-ia32` and reboot. SELinux users may need `selinux-policy-targeted-gaming`.

### Migration Tool (15->16)

`opensuse-migration-tool` (install on 15.6) handles migration to Leap 16, Slowroll, Tumbleweed, or SLES.

### openSUSE-Only Removals

- HexChat (upstream archived) -- use Polari or Flatpak
- `ansible-9` / `ansible-core-2.16`
- `criu`
- nmap deprecated (license change)

### Desktop Environments (Leap 16.0)

- **Plasma 6.4**: Per-desktop tiling layouts, overhauled Spectacle
- **GNOME 48**: Notification stacking, triple buffering, Digital Wellbeing
- **Xfce 4.20**: Fractional scaling, improved file manager (experimental Wayland session)

### Lifecycle

24-month community support per release. Annual minor releases through Leap 16.6 (fall 2031). Leap 15.6 support extended to April 2026.

## openSUSE Leap 15.6 (June 2024)

Pre-16.0 changes specific to openSUSE Leap. See [references/leap-15.6-changes.md](references/leap-15.6-changes.md).

- **Bumblebee removed** -- use NVIDIA SUSE Prime for hybrid graphics
- **Cockpit added** -- root login disabled by default; edit `/etc/cockpit/disallowed-users`
- **nouveau disabled** for Turing/Ampere GPUs -- install `nvidia-open-driver-G06-signed-kmp-default`
- **4096-bit RSA signing key** -- manual import needed from pre-15.4

## Reference Files

| File | Contents |
|------|----------|
| [installer-and-management.md](references/installer-and-management.md) | Agama installer, profiles, Cockpit, Salt/Ansible, Kdump |
| [security-and-networking.md](references/security-and-networking.md) | SELinux setup, NetworkManager migration, SSH hardening |
| [system-defaults.md](references/system-defaults.md) | /usr defaults, /tmp tmpfs, cgroup v2, per-user groups, mountfd API, Python 3.13, gcc13 |
| [removals-and-migrations.md](references/removals-and-migrations.md) | Full removal list with migration paths |
| [leap-15.6-changes.md](references/leap-15.6-changes.md) | openSUSE Leap 15.6 details (Bumblebee, Cockpit, NVIDIA, signing key) |
| [leap-16.0-opensuse-specific.md](references/leap-16.0-opensuse-specific.md) | openSUSE-only 16.0 details (PipeWire, NVIDIA auto-setup, libvirt, migration tool, desktops) |
