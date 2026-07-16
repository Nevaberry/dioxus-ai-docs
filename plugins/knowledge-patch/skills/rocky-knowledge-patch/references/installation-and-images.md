# Installation, images, and user environments

## Choose supported hardware and architecture

- Rocky Linux 10.0 requires the x86-64-v3 feature level for `x86_64` and
  removes 32-bit compatibility. Use 64-bit libraries or isolate 32-bit
  dependencies in a container.
- Rocky Linux 10.0 limits RISC-V support to StarFive VisionFive 2, QEMU, and
  SiFive HiFive Premier P550.
- Rocky Pi images in 10.0 support Raspberry Pi 4 and 5, not Pi 3 or Pi Zero 2W.
- Rocky Linux 10.1 supports ARMv8.0-A or later (`aarch64`), POWER10 or later in
  little-endian mode (`ppc64le`), and IBM z15 or later (`s390x`).

## Install Rocky Linux

On Rocky Linux 10.0, Anaconda disables the root account by default. Create an
administrative user with full `sudo` access. Remote graphical installation uses
RDP instead of VNC. Add third-party repositories with `inst.addrepo` or
Kickstart because the graphical installer can no longer add them.

If Anaconda hangs on a grey screen before showing its wizard, particularly in a
virtual machine with 3D graphics enabled, switch from tty6 to tty1 with
`Ctrl`+`Alt`+`F1`, then return with `Ctrl`+`Alt`+`F6` (10.0).

## Select published and generated images

Most Rocky Linux 9.4 cloud, container, and Vagrant images moved from
imagefactory to KIWI. `Vagrant-VBox`, `Vagrant-VMware`, and `OCP-Base` remain on
imagefactory. The Azure publisher account also changed, deprecating earlier
images; free images are available through the Azure Community Gallery.

Image Builder in 9.4 accepts arbitrary custom mount points except reserved
operating-system paths. It supports `auto-lvm`, `lvm`, and `raw` partitioning,
and blueprints can tailor security profiles by selecting or unselecting rules.
In 10.1, Image Builder can produce WSL2 images and Vagrant images for the
libvirt provider.

## Install WSL images

Rocky Linux 9.6 publishes installable `.wsl` images for `x86_64` and `aarch64`.
The first launch prompts for a username.

```powershell
wsl --install --from-file path/to/Rocky-9-WSL-Base.latest.x86_64.wsl rocky-wsl-base
```

## Plan desktop and remote access

Rocky Linux 10.0 replaces the X.Org Server with Wayland while retaining
Xwayland for compatible X11 clients. Package and application replacements are:

| Removed or replaced | Replacement or path forward |
|---|---|
| gedit | GNOME Text Editor |
| Eye of GNOME | Loupe |
| GNOME Terminal | Ptyxis |
| Cheese | Snapshot |
| Festival | Espeak NG |
| PulseAudio daemon | PipeWire; PulseAudio client interfaces remain |
| Evolution | Thunderbird as packaged mail client |
| LibreOffice, Inkscape, Totem, Motif | Upstream or Flatpak builds where available |
| TigerVNC server | GNOME Remote Desktop over RDP |

Connections remains available as a VNC client. Use GNOME Remote Desktop over
RDP for desktop sharing, remote login, and headless sessions. Rocky Linux 10.1
also confirms that X11-dependent packages such as `xrdp` are absent, so
instructions that install `xrdp` or `x11vnc` do not work as written.

