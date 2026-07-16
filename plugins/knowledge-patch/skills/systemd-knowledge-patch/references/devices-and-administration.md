# Devices and Administrative Tools

## Test and trace udev rules

- `udevadm test` and `test-builtin` do not modify sysfs, sysctls, interface settings, or the udev database, making privileged diagnostic runs side-effect free (since 256).
- Udev comparisons can prefix the comparison value with `i` for case-insensitive matching. `udevadm info` emits device IDs on `J:` lines and driver subsystems on `B:` lines; output parsers must recognize them (since 257).

```udev
ATTR{product}==i"example"
```

- Enable tracing at boot with `udev.trace=` or at runtime with `udevadm control --trace=`. `OPTIONS="dump"` logs event state at that point in a rule (since 258).
- `udevadm test` supports `--verbose`, `--json=`, and `--extra-rules-dir=` so an alternate ruleset can be tested before installation (since 258).

## Preserve device ACLs and ownership

- Device ACL application moved fully into udev. A `uaccess` rule must match `change` as well as `add`, and sort before rule number 73; `ACTION=="add"` alone loses access when logind causes a change event (since 258).

```udev
ACTION!="remove", SUBSYSTEM=="hidraw", TAG+="uaccess"
```

- In 258, udev ignored `OWNER=` and `GROUP=` values naming non-system accounts, and networkd rejected such `User=`/`Group=` values for Tun/Tap devices. Use `udevadm verify` and `udevadm test` to identify affected rules. This restriction was partially reverted in 260 and may be backported to 259.
- Udev grants active local sessions `uaccess` to `/dev/udmabuf` and recognized USB hardware wallets. Logind can also hand session-scoped hidraw descriptors to unprivileged clients (since 257).
- The `xaccess` mechanism extends selected foreground-seat `uaccess` rules to specially marked sessions, chiefly local graphical sessions owned by a remote user that need GPU render devices. PAM marks the session with `XDG_SESSION_EXTRA_DEVICE_ACCESS=` (since 260).

## Use stable device identities

- Storage devices have nested `/dev/disk/by-path/<path>/by-<kind>/<value>` links, disambiguating cloned or identically labeled media (since 256).
- Unqualified `/dev/disk/by-id/nvme-*` links mean namespace 1 and do not exist when namespace 1 is absent. Multi-namespace software should use namespace-qualified links (since 257).
- Virtual block devices including loop, device-mapper, MD, and zram expose `ID_BLOCK_SUBSYSTEM`; GPIO devices gain `/dev/gpio/by-id/` links. The `net_id` builtin generates predictable Wi-Fi names on DeviceTree systems (since 259).
- `ID_INTEGRATION=` classifies a device with `ID_BUS=` as `internal` or `external`, using USB port removability where relevant. It replaces removed `ID_INPUT_JOYSTICK_INTEGRATION=` (since 260).
- The `tpm2_id` udev builtin records TPM manufacturer and product identity; inspect it with `systemd-analyze identify-tpm2` (since 260).
- Dissected image partitions appear below `/dev/disk/by-designator/` (since 258).

## Understand enumeration defaults

- MTD devices appear as `.device` units. Serial ports appear only when backed by assigned I/O or memory resources (since 257).
- DeviceTree aliases and `firmware_node/sun` contribute to predictable network-interface naming (since 257). DeviceTree Wi-Fi, MCTP devices with the `mc` prefix, and additional virtual devices gained stable naming later (since 259 and 260).
- `/dev/ptp*` now uses mode `0664` instead of `0660`. Safe unprivileged read-only access requires Linux 6.15 or patched releases at least 6.12.68, 6.6.122, 6.1.162, 5.15.199, or 5.10.249 (since 260).
- The minimum restored backlight brightness at boot is 1%, down from 5% (since 260).

## Purge tmpfiles-managed state

- The initial `systemd-tmpfiles --purge` in 256 removed every path declared as created by tmpfiles configuration. `--dry-run` previews destructive work.
- Since 257, purge requires at least one configuration-file argument and removes only objects declared on lines with the `$` modifier. `L?` creates a symlink only when its source exists.

```text
d$ /var/lib/example 0755 root root -
L? /usr/local/bin/example - - - - /opt/example/bin/example
```

## Create locked service accounts

- The `!` modifier on a sysusers `u` line creates a fully locked account. Unlike merely assigning an invalid password, it also blocks non-password interactive authentication such as SSH and is appropriate for service identities (since 257).

```text
u! example - "Example service" /var/lib/example
```

## Schedule destructive administration

- `systemd-factory-reset request` schedules reset for the next boot; `cancel` withdraws it, `factory-reset-now.target` starts immediately, and `systemd.factory_reset=` requests it from the kernel command line (since 258).
- The reset target can include `systemd-tpm2-clear.service`, gated by `systemd.tpm2_allow_clear=`, so a storage reset can also invalidate TPM-held secrets (since 258).
