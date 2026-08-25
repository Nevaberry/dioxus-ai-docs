# Devices and Administrative Tools

## Udev rules and testing

### Side-effect-free tests and stable storage paths (256)

`udevadm test` and `test-builtin` no longer modify sysfs, sysctls, interface
settings, or the udev database. Storage also gains nested
`/dev/disk/by-path/<path>/by-<kind>/<value>` links to disambiguate cloned or
identically labeled media.

### Case-insensitive matches and output fields (257)

Prefix a comparison value with `i` for case-insensitive matching, for example
`ATTR{vendor}==i"example"`. `udevadm info` uses `J:` for device IDs and `B:`
for driver subsystems; parsers must recognize them.

### ACL rules must survive change events (258)

ACL application lives in udev. A `uaccess` rule must tag `change` as well as
`add` and sort before rule 73:

```udev
ACTION!="remove", SUBSYSTEM=="hidraw", TAG+="uaccess"
```

### Device ownership restriction (258)

V258 udev ignores `OWNER=`/`GROUP=` naming non-system accounts, and networkd
rejects non-system `User=`/`Group=` for Tun/Tap. Find affected rules with
`udevadm verify` and `udevadm test`. This was partly reverted in v260 and may
be backported to v259, so inspect the deployed point release.

### Tracing and alternate rulesets (258)

Enable boot tracing with `udev.trace=` or runtime tracing with
`udevadm control --trace`. `OPTIONS="dump"` logs event state at a rule point.
`udevadm test` accepts `--verbose`, `--json=`, and `--extra-rules-dir=`.

### CVM matching and exact builtin names (258.10-261.2)

All covered point releases support `CONST{cvm}`. Builtin command names must
match exactly; replace prefix abbreviations, for example:

```udev
SUBSYSTEM=="block", CONST{cvm}=="sev-snp", TAG+="cvm"
SUBSYSTEM=="block", IMPORT{builtin}="path_id"
```

## Device identity and access

### Network ownership and link properties (256)

Shipped networkd-only link rules set
`ID_NET_MANAGED_BY=io.systemd.Network`. `.link` files can set, import, or unset
udev properties. Network generator and WireGuard credential behavior is
covered in the networking reference.

### Access and enumeration defaults (257)

Active local sessions receive `uaccess` for `/dev/udmabuf` and recognized USB
hardware wallets. MTD devices appear as `.device` units; serial ports do only
with assigned I/O or memory. DeviceTree aliases and `firmware_node/sun`
participate in predictable interface naming.

### NVMe namespace links (257)

An unqualified `/dev/disk/by-id/nvme-*` link means namespace 1 and is absent
when namespace 1 does not exist. Multi-namespace software should use
namespace-qualified links.

### Virtual block, GPIO, and DeviceTree Wi-Fi identity (259)

Loop, device-mapper, MD, zram, and other virtual block devices expose
`ID_BLOCK_SUBSYSTEM`; GPIO gains `/dev/gpio/by-id/`. The `net_id` builtin can
name DeviceTree Wi-Fi interfaces predictably.

### PTP access requires fixed kernels (260)

`/dev/ptp*` uses mode `0664`. Safe unprivileged read-only access requires
Linux 6.15 or patched LTS versions at least 6.12.68, 6.6.122, 6.1.162,
5.15.199, or 5.10.249.

### Integration, TPM, backlight, and MCTP identity (260)

For devices with `ID_BUS=`, `ID_INTEGRATION=` classifies `internal` or
`external` and replaces removed `ID_INPUT_JOYSTICK_INTEGRATION=`. Builtin
`tpm2_id` records TPM identity shown by `systemd-analyze identify-tpm2`.
Backlight restore minimum is 1% rather than 5%; MCTP predictable names use
the `mc` prefix.

### Remote graphical device access (260)

`xaccess` extends selected foreground-seat `uaccess` rules to specially
marked sessions, chiefly remote users in local graphical sessions needing GPU
render devices. PAM sets `XDG_SESSION_EXTRA_DEVICE_ACCESS=`.

## Administrative cleanup and provisioning

### Tmpfiles purge (256, 257)

The initial `--purge` operation broadly removed paths declared as created and
`--dry-run` previewed it. Since 257, purge requires at least one named config
file and removes only lines marked `$`. Use the same arguments in preview and
execution. Type `L?` creates a symlink only when its source exists.

```text
d$ /var/lib/example 0755 root root -
L? /usr/local/bin/example - - - - /opt/example/bin/example
```

### Fully locked service accounts (257)

A sysusers `u!` line makes a fully locked account, blocking password and other
interactive authentication such as SSH. Prefer it for ordinary service users.

### Factory-reset orchestration (258)

`systemd-factory-reset request|cancel` controls next-boot reset;
`factory-reset-now.target` starts immediately and `systemd.factory_reset=`
requests it from the kernel line. The reset may include
`systemd-tpm2-clear.service`, gated by `systemd.tpm2_allow_clear=`, to
invalidate TPM-held secrets.

### Secure attention and scheduled maintenance (257)

`DesignatedMaintenanceTime=` schedules shutdown. Ctrl-Alt-Shift-Esc emits
`org.freedesktop.login1.SecureAttentionKey` unless disabled. Logind can hand
session-scoped hidraw descriptors to unprivileged clients.
