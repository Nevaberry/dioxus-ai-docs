# Language and builtins

## Control flow and declaration literals

### Labeled switch transitions

Since 0.14.0, `continue :label new_operand` can target a labeled `switch`; the
operand becomes the next switch operand. `break :label` exits it. A switch that
uses this transition executes at runtime unless placed in a `comptime` context.

```zig
state: switch (@as(u8, 1)) {
    1 => continue :state 2,
    2 => {},
    else => unreachable,
}
```

### Declaration literals

Since 0.14.0, `.name` can resolve to a declaration or function on a known result
type, not only to an enum field. This permits `.default`, `.empty`, `.init(...)`,
and `try .init(...)`. It is also a safe replacement for interdependent default
field values.

```zig
const S = struct {
    x: u32,
    const default: S = .{ .x = 123 };
};
const value: S = .default;
```

A `struct`, `union`, `enum`, or `opaque` type may no longer give a field and a
declaration the same name (since 0.14.0). Rename one side; lowercase fields and
uppercase type declarations usually avoid the collision.

### Non-exhaustive enum switches

Since 0.15.1, a switch can combine explicit enum tags, `else`, and `_`. `else`
handles remaining named tags; `_` handles unnamed integer values.

```zig
switch (value) {
    .A => {},
    else => {},
    _ => {},
}
```

## Removed language features

### `usingnamespace`

`usingnamespace` was removed in 0.15.1. Replace conditional inclusion with an
unconditional or conditionally failing declaration and replace implementation
switching with conditional declarations. Feature APIs can expose `{}` when
unsupported and test `@TypeOf(api.feature) == void`. For mixins, embed a named
zero-bit field whose methods recover the owner with `@fieldParentPtr`.

### Async keywords

The `async` and `await` keywords and `@frameSize` were removed in 0.15.1. Async I/O
is intended to come from standard-library interfaces rather than language syntax.

## Values, coercions, and aggregate rules

### Array splats and static pointers

Since 0.14.0, the result type can make `@splat` initialize an ordinary or
sentinel-terminated array with a comptime- or runtime-known value. The declared
sentinel remains unchanged.

```zig
const bytes: [16]u8 = @splat(0xff);
const terminated: [2:0]u8 = @splat(10);
```

Container-level variables can hold forward or cyclic pointers to one another
(since 0.14.0), enabling static linked structures without runtime initialization.

### Anonymous structs and tuples

Since 0.14.0, an untyped `.{ .field = value }` has a normal struct type tied to its
AST node and structure rather than the old structurally coercible anonymous type.
Tuples use structural equivalence, but cannot have non-`auto` layout, aligned
fields, or non-comptime default values.

### Sentinels and packed aggregates

Array and slice sentinel values must be scalar and support equality (since
0.14.0); aggregate sentinels are rejected. Packed structs can be compared with
`==` and used directly with `@atomicRmw` without bit-casting to their backing
integer.

Packed-union fields cannot override alignment (since 0.15.1), matching packed
struct behavior. Remove the ineffective `align` attribute.

### Undefined arithmetic and integer-to-float coercion

Since 0.15.1, only operations that can never cause Illegal Behavior may accept an
`undefined` operand. Other arithmetic is Illegal Behavior at runtime and a
compile error at comptime; avoid all operations on undefined values.

Comptime integer-to-float coercion must be exact. When rounding is intentional,
write a floating-point literal such as `123_456_789.0` to opt into it.

### Boolean vectors

Vectors of `bool` accept logical and bitwise `!`, `~`, `&`, `|`, and `^` directly
since 0.15.1.

## Builtins and reflection

### Exports and branch hints

Since 0.14.0, `@export` takes a pointer as its first operand; most migrations add
`&` to the exported value.

`@branchHint` replaces `@setCold` and must be the first statement of a conditional
block or function. It accepts `.likely`, `.unlikely`, `.cold`, `.unpredictable`,
and `.none`; a comptime expression can choose a hint for conditional coldness.

### Atomic fences

`@fence` was removed in 0.14.0. Strengthen the relevant atomic operation instead:
for example, use an `.acq_rel` decrement in place of release decrement followed by
acquire fence, or conditionally perform an acquire load. A sequentially consistent
cross-variable barrier requires all related operations to use `.seq_cst`, or an
explicit atomic read-modify-write used as the barrier.

### Type information

Since 0.14.0, `std.builtin.Type` tags are lowercase (`.int`, `.pointer`,
`.comptime_int`), keyword tags require quoting (`.@"struct"`, `.@"union"`,
`.@"enum"`), and `Pointer.Size` values are lowercase (`.one`, `.many`, and so on).
Opaque-pointer fields became `default_value_ptr` and `sentinel_ptr`. Retrieve typed
values through `StructField.defaultValue()` and `Pointer`/`Array.sentinel()`.

`@FieldType(Container, "field")` returns the declared type of a struct, union, or
tagged-union field and replaces `std.meta.FieldType` (since 0.14.0).

`@src()` returns a `std.builtin.SourceLocation` whose new `module` field is the
comptime module name; `file` is relative to that module's root (since 0.14.0).

### Raw copies and function attributes

Since 0.14.0, `@memcpy` only copies element types that are in-memory coercible.
Comptime copies do not apply other coercions, and aliased source/destination
arguments are rejected.

A function's `callconv`, `align`, `addrspace`, and `linksection` expressions may no
longer reference that function's parameters (since 0.14.0).

### Pointer-to-slice casting

Since 0.15.1, `@ptrCast` can infer a byte-equivalent destination slice from a
single-item pointer. Its length covers the same byte count as the pointed-to value.

```zig
const value: u32 = 1;
const bytes: []const u8 = @ptrCast(&value);
```

## Inline assembly

Inline-assembly clobbers are a typed struct value rather than a list of register
name strings in 0.15.1. `zig fmt` can migrate existing syntax.

```zig
return asm volatile ("syscall"
    : [ret] "={rax}" (-> usize),
    : [number] "{rax}" (number),
      [arg1] "{rdi}" (arg1),
    : .{ .rcx = true, .r11 = true });
```
