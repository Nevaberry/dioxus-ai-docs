# Administration and Desktop

Use this reference for service management, desktop sessions, resource controls, tuning, and local administration.

## Administration stack

### Cockpit and YaST

Leap 16 removes YaST in favor of Cockpit for manual administration. Cockpit modules cover subscriptions, repositories, and package installation or removal, and the PackageKit module can select individual updates. The subscription and repository modules do not yet work for unprivileged users, and package removal does not protect overall system usability.

Leap 15.6 includes Cockpit but disables password login as `root` by default. To allow it, remove `root` from `/etc/cockpit/disallowed-users` and restart the socket:

```sh
systemctl restart cockpit.socket
```

### systemd configuration and compatibility

Leap 16 ships main systemd configuration under `/usr`, so local files under `/etc` take precedence. Prefer drop-ins such as `/etc/systemd/coredump.conf.d/*.conf`, or copy a packaged default into `/etc` before editing it. Remove the `/etc` override to restore the packaged default.

SLES 15 SP6 moves systemd from 249 to 254. It adds encrypted and authenticated credentials, raises the maximum inode count for `/dev` and `/tmp` to one million, changes `busctl capture` output to `pcapng`, deprecates `udevadm hwdb` in favor of `systemd-hwdb`, warns when `systemctl` runs in a chroot without `/proc`, and allows all matching `modalias` patterns to contribute hardware-database properties. The `after-local` SysV script is removed except where an upgrade creates a compatibility path.

Leap 16 removes SysV `init.d` support and `rc<service>` controls; use native systemd units.

### Resource control

SLES 15 SP6 defaults to unified cgroup v2 but can still boot in hybrid mode for v1-dependent workloads. Access to v1-only controls—including `cpu.rt_quota_us`, `cpuset.*`, `freezer.state`, older `memory.*` attributes, and the v1-specific `/proc/cgroups`—emits deprecation messages.

Leap 16 supports cgroup v2 only; do not design a supported deployment around cgroup v1 or a hybrid hierarchy.

Query inherited effective systemd limits through `EffectiveMemoryMax`, `EffectiveMemoryHigh`, and `EffectiveTasksMax` rather than manually walking the hierarchy.

### Dynamic tuning

SLES 16 installs `tuned` and its dynamic tuning daemon by default. Check both service state and the selected profile when deployment policy requires deterministic tuning.

Replace removed `sapconf` with `saptune`. When no SAP Notes or Solutions were selected previously, migration gives `saptune` a base tuning automatically; update automation that invokes `sapconf` or assumes its configuration model.

## Desktop sessions and applications

### Wayland and remote desktops

Leap 16 installation offers only Wayland desktop variants. The Xorg server is no longer the supported graphical display server; add Xorg-based environments after installation when needed and run X11 applications through XWayland. The Xfce Wayland session is experimental and uses `gtkgreet` with `greetd`; the LXQt Wayland session is available only after installation.

SLES 16 supplies only a minimal GNOME environment and has no planned SUSE Linux Enterprise Desktop release for 16.0. It removes the VNC server, GTK2, Qt5, and wxWidgets; use RDP for remote desktops and port GUI dependencies to GTK4, Qt6, or another supported toolkit.

### Welcome applications

`opensuse-welcome-launcher` selects `gnome-tour` or `plasma-welcome` instead of the former Qt 5 greeter. Remove the launcher from appliances or managed systems where no welcome application may appear.

### KDE and IBus

KDE Plasma on Leap 15.6 does not start IBus automatically. Add this command as an Autostart application in System Settings:

```sh
ibus-daemon -x
```

On SLES 15 SP7, the full `kde` pattern requires a Workstation Extension subscription and can block upgrade without one. Complete the upgrade, then install the subscription-free minimal pattern:

```sh
zypper rm -t pattern kde
zypper in -t pattern kde_minimal
```

### Audio

Leap 16 uses PipeWire instead of PulseAudio by default, and upgrades should migrate automatically. Use the post-migration script supplied by `opensuse-migration-tool` if they do not, and rule out the `wireplumber-video-only-profile` configuration during troubleshooting.

## Local state and diagnostics

### Temporary storage

Leap 16 mounts `/tmp` as `tmpfs`; it does not survive reboot. Store persistent work state elsewhere.

### Kdump administration

SLES 15 SP6 changes Kdump directory names from `YYYY-MM-DD-HH:MN` to `YYYY-MM-DD-HH-MN`. Update parsers and retention jobs for the hyphen between hour and minute.

SLES 16 removes the YaST Kdump module. Configure `KDUMP_CRASHKERNEL` and `KDUMP_UPDATE_BOOTLOADER` in `/etc/sysconfig/kdump`; use `kdumptool` to verify crash-kernel settings, update the boot loader, or disable Kdump by removing `crashkernel` settings from the boot loader.

### Year 2038

Leap 16 date and time handling is 2038-safe and is intended to work past the 32-bit Unix timestamp rollover.
