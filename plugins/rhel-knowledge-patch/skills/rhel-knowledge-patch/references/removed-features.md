# Removed Features — RHEL 10

## Packages Removed

| Package | Replacement |
|---------|------------|
| `sendmail` | `postfix` |
| `redis` | `valkey` |
| `dhcp` / `dhclient` | `dhcpcd` or ISC Kea |
| `mod_security` | Third-party (EPEL) |
| `spamassassin` | Third-party (EPEL) |
| `scap-workbench` | `oscap` / `oscap-ssh` CLI |
| `oscap-anaconda-addon` | RHEL image builder OpenSCAP |
| `pam_ssh_agent_auth` | (none) |
| `fips-mode-setup` | `fips=1` kernel arg at install |
| `openssl-pkcs11` | `pkcs11-provider` |
| `initial-setup` | `gnome-initial-setup` |
| `gpsd-minimal` | `gpsd` (renamed) |

## Network Teaming Removed

`teamd` and `libteam` are removed. Migrate to bonding:

```bash
# Before (RHEL 9)
nmcli connection add type team ...
nmcli connection add type team-slave ...

# After (RHEL 10)
nmcli connection add type bond ...
nmcli connection add type ethernet master bond0 ...
```

Migrate before upgrading from RHEL 9 to 10.

## DHCP Changes

ISC DHCP (`dhcp-client`, `dhclient`) removed. ISC Kea is the replacement DHCP server:

```bash
# ISC Kea replaces ISC DHCP
dnf install kea
```

NetworkManager internal DHCP client is the default (unchanged from RHEL 9 default).

## Installer Removals

| Feature | Status |
|---------|--------|
| VNC remote access | Replaced by RDP |
| `inst.xdriver` boot option | Removed (Wayland) |
| `inst.usefbx` boot option | Removed |
| `inst.vnc*` boot options | Replaced by `inst.rdp*` |
| `auth`/`authconfig` Kickstart | Use `authselect` |
| `pwpolicy` Kickstart | Removed |
| `%anaconda` Kickstart | Removed |
| `--teamslaves`/`--teamconfig` | Use `--bondslaves`/`--bondopts` |
| `timezone --ntpservers` | Use `timesource --ntp-server` |
| `timezone --nontp` | Use `timesource --ntp-disable` |
| `timezone --isUtc` | Use `timezone --utc` |
| `--excludeWeakdeps` in `%packages` | Use `--exclude-weakdeps` |
| `--instLangs` in `%packages` | Use `--inst-langs` |
| `--level` in `logging` | Removed |
| Additional repos from GUI | Use Kickstart or `inst.addrepo` |
| LUKS version selection in GUI | Default LUKS2; use Kickstart for other |
| NVDIMM reconfiguration | Removed (sector mode still usable) |

## Kernel and Filesystems

- `kexec_load` syscall removed — use `kexec_file_load`
- GFS2 filesystem removed
- VDO sysfs parameters removed (use `dmsetup` commands)
- `crash --log dumpfile` broken for kernel 5.10+ (use `makedumpfile --dump-dmesg`)

## Security Removals

- `/etc/system-fips` removed
- CVE OVALv2 feed not provided (use CSAF/VEX or Insights)
- OpenSSL ENGINE API removed
- HeartBeat extension removed from TLS
- SRP authentication removed from TLS

## Subscription Management

Removed modules: `attach`, `auto-attach`, `import`, `remove`, `redeem`, `role`, `service-level`, `usage`, `addons`, `syspurpose addons`. Use Red Hat Hybrid Cloud Console.

## Software Management

- `libreport` library support removed from DNF
- DNF `debug` plugin removed (`debug-dump`/`debug-restore`)
