# Migration and configuration

## Platform and dependency prerequisites

### Kernel and companion-project floors

Podman requires Linux kernel 5.2 or newer because it depends on the new mount API (since 5.2.0).
For a Podman 6 deployment, pair the engine with Buildah 1.44.0, Skopeo 1.23, Netavark and Aardvark
2.0.0, and containers/common configuration 0.68.0 (6.0.0).

Podman 6 removes Intel macOS and Windows 10 support, cgroups v1, iptables networking, CNI, and
`slirp4netns`. Migrate to cgroups v2, nftables, Netavark, and Pasta as appropriate. Remove the
slirp-only global `--network-cmd-path` option.

Remote-client support on cgroups v1 Linux was restored in 6.0.2, but that does not restore cgroups
v1 support to the Podman 6 engine.

### Source-build requirements

The minimum Go toolchain advanced from Go 1.22 in 5.3.0, to Go 1.23 in 5.5.0, Go 1.24 in 5.7.0,
and Go 1.25 in 6.0.0. Match the toolchain to the Podman source being built rather than using the
oldest value in that progression.

Makefile builds accept `BUILD_ORIGIN`, which appears in `podman version` and `podman info`
(since 5.4.0):

```console
BUILD_ORIGIN=distribution make
```

Makefile builds dynamically link sqlite3 when its headers and library are installed (since 5.6.0).
Non-Makefile packagers can force dynamic linkage with the `libsqlite3` build tag.

## Unified configuration lookup

The configuration behavior in this section comes from the `6.0-guide` batch and applies to
`containers.conf`, `storage.conf`, and `registries.conf` through the shared
`go.podman.io/storage/pkg/configfile` loader.

### Locations

On Linux and macOS, the loader considers vendor files under `/usr/share/containers`, administrator
files under `/etc/containers`, and user files under `$XDG_CONFIG_HOME/containers` with a fallback
to `$HOME/.config/containers`. It also supports `<name>.rootful.conf.d`,
`<name>.rootless.conf.d`, and per-UID rootless drop-in directories.

FreeBSD uses `/usr/local/share` and `/usr/local/etc`; Windows uses `ProgramData` and `APPDATA`.

### Main-file precedence

Read only the highest-priority existing main file:

1. User.
2. Administrator.
3. Vendor.

An empty user main file still suppresses the administrator and vendor main files. Do not merge all
main files.

### Drop-in precedence

After choosing the main file, collect drop-ins from all applicable tiers. A file in a later
location masks an earlier same-named file. Sort the remaining files globally by filename and let
lexicographically later names win. Location tier no longer decides the final collision: a vendor
`99-*.conf` can override a user `33-*.conf`.

String arrays replace earlier arrays by default. Append to an earlier array with the shared TOML
marker:

```toml
field = ["val", {append=true}]
```

### Environment-selected files

`CONTAINERS_<NAME>_CONF` selects one file and disables ordinary main-file and drop-in loading.
`CONTAINERS_<NAME>_CONF_OVERRIDE` loads one final override after the ordinary stack.

Concrete names include `CONTAINERS_CONF`, `CONTAINERS_CONF_OVERRIDE`,
`CONTAINERS_STORAGE_CONF`, `CONTAINERS_STORAGE_CONF_OVERRIDE`, and
`CONTAINERS_REGISTRIES_CONF`.

```console
CONTAINERS_STORAGE_CONF_OVERRIDE=/tmp/storage-test.conf podman info
```

## Configuration migrations

### Containers and storage configuration

`/etc/containers/containers.rootless.conf` is no longer searched. Put rootless and rootful changes
in their respective drop-ins. `podman --module` remains containers.conf-only and loads modules
after normal configuration.

In storage.conf, replace `rootless_storage_path` with `graphroot` in a rootless drop-in. Storage
library clients should cache `DefaultStoreOptions()`; `ReloadConfigurationFile()`,
`UpdateStoreOptions()`, and `Save()` are removed.

### Registries and policy configuration

Registries.conf V1 and `REGISTRIES_CONFIG_PATH` are unsupported. Use V2 and
`CONTAINERS_REGISTRIES_CONF`. The public Go `V2RegistriesConf` type is deprecated. Explicit
`SystemRegistriesConfPath` or `SystemRegistriesConfDirPath` values still bypass both normal lookup
and configuration environment variables.

`registries.d` is distinct from `registries.conf.d`. Both `registries.d` and registry `certs.d`
search unified vendor, administrator, root-mode, per-user, and XDG locations. `policy.json` gains
user/XDG and `/usr/share/containers` fallbacks but no drop-ins.

### Service reload and information output

The Podman system service does not reload configuration in-process. Stop and restart the service
to apply changes. Because storage settings can come from multiple files, `podman info` no longer
reports one storage.conf path.

## BoltDB-to-SQLite migration

### Warnings and preferred migration path

Podman 5.6.0 warns that BoltDB is being retired, although the warning was hidden until 5.7.0. The
visible warning can be temporarily suppressed with `SUPPRESS_BOLTDB_WARNING=true`.

Prefer reboot-driven migration because it minimizes races with other Podman processes. For manual
migration (`system-migration`), stop all Podman commands first, especially socket-activated
`podman system service` processes and Quadlets:

```console
podman system migrate --migrate-db
```

The legacy database is retained if migration fails.

### Avoid the 5.8.0 partial-database path

The 5.8.0 migrator can leave a partial SQLite database when Quadlets exist and has no automatic
recovery. Use 5.8.1 or later. When there are no persistent containers, pods, or volumes to preserve,
move `db.sql` aside and reboot with a fixed release to retry; otherwise preserve the databases and
recover deliberately.

## Reset behavior

`podman system reset` preserves the user's `podman.sock` (since 5.5.0). Cleanup automation must not
expect reset to remove that socket.

## Security and compatibility maintenance

### Runtime and Kubernetes fixes

- 5.6.1 prevents crafted `ConfigMap` or `Secret` symlinks in `kube play` YAML from overwriting host
  content and restores startup with runc 1.3.0 or newer.
- 5.6.2 restores non-root Containerfile builds that use cache mounts.
- 5.7.0 addresses CVE-2025-52881, an arbitrary-write/procfs path in runc that could allow
  container escape or denial of service.
- 5.7.1 restores rootless namespace recreation after both Conmon and the rootless pause process
  terminate unexpectedly.

### Machine, build-context, environment, and Quadlet fixes

- 5.8.2 fixes CVE-2026-33414, where a crafted Hyper-V machine image path could execute commands in
  a Windows host PowerShell session. It also fixes `unless-stopped` reboot behavior and Quadlet
  entrypoint/health-command parsing.
- 5.8.3 fixes CVE-2026-44517, where malicious Git or tar build contexts could escape `ADD`/`COPY`
  boundaries.
- 5.8.4 fixes CVE-2026-57231, where malformed image `Env` entries could expose host environment
  variables.
- 5.8.6 fixes CVE-2026-19730: `podman quadlet install --replace` truncates the destination, avoiding
  stale trailing content when the replacement is shorter.
- 6.0.1 fixes stale Pasta/Pesto forwarding rules after rootless bridge restarts or reloads.
