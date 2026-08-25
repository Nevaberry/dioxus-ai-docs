# Packages, toolchains, and desktops

## Replace retired commands and packages

These replacements are from `13-whats-new` and `13-known-issues`.

### Replace utmp and wtmp tools

The Y2038-unsafe utmp/wtmp databases are being displaced. Use the `lastlog2` package
instead of `lastlog`, `wtmpd` instead of `last`, and util-linux's `lslogins` where it
fits the query.

`util-linux-extra` removes `mesg` and `write` while adding tools including `exch` and
`waitpid`. Audit scripts for the removed commands and select alternatives rather than
assuming a compatible alias exists.

### Map removed packages deliberately

Use `libnss-myhostname` for `libnss-gw-name`, `grep -P` or `pcre2grep` for `pcregrep`,
and `request-tracker5` for `request-tracker4`.

The `git-daemon-run`, `git-daemon-sysvinit`, Tesla 470 NVIDIA driver, `deborphan`,
`tldr`, and `tpp` packages are also gone. Where applicable:

- replace `deborphan` workflows with `apt-mark minimize-manual` followed by
  `apt autoremove`;
- replace `tldr` with `tealdeer` or `tldr-py`;
- replace `tpp` with `lookatme` or `patat`.

## Review component and feature package splits

### libvirt

Every libvirt driver and storage backend has its own binary package. The upgrade tries
to preserve installed components, but review the resulting package set and read
`/usr/share/doc/libvirt-common/NEWS.Debian.gz` for obsolete conffile handling.

### Samba

Active Directory domain-controller support moved from `samba` to `samba-ad-dc`. Most
VFS modules moved into `samba`, while Ceph and GlusterFS support require
`samba-vfs-ceph` and `samba-vfs-glusterfs`, respectively.

### Legacy timezone names

Names outside the region/city scheme, including `US/*`, moved to `tzdata-legacy`.
The system timezone is converted automatically, but keep `tzdata-legacy` installed
when databases or services copied an old name.

## Reconcile configuration-system changes

### WirePlumber

Defaults need no action, but custom WirePlumber setups must be ported to the new
configuration system. Use `/usr/share/doc/wireplumber/NEWS.Debian.gz` as the migration
guide.

### sg3-utils udev data

A Trixie `sg3-utils` bug prevents SCSI devices from receiving all properties normally
injected by `sg3-utils-udev`. Migrate consumers away from those properties or prepare
for failures after reboot.

### usrmerge warnings

During upgrade, `dpkg` may warn that it cannot delete old nonempty directories under
paths such as `/lib/firmware`. These warnings are a consequence of usrmerge
finalization and can be ignored.

## Desktop and application compatibility

These desktop changes are from `13-whats-new`.

### Plasma compatibility stack

Plasma 6.3 uses Qt 6.8.2 and KDE Frameworks 6.13. Debian retains Qt 5.15.15 and KDE
Frameworks 5.116 for older applications. Existing Plasma profiles generally upgrade
in place, although quirks remain. Frameworks 5 is deprecated and planned for removal
during the Forky development cycle.

### Qt WebEngine spelling dictionaries

Hunspell language packages include compiled `.bdic` dictionaries. Supporting Qt
WebEngine browsers, including Falkon and Privacy Browser, can use them for spell
checking.

## Complete migrations before the next release

The pending removals in this section are from `13-known-issues`.

### sudo and OpenSSH features

Move `sudo-ldap` policy to `libsss-sudo`; otherwise privilege-escalation rules may
disappear when `sudo-ldap` is removed. `sudo_logsrvd` input/output logging may also be
removed unless it gains a maintainer.

The main OpenSSH packages will drop GSS-API authentication and key exchange. When
using `GSSAPI*` options, install the currently transitional `openssh-client-gssapi` or
`openssh-server-gssapi` package so the separately built implementation remains
installed.

### Build, input-method, container, and DHCP tooling

- Replace `sbuild-debian-developer-setup` with
  `sbuild --chroot-mode=unshare`.
- Replace fcitx 4 with `fcitx5`.
- Move Debian LXD deployments to Incus using tools in `incus-extra`.
- Remove `libnss-docker`; it depends on a Docker API removed after Engine 26.
- Do not add an ISC DHCP client for NetworkManager or systemd-networkd. With
  `ifupdown`, use `dhcpcd-base`; for servers, move from ISC DHCP to Kea.

## Account for stale GeoIP allocation data

This Bookworm package change is from `12.15`.

For licensing reasons, `geoip-database` contains allocation data from approximately
December 2019. Treat location or ownership results from applications consuming it as
potentially outdated.
