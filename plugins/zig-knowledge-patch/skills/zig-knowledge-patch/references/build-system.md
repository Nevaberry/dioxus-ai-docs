# Zig Build System Changes (0.13.0 - 0.14.0)

## 0.13.0 Changes

- `Step.Run`: global lock implemented for child processes inheriting stderr
- Windows DLLs installed to `<prefix>/bin/` by default (matches CMake)
- `Step.ObjCopy`: single section only (reflects actual `zig objcopy` behavior)

## 0.14.0 Changes

### File System Watching (--watch)

```bash
zig build --watch                # rebuild on source changes
zig build --watch --debounce 100 # custom debounce (default 50ms)
```

Watches minimal set of directories. Re-runs only dirty steps.

### Module-First API (root_module)

```zig
const mod = b.createModule(.{
    .root_source_file = b.path("src/main.zig"),
    .target = target,
    .optimize = optimize,
});
const exe = b.addExecutable(.{ .name = "hello", .root_module = mod });

// Same module for tests:
const tests = b.addTest(.{ .name = "hello-test", .root_module = mod });

// Module dependencies:
foo.addImport("bar", bar);
bar.addImport("foo", foo);  // mutual recursion supported
```

Old API (passing root_source_file/target/optimize directly) still works but deprecated.

### addLibrary

Replaces `addSharedLibrary`/`addStaticLibrary`:

```zig
const linkage = b.option(std.builtin.LinkMode, "linkage", "...") orelse .static;
const lib = b.addLibrary(.{ .linkage = linkage, .name = "foo", .root_module = mod });
```

### Package Hash Format

New format: `mime-3.0.0-zwmL-6wgAADu...` (includes name, version, fingerprint, disk size).

New rules for `build.zig.zon`:
- `name` and `version` limited to 32 bytes
- `name` must be valid bare Zig identifier
- `fingerprint` field auto-generated (globally unique package ID, never changes)

### Expose Arbitrary LazyPaths

```zig
// In dependency:
b.addNamedLazyPath("generated", generated_file);

// In consumer:
const gen = bar.namedLazyPath("generated");
```

### Incremental Compilation (opt-in)

```bash
zig build -Dno-bin -fincremental --watch
```

Not default yet. Works well with `-fno-emit-bin` for error-checking. Not compatible with `usingnamespace`.

### x86 Backend

98% behavior test pass rate. Select with `-fno-llvm` or `use_llvm = false`. Expected to become debug-mode default in 0.15.0. Supports multithreaded codegen.

### Integrated Fuzzer (alpha)

```bash
zig build test --fuzz
# Spawns HTTP server with live coverage UI
```

```zig
test "fuzz example" {
    try std.testing.fuzz(@as([]const u8, "canyoufindme"), findSecret, .{});
}
```

### Breaking Build API Changes

- `WriteFile` source updates -> `b.addUpdateSourceFiles()`
- `RemoveDir` takes `LazyPath` (was `[]const u8`): `.{ .cwd_relative = tmp_path }`
- `Compile.installHeader` takes `LazyPath`
- `Compile.installHeadersDirectory` consolidated, takes `LazyPath` with filters
- `b.addInstallHeaderFile` takes `LazyPath`
- `-femit-h` header never emitted; use `install_artifact.emitted_h = artifact.getEmittedH()`
- `addCopyDirectory` added to `WriteFile`
- SHA-256 Git repos supported for fetch
- Mach-O executable detection for fetch
- ConfigHeader values can be added outside comptime
- `-fno-omit-frame-pointer` default for ReleaseSmall on x86
- `-fallow-so-scripts` flag for ELF .so linker scripts

### Toolchain Updates

- LLVM 19
- glibc 2.41
- musl 1.2.5
- Linux 6.13.4 headers
- Darwin libSystem 15.1
- UBSan runtime included
