# Desktop Experience and Graphics

## Application installation and permissions

Ubuntu 24.10 App Center can install third-party deb packages directly. Its new
Security Center can enable experimental Home-directory permission prompting;
the seeded `prompting-client` snap handles the prompts.

## Default applications and integrations

Ubuntu 25.04 makes Papers the default PDF viewer instead of Evince. It installs
`xdg-terminal-exec` to select the terminal used by shortcuts and application
launches, uses BeaconDB for geolocation, and supports JPEG XL without an
additional package.

Ubuntu 25.10 replaces Eye of GNOME with Loupe as the default Image Viewer and
replaces GNOME Terminal with Ptyxis.

## Session and reporting changes

Ubuntu Desktop 25.10 is Wayland-only: GNOME Shell can no longer run as an X.org
session, and Ubuntu-on-X.org is not offered.

Ubuntu Insights replaces Ubuntu Report in GNOME Initial Setup and adds opt-in,
periodic collection of selected non-personally-identifying metrics. Previous
Ubuntu Report consent is not migrated, so users must opt in again.

Ubuntu Desktop 26.04 uses GNOME 50. Validate extensions and desktop-management
integrations against that GNOME generation.

## Graphics acceleration

### VA-API and NVIDIA Dynamic Boost

VA-API support is available from `main` in Ubuntu 25.04. Enable it during
installation with third-party drivers or later with:

```sh
sudo apt install va-driver-all
```

Intel Core Ultra Xe2 and Arc B580/B570 graphics have full acceleration support.
NVIDIA Dynamic Boost is enabled by default on supported laptops and activates
only under GPU load while connected to AC power.

### Intel Xe3 and Panther Lake

Ubuntu 25.10 fully supports Intel Core Ultra Xe3 integrated graphics and Arc Pro
B50/B60 discrete GPUs, with initial Panther Lake support in Linux 6.17. The
stack adds enhanced Intel GPU virtualization and passthrough, OpenCL 2.0
coarse-grain buffer SVM, Panther Lake decoding and VP9 encoding, and Level Zero
ray-tracing acceleration structures.

### Installation and virtualization limitations

Selecting NVIDIA drivers during an offline Ubuntu 25.10 installation installs
Nouveau. Install while online or update the driver afterward.

GTK4 applications, including the desktop wallpaper, can render incorrectly in
VirtualBox or VMware with 3D acceleration enabled. The Snap Store can crash on
Qualcomm Snapdragon X Elite hardware.

## Raspberry Pi desktop images

Ubuntu 25.04 Raspberry Pi desktop images use `gnome-initial-setup`. This also
makes cloud-init usable for automated first-user creation, package installation,
and customization.

Ubuntu 25.10 Raspberry Pi desktop images use the `desktop-minimal` seed and omit
the previously seeded backup, archive, calendar, camera, office,
remote-desktop, media, scanning, mail, and BitTorrent applications. Upgraded
installations retain the manually installed `ubuntu-desktop` metapackage and its
applications.

Cloud-init creates the desktop swap file. Customize its size in boot-partition
user-data before first boot.
