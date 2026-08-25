# System Services and Operations

Consult this reference for systemd and polkit, reboot and session behavior, recovery and diagnostics, Cockpit, desktop transitions, printing, time services, metrics, and edge operations.

## Contents

- [Systemd, polkit, reboot, sessions, and time](#systemd-polkit-reboot-sessions-and-time)
- [Recovery, diagnostics, and support collection](#recovery-diagnostics-and-support-collection)
- [Cockpit, desktop, and administrative interfaces](#cockpit-desktop-and-administrative-interfaces)
- [Printing, edge onboarding, and metrics](#printing-edge-onboarding-and-metrics)

## Systemd, polkit, reboot, sessions, and time

### systemd and polkit layout changes (10.0)

systemd 257 always uses cgroup v2, ignores the old legacy-controller boot switch, deprecates SysV scripts, and moves vendor defaults from `/etc/systemd` to `/usr/lib/systemd` while preserving `/etc` overrides. Polkit vendor rules under `/usr/share` are world-readable, local rules belong under `/etc/polkit-1/rules.d` with `0750 root:polkitd`, and its service defaults to error-level logging.

### Soft reboots (10.1)

Systemd can restart userspace without a full reboot; in image mode this either restarts the current userspace or switches to a staged image update. A soft reboot does not apply kernel, kpatch, firmware-initialization, or kernel-module changes, and can leave modules mismatched with the running kernel.

### Cron sessions and Environment Modules (10.2)

Set `XDG_SESSION_CLASS=background-light` in a crontab to avoid starting a per-user systemd manager for that session. Environment Modules 5.6 adds recursive `spider` search, module aliases through `provide`, `module-help`/`module-warn`, event logging, and automatic conflict unloading when both `auto_handling` and `conflict_unload` are enabled.

### Reduced-privilege time services (10.2)

LinuxPTP can drop `ptp4l` to the new `linuxptp` user with `user linuxptp`; custom `uds_address` values must then move under `/run/ptp`. Chrony 4.8 adds `maxunreach`, `chronyc -u`, `opencommands`, `local waitsynced|waitunsynced`, and an RTC refclock, while s390x defaults to the STP reference clock instead of public NTP pools.


## Recovery, diagnostics, and support collection

### ReaR and command-line defaults (10.0)

ReaR replaces IBM Z `OUTPUT=IPL` with portable `OUTPUT=RAMDISK`, whose files use `kernel-$RAMDISK_SUFFIX` and `initramfs-$RAMDISK_SUFFIX.img`; its ISO label changes from `RELAXRECOVER` to `REAR-ISO`. `traceroute` now prefers IPv6, and `uname -i`/`-p` return `unknown`, so scripts should use `uname -m`.

### Sos command-line changes (10.0)

Sos plugin option names use hyphens instead of underscores, for example `--plugin-option networking.namespace-pattern=...`. `sos collect` adds `--api-url`, and `sos report --clean` adds `--skip-cleaning-files` with glob support.

### RHEL Lightspeed interfaces (10.1)

The command-line assistant can be included in image-mode Containerfiles, raises its input limit from 2 KB to 32 KB, and returns more specific errors and exit codes. A Developer Preview RHEL MCP server exposes system log and performance context to compatible troubleshooting applications.

### Sos collection behavior (10.1)

Sos 4.10 collects only the three newest coredumps by default, excludes per-user SSH configuration unless `ssh.userconfs=on`, redacts iSCSI CHAP credentials, and emits uncompressed `.tar` files from `sos collect`. Runtime `-k` plugin options are now merged with preset and `/etc/sos/sos.conf` options instead of disabling unrelated settings.

### Sos certificate and cloud handling (10.2)

`sos clean --treat-certificates` can remove, obfuscate, or retain SSL/TLS certificate binaries. Sos also gains an `aws` plugin for instance metadata and automatically identifies the container-running user in AAP deployments.


## Cockpit, desktop, and administrative interfaces

### Desktop and graphical-stack transition (10.0)

The Xorg server is removed but X11 applications remain usable through Xwayland; TigerVNC is replaced by `gnome-remote-desktop` RDP modes, and GNOME Classic must be installed separately. PipeWire replaces the PulseAudio daemon, Qt 6 replaces Qt 5, Ptyxis replaces GNOME Terminal, Papers replaces Evince, and GNOME Text Editor replaces gedit.

### Removed desktop packages (10.0)

WebKitGTK, Evolution, LibreOffice RPMs, Xorg server, the PulseAudio daemon, and several GNOME applications are no longer shipped; Flatpak or upstream packages are required where no in-distribution replacement exists. `power-profiles-daemon` is replaced by TuneD through `tuned-ppd`, configurable in `/etc/tuned/ppd.conf`.

### Toolbx and Cockpit additions (10.1)

Updated UBI Toolbx images include Mesa OpenGL and Vulkan support by default, but not proprietary drivers. Cockpit 344 adds SMART, Stratis 3.8 pools, improved VM consoles, WireGuard IPv6, site-wide `branding.css`, and a separate `cockpit-ws-selinux` policy subpackage.

### Desktop application changes (10.2)

Papers 48.4 removes PostScript, XPS, and the bookmarks sidebar. Libinput 1.30 adds three-finger drag, sticky drag lock, eraser-button mapping, and configurable active tablet areas, subject to compositor support.

### Cockpit 356 compatibility (10.2)

Cockpit-created timers now execute through `/bin/sh`, VM creation adds VNC rather than both VNC and SPICE, and the Podman page manages inactive Quadlets and their lifecycle. Remove obsolete `pam_cockpit_cert` entries; `cockpit-ws` no longer provides TLS itself, so containers use `cockpit-tls` to front it.


## Printing, edge onboarding, and metrics

### CUPS browse-option refresh (10.1)

`BrowseOptionsInterval=None|Static|Dynamic` in `/etc/cups/cups-browsed.conf` controls whether cached defaults are used, defaults are fetched once at startup, or defaults are refreshed on `BrowseInterval`; `None` is the default. Restart `cups-browsed` after changing it.

### Edge onboarding and rollback (10.2)

The new supported `go-fdo-*` client and manufacturer, owner, and rendezvous servers cannot be mixed with the older preview `fdo-*` RPMs or containers. `greenboot-rs` is compatible with existing greenboot health checks and rollback behavior.

### PPD allowlisting (10.2)

`foomatic-rip` rejects unrecognized PPD values; on new installations, scan approved values with `foomatic-hash` and place their hashes in `/etc/foomatic/hashes.d/`. Existing installations should review automatically accepted values in `/var/tmp/foomatic.*`.

### PCP and OpenTelemetry interchange (10.2)

`pmdaopentelemetry` ingests OTLP JSON into PCP, `pcp2opentelemetry` exports live or archived PCP data, and `pmproxy /metrics` returns OpenTelemetry `resourceMetrics` when sent `Accept: application/json`. A new `pmlogger` push model streams archives to a central `pmproxy` without retaining local copies, and a separate PMDA collects SAP HANA metrics.

