# Administration and Desktop

## Cockpit and administration

Leap 15.6 includes Cockpit but disables password login as `root`. Remove `root`
from `/etc/cockpit/disallowed-users` and restart the socket only when direct root
login is deliberately required:

```sh
systemctl restart cockpit.socket
```

Leap 16 removes YaST for manual administration in favor of Cockpit. Its Leap
modules cover subscriptions, repositories, and package installation/removal;
the subscription and repository modules do not yet work for unprivileged users,
and package removal has no system-usability safeguard. (leap-16.0-guide)

## Desktop sessions and applications

KDE Plasma does not autostart IBus. Add `ibus-daemon -x` in System Settings,
Startup and Shutdown, Autostart. (leap-15.6)

Leap 16 installation offers Wayland desktop variants only. Install an
Xorg-based environment afterward if required; X11 applications run through
XWayland. Xfce's Wayland session is experimental and uses `gtkgreet` with
`greetd`; the LXQt Wayland session is available only after installation.

`opensuse-welcome-launcher` selects `gnome-tour` or `plasma-welcome` instead of
the old Qt 5 greeter. Remove the launcher from appliances and managed systems
where no welcome application may appear.

PipeWire replaces PulseAudio by default. Upgrades should migrate automatically,
and `opensuse-migration-tool` supplies a post-migration script when they do not.
When audio is still unavailable, also inspect the
`wireplumber-video-only-profile` configuration.

GNOME Software now handles online updates and detects transactional systems, so
desktop workflows can distinguish those hosts. (16.0-rev-2026-08-04)

The full `kde` pattern requires a Workstation Extension subscription and can
block an SLES 15 SP7 upgrade without one. Finish the upgrade and then select the
minimal pattern:

```sh
zypper rm -t pattern kde
zypper in -t pattern kde_minimal
```

## systemd and cgroups

Leap 16 ships main systemd configuration under `/usr`; local `/etc` files and
drop-ins such as `/etc/systemd/coredump.conf.d/*.conf` take precedence. Copy a
default into `/etc` before editing when needed, and remove the `/etc` override to
restore the package default.

SLES 15 SP6 moves systemd from 249 to 254. It adds encrypted/authenticated
credentials and raises the `/dev` and `/tmp` inode limits to one million.
Compatibility changes include:

- `busctl capture` writes `pcapng`.
- `udevadm hwdb` is deprecated; use `systemd-hwdb`.
- `systemctl` warns in chroots without `/proc`.
- All matching `modalias` patterns can contribute hardware-database properties.
- `after-local` is removed except for upgrade-created compatibility paths.

SLES 15 SP6 defaults to unified cgroup v2 but still permits a boot option for
hybrid mode. Use of v1 controls such as `cpu.rt_quota_us`, `cpuset.*`,
`freezer.state`, older `memory.*` attributes, and `/proc/cgroups` emits
deprecation messages. Leap 16 supports only cgroup v2.

Query `EffectiveMemoryMax`, `EffectiveMemoryHigh`, and `EffectiveTasksMax` to
obtain inherited effective systemd session limits directly.

## Files, users, and host settings

Leap 16 mounts `/tmp` as `tmpfs`; it does not survive reboot. Move persistent
work state elsewhere.

With `USERGROUPS_ENAB` in `/usr/etc/login.defs`, newly created Leap 16 users get
a same-named primary group rather than `users`, including after upgrades that
did not override `/etc/login.defs`. Audit `@users` policy and home-directory
group ownership. If a home uses no other group, convert it with:

```sh
chgrp -R myuser "$HOME"
```

SLES 16 applies `/etc/hostname` literally rather than stripping the domain from
an FQDN. Prefer an unqualified hostname to avoid application-specific surprises.

The `tuned` package and dynamic tuning daemon are installed by default. Inspect
the service and selected profile whenever deployment policy must control tuning.
The later SLES 16.0 revision also centralizes kernel hardening in a `tuned`
profile, so compliance automation must account for the profile rather than
assuming every hardening control is independent.

## SAP tuning and Kdump

Leap 16 replaces `sapconf` with `saptune`. When no SAP Notes or Solutions were
selected, `saptune` receives a base tuning automatically; migrate automation and
assumptions that invoke `sapconf`.

SLES 15 SP6 Kdump directories use `YYYY-MM-DD-HH-MN`, not
`YYYY-MM-DD-HH:MN`; update parsers and retention jobs.

With the YaST Kdump module removed in SLES 16, set `KDUMP_CRASHKERNEL` and
`KDUMP_UPDATE_BOOTLOADER` in `/etc/sysconfig/kdump`. Use `kdumptool` to verify
settings and update the boot loader, or disable Kdump by removing its
`crashkernel` boot-loader settings.
