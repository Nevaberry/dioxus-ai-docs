# Go SDK and Docker CLI Integration

Use this reference when compiling against Moby or Docker CLI packages, migrating Engine clients, embedding CLI behavior, or parsing command results.

## Supported modules and toolchain

- `github.com/docker/docker` is deprecated for Engine 29 development.
- Use the public modules `github.com/moby/moby/client` and `github.com/moby/moby/api`. The parent `github.com/moby/moby` module is internal.
- Engine release tags use the `docker-v29.0.0` form.
- The Engine SDK requires Go 1.24 or newer.

## Client construction and interfaces

- `NewClient` and `NewEnvClient` are removed in Engine 29; migrate to supported client construction in `github.com/moby/moby/client`.
- `CommonAPIClient` is deprecated in favor of `APIClient` (since 28.0.0).
- `*client.Client` is safe for concurrent goroutine use, including with `WithAPIVersionNegotiation()` (since 27.0.1).
- Engine 28.0.0 adds client surfaces `WithTraceOptions`, `HijackDialer`, and `SwarmManagementAPIClient`.
- Empty IDs passed to inspect-style calls now return an invalid-parameter error rather than not-found (since 28.0.0). Validate identifiers or update error classification.

## Function signatures and result types

- Starting in 28.0.0, `ImageHistory`, `ImageLoad`, and `ImageSave` take variadic functional options.
- Engine 29 broadly moves config, image, plugin-list, and prune calls from positional arguments to option structs and dedicated result structs.
- `ContainerExec...` methods become `Exec...`.
- Image inspect, history, load, and save wrap their returns in result structs.
- Image pull and push return objects whose `JSONMessages` method iterates progress records.
- `container.Stats` and `StatsResponse` merge into one type (since 28.0.0).
- `CommitResponse` and `ExecCreateResponse` replace generic response typing (since 28.0.0).
- `client.ImageInspectWithRaw` is deprecated in favor of `client.ImageInspect` (since 28.0.0).
- `client.RequestPrivilegeFunc`, `client.ImageSearchOptions.AcceptPermissionsFunc`, and `image.ImportOptions.PrivilegeFunc` require a context parameter starting in 27.0.1.

## Network and filter types

- Engine 29 SDK IP addresses and subnets use `netip.Addr` and `netip.Prefix`.
- MAC addresses use byte slices compatible with `net.HardwareAddr`.
- Container `Port` becomes `PortSummary`.
- The client package has its own `client.Filters`.
- Network `Summary` and `Inspect` are no longer aliases; both embed most fields in a shared struct.

## Type relocations introduced in 27.0.1

- Move container stats, exec, copy, and prune types to `api/types/container`.
- Move `ImagesPruneReport`, `ImageImportSource`, and `ImageLoadResponse` to `api/types/image`.
- Move `ExecStartOptions` to `api/types/backend`.
- Move `VolumesPruneReport` to `api/types/volume`.
- Move `EventsOptions` to `api/types/events`.
- Move `ImageSearchOptions` to `api/types/registry`.
- Move network create, connect, disconnect, inspect, endpoint, list, and prune types to `api/types/network`; remove the `Network` prefix from their names.
- Move `NetworkResource` into `api/types/network`.
- Use the SDK's `Ulimit` alias rather than importing `github.com/docker/go-units.Ulimit` directly, insulating code from that type's future module move.
- Remove deprecated aliases `ImageImportOptions`, `ImageCreateOptions`, `ImagePullOptions`, `ImagePushOptions`, `ImageListOptions`, and `ImageRemoveOptions`.

## Additional migration targets in 28.0.0

- Compatibility aliases in top-level `api/types` are removed. Import the container, image, network, volume, events, registry, and backend subpackages directly.
- Move `GraphDriverData` to its storage package.
- Move `RequestPrivilegeFunc` to its registry package.
- Move container network, health, and state types to `api/types/container`.
- Move `ImageInspect` and `RootFS` to `api/types/image`.
- Move `pkg/reexec` usage to `github.com/moby/sys/reexec`.

## Removed client and utility surfaces

- Engine 26.0.0 removes `IDFromDigest`; `pkg/loopback`; `pkg/system.ErrNotSupportedOperatingSystem` and `IsOSSupported`; `pkg/homedir.Key` and `GetShortcutString`; and `pkg/containerfs.ResolveScopedPath`.
- Engine 26.0.0 also removes the temporary top-level `api/types` aliases deprecated in v25.
- Engine 28.0.0 removes deprecated `pkg/ioutils` helpers, `pkg/sysinfo.NumCPU`, `cli.Errors`, `pkg/directory`, and `pkg/dmesg.Dmesg`.
- Engine 28.0.0 removes additional deprecated archive, string-ID, and runconfig helpers and makes `pkg/containerfs` internal.
- Engine 29 removes `client.ImageCreate`; use `ImagePull` or `ImageImport`.
- Engine 29 removes deprecated image-client interfaces.
- Engine 29 removes or relocates `api/pkg/progress`, `api/pkg/streamformatter`, `pkg/fileutils`, `pkg/idtools`, `pkg/system`, `pkg/stdcopy`, `pkg/stringid`, and profiles.
- Use the documented client/API subpackages, `github.com/moby/profiles`, `github.com/moby/go-archive`, `github.com/moby/sys`, or the Go standard library as appropriate.

## Moby extension deprecations

The following extension surfaces were deprecated in 27.0.1 and should not be used in new integrations:

- Experimental GraphDriver plugins.
- `pkg/archive.NewTempArchive`, `TempArchive`, and `CanonicalTarNameForPath`.
- `pkg/dmesg`.
- `pkg/stringid.ValidateID` and `IsShortID`.
- Runconfig helpers `SetDefaultNetModeIfBlank` and `DefaultDaemonNetworkMode`.
- `opts.ConvertKVStringsToMap` and `IsPreDefinedNetwork`.

`ContainerConfigWrapper` moved to `api/types/container`, and the default daemon network-mode definition moved to `daemon/network`.

## CLI API and embedding removals

- Engine 26.0.0 removes CLI APIs `NewStartOptions`, `DockerCliOption`, and `InitializeOpt`; use their replacement packages and types directly.
- Engine 29 removes most exported `New...Command` constructors across container, image, network, Swarm, registry, volume, context, and trust commands.
- Many old formatter and `Run...` helpers are also removed.
- Stop constructing the stock Docker command tree through removed APIs. Use the supported Engine client modules or build a separate command layer.

## Command-line behavior

- `docker stop` and `docker restart` use `--timeout`; deprecated `--time` was removed in 28.0.0.
- `docker commit --pause` is deprecated in favor of `--no-pause`.
- `--kernel-memory` is hidden and warns because the daemon and kernel no longer support it.
- Docker no longer specially unquotes `--tlscacert`, `--tlscert`, and `--tlskey` values.
- Docker Content Trust commands and classic-builder DCT support are removed from the Engine 29 CLI. Build and install the trust command as a separate CLI plugin if required.

## Contexts and CLI plugins

- When Docker context metadata contains a `"GODEBUG":"..."` entry, the CLI applies that value while commands use the context.
- CLI plugin hooks run after failed as well as successful commands.
- Plugins can declare `error-hooks`; their hints appear only after failures.
- On Windows, install CLI plugins in `%ProgramFiles%\Docker\cli-plugins`. The former `%PROGRAMDATA%\Docker\cli-plugins` lookup is removed.
