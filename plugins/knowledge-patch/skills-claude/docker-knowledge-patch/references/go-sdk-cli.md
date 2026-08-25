# Go SDK and Docker CLI Integration

## Supported modules and toolchain

Engine 29 deprecates `github.com/docker/docker`. Use the public
`github.com/moby/moby/client` and `github.com/moby/moby/api` modules; the root
`github.com/moby/moby` module is internal. Release tags use
`docker-v29.0.0` form, and the SDK requires Go 1.24 or later.

Do not embed Docker CLI internals as a substitute for the public client. Engine
29 removes many exported command constructors, formatters, and `Run...`
helpers; implement an application-owned command layer.

## Client construction and concurrency

Since 27.0.1, `*client.Client` is safe for concurrent goroutine use, including
API negotiation. Engine 29 removes `NewClient`, `NewEnvClient`,
`CommonAPIClient`, and old image-client interfaces. Move to the current client
constructors and validate the negotiated API explicitly.

## Call-shape migration

### Functional options and result wrappers

In 28.0.0, `ImageHistory`, `ImageLoad`, and `ImageSave` switch to variadic
functional options. `StatsResponse` merges into `Stats`. Commit and exec create
gain `CommitResponse` and `ExecCreateResponse`; stop using generic `IDResponse`
for them.

Engine 29 broadly moves configuration, image, plugin-list, and prune calls from
positional arguments to option structs and dedicated results. Inspect, history,
load, and save return wrappers. Pull and push return objects whose
`JSONMessages` iterators expose progress. Rename `ContainerExec...` calls to
`Exec...`. Replace `ContainerCommitOptions.Pause` with `NoPause`.

`ImageCreate` is removed; choose `ImagePull` for registry content or
`ImageImport` for imported content.

### Context-aware callbacks

Since 27.0.1, `client.RequestPrivilegeFunc`,
`client.ImageSearchOptions.AcceptPermissionsFunc`, and
`image.ImportOptions.PrivilegeFunc` receive a context parameter. Propagate
cancellation and deadlines rather than adapting with a context-blind wrapper.

### Option type locations

The 27.0.1 deprecated aliases `ImageImportOptions`, `ImageCreateOptions`,
`ImagePullOptions`, `ImagePushOptions`, `ImageListOptions`, and
`ImageRemoveOptions` are removed; use `api/types/image` option types for that
generation.

Engine 29 moves operation option types from `api/types` component packages into
`client`, and filters use the client's `Filters` type. Follow the dependency's
versioned signatures rather than mixing generations.

## Value and network types

Engine 29 migrates IP addresses and subnets to `netip.Addr` and `netip.Prefix`,
MAC addresses to byte slices compatible with `net.HardwareAddr`, and container
`Port` to `PortSummary`. Network `Summary` and `Inspect` cease to be aliases.
Audit comparisons, JSON assumptions, zero values, and map keys during migration.

## Type relocations in 27.0.1

Move these statistics, exec, copy, and prune types to `api/types/container`:
`BlkioStatEntry`, `BlkioStats`, `CPUStats`, `CPUUsage`,
`ContainerExecInspect`, `ContainerPathStat`, `ContainerStats`,
`ContainersPruneReport`, `CopyToContainerOptions`, `ExecConfig`,
`ExecStartCheck`, `MemoryStats`, `NetworkStats`, `PidsStats`, `StatsJSON`,
`Stats`, `StorageStats`, and `ThrottlingData`.

Other moves:

- `ImagesPruneReport`, `ImageImportSource`, and `ImageLoadResponse` to
  `api/types/image`.
- `ExecStartOptions` to `api/types/backend`.
- `VolumesPruneReport` to `api/types/volume`.
- `EventsOptions` to `api/types/events`.
- `ImageSearchOptions` to `api/types/registry`.
- Network API types to `api/types/network`, dropping a `Network` prefix where
  applicable; `NetworkResource` moves there too.

## Removed compatibility surface

### Engine 26.0.0 removals

The Go tree removes `image.IDFromDigest`, `pkg/loopback`,
`pkg/system.ErrNotSupportedOperatingSystem`, `pkg/system.IsOSSupported`,
`pkg/homedir.Key`, `pkg/homedir.GetShortcutString`, and
`pkg/containerfs.ResolveScopedPath`.

Temporary top-level `api/types` aliases for info, commit, plugin, network pool,
runtime, security, checkpoint, image, service response, resize, and container
options are removed. CLI users must stop using
`cli/command/container.NewStartOptions`, `cli/command.DockerCliOption`, and
`cli/command.InitializeOpt`.

### Engine 28.0.0 removals and replacements

Removed helpers include `pkg/ioutils` pipes, counters, writers, and flushers;
`pkg/directory`; `pkg/dmsg.Dmesg`; `pkg/sysinfo.NumCPU`; `cli.Errors`; old
image-spec; archive temporary-file APIs; `pkg/fileutils.GetTotalUsedFds`;
`pkg/longpath.Prefix`; string-ID validators; and legacy `runconfig` conversion
and network-default functions.

`Daemon.ContainerInspectCurrent`, `Daemon.Exists`, and `Daemon.IsPaused` are
gone. `Daemon.ContainerInspect` takes `backend.ContainerInspectOptions`.
Deprecated libnetwork iptables types and old top-level `api/types` aliases are
also removed.

Use these migration targets:

- `client.ImageInspect` instead of `ImageInspectWithRaw`.
- `config.Validate` instead of `Config.ValidatePlatformConfig`.
- `github.com/moby/sys/reexec` instead of `pkg/reexec`.
- `pkg/atomicwriter` for atomic-file helpers.
- `os.MkdirAll`, `container.UpdateResponse`, and `container.TopResponse` instead
  of their deprecated wrappers.
- `github.com/moby/docker-image-spec` instead of the removed old image-spec
  package.

### Engine 29 removals

In addition to old constructors and client interfaces, Engine 29 removes
`api/pkg/progress`, `api/pkg/streamformatter`, `pkg/system`, `pkg/fileutils`,
`pkg/idtools`, and old archive, chroot-archive, atomic-writer, reexec, platform,
and parser packages. Replacements live in `github.com/moby/go-archive`,
`github.com/moby/sys`, or the standard library.

## CLI flags, plugins, and embedding

Engine 28.0.0 renames `docker stop/restart --time` to `--timeout`. It removes
many internal CLI entry points as described above.

Engine 29 runs CLI plugin hooks for failed as well as successful commands.
Plugins may register `error-hooks` for failure-only hints. Make hooks
idempotent and account for a partially completed command.

Engine 29 removes Docker Content Trust commands from the stock CLI; legacy use
requires a separately built plugin. It also stops Windows plugin discovery in
`%PROGRAMDATA%\Docker\cli-plugins`; install under
`%ProgramFiles%\Docker\cli-plugins`.

The CLI's special stripping of quote characters in equals-form TLS path flags
was deprecated in 28.4 and removed in 29. Pass path values as normal separate
arguments.

## Migration workflow

1. Pin the public client/API module and supported Go version.
2. Compile after changing constructors, method names, options, and results.
3. Replace imports and aliases systematically; do not bridge incompatible type
   generations with unsafe conversions.
4. Test API negotiation, concurrent use, cancellation, streamed progress, and
   absent optional fields.
5. Keep CLI plugins and application command presentation separate from the Go
   API client.
