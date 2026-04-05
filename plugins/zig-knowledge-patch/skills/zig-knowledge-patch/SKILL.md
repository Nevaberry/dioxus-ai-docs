---
name: zig-knowledge-patch
description: "Zig changes since training cutoff (latest: 0.14.0) \u2014 labeled switch, decl literals, @branchHint, DebugAllocator, unmanaged containers, root_module build API. Load before working with Zig."
license: MIT
metadata:
  author: Nevaberry
  version: "0.14.0"
---

# Zig Knowledge Patch

Claude's baseline knowledge covers Zig through 0.12.x. This skill provides breaking changes and new features in 0.13.0 and 0.14.0.

## Breaking Changes Quick Reference

| Version | Change | Impact | Details |
|---------|--------|--------|---------|
| 0.13.0 | `ComptimeStringMap` -> `StaticStringMap` | API rename + new init pattern | [stdlib-changes](references/stdlib-changes.md) |
| 0.13.0 | `zig-cache` -> `.zig-cache` | Update .gitignore | [stdlib-changes](references/stdlib-changes.md) |
| 0.13.0 | `std.Progress` rework | Pass `Node` by value, new init API | [stdlib-changes](references/stdlib-changes.md) |
| 0.14.0 | `std.builtin.Type` fields lowercased | `.Int` -> `.int`, `.Struct` -> `.@"struct"` | [language-changes](references/language-changes.md) |
| 0.14.0 | `@setCold` removed | Use `@branchHint(.cold)` | [language-changes](references/language-changes.md) |
| 0.14.0 | `@fence` removed | Use stronger atomic orderings | [language-changes](references/language-changes.md) |
| 0.14.0 | `@export` takes pointer | Add `&` operator | [language-changes](references/language-changes.md) |
| 0.14.0 | `CallingConvention` overhauled | Tagged union, `.C` -> `.c` | [language-changes](references/language-changes.md) |
| 0.14.0 | Anonymous struct types removed | Tuples unified, structural equivalence | [language-changes](references/language-changes.md) |
| 0.14.0 | `GeneralPurposeAllocator` -> `DebugAllocator` | New init pattern | [stdlib-changes](references/stdlib-changes.md) |
| 0.14.0 | `ArrayList` deprecated | Use `ArrayListUnmanaged`, pass allocator | [stdlib-changes](references/stdlib-changes.md) |
| 0.14.0 | `std.mem.page_size` removed | Use `std.heap.pageSize()` | [stdlib-changes](references/stdlib-changes.md) |
| 0.14.0 | Build API: `root_module` | `addExecutable` takes `root_module` | [build-system](references/build-system.md) |
| 0.14.0 | Package hash format changed | New format includes name/version/fingerprint | [build-system](references/build-system.md) |

## New Language Features (0.14.0)

### Labeled Switch

Switch statements can be labeled and targeted by `continue` for state machines:

```zig
foo: switch (@as(u8, 1)) {
    1 => continue :foo 2, // jump to case 2
    2 => continue :foo 3,
    3 => return,
    else => unreachable,
}
```

Generates optimized branch prediction code. Also supports `break` from labeled switch.

### Decl Literals

`.foo` syntax resolves to declarations on the target type (not just enum variants):

```zig
const S = struct {
    x: u32,
    const default: S = .{ .x = 123 };
    fn init(val: u32) S {
        return .{ .x = val + 1 };
    }
};
const a: S = .default; // S.default
const b: S = .init(100); // S.init(100)
```

**Key pattern**: Unmanaged containers use `.empty` instead of `.{}`:

```zig
var list: std.ArrayListUnmanaged(u32) = .empty;
foo: std.ArrayListUnmanaged(u32) = .empty, // as struct field default
```

Fields and declarations in the same container cannot share names.

### @branchHint

Replaces `@setCold`. Must be first statement in block:

```zig
@branchHint(.unlikely);  // .none, .likely, .unlikely, .cold, .unpredictable
```

### @FieldType Builtin

```zig
comptime assert(@FieldType(MyStruct, "field_name") == u32);
```

### @splat for Arrays

```zig
var pixels: [W][H]Rgba = @splat(@splat(.black));
```

See [references/language-changes.md](references/language-changes.md) for full details.

## Standard Library (0.14.0)

### Allocator Changes

```zig
// DebugAllocator (replaces GeneralPurposeAllocator)
var debug_allocator: std.heap.DebugAllocator(.{}) = .init;
const gpa = debug_allocator.allocator();
defer _ = debug_allocator.deinit();

// SmpAllocator (for ReleaseFast, competitive with glibc)
const allocator = std.heap.smp_allocator;
```

New `remap` on Allocator.VTable enables relocation during resize (uses `mremap` on Linux).

### Unmanaged Containers (managed versions deprecated)

```zig
var list: std.ArrayListUnmanaged(i32) = .empty;
defer list.deinit(gpa);
try list.append(gpa, 1234);  // allocator passed to methods
```

Same for `ArrayHashMapUnmanaged`. `popOrNull` renamed to `pop`.

### ZON Support

Runtime: `std.zon.parse.fromSlice(T, allocator, zon_bytes, .{})`.
Compile-time: `const cfg: Config = @import("config.zon");`.

### Runtime Page Size

`std.heap.pageSize()` (runtime, memoized). Comptime bounds: `page_size_min`, `page_size_max`.

See [references/stdlib-changes.md](references/stdlib-changes.md) for full details.

## Build System (0.14.0)

### File System Watching

```bash
zig build --watch                # rebuilds on source changes
zig build --watch --debounce 100 # custom debounce (default 50ms)
```

### Module-First API

```zig
const mod = b.createModule(.{
    .root_source_file = b.path("src/main.zig"),
    .target = target,
    .optimize = optimize,
});
const exe = b.addExecutable(.{ .name = "hello", .root_module = mod });
// Reuse same module for tests:
const tests = b.addTest(.{ .name = "hello-test", .root_module = mod });
```

### Incremental Compilation (opt-in)

```bash
zig build -Dno-bin -fincremental --watch  # fast error-checking loop
```

### x86 Backend

98% behavior test pass rate. Select with `-fno-llvm`. Expected default for debug mode in 0.15.0.

See [references/build-system.md](references/build-system.md) for full details.

## Major Deprecation Removals (0.14.0)

Now compile errors: `std.mem.tokenize` (use `tokenizeAny`/`tokenizeSequence`/`tokenizeScalar`), `std.mem.split` (use `splitSequence`/`splitAny`/`splitScalar`), `std.rand` (use `std.Random`), `std.TailQueue` (use `std.DoublyLinkedList`), `std.zig.CrossTarget` (use `std.Target.Query`), `std.fs.MAX_PATH_BYTES` (use `max_path_bytes`).

## Reference Files

| File | Contents |
|------|----------|
| [language-changes.md](references/language-changes.md) | Labeled switch, decl literals, @branchHint, @fence removal, CallingConvention, type field renames, packed struct changes, tuple unification |
| [stdlib-changes.md](references/stdlib-changes.md) | DebugAllocator, SmpAllocator, remap API, unmanaged containers, ZON, runtime page size, StaticStringMap, Progress rework, deprecations |
| [build-system.md](references/build-system.md) | --watch, root_module API, addLibrary, package hash format, incremental compilation, fuzzer, WriteFile/RemoveDir changes |
