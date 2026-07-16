# Build, packages, and tools

## Build graph behavior

### Inherited stdio serialization

Since 0.13.0, a `Step.Run` configured with inherited stdio holds the documented
global lock, preventing other build steps from running concurrently while the
child owns stdout or stderr. The step is side-effecting, always runs when it is in
the graph, and fails on a crash or nonzero exit.

### Object-copy section retention

`Step.ObjCopy` accepts only one section to keep (since 0.13.0). This matches
`zig objcopy`, where repeated `-j` options retain only the last section.

### Source updates

`WriteFile` stopped mutating source files in 0.14.0. Use
`b.addUpdateSourceFiles()` instead of `b.addWriteFiles()` for copy/update
operations whose destination is in the source tree.

## Modules, artifacts, and generated paths

In 0.14.0, `addExecutable`, `addTest`, and related artifact constructors moved to
an existing module passed as `root_module`. Direct `root_source_file`, `target`,
and `optimize` options are deprecated. Create one module with
`b.createModule(...)` to reuse its imports and configuration across artifacts.

A package can expose any generated `LazyPath` with
`b.addNamedLazyPath("name", path)`. A dependent build retrieves it with
`dependency.namedLazyPath("name")`, allowing generated paths to cross a package
boundary without publishing an entire artifact or module.

## Headers, paths, and installation

Build APIs increasingly require `LazyPath` in 0.14.0, including
`Compile.installHeader`, `b.addInstallHeaderFile`, header-directory installation,
and `addRemoveDirTree`. Wrap a configured relative removal path as
`.{ .cwd_relative = path }`.

`installConfigHeader` no longer takes a subpath; it uses `include_path`. Generated
`-femit-h` output is not implicitly wired for installation: when required, set
`install_artifact.emitted_h = artifact.getEmittedH()`.

Since 0.13.0, installed Windows DLLs default to `<prefix>/bin/` beside executables
so the loader finds them without `lib` on `PATH`. Their import libraries remain in
`<prefix>/lib/`.

## Packages and caches

### ZIP dependencies

Since 0.13.0, `build.zig.zon` package dependencies may use `.zip` archives, and
`std.zip` can extract ZIP files.

### Package identity hashes

Since 0.14.0, package hashes encode the name, version, fingerprint component, and
unpacked size. Package names and versions are limited to 32 bytes, and names must
be bare Zig identifiers. Preserve the auto-generated `fingerprint`; a maintained
upstream fork should delete it and run `zig build` to generate a new identity.

### Local cache path

The project-local cache directory became `.zig-cache` in 0.13.0. `zig-out` did not
change.

## Watching, incremental compilation, and diagnostics

`zig build --watch` was added in 0.14.0. It keeps the runner alive, watches known
inputs, and reruns only dirty steps. `--debounce <ms>` changes the default 50 ms
debounce interval.

Incremental compilation is experimental and opt-in through `-fincremental`. It is
best paired with watch mode and a build option that skips binary emission because
compiler-state serialization and general linker output are not ready. It is not
compatible with `usingnamespace`.

```sh
zig build -Dno-bin -fincremental --watch
```

In 0.15.1, watch mode works reliably on macOS. `zig build --webui` keeps the build
process running with a rebuild UI; adding `--time-report` exposes timing for build
steps and declarations there.

## Testing and fuzzing

The 0.14.0 build runner added alpha-quality in-process fuzzing and a live coverage
UI. Register with `std.testing.fuzz(context, function, .{})`, run the test step as
`zig build test --fuzz`, and use `--port` to choose its listening port.

Since 0.15.1, `zig test-obj` compiles tests directly to an object file. The build
API equivalent is `emit_object` on `std.Build.addTest`; use it for external test
harnesses or later link steps.

## Initialization and CLI environment

In 0.15.1, the default `zig init` template creates a reusable module and an
executable. `zig init --minimal` (or `-m`) emits `build.zig.zon` with a valid
fingerprint and, when necessary, a stub `build.zig`.

Since 0.13.0, use `CLICOLOR_FORCE`, not `YES_COLOR`, to force color when stdout is
not a terminal. `zig env` reports `CLICOLOR_FORCE`.

## Linker and output behavior

Since 0.14.0, x86 `ReleaseSmall` defaults to keeping frame pointers
(`-fno-omit-frame-pointer`). Opt out explicitly only when size matters more than
stack-unwinding support.

ELF shared objects that are actually GNU ld scripts require `-fallow-so-scripts`
in 0.14.0. Ordinary builds skip the additional filesystem probing by default.

`zig objcopy` has reduced functionality in 0.15.1; some formerly supported
operations fail with `unimplemented`, so do not assume the previous feature set.
