# Devices and Administrative Tools

## Udev rules and safe testing

### Side-effect-free tests and stable disk paths (256)

`udevadm test` and `test-builtin` do not modify sysfs, sysctls, interface
settings, or the udev database. Storage receives nested
`/dev/disk/by-path/<path>/by-<kind>/<value>` links to distinguish cloned or
identically labeled media.

### Case-insensitive matches and info fields (257)

Prefix a comparison value with `i` for case-insensitive matching. Parsers of
`udevadm info` should accept device IDs on `J:` lines and driver subsystems on
`B:` lines.

```udev
ATTR{vendor}==i"example"
```

### ACL rules must survive change events (258)

Because ACL handling is in udev, a `uaccess` rule must match `change` as well
as `add`; an `ACTION=="add"`-only rule is insufficient. Sort it before rule 73:

```udev
ACTION!="remove", SUBSYSTEM=="hidraw", TAG+="uaccess"
```

Trace with `udev.trace=` or `udevadm control --trace=`; `OPTIONS="dump"` logs
the event state. `udevadm test` supports `--verbose`, `--json=`, and
`--extra-rules-dir=`; use `udevadm verify` before deployment.

### Exact builtins and CVM matching (258.10-261.2)

Udev accepts `CONST{cvm}` for confidential-VM matching. Builtin names must be
exact; replace abbreviations that previously matched by prefix.

```udev
SUBSYSTEM=="block", CONST{cvm}=="sev-snp", TAG+="cvm"
SUBSYSTEM=="block", IMPORT{builtin}="path_id"
```

## Ownership, ACLs, and session access

### Device access defaults (257)

Active local sessions get `uaccess` for `/dev/udmabuf` and recognized USB
hardware wallets. MTD devices appear as `.device` units; serial ports do so
only when backed by assigned I/O or memory. DeviceTree aliases and
`firmware_node/sun` participate in predictable network names.

### Restricted ownership in v258

Udev ignores `OWNER=`/`GROUP=` values for non-system accounts, and networkd
rejects non-system `User=`/`Group=` on Tun/Tap devices. Test affected rules.
This restriction was partially reverted in v260 and may be backported to v259,
so verify downstream behavior.

### Private terminals and remote graphical access (258, 260)

TTY and PTY nodes default to `0600` rather than `0620`, changing `mesg y` to
`mesg n`; only `-Dtty-mode=0620` restores the old default. The `xaccess`
tag extends foreground-seat `uaccess` to specially marked sessions, chiefly
for remote users in local graphical sessions; PAM sets
`XDG_SESSION_EXTRA_DEVICE_ACCESS=`.

### PTP read access (260)

`/dev/ptp*` defaults to `0664` rather than `0660`. Safe read-only access requires the PHC ioctl
permission fix: kernel 6.15 or patched LTS releases at least 6.12.68, 6.6.122,
6.1.162, 5.15.199, or 5.10.249.

## Stable device identity and defaults

### NVMe namespace links (257)

Unqualified `/dev/disk/by-id/nvme-*` links refer only to namespace 1 and are
absent if namespace 1 does not exist. Multi-namespace software must use
qualified links.

### Virtual block, GPIO, and Wi-Fi identity (259)

Loop, device-mapper, MD, zram, and other virtual block devices expose
`ID_BLOCK_SUBSYSTEM`; GPIO devices gain `/dev/gpio/by-id/`. `net_id` provides
predictable Wi-Fi names on DeviceTree systems.

### Integration and TPM identity (260)

For devices with `ID_BUS=`, `ID_INTEGRATION=` reports `internal` or `external`
and replaces `ID_INPUT_JOYSTICK_INTEGRATION=`. The `tpm2_id` builtin records
vendor/model information; inspect it with `systemd-analyze identify-tpm2`.

Backlight restoration now has a 1% boot-time minimum rather than 5%, and
predictable naming uses the `mc` prefix for MCTP devices.

### Userspace MAC ownership (258.10-261.2)

Systemd networking no longer regenerates a MAC address already set by
userspace, so early provisioning can rely on its assigned value.

## Administrative lifecycle tools

### Tmpfiles purge semantics (256, 257)

Version 256 introduced `--purge` as broader than age-based cleanup and
`--dry-run` as its preview. From 257 onward, purge requires named config files
and removes only entries marked `$`. `L?` creates a symlink only when its
source exists.

```text
d$ /var/lib/example 0755 root root -
L? /usr/local/bin/example - - - - /opt/example/bin/example
```

### Fully locked sysusers accounts (257)

Use the `!` modifier on a `u` line for a fully locked service identity. It
blocks password and non-password interactive login, including SSH.

```text
u! example - "Example service" /var/lib/example
```

### Factory reset (258)

`systemd-factory-reset` requests or cancels reset on next boot;
`factory-reset-now.target` starts immediately, and `systemd.factory_reset=`
requests reset from the kernel command line. The reset target can include
`systemd-tpm2-clear.service`, gated by `systemd.tpm2_allow_clear=`.

### Polkit-capable tools (260)

Systemd-sysext and `varlinkctl` may request interactive Polkit authorization.
Authorized unprivileged callers may also use `systemd-ask-password`.

## Upgrade preparation

### Input and firmware interfaces (257)

Before v258, install `xf86-input-evdev` 2.11.0 or newer and
`xf86-input-libinput` 1.5.0 or newer because F20-F23 microphone/touchpad
remapping moved out of the hardware database. `SystemdOptions` and
`bootctl systemd-efi-options` are deprecated; use credentials and confexts.
