# Fedora System Changes (41–44)

## /usr/sbin Merged into /usr/bin (Fedora 42)

`/usr/sbin` is now a symlink to `/usr/bin`. `/usr/sbin` has been removed from the default `$PATH`.

All system binaries are now in `/usr/bin`. This follows the UsrMerge pattern already adopted by Debian and Arch.

### Impact

- **Hardcoded `/usr/sbin/` paths** still resolve via symlink — existing scripts won't break immediately
- **`$PATH`-based lookups** for tools that were sbin-only now find them in `/usr/bin`
- **New scripts and Dockerfiles** should use `/usr/bin/` exclusively
- **RPM specs**: `%_sbindir` now expands to `%_bindir`

### Recommendation

Use `/usr/bin/` for all new absolute paths. Don't add `/usr/sbin` back to `$PATH`.

## NetworkManager Drops ifcfg Support (Fedora 41)

The `ifcfg-rh` plugin and the entire `/etc/sysconfig/network-scripts/` configuration format have been removed from NetworkManager.

Packages removed: `NetworkManager-initscripts-ifcfg-rh`, `NetworkManager-dispatcher-routing-rules`, `NetworkManager-initscripts-updown`.

### New Format

Use **keyfile format** — `.nmconnection` files in `/etc/NetworkManager/system-connections/`.

### Migration

```bash
nmcli connection migrate   # converts all ifcfg profiles to keyfile format
```

Note: Auto-migration has been running since F39, so most upgraded systems are already converted.

### Key Differences

| ifcfg format | keyfile format |
|-------------|----------------|
| `/etc/sysconfig/network-scripts/ifcfg-eth0` | `/etc/NetworkManager/system-connections/eth0.nmconnection` |
| `BOOTPROTO=dhcp` | `[ipv4]\nmethod=auto` |
| `ONBOOT=yes` | `[connection]\nautoconnect=true` |
| Custom scripts in `network-scripts/` | Use NetworkManager dispatcher scripts |

### network-scripts Package Also Removed (Fedora 41)

The `network-scripts` package providing `ifup`/`ifdown` is removed.

```bash
# Old (breaks)         → New
ifup eth0              → nmcli connection up eth0
ifdown eth0            → nmcli connection down eth0
```

### Impact on Ansible/Automation

Playbooks using `community.general.nmcli` module are unaffected (it uses D-Bus). Playbooks that template `ifcfg-*` files directly must switch to keyfile format or use the `nmcli` module.

## nftables Default for Podman and Libvirt (Fedora 41)

### Podman/Netavark

Container firewall rules are now managed via **nftables** instead of iptables. Custom `iptables` rules interacting with Podman networking may conflict.

```bash
# Old (shows nothing for container rules on F41+)
iptables -L

# New
nft list ruleset
```

### Libvirt

The default firewall backend for `virbr0` and other virtual networks switches from iptables to nftables. Libvirt creates rules in a dedicated `libvirt_network` nftables table.

**Docker incompatibility:** Docker sets the iptables FORWARD chain policy to DENY, which blocks traffic in libvirt's separate nftables table. If running Docker alongside libvirt VMs:

```ini
# /etc/libvirt/network.conf
firewall_backend = "iptables"
```

Then restart: `systemctl restart virtnetworkd`

## Anaconda Installer Changes (Fedora 42–43)

### WebUI Installer (Fedora 42+)

The GTK-based Anaconda installer is replaced by a **PatternFly-based WebUI** (wizard-style). Default for Workstation in F42, expanded to all Spins and KDE in F43.

Features: Guided partitioning, dual-boot support, remote installation via any web browser.

### VNC Removed, RDP Replaces It (Fedora 42)

The installer no longer supports VNC for remote installations. Anaconda is now a native Wayland application.

```bash
# Old boot options (break on F42+)
inst.vnc
inst.vnc.password=secret

# New boot options
inst.rdp
inst.rdp.password=secret
```

## lastlog → lastlog2 (Fedora 43)

The traditional `lastlog` (binary format in `/var/log/lastlog`) and `pam_lastlog` are replaced by **lastlog2** from util-linux. Motivated by Y2038 fix (old format used 32-bit timestamps).

| Old | New |
|-----|-----|
| `/var/log/lastlog` (binary) | SQLite database |
| `lastlog` command | `lastlog2` command |
| `pam_lastlog.so` | `pam_lastlog2.so` |

Migration is automatic on upgrade. Scripts that parse the old binary format will break.

## Wayland-Only GNOME (Fedora 43)

GNOME X11 session packages removed from repositories:

- `gnome-session-xsession`
- `gnome-classic-session-xsession`

XWayland remains available — X11 **applications** still work, but the X11 **session** (display server) is gone. GDM still supports launching X11 sessions from other desktop environments (KDE, etc.).

Applications that require X11 features not yet available in Wayland should use XWayland (automatic for most apps via `GDK_BACKEND=x11` or similar).
