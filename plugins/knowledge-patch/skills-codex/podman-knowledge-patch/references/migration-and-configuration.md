# Migration and configuration

## Upgrade and platform prerequisites

### Linux kernel floor (5.2.0)

Podman uses the new kernel mount API and requires Linux kernel 5.2 or newer.

### Podman 6 component and build floor (6.0.0)

Pair Podman 6.0 with Buildah 1.44.0, Skopeo 1.23, Netavark and Aardvark 2.0.0, and
containers/common configuration 0.68.0. Building Podman itself requires Go 1.25 or newer.

### Removed hosts and legacy stacks (6.0.0)

Podman 6 removes support for Intel Macs, Windows 10, cgroups v1, iptables networking, CNI, and
`slirp4netns`. Move engines to cgroups v2, nftables, Netavark, and Pasta as applicable. The
slirp4netns-only global `--network-cmd-path` option is removed too.

Podman 6.0.2 restores the remote client on cgroups v1 Linux hosts, as described in the machine
reference, but does not restore cgroups v1 support to the engine.

### Go module and binding breaks (6.0.0)

Move imports from `github.com/containers/podman/v5` to `go.podman.io/podman/v6`. The REST
bindings also remove the redundant `nameOrID` argument from `artifacts.Remove()`.

## Unified configuration lookup

### Locations (6.0-guide)

`containers.conf`, `storage.conf`, and `registries.conf` use the common lookup implementation in
`go.podman.io/storage/pkg/configfile`.

- Linux and macOS: vendor files under `/usr/share/containers`, administrator files under
  `/etc/containers`, and user files under `$XDG_CONFIG_HOME/containers` with `$HOME/.config` as
  the fallback.
- The search also covers `<name>.rootful.conf.d`, `<name>.rootless.conf.d`, and per-UID rootless
  drop-in directories.
- FreeBSD uses `/usr/local/share` and `/usr/local/etc`.
- Windows uses `ProgramData` and `APPDATA`.

### Main-file and drop-in precedence (6.0-guide)

For each configuration, read only the highest-priority existing main file: user, otherwise
administrator, otherwise vendor. An empty user main file still suppresses both lower-tier main
files.

After choosing the main file, collect drop-ins from every applicable tier. A same-named file in a
later location masks an earlier one. Sort the survivors globally by filename and let
lexicographically later files win. Location does not override filename order, so a vendor
`99-*.conf` can beat a user `33-*.conf`.

### Environment overrides (6.0-guide)

`CONTAINERS_<NAME>_CONF` selects one file and disables normal main-file and drop-in loading.
`CONTAINERS_<NAME>_CONF_OVERRIDE` loads one final override after the normal stack. Concrete names
include `CONTAINERS_CONF`, `CONTAINERS_CONF_OVERRIDE`, `CONTAINERS_STORAGE_CONF`, and
`CONTAINERS_REGISTRIES_CONF`.

```console
CONTAINERS_STORAGE_CONF_OVERRIDE=/tmp/storage-test.conf podman info
```

### Appending TOML arrays (6.0-guide)

String arrays normally replace an earlier value. Use the shared append marker when a drop-in must
extend an array:

```toml
field = ["val", {append=true}]
```

### Main-file migrations (6.0-guide)

- `/etc/containers/containers.rootless.conf` is no longer searched. Put rootless and rootful
  customization in drop-ins. `podman --module` remains specific to containers.conf and loads
  modules after regular configuration.
- In storage.conf, replace `rootless_storage_path` with `graphroot` in a rootless drop-in.
- Storage-library consumers must cache `DefaultStoreOptions()`;
  `ReloadConfigurationFile()`, `UpdateStoreOptions()`, and `Save()` are removed.
- Registries.conf V1 and `REGISTRIES_CONFIG_PATH` are removed. Use V2 and
  `CONTAINERS_REGISTRIES_CONF`.
- The public Go `V2RegistriesConf` type is deprecated. Explicit
  `SystemRegistriesConfPath` or `SystemRegistriesConfDirPath` values still bypass normal lookup
  and configuration environment variables.

### Registry-adjacent lookup (6.0-guide)

`registries.d` (distinct from `registries.conf.d`) and registry `certs.d` search unified vendor,
administrator, root-mode, per-user, and XDG locations. `policy.json` gains user/XDG and
`/usr/share/containers` fallback lookup, but has no drop-ins.

### Service reload and inspection (6.0-guide)

The Podman system service no longer reloads configuration in process. Stop and restart the
service to pick up changes. Because storage settings can come from multiple files, `podman info`
no longer reports one storage.conf path.

## Storage database migration

### Warning progression (5.6.0 and 5.7.0)

Podman 5.6 warns when an installation still uses BoltDB, but the warning is hidden by default.
Podman 5.7 shows it by default; `SUPPRESS_BOLTDB_WARNING=true` suppresses it temporarily.

### Automatic migration hazard (5.8.0)

Podman attempts to migrate legacy BoltDB state to SQLite on reboot. The 5.8.0 path can leave a
partial SQLite database when Quadlets are present and has no automatic recovery. Use 5.8.1 or
later. If the installation has no persistent containers, pods, or volumes, move `db.sql` aside
and reboot with 5.8.1 or later to retry.

### Safe manual migration (system-migration)

Prefer a reboot because it reduces races with other Podman processes. If manual migration is
necessary, stop all other Podman commands first, especially socket-activated
`podman system service` instances and Quadlets. A failed migration retains the legacy database.

```console
podman system migrate --migrate-db
```

## Packaging and security maintenance

### SQLite linking (5.6.0)

Makefile builds dynamically link sqlite3 when its headers and library are installed. Other
packaging systems can force dynamic linking with the `libsqlite3` build tag.

### Runtime and build compatibility (5.6.0)

Use 5.6.1 or later for container startup with runc 1.3.0 or later. Use 5.6.2 or later for
Containerfile builds that combine a non-root user with cache mounts.

### Kubernetes YAML overwrite fix (5.6.0)

Podman 5.6.1 fixes CVE-2025-9566, where crafted symlinks in `ConfigMap` or `Secret` volumes passed
to `podman kube play` could overwrite host content. Use at least 5.6.1 for untrusted YAML.

### Container escape and namespace recovery (5.7.0)

Podman 5.7.0 addresses CVE-2025-52881, where runc arbitrary-write gadgets and procfs redirects
could allow container escape or denial of service. Podman 5.7.1 restores rootless namespace
recreation when both Conmon and the rootless pause process die unexpectedly.

### Patch-release security fixes (5.8.0)

- 5.8.2 fixes CVE-2026-33414, which allowed commands embedded in a Hyper-V machine image path to
  execute in the Windows host's PowerShell session.
- 5.8.3 fixes CVE-2026-44517, which allowed `ADD` or `COPY` from a malicious Git or tar context
  to include files outside the build context.
- 5.8.4 fixes CVE-2026-57231, which allowed malformed image `Env` entries to expose host
  environment variables inside containers.
