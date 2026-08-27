# Administration and Desktop

## Cockpit and administration tools

### Cockpit root login on Leap 15.6 (`leap-15.6`)

Cockpit is included, but password login as `root` is disabled by default. To
allow it, remove `root` from `/etc/cockpit/disallowed-users` and restart the
socket:

```sh
systemctl restart cockpit.socket
```

### Cockpit replaces YaST on Leap 16 (`leap-16.0-guide`)

YaST is removed for manual administration. Cockpit supplies modules for
subscriptions, repositories, and package installation/removal, while the
PackageKit module can select individual updates. Subscription and repository
modules do not yet work for unprivileged users, and package removal does not
protect against making the system unusable.

## Desktop sessions and applications

### IBus under KDE Plasma (`leap-15.6`)

KDE Plasma does not start IBus automatically. Add an autostart application in
System Settings using:

```sh
ibus-daemon -x
```

### Wayland-only installation (`leap-16.0-guide`)

The Leap 16 installer offers only Wayland desktop variants. Add Xorg-based
environments after installation; X11 applications run through XWayland because
Xorg is no longer the supported display server. Xfce's Wayland session is
experimental and uses `gtkgreet` with `greetd`; LXQt Wayland is available only
after installation.

### Welcome-screen control (`leap-16.0-guide`)

`opensuse-welcome-launcher` selects `gnome-tour` or `plasma-welcome` rather than
the old Qt 5 greeter. Remove the launcher from managed images and appliances
where no welcome application may appear.

### PipeWire migration (`leap-16.0-guide`)

PipeWire replaces PulseAudio. Upgrades normally migrate automatically; the
openSUSE migration tool supplies a post-migration script when they do not. When
audio still fails, check whether `wireplumber-video-only-profile` selected an
inappropriate WirePlumber profile.

### KDE upgrade without Workstation Extension

On SLES 15 SP7, the full `kde` pattern requires a Workstation Extension
subscription and can block upgrade when that subscription is absent. Complete
the upgrade, then install the subscription-free minimal pattern:

```sh
zypper rm -t pattern kde
zypper in -t pattern kde_minimal
```

### Reduced SLES 16 desktop compatibility

SUSE Linux Enterprise Desktop is not planned for 16.0; SLES supplies only a
minimal GNOME environment. VNC server, GTK2, Qt5, and wxWidgets are removed.
Use RDP for remote desktop access and port applications to GTK4, Qt6, or other
supported toolkits.

### GNOME Software updates (`16.0-rev-2026-08-04`)

GNOME Software supports online updates and detects transactional systems, so a
desktop update workflow can distinguish and correctly handle transactional
hosts.

## systemd and local configuration

### Packaged defaults under `/usr` (`leap-16.0-guide`)

Main systemd configuration files now live under `/usr`; local files under
`/etc` have higher precedence. Prefer drop-ins such as
`/etc/systemd/coredump.conf.d/*.conf`, or copy a default into `/etc` before
editing. Remove the `/etc` override to restore the packaged default.

### Volatile `/tmp` (`leap-16.0-guide`)

`/tmp` is a `tmpfs` and does not survive reboot. Move persistent work state to
another location.

### systemd 254 changes on SLES 15 SP6

The move from systemd 249 to 254 adds encrypted/authenticated credentials and
raises the inode limits for `/dev` and `/tmp` to one million. It also changes
several interfaces:

- `busctl capture` writes `pcapng`.
- `udevadm hwdb` is deprecated; use `systemd-hwdb`.
- `systemctl` warns in chroots that lack `/proc`.
- Every matching `modalias` pattern can contribute hardware-database properties.
- The `after-local` SysV script is removed except on upgrades that created a
  compatibility path.

## cgroups and effective limits

### Leap 16 requires cgroup v2 (`leap-16.0-guide`)

systemd uses cgroup v2; cgroup v1 and hybrid hierarchies are unsupported.
Workloads that require v1 cannot use the supported Leap 16 configuration.

### SLES 15 SP6 transition behavior

Unified cgroup v2 becomes the default, but a boot option can still select hybrid
mode for v1-dependent workloads. Accessing `cpu.rt_quota_us`, `cpuset.*`,
`freezer.state`, older `memory.*` attributes, or v1-specific `/proc/cgroups`
emits deprecation messages.

systemd also exposes `EffectiveMemoryMax`, `EffectiveMemoryHigh`, and
`EffectiveTasksMax`, so query these properties for inherited effective session
limits instead of walking the hierarchy manually.

## Kdump administration

### Output-directory naming on SLES 15 SP6

Kdump directory names change from `YYYY-MM-DD-HH:MN` to
`YYYY-MM-DD-HH-MN`. Update parsers and retention jobs for the hyphen between
hour and minute.

### Command-line configuration on SLES 16

The YaST Kdump module is gone. Configure `/etc/sysconfig/kdump` using
`KDUMP_CRASHKERNEL` and `KDUMP_UPDATE_BOOTLOADER`; use `kdumptool` to verify
crash-kernel settings and update the boot loader. To disable Kdump, remove
`crashkernel` settings from the boot loader.

## Tuning and host behavior

### SAP tuning migration (`leap-16.0-guide`)

`saptune` replaces `sapconf`. When no SAP Notes or Solutions were selected,
`saptune` applies a base tuning automatically. Migrate automation and assumptions
that invoke `sapconf`.

### Literal hostname handling

SLES 16 applies `/etc/hostname` literally instead of stripping the domain from
an FQDN. Prefer an unqualified hostname because applications can interpret an
FQDN there differently.

### `tuned` defaults and centralized hardening

SLES 16 installs the `tuned` daemon by default. Inspect whether it is running
and which profile is selected whenever a deployment controls dynamic tuning.
The `16.0-rev-2026-08-04` revision also centralizes kernel hardening in a
`tuned` profile; compliance automation must account for the profile rather than
assuming independent activation of every hardening control.
