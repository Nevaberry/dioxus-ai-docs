# Memory and containers

## Allocators

### Debug and high-throughput allocators

`std.heap.DebugAllocator(options)` replaces `GeneralPurposeAllocator` in 0.14.0.
It supports runtime page sizes while preserving leak and debugging behavior, and
is initialized with `.init`.

```zig
var debug_allocator: std.heap.DebugAllocator(.{}) = .init;
defer _ = debug_allocator.deinit();
const allocator = debug_allocator.allocator();
```

`std.heap.smp_allocator` is the process-wide singleton intended for fast
multithreaded allocation in `ReleaseFast`. A common policy selects
`DebugAllocator` for Debug/ReleaseSafe and `smp_allocator` for
ReleaseFast/ReleaseSmall.

### Allocator vtables and removed allocators

In 0.14.0, `std.mem.Allocator.VTable` gained `remap`, which may resize and return a
relocated pointer to avoid an internal copy. `resize` retains its no-relocation
promise. Vtable alignment arguments use `std.mem.Alignment` rather than `u8`.

`WasmPageAllocator`, `LoggingAllocator`, and the Windows-only `HeapAllocator` were
removed in 0.14.0.

Do not compare allocator interface `ptr` fields (or random interface `ptr` fields):
stateless implementations may leave them undefined.

### Runtime page size

`std.mem.page_size` was removed in 0.14.0. Use the memoized runtime
`std.heap.pageSize()` for the actual page size. When a comptime alignment bound is
required, use `std.heap.page_size_min` or `std.heap.page_size_max`.

## Allocator-explicit container transition

In 0.14.0, managed containers such as `std.ArrayList` and `std.ArrayHashMap` were
deprecated in favor of `Unmanaged` variants. Initialize an unmanaged value with
`.empty`; pass an allocator to allocating methods and `deinit`, but not to calls
such as `appendAssumeCapacity` that do not allocate.

In 0.15.1, `std.ArrayList` became the allocator-explicit, unmanaged type and added
static initialization. Use `std.array_list.Managed` for the old allocator-owning
behavior; its aligned counterpart is `std.array_list.AlignedManaged`.

```zig
var items: std.ArrayList(u8) = .empty;
defer items.deinit(allocator);
try items.append(allocator, 1);
```

## Queues and linked lists

### Priority queue storage

Since 0.13.0, `PriorityQueue.items` contains only valid queue elements; spare
allocation is represented by `cap`. Do not treat `items` as the complete allocated
slice or expect a separate `len` field. The layout is ArrayList-like.

### Intrusive doubly linked lists

By 0.15.1, linked lists are intrusive and non-generic. Embed
`std.DoublyLinkedList.Node` in the owning type rather than instantiating
`std.DoublyLinkedList(T).Node`, and recover the owner with `@fieldParentPtr`.

The older `std.TailQueue` alias had already been removed in 0.14.0; use
`std.DoublyLinkedList`.

## Fixed-capacity and streaming buffers

`std.BoundedArray` was removed in 0.15.1. Replace it with
`std.ArrayListUnmanaged.initBuffer` plus bounded operations such as
`appendSliceBounded`.

```zig
var storage: [8]i32 = undefined;
var stack = std.ArrayListUnmanaged(i32).initBuffer(&storage);
try stack.appendSliceBounded(initial_values);
```

`std.fifo.LinearFifo`, `std.RingBuffer`, and `std.fifo` were also removed in
0.15.1. Many streaming use cases should move to the ring buffers built into
`std.Io.Reader` and `std.Io.Writer`.
