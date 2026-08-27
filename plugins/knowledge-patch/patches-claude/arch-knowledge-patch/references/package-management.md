# Package Management

Covered batches: `7.0.0`, `2024-11`, `2025-h1-platform`, and `7.1.0`.

## Pacman configuration and downloads

### Configure privilege-separated downloads

Pacman 7.0.0 can use `DownloadUser` to download into a temporary directory as a less-privileged user. Merge pacman's `.pacnew` files to apply Arch's default.

Grant the `alpm` group access to local repositories, including traversal permission on every directory:

```sh
chown :alpm -R /path/to/local/repo
find /path/to/local/repo -type d -exec chmod g+x {} +
```

Without that access, privilege-separated downloads cannot read a local repository.

### Account for the Linux download sandbox

Since 7.0.0, the Linux downloader is restricted from writing outside its download directory. Use `DisableSandbox` in `pacman.conf` or `--disable-sandbox` on the command line only when the restriction must be disabled.

Since 7.1.0, the sandbox also restricts system calls and sets `NO_NEW_PRIVS`. Control individual restrictions with the new configuration and command-line options when possible instead of disabling the complete sandbox.

### Enforce signature policy

Since 7.1.0, pacman's default `SigLevel` is `Required` for both databases and packages. Add an explicit configuration exception when an unsigned repository or package is intentional; the default no longer accepts it.

## Repository changes

### Remove retired official repositories

Arch removed `[community]`, `[community-testing]`, `[testing]`, `[testing-debug]`, `[staging]`, and `[staging-debug]` on 2025-03-01 as part of batch `2025-h1-platform`. Leaving any of these in `/etc/pacman.conf` causes `pacman -Sy` to fail while synchronizing metadata.

Merge the `.pacnew` shipped with `pacman>=6.0.2-7`, or remove every reference to the retired repositories manually.

### Maintain repositories with repo-add

Since 7.1.0, use `repo-add --wait-for-lock` to wait for a repository lock and serialize concurrent updates. Use `repo-add --remove` to delete old package files while updating repository metadata.

## makepkg and PKGBUILD behavior

### Refresh Git source checksums once

Since 7.0.0, makepkg creates stable checksums for Git sources independently of user configuration, including repositories that use `.gitattributes`. Update affected PKGBUILD checksums once when the new calculation differs.

### Remove GITFLAGS

Since 7.0.0, makepkg no longer supports `GITFLAGS`. Remove any PKGBUILD or makepkg configuration that relies on those flags for Git source handling.

### Stop overriding protected build configuration

Since 7.0.0, a PKGBUILD cannot override `BUILDENV`, and `options=(!buildenv)` no longer disables `MAKEFLAGS` or `CHOST`. Adjust PKGBUILDs that depend on either behavior.

Since 7.1.0, makepkg uses `/etc/makepkg.d/gitconfig` for Git operations and ignores system Git configuration. A PKGBUILD can no longer alter `OPTIONS`.

### Separate makepkg parallelism from build parallelism

Since 7.1.0, set `NPROC` in makepkg configuration to control parallel operations performed by makepkg itself. Do not use it as a substitute for the build system's own job or parallelism setting.

### Add tracked and architecture-specific data

Since 7.1.0, use `xdata` for generic tracked PKGBUILD data and `options_$arch` for architecture-specific options. Architecture-specific split packages are also supported.

## Package layout interventions

### Complete the linux-firmware split

In `linux-firmware>=20250613.12fe085f-5`, firmware is divided into hardware-specific packages. `linux-firmware` becomes an empty package that depends on the default set.

When upgrading from `20250508.788aadc8-2` or earlier, remove the old aggregate package without dependency checks, then reinstall it as part of the full system upgrade:

```sh
pacman -Rdd linux-firmware
pacman -Syu linux-firmware
```

Do not stop after `pacman -Rdd`; complete the full upgrade immediately.

## Package-source licensing

Under batch `2024-11`, Arch agreed to license all package sources, including PKGBUILD files, under the permissive 0BSD license. Treat those package sources as reusable under 0BSD rather than as material with uncertain reuse terms.
