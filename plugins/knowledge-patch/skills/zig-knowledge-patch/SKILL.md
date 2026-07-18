---
name: zig-knowledge-patch
description: Zig
license: MIT
version: "0.15.1"
metadata:
  author: Nevaberry
---

# Zig Knowledge Patch

Baseline: Zig through 0.12.x. Covered range: Zig 0.13.0 through 0.15.1.

Use this patch before writing or migrating Zig code in the covered range. Check the
reference for the subsystem being changed; many old names were removed rather than
soft-deprecated.

## Reference index

| Reference | Topics |
|---|---|
| [Language and builtins](references/language-and-builtins.md) | Removed syntax, switches, literals, reflection, atomics, pointers, assembly, type-system rules |
| [Memory and containers](references/memory-and-containers.md) | Allocators, page size, `ArrayList`, queues, linked lists, fixed-capacity and ring buffers |
| [I/O, formatting, compression, and networking](references/io-format-networking.md) | `std.Io`, file interfaces, formatting, flate, HTTP, TLS |
| [Standard library and processes](references/stdlib-and-processes.md) | CRC, string maps, process children, progress, POSIX, ZON, renamed and removed APIs |
| [Build, packages, and tools](references/build-packages-and-tools.md) | Build graph APIs, `LazyPath`, modules, packages, watch/fuzz workflows, CLI changes |
| [Targets, platform, and toolchain](references/targets-platform-toolchain.md) | Target triples, OS floors, calling conventions, C interop, backends, sanitizers, libc, SPIR-V |

## Breaking language removals

### Remove `usingnamespace`, `async`, and `await`

Zig 0.15.1 removes `usingnamespace`, the `async` and `await` keywords, and
`@frameSize`. Replace namespace injection with explicit declarations. Represent an
unsupported API as `void`/`{}` or a declaration that conditionally emits
`@compileError`; replace mixins with a named zero-bit field and
`@fieldParentPtr`. Async I/O is provided through library interfaces instead of the
removed language feature.

```zig
const have_feature = true;
pub const feature = if (have_feature)
    123
else
    @compileError("feature is unavailable");
```

### Replace removed atomics and branch annotations

`@fence` is gone in 0.14.0. Put the required ordering on the relevant atomic
operation: for example, turn release decrement plus acquire fence into an
`.acq_rel` decrement. Cross-variable sequential consistency requires `.seq_cst`
on all related operations or an explicit atomic read-modify-write barrier.

`@branchHint` replaces `@setCold`. It must be the first statement of the affected
conditional block or function and accepts `.likely`, `.unlikely`, `.cold`,
`.unpredictable`, or `.none`.

```zig
if (unlikely_condition) {
    @branchHint(.unlikely);
    handleSlowPath();
}
```

### Update reflection and export code

`std.builtin.Type` and `Pointer.Size` tags are lowercase; keyword tags are quoted,
for example `.int`, `.pointer`, `.one`, `.@"struct"`, and `.@"enum"`. Opaque
reflection fields became `default_value_ptr` and `sentinel_ptr`; prefer typed
accessors such as `StructField.defaultValue()` and `Pointer.sentinel()`.

`@export` takes a pointer in 0.14.0:

```zig
const value: u32 = 123;
comptime { @export(&value, .{ .name = "exported_value" }); }
```

Use `@FieldType(Container, "field")` instead of `std.meta.FieldType`.

## Allocators and containers

### Treat `ArrayList` as allocator-explicit

The 0.14.0 transition deprecated managed containers in favor of unmanaged forms.
In 0.15.1, `std.ArrayList` itself is unmanaged: initialize with `.empty` or static
storage and pass the allocator to allocating operations and `deinit`. Use
`std.array_list.Managed` only when allocator-owning behavior is required.

```zig
var values: std.ArrayList(u8) = .empty;
defer values.deinit(allocator);
try values.append(allocator, 42);
```

The aligned managed spelling is `std.array_list.AlignedManaged`. Keep
allocator-free calls such as `appendAssumeCapacity` allocator-free.

### Select current allocators

`std.heap.DebugAllocator(options)` replaces `GeneralPurposeAllocator` and starts
from `.init`. `std.heap.smp_allocator` is the fast process-wide allocator intended
for multithreaded `ReleaseFast` programs.

