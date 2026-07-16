# Services, HA, observability, and desktop

## Desktop and interactive sessions

### Xorg server removal

`xorg-x11-server-Xorg` is absent from CentOS Stream 10. Wayland is the display stack, and `xorg-x11-server-Xwayland` supports legacy X11 applications. (10.0)

### Desktop application removals

GIMP, LibreOffice, and Inkscape are not included as RPM packages. Install them from Flathub or request suitable EPEL packages. (10.0)

### GNOME power profiles use TuneD

GNOME Settings implements Power Saver, Balanced, and Performance through `tuned-ppd` and TuneD instead of `power-profiles-daemon`. Customize the corresponding TuneD profiles for site-specific desktop power policy.

### `vi` no longer selects enhanced Vim

When both `vim-minimal` and `vim-enhanced` are installed, `vi` starts the minimal editor. Invoke `vim` explicitly for the enhanced editor. (10.2)

### Lightweight cron sessions

Set `XDG_SESSION_CLASS=background-light` in a crontab when its jobs should not start the per-user `systemd --user` manager. (10.2)

## Printing, file, and web services

### PPD value allowlisting

`foomatic-rip` rejects unrecognized keyword values. Scan PPD files with `foomatic-hash` and place generated hashes under `/etc/foomatic/hashes.d`; hashes produced another way are not accepted. Existing printers are enabled automatically to prevent regressions. (9.8)

### Samba 4.23 defaults and services

Samba 4.23 enables SMB3 UNIX Extensions by default, offers experimental SMB-over-QUIC through `client smb transports` and `server smb transports`, and adds the `smb_prometheus_endpoint` exporter. `samba-tool domain backup --no-secrets` removes confidential attributes such as BitLocker recovery material and KDS root keys. (9.8)

### Web-server deployment changes

`httpd.service` applies hardening such as `ProtectHome=read-only`, and `mod_authnz_fcgi` loads by default. Test applications that write home directories or manage their own module loading. In image mode, nginx cannot write its default `/usr/share/nginx/html` document root; choose a writable alternative with a drop-in under `/etc/nginx/default.d`.

## Cockpit and host administration

### Cockpit 356 migration points

Cockpit removes obsolete `pam_cockpit_cert` PAM integration and TLS handling from `cockpit-ws`; remove that PAM module manually and use `cockpit-tls` in containers. Timers created in the console run directly through `/bin/sh`. Override branding at `/etc/cockpit/branding.css`. New VMs receive VNC rather than both VNC and SPICE graphics. (9.8)

### Cockpit host-switcher deprecation

Cockpit's multi-host SSH switcher is disabled by default because the browser design cannot secure it adequately. Prefer separate login sessions or Cockpit Client. A temporary, risk-accepted re-enable sets `AllowMultiHost=yes` under `[WebService]` in `cockpit.conf`.

## System Roles

### System Roles for storage, immutable hosts, and upgrades

The storage role can add, remove, resize, and format disk partitions and create bootable Snapm snapshots. System Roles can manage `ostree`-based immutable hosts except through `nbde_client`. New `analysis`, `remediate`, and `upgrade` roles automate large 8-to-9 upgrade phases. (9.8)

### Expanded networking, HA, SSH, and metrics roles

The firewall role accepts IPv6 `ipset_entries` and `ipset_options`, but a set cannot mix IPv4, IPv6, and MAC entries. The HA role exports cluster properties, defaults, and all four constraint classes, preserving `stonith-watchdog-timeout` and `fencing-watchdog-timeout`. SSH roles add canonical-user, version-addendum, and GSSAPI-delegation controls. The metrics role can provision or copy Grafana TLS certificates and keys. (9.8)

### System-role controller compatibility

The release 10 `ansible-core` 2.16 control node supports managing only release 9 and 10 nodes. The `microsoft.sql.server` role can run on a release 10 controller but cannot configure a release 10 target until SQL Server supports that platform.

## High availability and Pacemaker

### Pacemaker descriptions and nftables port blocking

`pcs cib element description` adds descriptions to CIB elements; `pcs resource description` and `pcs stonith description` are aliases. The `portblock` resource agent uses nftables by default. Set its `firewall` parameter to `iptables` only for legacy behavior. (10.2)

### HA console and resource-model changes

The `pcsd` web UI is available only through the `cockpit-ha-cluster` web-console add-on, not standalone. RKT bundles, `upstart` and `nagios` resource classes, multiple top-level location rules, and legacy `master` and `slave` role terms are unsupported. Run `pcs cluster cib-upgrade` to split multi-rule constraints and use promoted-clone terminology.

### `pcs` command migrations

Removed forms include `pcs cluster pcsd-status`, `pcs cluster certkey`, and `show` or `list` for ACLs, alerts, constraints, properties, and tags. Use `pcs status pcsd` or `pcs pcsd status`, `pcs pcsd certkey`, and corresponding `config` commands. Defaults assignments require `defaults update`. Cross-use of resource and STONITH commands, STONITH resources in groups, `pcs resource move --autodelete`, and several STONITH disable flags are rejected.

### Pacemaker CIB upgrade transformations

CIB upgrade sets `validate-with` to `pacemaker-4.0`, changes `stonith-action=poweroff` to `off`, converts legacy master resources to promotable clones, and renames `crmd-finalization-timeout`, `crmd-integration-timeout`, and `crmd-transition-delay` to their `join-*` or `transition-delay` names. It removes obsolete classes, attributes, properties, and `lifetime` elements. `concurrent-fencing` defaults to `true`; `globally-unique` defaults to `true` when `clone-node-max` exceeds one.

## Metrics and telemetry

### PCP and OpenTelemetry interchange

`pmdaopentelemetry` ingests OTLP JSON into dynamically created PCP metrics, and `pcp2opentelemetry` exports live or archived PCP data. `pmproxy` returns OpenTelemetry `resourceMetrics` JSON from `/metrics` when a request uses `Accept: application/json`; OpenMetrics text remains the default. (10.2)
