# Go SDK and Docker CLI Integration

Use this reference when maintaining Go clients, daemon integrations, or Docker
CLI plugins across API and package-surface changes.

## Concurrency and callback signatures

### Concurrent Go clients (27.0.1)

`*client.Client` is now safe for concurrent use by multiple goroutines,
including when API-version negotiation is enabled; callers no longer need to
serialize access to avoid the former negotiation data race.

### Go SDK callback and image-option changes (27.0.1)

`client.RequestPrivilegeFunc`,
`client.ImageSearchOptions.AcceptPermissionsFunc`, and
`image.ImportOptions.PrivilegeFunc` callbacks now require a context parameter.
The deprecated `ImageImportOptions`, `ImageCreateOptions`, `ImagePullOptions`,
`ImagePushOptions`, `ImageListOptions`, and `ImageRemoveOptions` aliases are
removed; use the option types in `api/types/image`.

## Type relocations

### Go SDK type relocations (27.0.1)

Container statistics, exec, copy, and prune types move to
`api/types/container`, including `BlkioStatEntry`, `BlkioStats`, `CPUStats`,
`CPUUsage`, `ContainerExecInspect`, `ContainerPathStat`, `ContainerStats`,
`ContainersPruneReport`, `CopyToContainerOptions`, `ExecConfig`,
`ExecStartCheck`, `MemoryStats`, `NetworkStats`, `PidsStats`, `StatsJSON`,
`Stats`, `StorageStats`, and `ThrottlingData`.

`ImagesPruneReport`, `ImageImportSource`, and `ImageLoadResponse` move to
`api/types/image`; `ExecStartOptions`, `VolumesPruneReport`, `EventsOptions`,
and `ImageSearchOptions` move respectively to `api/types/backend`,
`api/types/volume`, `api/types/events`, and `api/types/registry`. Network API
types move to `api/types/network`, dropping the `Network` prefix where
applicable, and `NetworkResource` moves there as well.

### Go client network and value types (engine-release-history)

Operation option types move from `api/types` packages into `client`, filters use
the client's own `Filters` type, and IP addresses and subnets use `netip.Addr`
and `netip.Prefix`. MAC addresses become `net.HardwareAddr`-compatible byte
slices, container `Port` becomes `PortSummary`, and network `Summary` and
`Inspect` are no longer aliases.

## Call-shape migrations

### Go client call and response changes (28.0.0)

`ImageHistory`, `ImageLoad`, and `ImageSave` now take variadic functional
options, and container `StatsResponse` is merged into `Stats`. Container commit
and exec creation gain dedicated `CommitResponse` and `ExecCreateResponse`
aliases; the generic `IDResponse` is deprecated in their favor.

### Go SDK migration targets (28.0.0)

Use `client.ImageInspect` instead of `ImageInspectWithRaw`, `config.Validate`
instead of `Config.ValidatePlatformConfig`, and `github.com/moby/sys/reexec`
instead of `pkg/reexec`. Atomic-file helpers move to `pkg/atomicwriter`; use
`os.MkdirAll`, `container.UpdateResponse`, and `container.TopResponse` in place
of their deprecated wrappers.

### Go client call-shape migration (engine-release-history)

Configuration, image, plugin-list, and prune operations move from positional
arguments to option structs and dedicated result structs. `ContainerExec...`
methods become `Exec...`; image pull and push return objects with
`JSONMessages` iterators; inspect, history, load, and save results are wrapped;
`ContainerCommitOptions.Pause` becomes `NoPause`; and `ImageCreate` is removed
in favor of `ImagePull` or `ImageImport`.

## Removed packages and symbols

### Removed Go and CLI compatibility symbols (26.0.0)

The Go packages remove `image.IDFromDigest`, `pkg/loopback`,
`pkg/system.ErrNotSupportedOperatingSystem`, `pkg/system.IsOSSupported`,
`pkg/homedir.Key`, `pkg/homedir.GetShortcutString`, and
`pkg/containerfs.ResolveScopedPath`. The temporary aliases in `api/types` for
info, commit, plugin, network-pool, runtime, security, checkpoint, image,
service-response, resize, and container-option types are also removed; CLI
integrations must stop using `cli/command/container.NewStartOptions`,
`cli/command.DockerCliOption`, and `cli/command.InitializeOpt`.

### Go SDK removals (28.0.0)

Engine removes deprecated `pkg/ioutils` pipe, counter, writer, and flusher
helpers; `pkg/directory`, `pkg/dmsg.Dmesg`, `pkg/sysinfo.NumCPU`, `cli.Errors`,
and the old image-spec package (use `github.com/moby/docker-image-spec`). Removed
helpers also include archive temporary-file APIs,
`pkg/fileutils.GetTotalUsedFds`, `pkg/longpath.Prefix`, string-ID validators,
and legacy `runconfig` conversion and network-default functions.

`Daemon.ContainerInspectCurrent`, `Daemon.Exists`, and `Daemon.IsPaused` are
gone, and `Daemon.ContainerInspect` now takes
`backend.ContainerInspectOptions`. Deprecated libnetwork iptables types and a
set of old top-level `api/types` aliases are removed as well.

### Supported Go modules and release tags (engine-release-history)

`github.com/docker/docker` is deprecated; the supported public modules are
`github.com/moby/moby/client` and `github.com/moby/moby/api`, while the root
`github.com/moby/moby` module is internal. Engine 29 release tags use the
`docker-v29.0.0` form, and the SDK now requires Go 1.24 or later.

### Removed Go SDK surface (engine-release-history)

Engine 29 removes deprecated client constructors and interfaces including
`NewClient`, `NewEnvClient`, `CommonAPIClient`, and the old image-client
interfaces. It also removes `api/pkg/progress`, `api/pkg/streamformatter`,
`pkg/system`, `pkg/fileutils`, `pkg/idtools`, the old archive, chroot-archive,
atomic-writer, reexec, platform, and parser packages, and numerous CLI command
constructors and formatters; replacements live in
`github.com/moby/go-archive`, `github.com/moby/sys`, or the standard library.

## CLI plugin behavior and installation

### Failure-aware CLI plugin hooks (engine-release-history)

CLI plugin hooks now run when a command fails as well as when it succeeds.
Plugins can register `error-hooks` when a hint should appear only for failed
commands.

### Windows runtime, networking, and plugin changes (engine-release-history)

Windows containers now support `docker run --runtime`, and the Windows overlay
network driver accepts `--dns`. The CLI no longer discovers plugins under
`%PROGRAMDATA%\Docker\cli-plugins`; install them under
`%ProgramFiles%\Docker\cli-plugins` instead.
