# Packages, toolchains, and desktops

Use this reference to reconcile package splits, removals, replacements,
toolchain baselines, desktop compatibility, and package data changes.

## Core platform versions

The platform versions reported in `13-whats-new` include:

| Component | Version |
| --- | --- |
| Linux | 6.12 |
| glibc | 2.41 |
| GCC | 14.2 |
| LLVM/Clang | 19 |
| OpenJDK | 21 |
| OpenSSH | 10.0p1 |
| OpenSSL | 3.5 |
| Perl | 5.40 |
| PHP | 8.4 |
| PostgreSQL | 17 |
| Python | 3.13 |
| Rust | 1.85 |
| MariaDB | 11.8 |
| Samba | 4.22 |
| systemd | 257 |

Use these versions when assessing source compatibility and rebuilding local or
third-party software.

## Package splits

### Review libvirt components

Each libvirt driver and storage backend has its own binary package. The upgrade
tries to preserve installed components, but administrators should review the
resulting package set and consult
`/usr/share/doc/libvirt-common/NEWS.Debian.gz` for obsolete conffile handling.

### Install Samba features explicitly

Active Directory domain-controller support moved from `samba` to
`samba-ad-dc`. Most VFS modules are included in `samba`, while Ceph and
GlusterFS integration require `samba-vfs-ceph` and
`samba-vfs-glusterfs`, respectively.

## Removed packages and commands

Use these replacements where their behavior matches the old dependency:

| Removed item | Replacement or action |
| --- | --- |
| `libnss-gw-name` | `libnss-myhostname` |
| `pcregrep` | `grep -P` or `pcre2grep` |
| `request-tracker4` | `request-tracker5` |
| `deborphan` | `apt-mark minimize-manual`, then `apt autoremove` |
| `tldr` | `tealdeer` or `tldr-py` |
| `tpp` | `lookatme` or `patat` |

`git-daemon-run`, `git-daemon-sysvinit`, and the Tesla 470 NVIDIA drivers are
also gone; no direct replacement is specified. Do not invent a substitute
without checking the role each package served.

The accounting commands also changed: `lastlog2` replaces `lastlog`, `wtmpd`
replaces `last`, and util-linux provides `lslogins`. The `util-linux-extra`
package removes `mesg` and `write` while adding tools including `exch` and
`waitpid`. Audit scripts for every removed executable.

## Package data caveat

In Debian 12.15, `geoip-database` reverted for licensing reasons to allocation
data from approximately December 2019. Applications that consume it can make
decisions from outdated address-allocation information. Do not treat the
packaged database as a current geolocation source.

## Desktop stacks

Desktop versions include GNOME 48, Plasma 6.3, LXDE 13, LXQt 2.1, and Xfce
4.20.

Plasma 6.3 uses Qt 6.8.2 and KDE Frameworks 6.13. Qt 5.15.15 and KDE Frameworks
5.116 remain available for older applications, so both generations can coexist.
Frameworks 5 is deprecated and planned for removal during the Forky development
cycle. Existing Plasma profiles generally upgrade in place, though
configuration quirks can remain and should be tested.

## Browser spell-checking

Hunspell language packages include compiled `.bdic` dictionaries. Supporting
Qt WebEngine browsers, including Falkon and Privacy Browser, can use them for
spell-checking without a separately generated dictionary.

Unless noted otherwise, package split and removal guidance in this reference
comes from batch `13-known-issues`.
