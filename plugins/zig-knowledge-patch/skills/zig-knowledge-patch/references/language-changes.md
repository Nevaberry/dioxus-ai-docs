# Zig Language Changes (0.13.0 - 0.14.0)

## Labeled Switch (0.14.0)

Switch statements can be labeled and targeted by `continue`, ideal for FSAs:

```zig
foo: switch (@as(u8, 1)) {
    1 => continue :foo 2,
    2 => continue :foo 3,
    3 => return,
    4 => {},
    else => unreachable,
}
```

- `continue :label value` jumps to the case matching `value`
- `break` terminates the switch (like labeled blocks)
- Not implicitly evaluated at comptime (like loops); force with `comptime` context
- Generates separate conditional branches per `continue` to aid CPU branch prediction
- Comptime-known operands become unconditional branches

## Decl Literals (0.14.0)

`.foo` syntax resolves to any declaration on the target type via Result Location Semantics:

```zig
const S = struct {
    x: u32,
    const default: S = .{ .x = 123 };
    fn init(val: u32) S {
        return .{ .x = val + 1, .y = val + 2 };
    }
};
const val: S = .default; // S.default
const val2: S = .init(100); // calls S.init(100)

// Struct field defaults:
const Wrapper = struct { val: S = .default };

// Nested:
fn initCapacity(alloc: Allocator, cap: usize) !Buffer {
    return .{ .data = try .initCapacity(alloc, cap) };
}
```

**Fields and declarations cannot share names** in structs, unions, enums, opaques.

## @branchHint (0.14.0, replaces @setCold)

Must be first statement in block or function:

```zig
if (cond) {
    @branchHint(.unlikely);
    // ...
}
fn cold_fn() void {
    @branchHint(.cold);
}
// Conditional:
fn foo(comptime x: u8) void {
    @branchHint(if (x == 0) .cold else .none);
}
```

Variants: `.none`, `.likely`, `.unlikely`, `.cold`, `.unpredictable`.

## @fence Removed (0.14.0)

Replace with stronger orderings:

| Pattern | Before | After |
|---------|--------|-------|
| SeqCst barrier | `@fence(.seq_cst)` | Make all related ops `.seq_cst`, or use `fetchAdd(0, .seq_cst)` |
| Conditional acquire | `@fence(.acquire)` after fetchSub | `fetchSub(1, .acq_rel)` or add `rc.load(.acquire)` |
| External sync | `@fence(.seq_cst)` | `fetchAdd(0, .seq_cst)` on new atomic var |

## @FieldType Builtin (0.14.0)

```zig
const S = struct { a: u32, b: f64 };
comptime assert(@FieldType(S, "a") == u32);
// Works on structs, unions, tagged unions
```

## @splat Supports Arrays (0.14.0)

```zig
var pixels: [W][H]Rgba = @splat(@splat(.black));
const arr: [2:0]u8 = @splat(10); // sentinel-terminated
// Works with runtime-known values
```

## @export Takes Pointer (0.14.0)

```zig
@export(&foo, .{ .name = "bar" });  // was: @export(foo, ...)
```

## Packed Struct Equality and Atomics (0.14.0)

```zig
const x: PackedS = .{ .a = 1, .b = 2 };
const y: PackedS = .{ .a = 1, .b = 2 };
if (x == y) {}  // works without @bitCast

const prev = @atomicRmw(PackedS, &x, .Xchg, y, .seq_cst);  // works directly
```

## @ptrCast Allows Changing Slice Length (0.14.0)

## Remove Anonymous Struct Types, Unify Tuples (0.14.0)

- Untyped anonymous struct literals get "normal" struct types (not special coercing ones)
- All tuples use structural equivalence, no staged type resolution
- Tuples cannot have non-auto layouts, aligned fields, or default values (except comptime fields)

## CallingConvention Overhaul (0.14.0)

Changed from enum to tagged union with per-target variants:

```zig
// Old (deprecated, still works via decl literals):
callconv(.C)       // now: callconv(.c) (decl literal)
callconv(.Stdcall) // now: callconv(.x86_stdcall)

// New per-target variants:
callconv(.x86_64_sysv)
callconv(.arm_aapcs)
callconv(.riscv64_interrupt)

// Stack alignment (replaces @setAlignStack):
callconv(.withStackAlign(.c, 4))
```

Options payload (`CommonOptions`) allows `incoming_stack_alignment`.

## std.builtin.Type Fields Lowercased (0.14.0)

```zig
// Before -> After:
.Int -> .int
.Struct -> .@"struct"
.ComptimeInt -> .comptime_int
.Pointer -> .pointer
// etc.

// Pointer.Size also lowercased:
.One -> .one, .Many -> .many, .Slice -> .slice

// sentinel/default_value renamed:
.sentinel -> .sentinel_ptr  (use .sentinel() helper)
.default_value -> .default_value_ptr (use .defaultValue() helper)
```

## Non-Scalar Sentinel Types Disallowed (0.14.0)

Only types supporting `==` can be used as sentinels.

## @src Gains Module Field (0.14.0)

`std.builtin.SourceLocation` now has a `module: [:0]const u8` field.

## @memcpy: source/dest must be in-memory coercible (0.14.0)

Aliasing check at comptime. Old coercion behavior removed.
