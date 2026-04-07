# Language Features (1.84–1.94)

## Async Closures — 1.85

`async || {}` can borrow captures across `.await`. Unlike `|| async {}`, the returned future holds a borrow into the closure's environment. New traits in prelude: `AsyncFn`, `AsyncFnMut`, `AsyncFnOnce`.

```rust
let mut vec: Vec<String> = vec![];
let closure = async || {
    vec.push(ready(String::from("")).await);  // borrows vec across await point
};

// Higher-ranked async bounds — not expressible with Fn + Future:
async fn call_it(_: impl for<'a> AsyncFn(&'a u8)) {}

// Accepting async closures in function signatures:
async fn run<F: AsyncFn() -> String>(f: F) {
    println!("{}", f().await);
}
```

## `#[diagnostic::do_not_recommend]` — 1.85

Hint to suppress a blanket impl from appearing in compiler error messages. For library authors.

```rust
#[diagnostic::do_not_recommend]
impl<T: Foo> Bar for T {}
// Compiler won't say "implement Foo to satisfy Bar" in errors
```

## Trait Upcasting — 1.86

Coerce `dyn Trait` to `dyn Supertrait`. Works for `&`, `&mut`, `Box`, `Arc`, `Rc`, `*const`, `*mut`.

```rust
trait Trait: Supertrait {}
trait Supertrait {}

fn upcast(x: &dyn Trait) -> &dyn Supertrait { x }
fn upcast_box(x: Box<dyn Trait>) -> Box<dyn Supertrait> { x }

// Downcasting without external crates:
use std::any::Any;
trait MyAny: Any {}
impl dyn MyAny {
    fn downcast_ref<T: 'static>(&self) -> Option<&T> {
        (self as &dyn Any).downcast_ref()
    }
    fn downcast_mut<T: 'static>(&mut self) -> Option<&mut T> {
        (self as &mut dyn Any).downcast_mut()
    }
}
```

## Safe `#[target_feature]` Functions — 1.86

Non-`unsafe` functions can carry `#[target_feature]`. Safe to call from functions with the same feature; requires `unsafe {}` from general code.

```rust
#[target_feature(enable = "avx2")]
fn avx2_work() { /* safe, no unsafe fn */
}

#[target_feature(enable = "avx2")]
fn caller() {
    avx2_work();
} // safe: same feature context

fn dynamic_caller() {
    if is_x86_feature_detected!("avx2") {
        unsafe {
            avx2_work();
        } // still requires unsafe
    }
}
```

## Safe `std::arch` Intrinsics — 1.87

`std::arch` intrinsics that only need a target feature are now safe inside `#[target_feature]` functions with that feature enabled.

```rust
#[target_feature(enable = "avx2")]
fn process() {
    let a = _mm256_setzero_si256(); // safe here, no unsafe block needed
    let b = _mm256_set1_epi32(1);
    let c = _mm256_add_epi32(a, b);
}
```

## Naked Functions — 1.88

`#[unsafe(naked)]` functions have no compiler-generated prologue/epilogue. Body must be a single `naked_asm!` call.

```rust
use core::arch::naked_asm;

#[unsafe(naked)]
pub unsafe extern "sysv64" fn wrapping_add(a: u64, b: u64) -> u64 {
    naked_asm!("lea rax, [rdi + rsi]", "ret");
}

// Useful for: OS/hypervisor stubs, FFI thunks, custom calling conventions
```

## `cfg(true)` / `cfg(false)` — 1.88

Boolean literals in `cfg`/`cfg_attr`/`cfg!`. Clearer alternatives to `cfg(all())` and `cfg(any())`.

```rust
#[cfg(false)]
fn dead_code() {} // never compiled

#[cfg(true)]
fn always_compiled() {}

#[cfg_attr(true, derive(Debug))]
struct Foo;

// In macros:
let always = cfg!(true);
```

## `_` in Const Generic Arguments (Body Context) — 1.89

Infer const generic values with `_` inside function/const bodies. Not allowed in signatures.

```rust
pub fn all_false<const LEN: usize>() -> [bool; LEN] {
    [false; _] // compiler infers LEN from return type
}

// Not allowed:
// fn foo() -> [bool; _]  // error: in signatures
```

## Closure Capture Changes with Patterns — 1.94

Closures that pattern-match captured variables may now capture only sub-fields by move (others by borrow). Can cause new borrow errors or changed `Drop` order.

```rust
let s = (String::new(), String::new());
// Previously: move captured all of `s`
// Now: may only capture `s.0` by move, `s.1` by borrow
let f = move || println!("{}", s.0);
// If this causes issues, capture explicitly:
let s0 = s.0;
let f = move || println!("{}", s0);
```
