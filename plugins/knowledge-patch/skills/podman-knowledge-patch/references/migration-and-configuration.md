# Migration and configuration

Use this reference for host upgrades, configuration discovery, database conversion, build
prerequisites, and maintenance-release safety requirements.

## BoltDB-to-SQLite migration

### Warning and automatic migration behavior

- Podman 5.6.0 warns that BoltDB will be removed in 6.0, but that warning is hidden by default.
- Podman 5.7.0 shows the warning by default. Set `SUPPRESS_BOLTDB_WARNING=true` only as a
  temporary suppression while planning migration.
- Podman 5.8.0 attempts to migrate a legacy BoltDB database to SQLite on reboot and adds
  `podman system migrate --migrate-db` for environments where reboot migration is unavailable.

### Avoid the 5.8.0 partial-database path

Do not migrate persistent installations with Podman 5.8.0 when Quadlets are present. That path
can leave a partial `db.sql`, and Podman has no automatic recovery for it. Upgrade to 5.8.1 or
later before migrating.

If the damaged installation has no persistent containers, pods, or volumes, move `db.sql` aside,
reboot with 5.8.1 or later, and let migration retry. Do not use this recovery shortcut when state
must be retained.

### Run a safe manual migration (`system-migration`)

Prefer a reboot because it minimizes races with other Podman processes. If manual migration is
necessary:

1. Stop every other Podman command.
2. Stop socket- or systemd-activated `podman system service` processes.
3. Stop Quadlets.
4. Run the migration.

```console
podman system migrate --migrate-db
```

The legacy database remains available if conversion fails.

## Host and component requirements

### Linux and build-tool floors

Podman has required Linux kernel 5.2 or newer since 5.2.0 because it uses the new kernel mount
API. Building Podman itself requires these Go versions:

| Podman release | Minimum Go version |
| --- | --- |
| 5.3.0 | Go 1.22 |
| 5.5.0 | Go 1.23 |
| 5.7.0 | Go 1.24 |
| 6.0.0 | Go 1.25 |

### Podman 6 companion components

Pair Podman 6.0.0 with:

- Buildah 1.44.0;
- Skopeo 1.23;
- Netavark 2.0.0 and Aardvark 2.0.0;
- configuration files compatible with containers/common 0.68.0.

### Removed hosts and legacy stacks

Podman 6.0.0 removes support for Intel Macs, Windows 10, cgroups v1, iptables networking, CNI,
and `slirp4netns`. Move to supported hosts, cgroups v2, nftables, Netavark, and Pasta as
appropriate. The `slirp4netns`-only global `--network-cmd-path` option is also removed.

## Unified configuration resolution (`6.0-guide`)

Podman 6 uses `go.podman.io/storage/pkg/configfile` to give `containers.conf`, `storage.conf`,
and `registries.conf` the same resolution model.

### Location tiers

On Linux and macOS, resolution considers:

- vendor files under `/usr/share/containers`;
- administrator files under `/etc/containers`;
- user files under `$XDG_CONFIG_HOME/containers`, falling back to `$HOME/.config/containers`;
- `<name>.rootful.conf.d` and `<name>.rootless.conf.d` directories;
- per-UID rootless drop-in directories.

FreeBSD substitutes `/usr/local/share` and `/usr/local/etc`. Windows uses `ProgramData` and
`APPDATA`.

### Main-file selection

Read exactly one main file: the highest-priority existing user file, otherwise the administrator
file, otherwise the vendor file. An empty user main file still suppresses both lower-tier main
files.

### Drop-in precedence

Collect drop-ins from every applicable tier after selecting the main file:

1. If files in later locations have the same filename as earlier files, mask the earlier copy.
2. Sort all remaining `.conf` files globally by filename.
3. Apply them in that order, with lexicographically later files taking priority.

Location tier does not outrank the final global filename order. For example, a vendor
`99-vendor.conf` can override a user `33-user.conf` when both survive masking.

### Environment overrides

Each config supports `CONTAINERS_<NAME>_CONF` and `CONTAINERS_<NAME>_CONF_OVERRIDE`:

- `CONTAINERS_<NAME>_CONF` selects one file and disables all normal main-file and drop-in
  loading.
