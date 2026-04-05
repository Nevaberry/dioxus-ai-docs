# Language Features (1.85–1.94)

## Async Closures (1.85)

`async || {}` closures with `AsyncFn`, `AsyncFnMut`, `AsyncFnOnce` traits:

```rust
// Async closure can borrow from its captures (unlike `|| async {}`)
let mut data = vec![];
let closure = async || {
    data.push(String::from("hello"));
};
closure().await;

// AsyncFn trait bounds work with higher-ranked lifetimes
async fn call_with_ref(f: impl for<'a> AsyncFn(&'a str)) {
    f("hello").await;
}
```

Key difference from `|| async {}`: async closures can borrow from their environment across `.await` points.

## Trait Upcasting (1.86)

Trait objects can be upcast to supertrait objects via implicit coercion:

```rust
trait Supertrait {}
trait Trait: Supertrait {}

fn upcast(x: &dyn Trait) -> &dyn Supertrait {
    x // implicit coercion, no cast needed
}
// Works with any pointer type: Arc<dyn Trait> -> Arc<dyn Supertrait>
```

Especially useful with `Any` — add `Any` as a supertrait, then upcast to `dyn Any` for downcasting.

## `#[diagnostic::do_not_recommend]` (1.85)

Hint to compiler to hide a trait impl from error diagnostics:

```rust
#[diagnostic::do_not_recommend]
impl<T: Foo> Bar for T {} // won't suggest implementing Foo when Bar is missing
```

## Precise Capturing `use<...>` in Trait Definitions (1.87)

The `+ use<...>` syntax now works in trait method return types:

```rust
trait Foo {
    fn method<'a>(&'a self) -> impl Sized + use<Self>; // captures Self but not 'a
}
```

## Safe `#[target_feature]` (1.86) + Safe `std::arch` Intrinsics (1.87)

Safe functions can use `#[target_feature]`. They can only be called safely from other `#[target_feature]` functions with the same feature:

```rust
#[target_feature(enable = "avx2")]
fn do_avx2_work() { /* safe, no unsafe needed */
}

#[target_feature(enable = "avx2")]
fn caller() {
    do_avx2_work();
} // safe call

fn generic_caller() {
    if is_x86_feature_detected!("avx2") {
        unsafe {
            do_avx2_work();
        } // requires unsafe from non-target_feature context
    }
}
```

Since 1.87, most `std::arch` intrinsics (that don't take pointer args) are safe within `#[target_feature]` functions:

```rust
#[target_feature(enable = "avx2")]
fn sum_avx2(a: __m256i, b: __m256i) -> __m256i {
    _mm256_add_epi32(a, b) // safe call, no unsafe needed
}
```

## Let Chains (1.88, 2024 Edition Only)

Chain `let` patterns with `&&` in `if`/`while` conditions:

```rust
if let Some(user) = get_user()
    && let Role::Admin(level) = user.role
    && level > 3
{
    grant_access(user);
}
```

Bindings from earlier `let`s are available in later parts of the chain and the body. Requires 2024 edition.

## Naked Functions (1.88)

`#[unsafe(naked)]` with `naked_asm!` — no compiler-generated prologue/epilogue:

```rust
#[unsafe(naked)]
pub unsafe extern "sysv64" fn wrapping_add(a: u64, b: u64) -> u64 {
    core::arch::naked_asm!(
        "lea rax, [rdi + rsi]",
        "ret"
    );
}
```

More ergonomic than `global_asm!` for defining individual assembly functions.

## `asm!` Label Operand (1.87)

Inline assembly can jump to Rust code blocks:

```rust
unsafe {
    asm!(
        "jmp {}",
        label {
            println!("Jumped from asm!");
        }
    );
}
```

The label block must return `()` or `!`. Using output and label operands together is still unstable.

## Const Generic Inference with `_` (1.89)

Use `_` as a const generic argument to infer the value:

```rust
pub fn all_false<const LEN: usize>() -> [bool; LEN] {
    [false; _] // inferred as LEN
}
```

Not allowed in signatures or const item types.

## `#[repr(u128)]` / `#[repr(i128)]` (1.89)

Enums can use 128-bit discriminant representations:

```rust
#[repr(u128)]
enum BigEnum {
    A = 1,
    B = u128::MAX,
}
```

## `cfg(true)` / `cfg(false)` (1.88)

Boolean literals in cfg predicates — clearer replacement for `cfg(all())` / `cfg(any())`.

## `dangerous_implicit_autorefs` Lint (1.88–1.89)

Warn-by-default in 1.88, deny-by-default in 1.89. Implicit autoref of raw pointer dereferences is now a hard error.

## `&raw` on Union Fields in Safe Code (1.92)

`&raw const` and `&raw mut` on union fields no longer requires `unsafe`:

```rust
union MyUnion { f1: u32, f2: f32 }
let u = MyUnion { f1: 42 };
let ptr: *const u32 = &raw const u.f1; // safe
```