```zig
var debug_allocator: std.heap.DebugAllocator(.{}) = .init;
defer _ = debug_allocator.deinit();
const allocator = debug_allocator.allocator();
```

Allocator vtables now include `remap`, which may return relocated storage;
`resize` still promises not to relocate. Alignment parameters use
`std.mem.Alignment`, not `u8`.

## Concrete I/O interfaces

### Migrate readers and writers

Zig 0.15.1 replaces generic `std.io` stream types with non-generic
`std.Io.Reader` and `std.Io.Writer`. Their buffers are caller-owned and live in
the concrete interface. Old writers can temporarily bridge with
`old_writer.adaptToNewApi(&.{})`.

```zig
var buffer: [1024]u8 = undefined;
var file_writer = std.fs.File.stdout().writer(&buffer);
const stdout: *std.Io.Writer = &file_writer.interface;
try stdout.print("{s}\n", .{"hello"});
try stdout.flush();
```

Use `File.Reader` and `File.Writer` for seeking, position tracking, file transfer,
and streaming versus positional access. `posix.sendfile` is replaced by
`File.Reader.sendFile`.

### Make custom formatting explicit

Use `{f}` to invoke a value's `format` method and `{any}` to bypass it. The method
now accepts only the value and `*std.Io.Writer`, returning
`std.Io.Writer.Error!void`.

```zig
pub fn format(value: Value, writer: *std.Io.Writer) std.Io.Writer.Error!void {
    try writer.print("{d}", .{value.number});
}
```

## Build-system migrations

### Create artifacts from modules

`addExecutable`, `addTest`, and related APIs take `root_module`. Create a reusable
module with `b.createModule(...)` rather than passing `root_source_file`, `target`,
and `optimize` directly to each artifact.

Build APIs for header installation and removal increasingly require `LazyPath`.
For a configured relative removal path use `.{ .cwd_relative = path }`.

### Keep source mutation explicit

`WriteFile` no longer updates source-tree files. Use `b.addUpdateSourceFiles()` for
copy or update operations whose destination belongs to the source tree.

For generated headers, assign
`install_artifact.emitted_h = artifact.getEmittedH()` when installation needs the
`-femit-h` output. `installConfigHeader` now gets its destination from
`include_path` and no longer takes a subpath argument.

### Watch, fuzz, and incremental workflows

`zig build --watch` keeps the runner alive and reruns only dirty steps;
`--debounce <ms>` overrides its 50 ms debounce. In 0.15.1 it works on macOS, and
`--webui --time-report` exposes rebuild controls and timing.

Register fuzz targets with `std.testing.fuzz(context, function, .{})`, then run
`zig build test --fuzz`; `--port` selects the coverage UI port.

Incremental compilation is experimental and opt-in with `-fincremental`. It is not
compatible with `usingnamespace`; prefer it with watch mode and a build option that
skips binary emission:

```sh
zig build -Dno-bin -fincremental --watch
```

## Frequent standard-library migrations

- Use `std.process.Child`, not `std.ChildProcess`; `collectOutput` takes the
  allocator plus unmanaged output lists.
- Use `std.StaticStringMap(T).initComptime(kvs)`, not `ComptimeStringMap`.
- Use `std.heap.pageSize()` at runtime; use `page_size_min` or `page_size_max` for
  comptime alignment bounds.
- Use `std.Random`, `std.Target.Query`, and `std.DoublyLinkedList`; old aliases
  including `std.rand`, `std.zig.CrossTarget`, and `std.TailQueue` are removed.
- Initialize `std.posix.iovec` with `.base` and `.len`.
- Use `CLICOLOR_FORCE` to force colored CLI output; the local cache is
  `.zig-cache`.

## Platform and backend checks

Zig 0.15.1 raises explicit supported OS floors; verify deployment targets before
upgrading. Debug x86-64 builds default to the self-hosted backend except on
NetBSD, OpenBSD, and Windows. Pass `-fllvm` or set `.use_llvm = true` when LLVM is
required.

C undefined-behavior sanitization accepts `-fsanitize-c=full` or
`-fsanitize-c=trap`; build configuration uses `?std.zig.SanitizeC`, with `.full`
and `.off` replacing booleans. See the platform reference for target-triple,
cross-libc, calling-convention, and SPIR-V details.
