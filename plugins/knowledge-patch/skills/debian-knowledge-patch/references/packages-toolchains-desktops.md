# Packages, toolchains, and desktops

## Core platform versions

Key packaged versions are:

| Component | Version | Component | Version |
| --- | --- | --- | --- |
| Linux | 6.12 | glibc | 2.41 |
| GCC | 14.2 | LLVM/Clang | 19 |
| OpenJDK | 21 | OpenSSH | 10.0p1 |
| OpenSSL | 3.5 | Perl | 5.40 |
| PHP | 8.4 | PostgreSQL | 17 |
| Python | 3.13 | Rust | 1.85 |
| MariaDB | 11.8 | Samba | 4.22 |
| systemd | 257 |  |  |

## Desktop versions and compatibility

Desktop choices include GNOME 48, Plasma 6.3, LXDE 13, LXQt 2.1, and Xfce 4.20.

Plasma 6.3 is built on Qt 6.8.2 and KDE Frameworks 6.13. Qt 5.15.15 and KDE
Frameworks 5.116 remain available for older applications. Frameworks 5 is deprecated
and planned for removal during the Forky development cycle.

Existing Plasma profiles generally upgrade in place, although some quirks remain.

## Qt WebEngine spelling dictionaries

Hunspell language packages include compiled `.bdic` dictionaries. Supporting Qt
WebEngine browsers, including Falkon and Privacy Browser, can use them for spell-checking.

## libvirt package split

Each libvirt driver and storage backend now has its own binary package. Upgrades try to
preserve installed components, but review the resulting package set. Consult
`/usr/share/doc/libvirt-common/NEWS.Debian.gz` for obsolete conffile handling.

## Samba feature packages

Active Directory domain-controller support moved from `samba` to `samba-ad-dc`.

Most VFS modules moved into `samba`. Ceph and GlusterFS support instead require
`samba-vfs-ceph` and `samba-vfs-glusterfs`, respectively.

## Removed packages and replacements

Apply replacements selectively:

| Removed package or command | Replacement or action |
| --- | --- |
| `libnss-gw-name` | Use `libnss-myhostname`. |
| `pcregrep` | Use `grep -P` or `pcre2grep`. |
| `request-tracker4` | Use `request-tracker5`. |
| `deborphan` | Run `apt-mark minimize-manual`, then `apt autoremove`. |
| `tldr` | Use `tealdeer` or `tldr-py`. |
| `tpp` | Use `lookatme` or `patat`. |

The following packages are also gone, with no replacement specified here:

- `git-daemon-run`
- `git-daemon-sysvinit`
- the Tesla 470 NVIDIA drivers
