# Numeric Methods (1.84–1.94)

## `isqrt` / `checked_isqrt` — 1.84

Integer square root (floor). Available on all integer types.

```rust
assert_eq!(16u32.isqrt(), 4);
assert_eq!(17u32.isqrt(), 4); // floors
assert_eq!(0u32.isqrt(), 0);

// Signed: checked variant returns None for negative
assert_eq!(16i32.checked_isqrt(), Some(4));
assert_eq!((-4i32).checked_isqrt(), None);
```

## `midpoint` — 1.85

Overflow-safe `(a + b) / 2` for floats and unsigned integers.

```rust
// Integers: rounds toward negative infinity
assert_eq!(250u8.midpoint(10), 130); // no overflow
assert_eq!(3u32.midpoint(4), 3); // (3+4)/2 = 3 (floors)

// Floats:
assert_eq!(1.0f32.midpoint(2.0), 1.5);
assert_eq!(f64::MAX.midpoint(f64::MAX), f64::MAX); // no overflow
```

## `unbounded_shl` / `unbounded_shr` — 1.87

Shifts that return 0 (or all-bits for signed `>>`) when shift amount ≥ bit width, instead of panicking or UB.

```rust
assert_eq!(1u32.unbounded_shl(31), 0x8000_0000);
assert_eq!(1u32.unbounded_shl(32), 0); // instead of panic
assert_eq!(1u32.unbounded_shl(99), 0);

assert_eq!(0x8000_0000u32.unbounded_shr(31), 1);
assert_eq!(0x8000_0000u32.unbounded_shr(32), 0);

// Signed right shift: fills with sign bit, then 0 when ≥ bits
assert_eq!((-1i32).unbounded_shr(31), -1); // arithmetic shift
assert_eq!((-1i32).unbounded_shr(32), 0); // beyond: returns 0 for >>
```

## `u{n}::*_sub_signed` — 1.90

Subtract a signed value from an unsigned integer with the full arithmetic family.

```rust
let x: u32 = 100;

assert_eq!(x.checked_sub_signed(-5), Some(105)); // negative rhs adds
assert_eq!(x.checked_sub_signed(200), None); // would underflow

assert_eq!(x.wrapping_sub_signed(-5), 105u32);
assert_eq!(x.wrapping_sub_signed(200), x.wrapping_sub(200));

assert_eq!(x.saturating_sub_signed(200), 0u32);
assert_eq!(x.saturating_sub_signed(-5), 105u32);

let (result, overflowed) = x.overflowing_sub_signed(-5);
// (105, false)
```

## `strict_*` Arithmetic — 1.91

Panic on overflow in **both debug and release** builds. Unlike `checked_*` (returns `None`), `wrapping_*` (wraps), or `saturating_*`.

```rust
// Panics on overflow in release too:
100u32.strict_add(200)
100i32.strict_sub(200)
100u32.strict_mul(200)
100u32.strict_div(0)     // panics on divide-by-zero too
100u32.strict_rem(0)
(-100i32).strict_neg()   // panics on i32::MIN.strict_neg()
2u32.strict_pow(31)
1u8.strict_shl(8)
1u8.strict_shr(8)

// Cross-type variants:
100i32.strict_add_unsigned(200u32)
100i32.strict_sub_unsigned(200u32)
(-100i32).strict_abs()
100u32.strict_add_signed(-200i32)
100u32.strict_sub_signed(200i32)
```

## Const Float Rounding — 1.90

`f32`/`f64` rounding methods usable in `const` contexts.

```rust
const FLOOR: f32 = 1.7f32.floor(); // 1.0
const CEIL: f64 = 1.2f64.ceil(); // 2.0
const TRUNC: f32 = (-1.7f32).trunc(); // -1.0
const FRACT: f64 = 1.7f64.fract(); // 0.7
const ROUND: f32 = 1.5f32.round(); // 2.0
const ROUND_TIES: f64 = 0.5f64.round_ties_even(); // 0.0
```

## Float Constants — 1.94

```rust
use std::f64::consts::{EULER_GAMMA, GOLDEN_RATIO};
// EULER_GAMMA  ≈ 0.5772156649015329
// GOLDEN_RATIO ≈ 1.618033988749895

use std::f32::consts::{EULER_GAMMA, GOLDEN_RATIO};
```
