# openSUSE Leap 16.0 — Distribution-Specific Details

Changes in Leap 16.0 that differ from or go beyond the shared SUSE 16 foundation.

## PipeWire Replaces PulseAudio

PipeWire is the default audio stack. Upgrades from 15.6 auto-migrate. If audio issues after upgrade, ensure you are not using `wireplumber-video-only-profile`.

## NVIDIA Auto-Setup

On supported GPUs, the NVIDIA open driver and graphics repository are installed automatically during setup. User-space drivers also auto-installed for out-of-box graphical acceleration.

## libvirt + Docker nftables Conflict

Docker doesn't support nftables, which breaks libvirt VM networking. Fix:

```bash
# /etc/libvirt/network.conf
firewall_backend = "iptables"

firewall-cmd --add-interface=virbr0 --zone=libvirt --permanent
firewall-cmd --reload
systemctl restart libvirtd
```

## 32-bit / Steam

Steam removed from Non-OSS repo; use Flatpak. For 32-bit execution on x86_64: install `grub2-compat-ia32` and reboot. SELinux users may need `selinux-policy-targeted-gaming`.

## Migration Tool (15 to 16)

`opensuse-migration-tool` handles migration from Leap 15.6 to Leap 16, Slowroll, Tumbleweed, or SLES:

```bash
# Install on Leap 15.6
zypper install opensuse-migration-tool

# Run migration
opensuse-migration-tool
```

Users migrating with the tool are prompted to switch from AppArmor to SELinux or keep AppArmor. Manual migration retains the existing LSM.

## AppArmor Post-Install

AppArmor cannot be selected during Leap 16.0 installation but can be switched to post-install. AppArmor was updated from 3.1 to 4.1:
- 4.0: Fine-grained network rules by IP/port
- 4.1: `priority=<number>` rule prefix

## Desktop Environments

- **Plasma 6.4**: Flexible per-desktop tiling layouts, overhauled Spectacle for screenshots/recordings, improved Wayland accessibility
- **GNOME 48 "Bengaluru"**: Notification stacking, dynamic triple buffering, Digital Wellbeing tools, faster Files, initial HDR support
- **Xfce 4.20**: Fractional scaling, powerful file manager with customizable shortcuts, experimental Wayland session (uses `gtkgreet` + `greetd` instead of LightDM)

## Xfce Wayland Session

Experimental. Uses `gtkgreet` + `greetd` instead of LightDM. X11 Xfce session still available via XWayland.

## openSUSE-Only Removals

- HexChat (upstream archived) — use Polari or Flatpak
- `ansible-9` / `ansible-core-2.16`
- `criu`
- nmap deprecated (license change), replacement pending

## Lifecycle

- 24-month community support per release
- Annual minor releases expected through Leap 16.6 (fall 2031)
- Successor Leap 17 expected 2032
- Leap 15.6 support extended to April 2026
- 16.0 fully maintained until Jul 2034 (aligned with SLES timeline)
