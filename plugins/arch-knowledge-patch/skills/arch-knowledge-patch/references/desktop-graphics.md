# Desktop and Graphics

## Wine WoW64 transition (2025-06-16)

The `wine` and `wine-staging` packages switched to a pure WoW64 build. The multilib repository is no longer needed for Wine.

**Breaking**: Existing 32-bit Wine prefixes must be recreated after this update:

```bash
rm -rf ~/.wine
# Then reinstall your applications
```

Known limitation: 32-bit apps using OpenGL directly may have reduced performance under the new WoW64 mode.

## Plasma 6.4.0 — Wayland-only by default (2025-06-20)

Plasma 6.4 split `kwin` into `kwin-wayland` and `kwin-x11`. Only the Wayland session is installed by default. X11 users who don't intervene will lose their login session.

```bash
# If you use X11, install before upgrading:
pacman -S plasma-x11-session
```

## linux-firmware split (2025-06-21)

`linux-firmware` was split into separate vendor packages (e.g., `linux-firmware-nvidia`, `linux-firmware-intel`, etc.). The `linux-firmware` meta-package now depends on a default set of these.

**Breaking**: Upgrading from `20250508` or earlier fails due to NVIDIA firmware symlink conflicts. Workaround:

```bash
# Remove old monolithic package first (ignore deps), then upgrade
pacman -Rdd linux-firmware
pacman -Syu linux-firmware
```

## NVIDIA 590 driver — Open kernel modules (2025-12-20)

The `nvidia`, `nvidia-dkms`, and `nvidia-lts` packages are replaced by `nvidia-open`, `nvidia-open-dkms`, and `nvidia-lts-open` respectively. Turing (RTX 20xx / GTX 1650) and newer GPUs transition automatically on upgrade.

**Breaking for Pascal (GTX 10xx) and older**: The 590 driver no longer supports these GPUs. Upgrading will break your graphical environment. Switch to the legacy branch:

```bash
# Remove official package first
pacman -R nvidia # or nvidia-dkms / nvidia-lts
# Install legacy driver from AUR
yay -S nvidia-580xx-dkms
```
