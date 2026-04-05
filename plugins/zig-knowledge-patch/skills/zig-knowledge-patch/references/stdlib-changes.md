# Zig Standard Library Changes (0.13.0 - 0.14.0)

## 0.13.0 Changes

### StaticStringMap (renamed from ComptimeStringMap)

```zig
const map = std.StaticStringMap(T).initComptime(kvs_list);
// New methods: keys(), values(), init(allocator), deinit(allocator)
// getLongestPrefix(str), getLongestPrefixIndex(str)
```

### std.zip

New module for extracting zip files. `build.zig.zon` supports `.zip` dependencies.

### Progress API Rework

```zig
// Old:
var progress = std.Progress{ ... };
const root_node = progress.start("Test", test_fn_list.len);

// New:
const root_node = std.Progress.start(.{
    .root_name = "Test",
    .estimated_total_items = test_fn_list.len,
});
```

- Pass `Node` by value (not pointer)
- Remove `node.activate()` calls
- Short-lived strings safe (data copied)
- Only one `std.Progress` per process
- `std.debug.lockStdErr`/`unlockStdErr` for stderr integration
- Child process: set `child.progress_node = node` before `spawn()`
- `ZIG_PROGRESS` env var for parent-child protocol

### iovec Field Renames

`.iov_base` -> `.base`, `.iov_len` -> `.len`

### PriorityQueue

`items` now contains only valid items. Capacity in `cap` field (was: full slice in `items`, length in `len`).

### Cache Directory

`zig-cache` -> `.zig-cache` (hidden directory). `zig-out` unchanged.

### Color Env Variable

`YES_COLOR` -> `CLICOLOR_FORCE`

## 0.14.0 Changes

### DebugAllocator (replaces GeneralPurposeAllocator)

```zig
var debug_allocator: std.heap.DebugAllocator(.{}) = .init;
const gpa = debug_allocator.allocator();
defer _ = debug_allocator.deinit();
```

### SmpAllocator

Singleton allocator for `ReleaseFast` with multi-threading, competitive with glibc:

```zig
const allocator = std.heap.smp_allocator;
```

Per-thread freelists. Large allocations memory-mapped directly.

### Recommended allocator setup:

```zig
var debug_allocator: std.heap.DebugAllocator(.{}) = .init;
pub fn main() !void {
    const gpa, const is_debug = gpa: {
        if (native_os == .wasi) break :gpa .{ std.heap.wasm_allocator, false };
        break :gpa switch (builtin.mode) {
            .Debug, .ReleaseSafe => .{ debug_allocator.allocator(), true },
            .ReleaseFast, .ReleaseSmall => .{ std.heap.smp_allocator, false },
        };
    };
    defer if (is_debug) {
        _ = debug_allocator.deinit();
    };
}
```

### Allocator remap API

New `remap` function: attempt expand/shrink with possible relocation. Uses `mremap` on Linux.

```zig
remap: *const fn (*anyopaque, []u8, Alignment, usize, usize) ?[*]u8,
```

All VTable functions now take `std.mem.Alignment` (was `u8`).

Deleted: `WasmPageAllocator`, `LoggingAllocator`, `HeapAllocator`.

### Unmanaged Containers (managed deprecated)

`std.ArrayList` -> `std.ArrayListUnmanaged`
`std.ArrayHashMap` -> `std.ArrayHashMapUnmanaged`

```zig
var list: std.ArrayListUnmanaged(i32) = .empty;
defer list.deinit(gpa);
try list.append(gpa, 1234);
try list.ensureUnusedCapacity(gpa, 1);
list.appendAssumeCapacity(5678);
```

`popOrNull` renamed to `pop` in all containers.

### process.Child.collectOutput

```zig
var stdout: std.ArrayListUnmanaged(u8) = .empty;
defer stdout.deinit(allocator);
var stderr: std.ArrayListUnmanaged(u8) = .empty;
defer stderr.deinit(allocator);
try child.collectOutput(allocator, &stdout, &stderr, max_output_bytes);
```

### ZON Parsing and Serialization

```zig
// Runtime parsing:
const result = try std.zon.parse.fromSlice(MyType, allocator, zon_bytes, .{});
defer std.zon.parse.free(allocator, result);

// Runtime serialization:
try std.zon.stringify.serialize(writer, value, .{});

// Compile-time import:
const cfg: Config = @import("config.zon");
```

### Runtime Page Size

```zig
// Removed: std.mem.page_size
std.heap.page_size_min  // comptime lower bound
std.heap.page_size_max  // comptime upper bound
std.heap.pageSize()     // runtime query (memoized)
```

### std.hash_map rehash

New `rehash()` method to work around performance degradation from removals. Array hash maps not affected.

### std.c Reorganization

Last usage of `usingnamespace` eliminated. Non-existing symbols changed from `@compileError` to void types. Use `@TypeOf(f) != void` instead of `@hasDecl`.

### LLVM Builder API

Moved to `std.zig.llvm` for third-party use (implementation detail, not stable API).

### Deprecation Removals (now compile errors)

| Old | New |
|-----|-----|
| `std.fs.MAX_PATH_BYTES` | `std.fs.max_path_bytes` |
| `std.mem.tokenize` | `tokenizeAny`/`tokenizeSequence`/`tokenizeScalar` |
| `std.mem.split` | `splitSequence`/`splitAny`/`splitScalar` |
| `std.rand` | `std.Random` |
| `std.TailQueue` | `std.DoublyLinkedList` |
| `std.ChildProcess` | `std.process.Child` |
| `std.zig.CrossTarget` | `std.Target.Query` |
| `std.unicode.utf16leToUtf8*` | Capitalized `Le` variants |
| `std.crypto.tls.max_cipertext_inner_record_len` | `max_ciphertext_inner_record_len` |