- `CONTAINERS_<NAME>_CONF_OVERRIDE` loads one final override after the normal stack.

Containers-specific names are `CONTAINERS_CONF` and `CONTAINERS_CONF_OVERRIDE`. Other examples
include `CONTAINERS_STORAGE_CONF`, `CONTAINERS_STORAGE_CONF_OVERRIDE`,
`CONTAINERS_REGISTRIES_CONF`, and `CONTAINERS_REGISTRIES_CONF_OVERRIDE`.

```console
CONTAINERS_STORAGE_CONF_OVERRIDE=/tmp/storage-test.conf podman info
```

### Append TOML string arrays

String arrays normally replace earlier values. Append to an earlier array with the shared marker:

```toml
field = ["val", {append=true}]
```

### Containers configuration specifics

- Do not use `/etc/containers/containers.rootless.conf`; place rootless and rootful customization
  in the corresponding drop-in directories.
- Keep `podman --module` for `containers.conf` only. Modules load after regular configuration.
- Since 5.7.0, `containers.conf` supports `log_path` for the default `k8s-file` log location and
  `runtimes_flags` for default OCI runtime flags.

### Storage configuration specifics

- Replace deprecated `rootless_storage_path` with `graphroot` in a rootless drop-in.
- Storage-library users must cache `DefaultStoreOptions()`; `ReloadConfigurationFile()`,
  `UpdateStoreOptions()`, and `Save()` are removed.
- Because storage configuration may come from several files, `podman info` no longer reports one
  storage.conf path.

### Registry configuration specifics

- Convert registries.conf V1 to V2.
- Replace obsolete `REGISTRIES_CONFIG_PATH` with `CONTAINERS_REGISTRIES_CONF`.
- Treat the public Go `V2RegistriesConf` type as deprecated.
- Explicit `SystemRegistriesConfPath` or `SystemRegistriesConfDirPath` values still bypass normal
  lookup and the configuration environment variables.

Do not confuse `registries.d` with `registries.conf.d`. Both `registries.d` and registry
`certs.d` search the unified vendor, administrator, root-mode, per-user, and XDG locations.
`policy.json` gains user/XDG and `/usr/share/containers` fallback lookup, but no drop-ins.

### Service process behavior

The Podman system service no longer reloads configuration in place. Stop and restart the service
process to apply configuration changes.

## Packaging and downstream builds

### Build provenance

Since 5.4.0, Makefile builds accept `BUILD_ORIGIN`. The value identifies the builder in both
`podman version` and `podman info`:

```console
BUILD_ORIGIN=distribution make
```

### SQLite linking

Since 5.6.0, Makefile builds dynamically link sqlite3 when its library and headers are installed.
Non-Makefile packaging can force dynamic linking with the `libsqlite3` build tag.

## Maintenance-release compatibility and security

### Runtime and build compatibility

- Podman 5.6.1 restores container startup with runc 1.3.0 or later.
- Podman 5.6.2 restores Containerfile builds that combine a non-root user with cache mounts.
- Podman 5.7.1 restores rootless user-namespace recreation when both Conmon and the rootless
  pause process are killed unexpectedly.

### Kubernetes YAML host overwrite

Podman 5.6.1 fixes CVE-2025-9566. Crafted symlinks in `ConfigMap` or `Secret` volumes processed by
`podman kube play` could overwrite host content. Do not process untrusted Kubernetes YAML with an
earlier affected release.

### Runtime container escape

Podman 5.7.0 fixes CVE-2025-52881. Arbitrary-write gadgets and procfs write redirects in runc
could allow container escape or denial of service.

### Hyper-V machine image path injection

Podman 5.8.2 fixes CVE-2026-33414. Commands embedded in a `podman machine init --image` path
could execute in the Windows Hyper-V host's PowerShell session.

### Build-context escape

Podman 5.8.3 fixes CVE-2026-44517. `ADD` or `COPY` from a malicious Git repository or tar archive
could include files outside the build context.

### Image environment leakage

Podman 5.8.4 fixes CVE-2026-57231. Malformed image `Env` entries could expose host environment
variables inside containers.
