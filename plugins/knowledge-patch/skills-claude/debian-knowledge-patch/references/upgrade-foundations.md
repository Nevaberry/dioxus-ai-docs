# Upgrade foundations

This checklist consolidates upgrade-critical behavior from `13-known-issues`; use the
topic references for full service and subsystem details.

## Inventory the host before changing repositories

Record whether the host has:

- SSH as its only access path;
- a separate `/boot`, particularly on installations originating with Debian 10 or
  earlier;
- encrypted mounts or plain-mode dm-crypt entries;
- RabbitMQ, MariaDB, Dovecot, or Bacula state;
- `i40e` interfaces, ACPI `_SUN` naming, or hard-coded interface names;
- local policy in `/etc/sysctl.conf`;
- custom OpenLDAP TLS, strongSwan, WirePlumber, Samba, or libvirt configuration;
- third-party `armel` or `armhf` binaries;
- packages and commands scheduled for replacement.

Back up configuration and state, document recovery access, and define rollback points
for every matching risk.

## Establish remote and boot recovery

Before an SSH-supervised upgrade, install `openssh-server`
`1:9.2p1-2+deb12u7` or later from `stable-updates`. Open a second session and verify
that required environment variables no longer depend on `~/.pam_environment`.

Require a separate `/boot` to be at least 768 MB with about 300 MB free. An LVM-backed
boot logical volume can be enlarged with `lvextend`. Confirm that rescue media or an
out-of-band console is usable before continuing.

## Prepare storage and stateful services

Verify `systemd-cryptsetup` is installed. Pin the creation parameters for every
plain-mode dm-crypt volume in `/etc/crypttab`; do not infer them from new defaults.

Complete queue conversion and state preservation for RabbitMQ. Confirm a clean
MariaDB 10.11 shutdown. Test the Dovecot 2.4 configuration. Measure Bacula database,
backup, and temporary-space requirements. Treat these as prerequisites, not cleanup.

## Upgrade packages and inspect the result

After `apt full-upgrade` and before reboot:

1. Review libvirt, Samba, timezone, WirePlumber, strongSwan, OpenLDAP, and removed
   package transitions.
2. Confirm local sysctl policy exists under `/etc/sysctl.d/` and test unprivileged
   ping for the intended users.
3. Test every critical interface name:

   ```bash
   udevadm test-builtin net_setup_link /sys/class/net/<interface>
   ```

4. Add a `systemd.link` file if the predicted name differs from the configured name.
5. Reconfirm `/boot` free space and the presence of `systemd-cryptsetup`.
6. Treat usrmerge warnings about old nonempty directories such as `/lib/firmware` as
   harmless, but investigate unrelated `dpkg` errors.

## Verify after reboot

Check SSH login, all encrypted mounts, interface names and addresses, local sysctl
values, unprivileged ping, and every migrated stateful service. Confirm that SCSI
consumers do not depend on missing `sg3-utils-udev` properties and that legacy
timezone consumers still resolve their names.

Exercise application paths that use OpenLDAP TLS, Samba feature packages, libvirt
drivers or storage backends, WirePlumber customization, and strongSwan management.

## Schedule forward migrations

Before the following release upgrade, migrate `sudo-ldap`, OpenSSH GSS-API packaging,
fcitx 4, Debian LXD, `sbuild-debian-developer-setup`, `libnss-docker`, and ISC DHCP
deployments. Record these as owned work with deadlines; a successful Trixie reboot
does not complete them.
