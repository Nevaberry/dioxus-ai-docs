# Integers and Arithmetic

## Midpoint

Exact midpoint calculation without overflow.

```rust
assert_eq!(0u8.midpoint(255), 127);
assert_eq!(1.0_f64.midpoint(3.0), 2.0);
```

## `is_multiple_of`

Check divisibility.

```rust
assert!(15u32.is_multiple_of(5));
assert!(0u32.is_multiple_of(5));  // true
```

## Unbounded Shifts

Return 0 on overflow instead of panicking.

```rust
let x: u32 = 1;
assert_eq!(x.unbounded_shl(40), 0);  // No panic
assert_eq!(x.unbounded_shr(40), 0);
```

## Cast Methods

Explicit signed/unsigned reinterpretation.

```rust
let signed: i32 = -5;
let unsigned: u32 = signed.cast_unsigned();
let back: i32 = unsigned.cast_signed();
assert_eq!(back, -5);
```

## Signed-Subtraction from Unsigned

Subtract signed from unsigned with overflow control.

```rust
let x: u32 = 10;

x.checked_sub_signed(3)    // Some(7)
x.checked_sub_signed(-5)   // Some(15)
x.checked_sub_signed(20)   // None (underflow)

x.wrapping_sub_signed(20)  // Wraps
x.saturating_sub_signed(20) // Clamps to 0
x.overflowing_sub_signed(3) // (7, false)
```

## Strict Arithmetic

Panic on overflow in ALL builds (debug and release).

```rust
let x: u32 = 200;
x.strict_add(50);   // OK: 250
x.strict_sub(50);   // OK: 150
// x.strict_add(u32::MAX);  // Panics!

// Also: strict_mul, strict_div, strict_rem, strict_neg, strict_shl, strict_shr, strict_pow
```

## Carrying/Borrowing Arithmetic

Extended precision with carry/borrow propagation.

```rust
// carrying_add: returns (sum, carry)
let (sum, carry) = 250u8.carrying_add(10, false);
assert_eq!((sum, carry), (4, true));  // 260 overflows

// Chain for multi-word arithmetic
let (low, carry) = a_low.carrying_add(b_low, false);
let (high, _) = a_high.carrying_add(b_high, carry);

// borrowing_sub: returns (diff, borrow)
let (diff, borrow) = 5u8.borrowing_sub(10, false);
assert_eq!((diff, borrow), (251, true));

// carrying_mul: wide multiply
let (low, high) = 200u8.carrying_mul(200, 0);
```

## Unchecked Operations

UB if preconditions violated - for performance-critical code only.

```rust
// unchecked_neg: UB if result overflows (on MIN)
let negated = unsafe { (-5i32).unchecked_neg() };

// unchecked_shl/shr: UB if shift >= bit width
let shifted = unsafe { 1u32.unchecked_shl(4) };
```

## `NonZero::div_ceil`

Ceiling division for non-zero unsigned integers.

```rust
use std::num::NonZeroU32;

let n = NonZeroU32::new(10).unwrap();
let d = NonZeroU32::new(3).unwrap();
assert_eq!(n.div_ceil(d), 4);  // 10/3 = 3.33... → 4
```
