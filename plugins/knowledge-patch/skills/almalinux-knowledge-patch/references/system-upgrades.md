# System Upgrades and ELevate

Use this reference for beta-to-stable conversion, cross-major ELevate plans,
Leapp data compatibility, and third-party repository transitions. The ELevate
details reflect the `elevate-upgrades` snapshot dated 2026-07-11.

## Beta-to-stable upgrades

### AlmaLinux 9.4 beta

Replace the repository package before the normal package upgrade:

~~~console
rpm -i https://repo.almalinux.org/almalinux/9.4/BaseOS/x86_64/os/Packages/almalinux-repos-9.4-1.el9.x86_64.rpm --replacefiles
dnf upgrade -y
~~~

This procedure is specific to `9.4` beta systems.

### AlmaLinux 10.0 beta

Replace the release, repository, and key packages before upgrading:

~~~console
dnf install https://repo.almalinux.org/almalinux/almalinux-{release,repos,gpg-keys}-latest-10.$(uname -m).rpm
dnf upgrade -y
~~~

This procedure is specific to `10.0` beta systems.

## Current ELevate paths

- Stable ELevate supports AlmaLinux 9.8 to AlmaLinux 10.2.
- AlmaLinux 9 to AlmaLinux 10 and AlmaLinux Kitten 10 paths for
  `x86_64_v2` were released to NG. They use
  `leapp-data-almalinux-x86_64_v2` and
  `leapp-data-almalinux-kitten-x86_64_v2`.
- The `--target` option can select a supported destination minor. Published
  target support is release-gated; an unreleased target can be removed until
  that minor ships.
- Updated map files let non-`x86_64` architectures follow the standard
  quickstart without a separate architecture-specific procedure.

ELevate data covers AlmaLinux 10, AlmaLinux Kitten 10, and CentOS Stream 10.
EuroLinux support was discontinued after that distribution reached end of
life. CentOS 7 ELS repositories are supported on upgrades to Oracle Linux 8.

## Clean up before a chained upgrade

After CentOS 7 to EL8, remove every ELevate-related EL7 package before
starting EL8 to EL9. Old `leapp-data-*` packages can conflict with
`leapp-upgrade-*` under `/etc/leapp/repos.d/system_upgrade` and produce
malformed symlinks with semicolon suffixes.

## Leapp data contract

The May 2026 stable stack uses:

- Leapp Repository 0.24.0
- Leapp Framework 0.20.0-2
- data stream 4.2
- repomap format 1.3.0

ELevate combines the main and distribution-specific `RepositoriesMapping`
messages. EL9 also has a separate RPM for the Cockpit interface.

## Third-party repositories on EL9 to EL10

PES data handles EPEL, Docker CE, PostgreSQL, nginx, KernelCare, MariaDB,
Imunify, and Imunify360 alt-PHP. MariaDB MaxScale and Tools are not covered.
The ELevate vendor definition is enabled on every path, and TuxCare's
`alt-common` repository is represented separately.

### Microsoft keys

Microsoft repository support uses both signing keys:

- `BE1229CF` for EL8 and EL9
- `F748182B` for EL10

Per-release repository files point `gpgkey` to the bundled `microsoft.gpg`
with a local `file://` URL.

### PostgreSQL and MariaDB mappings

For EL8 to EL9, PostgreSQL 18 repositories and `ppc64le` are represented
where available. PostgreSQL 12 and 13 repositories that aged out now map to
`yum-archive.postgresql.org`.

MariaDB data uses `mirror.mariadb.org`; the EL7 mapping points to the
`11.rolling` repository.

### Imunify360 and EPEL transition actions

On EL7 to EL8:

- With Imunify360 enabled, `libunwind` uses a replace action; otherwise it is
  removed.
- With EPEL enabled, `GeoIP` uses a move action; otherwise it is removed.

Before an Imunify360 alt-PHP upgrade, replace
`<imunify360_alt-php_token>` in
`/etc/yum.repos.d/imunify360-alt-php.repo` with the token from
`/etc/leapp/files/vendors.d/imunify360-alt-php.repo`.

## Newly accepted and experimental configurations

- ELevate permits LUKS volumes bound to Clevis through a TPM 2.0 token.
- `net.naming-scheme` is enabled by default; network-name handling no longer
  needs an explicit opt-in.
- Leapp exposes `--enable-experimental-feature` for explicit experimental
  features, including the simplified LiveMode flow.
