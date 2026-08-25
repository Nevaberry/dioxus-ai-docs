# Standard library and processes

## Hashing and maps

### CRC algorithms

In 0.13.0, polynomial-specific CRC implementations were consolidated under the
generic `Crc` type. `Crc32` remains, but code using `Crc32WithPoly` must select an
algorithm explicitly:

```zig
const hash = Crc(.Crc32Iscsi);
```

Custom CRCs define an `Algorithm` value. When porting from the old implementation,
account for its pre-reflected polynomial, `initial = 0xffffffff`, reflected input
and output, and `xor_output = 0xffffffff`.

### Static string maps

`StaticStringMap` replaced `ComptimeStringMap` in 0.13.0. Key/value data moved from
a type parameter to `initComptime`, leaving a stable map struct type.

```zig
const map = std.StaticStringMap(T).initComptime(kvs_list);
```

It also offers `keys`, `values`, `getLongestPrefix`, and
`getLongestPrefixIndex`, plus allocator-taking runtime `init` and `deinit`.

## Child processes

Child processes moved under `std.process` in 0.13.0. Use `std.process.Child`
instead of removed `std.ChildProcess`; related functions moved from the type to
the `std.process` namespace.

In 0.14.0, `process.Child.collectOutput` changed to take the allocator explicitly
and write to unmanaged lists:

```zig
var stdout: std.ArrayListUnmanaged(u8) = .empty;
defer stdout.deinit(allocator);
var stderr: std.ArrayListUnmanaged(u8) = .empty;
defer stderr.deinit(allocator);
try child.collectOutput(allocator, &stdout, &stderr, max_output_bytes);
```

Do not compare allocator or random interface `ptr` fields; stateless
implementations may leave them undefined.

## Progress reporting

The progress API was reworked in 0.13.0:

- Nodes are values rather than pointers.
- `activate` calls are unnecessary.
- Progress can be initialized only once, normally in `main`.
- Start the root through the global API; every option is optional.
- `Node.start` copies names, so its input name may be short-lived.

```zig
const root_node = std.Progress.start(.{
    .root_name = "Test",
    .estimated_total_items = test_fn_list.len,
});
```

Guard direct stderr writes with `std.debug.lockStdErr` and
`std.debug.unlockStdErr` so they cooperate with progress. `std.debug.print`
already locks. To attach a child process's progress subtree, assign
`child.progress_node = node` before `child.spawn()`.

Since 0.15.1, `std.Progress.setStatus` publishes `.working`, `.success`,
`.failure`, or `.failure_working`, including for watched and long-running work.

## POSIX vectors

Since 0.13.0, initialize `std.posix.iovec` with `.base` and `.len`, not
`.iov_base` and `.iov_len`.

```zig
.{ .base = message.ptr, .len = message.len }
```

## ZON data APIs

ZON gained runtime and comptime data APIs in 0.14.0:

- Parse typed runtime data with `std.zon.parse.fromSlice` and release it with
  `std.zon.parse.free`.
- Serialize with `std.zon.stringify.serialize` or its depth/serializer variants.
- Import a ZON file at comptime when the result is typed:
  `const config: Config = @import("config.zon");`.

## Removed and renamed standard-library APIs

The following old names fail to compile as of 0.14.0:

| Removed or renamed | Replacement |
|---|---|
| `std.fs.MAX_PATH_BYTES` | Use current path APIs without this alias |
| Generic `std.mem.tokenize` | Scalar, sequence, or any-token variants |
| Generic `std.mem.split` / `splitBackwards` | Scalar, sequence, or any-split variants |
| `std.zig.CrossTarget` | `std.Target.Query` |
| `std.rand` | `std.Random` |
| `std.TailQueue` | `std.DoublyLinkedList` |
| `Dir.OpenDirOptions` | `Dir.OpenOptions` |
| Unicode `le` spellings | `Le` spellings |
| Container `popOrNull` | `pop` |

## C feature presence

Since 0.14.0, unavailable OS-specific `std.c` types are `void`, while unavailable
function symbols evaluate to `void` (`{}`) instead of causing a compile error.
Presence-only `@hasDecl` checks are insufficient: test `T != void` for a type or
`@TypeOf(function) != void` for a function.
