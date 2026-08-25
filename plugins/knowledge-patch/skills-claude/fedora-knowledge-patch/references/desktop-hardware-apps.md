# Desktop, Hardware, and Applications

## Contents

- Desktop sessions and shells
- Power, graphics, and application compatibility
- Input, multimedia, and printing
- Desktop application and plugin transitions

## Desktop sessions and shells

### GNOME installation media is Wayland-only (41)

Workstation and Silverblue installation media do not preinstall the GNOME X11
session. At this stage the session packages remain in repositories and can be
installed, or overlaid on Silverblue, when required.

### GNOME removes its X11 sessions (43)

The GNOME X11 session packages are now removed, not merely absent from media.
Upgrades move existing GNOME-on-X11 users to Wayland. X11 applications remain
supported, but **GNOME on Xorg** is no longer a login option.

### MiracleWM changes its desktop shell (44)

The MiracleWM Spin replaces `nwg-shell` with Dank Material Shell, built on
QuickShell. Do not carry `nwg-shell` configuration assumptions into a fresh
installation.

### Games Lab moves from Xfce to KDE Plasma (44)

The Games Lab image uses KDE Plasma and its Wayland stack instead of Xfce.
Image customization and session automation must target the new desktop.

### KDE variants replace SDDM with Plasma Login Manager (44)

All Fedora KDE variants use Plasma Login Manager by default. SDDM-specific
configuration does not control a fresh installation's login screen.

### Budgie moves from X11 to Wayland (44)

Budgie 10.10 changes Fedora's Budgie session from X11 to Wayland. Review
X11-specific startup, input, capture, display, and automation integrations.

## Power, graphics, and application compatibility

### TuneD replaces power-profiles-daemon (41)

TuneD backs Fedora's desktop power profiles. `tuned-ppd` preserves the
power-profiles-daemon interface used by applications. Administrators can map
the desktop-exposed profiles in `/etc/tuned/ppd.conf`.

### FEX is integrated on AArch64 (42)

Fedora supplies FEX and root-filesystem integration to run x86 and x86-64
Linux binaries on AArch64. Integration with `muvm` supports hosts using 16 KiB
pages.

### Older Intel GPUs lose compute support (42)

Rebased `intel-compute-runtime` and `intel-igc` add current hardware but drop
compute support for broadly pre-2020 Intel GPUs. Video support is unaffected:
`intel-media-driver` continues to support older generations.

### Wine and Steam enable NTSYNC through package recommendations (44)

Packages including Wine and Steam recommend the NTSYNC kernel module to
improve Windows-application compatibility. Fedora does not impose it as an
unconditional system-wide dependency.

## Input, multimedia, and printing

### Traditional Chinese input-method default (41)

For the `zh_TW` desktop locale, `ibus-chewing` replaces `ibus-libzhuyin` as the
default input method. Automation or documentation that still requires the
former engine must name it explicitly.

### Offline IBus speech-to-text (42)

`ibus-speech-to-text` provides voice dictation in any IBus-aware application
using local Vosk recognition and downloadable language models, without a
remote transcription service.

### Offline speech input gains WhisperCpp (44)

`ibus-speech-to-text` 0.7 adds a Whisper engine through `pywhispercpp` alongside
the existing Vosk engine.

### Foomatic command values are allowlisted (43)

`foomatic-rip` rejects unknown values in `FoomaticRIPCommandLine`,
`FoomaticRIPCommandLinePDF`, and `FoomaticRIPOptionSetting`. Run
`foomatic-hash` to scan installed printer drivers and generate the file that
allows their known values.

## Desktop application and plugin transitions

### GNOME Shell extension dependencies are generated (42)

Use the `gnome-shell-extension-rpm-macros` generator to derive supported GNOME
Shell versions from an extension's `metadata.json`. Extension RPMs no longer
need manually synchronized shell-version dependencies.

### Showtime replaces Totem (43)

Workstation uses the GTK 4 and Libadwaita-based Showtime application as its
default video player instead of Totem.

### GNOME applications move to Peas 2 (43)

Workstation carries `libpeas` version 2. Applications and plugins tied to the
1.x interfaces must follow the Peas 1-to-2 migration path.

### LibreOffice's KF5 integration package is removed (44)

`libreoffice-KF5` is dropped because Fedora KDE and LXQt use Qt 6. Remove
dependencies on the old Qt 5 integration subpackage.
