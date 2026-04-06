---
name: rust-knowledge-patch
description: "Rust changes since training cutoff (latest: 1.94.0) \u2014 Rust 2024 Edition, async closures, trait upcasting, new std APIs, cargo resolver v3. Load before working with Rust."
version: "1.94.0"
license: MIT
metadata:
  author: Nevaberry
---

# Rust Knowledge Patch

Covers Rust 1.84–1.94 (2025-01-09 through 2026-03-05). Claude Opus 4.6 knows Rust through 1.83 and the 2021 Edition. It is **unaware** of the Rust 2024 Edition and any of the features below.

## Index

| Topic | Reference | Key features |
|---|---|---|
| Rust 2024 Edition | [references/rust-2024-edition.md](references/rust-2024-edition.md) | Edition migration, breaking changes, let chains |
| Language features | [references/language-features.md](references/language-features.md) | Async closures, trait upcasting, naked functions, cfg booleans |
| Collections & iterators | [references/collections.md](references/collections.md) | `extract_if`, `as_chunks`, `array_windows`, slice splits |
| Numeric methods | [references/numerics.md](references/numerics.md) | `isqrt`, `midpoint`, `strict_*`, `sub_signed`, const floats |
| Memory & unsafe | [references/memory.md](references/memory.md) | Provenance APIs, `NonNull`, `MaybeUninit`, smart ptr alloc |
| Std library additions | [references/std-additions.md](references/std-additions.md) | Pipes, file locking, sync, paths, `Duration`, `fmt::from_fn` |
| Cargo & toolchain | [references/cargo.md](references/cargo.md) | Resolver v3, `publish --workspace`, LLD linker, TOML 1.1 |
| Lints & diagnostics | [references/lints.md](references/lints.md) | New default warnings, never-type lints, diagnostic hints |

---

## Rust 2024 Edition — Breaking Changes (inline)

Enable with `edition = "2024"` in `Cargo.toml`. Migrate with `cargo fix --edition`.

| Change | Before (2021) | After (2024) |
|---|---|---|
| `extern` blocks | `extern "C" { fn foo(); }` | `unsafe extern "C" { fn foo(); }` |
| Link attributes | `#[no_mangle]` | `#[unsafe(no_mangle)]` |
| `unsafe fn` bodies | implicit unsafe inside | require explicit `unsafe { }` |
| `static mut` refs | warned | hard error → use `&raw const`/`&raw mut` |
| `set_var`/`remove_var` | safe | now `unsafe` |
| `gen` keyword | valid identifier | reserved |
| `impl Trait` lifetime capture | opt-in | captures all in-scope lifetimes by default |
| `Future`/`IntoFuture` in prelude | not in prelude | added (may cause name conflicts) |

```rust
// 2021 → 2024 migration examples

// extern blocks
unsafe extern "C" {
    fn foo();
    safe fn bar();  // opt-in safe: callable without unsafe
}

// attributes on linked items
#[unsafe(no_mangle)]
pub extern "C" fn my_fn() {}

// unsafe fn bodies
unsafe fn helper() {
    unsafe { some_unsafe_op(); }  // now required
}

// static mut: use raw refs instead
static mut GLOBAL: u32 = 0;
let r = &raw const GLOBAL;  // safe in 2024, was safe since 1.84

// impl Trait lifetime restriction
fn foo<'a>(x: &'a str) -> impl Display + use<'a> { x }  // restrict captures
```

---

## Let Chains — 1.88 (Rust 2024 Edition only)

Chain `let` bindings with `&&` in `if`/`while`. Earlier bindings are available in later conditions.

```rust
if let Channel::Stable(v) = release_info()
    && let Semver { major, minor, .. } = v
    && major == 1
    && minor == 88
{
    println!("let chains stabilized here");
}

while let Some(x) = iter.next() && x < 10 {
    process(x);
}
```

---

## Async Closures — 1.85

`async || {}` can borrow captures across `.await`. Unlike `|| async {}`, the inner future holds a borrow into the closure's environment. New traits: `AsyncFn`, `AsyncFnMut`, `AsyncFnOnce`.

```rust
let mut vec: Vec<String> = vec![];
let closure = async || {
    vec.push(ready(String::from("")).await);  // borrows vec across await point
};

// Higher-ranked async bounds — not expressible with Fn + Future:
async fn call_it(_: impl for<'a> AsyncFn(&'a u8)) {}
```

---

## Trait Upcasting — 1.86

Coerce `&dyn Trait` to `&dyn Supertrait` (or any pointer wrapper). Previously required manual `as_supertrait()` workarounds.

```rust
trait Trait: Supertrait {}
trait Supertrait {}

fn upcast(x: &dyn Trait) -> &dyn Supertrait { x }
// Also: Arc<dyn Trait> -> Arc<dyn Supertrait>

// Downcasting without external crates:
use std::any::Any;
trait MyAny: Any {}
impl dyn MyAny {
    fn downcast_ref<T: 'static>(&self) -> Option<&T> {
        (self as &dyn Any).downcast_ref()
    }
}
```

---

## Quick Method Reference

### New in 1.84
| Method | Description |
|---|---|
| `n.isqrt()` / `n.checked_isqrt()` | Integer square root (floor); checked returns `None` for negative |
| `ptr::dangling::<T>()` | Non-null, well-aligned dangling pointer |
| `ptr.addr()` / `.with_addr(a)` / `.map_addr(f)` | Pointer provenance-preserving address ops |
| `ptr.expose_provenance()` / `ptr::with_exposed_provenance(a)` | Round-trip through integer with provenance |
| `ptr::without_provenance(a)` | Pointer with no provenance (sentinel values) |
| `&raw const *p` | Now safe (was unsafe) |

### New in 1.85–1.86
| Method | Description |
|---|---|
| `a.midpoint(b)` | Overflow-safe `(a+b)/2` for floats and unsigned ints |
| `v.pop_if(\|x\| ...)` | Pop last element if predicate holds |
| `v.get_disjoint_mut([i, j])` | Multiple `&mut` into slice/`HashMap` simultaneously |
| `lock.wait()` | Block until `OnceLock`/`Once` is initialized |

### New in 1.87–1.88
| Method | Description |
|---|---|
| `std::io::pipe()` | Returns `(PipeReader, PipeWriter)` |
| `v.extract_if(.., \|x\| ...)` | Drain matching elements (lazy iterator) |
| `s.split_off(n)` / `split_off_first()` / `split_off_last()` | Split slice, return tuple |
| `os_str.display()` | Lossily display `OsStr` / `OsString` |
| `n.unbounded_shl(k)` / `unbounded_shr(k)` | Shift returning 0 instead of panic when `k ≥ bits` |
| `s.as_chunks::<N>()` / `as_rchunks::<N>()` | Fixed-size array chunks with remainder |
| `map.extract_if(\|k,v\| ...)` | `HashMap`/`HashSet` drain by predicate |
| `cell.update(\|x\| ...)` | Update `Cell<T>` in place, return new value |

### New in 1.89–1.91
| Method | Description |
|---|---|
| `f.lock()` / `f.try_lock()` / `f.unlock()` | Advisory file locking (no `fs2` needed) |
| `r.flatten()` | `Result<Result<T,E>,E>` → `Result<T,E>` |
| `NonNull::from_ref(&x)` / `from_mut(&mut x)` | Safe `NonNull` from references |
| `x.checked_sub_signed(n)` etc. | Subtract signed from unsigned (`checked_`, `wrapping_`, `saturating_`, `overflowing_`) |
| `n.strict_add(m)` etc. | Panic on overflow in debug AND release |
| `s.ceil_char_boundary(i)` / `floor_char_boundary(i)` | Nearest valid UTF-8 boundary |
| `Path::file_prefix()` | Stem with ALL extensions stripped |
| `p.add_extension("gz")` | Append extension (unlike `set_extension` which replaces) |
| `Duration::from_mins(n)` / `from_hours(n)` | Convenience constructors |
| `Path == "/some/str"` | `PartialEq<str>` / `PartialEq<String>` now implemented |

### New in 1.92–1.94
| Method | Description |
|---|---|
| `RwLockWriteGuard::downgrade(guard)` | Atomically write→read lock downgrade |
| `Box::new_zeroed()` / `new_zeroed_slice(n)` | Zero-initialized allocation (also `Rc`, `Arc`) |
| `s.into_raw_parts()` / `v.into_raw_parts()` | Decompose `String`/`Vec` to `(ptr, len, cap)` |
| `Duration::from_nanos_u128(n)` | Like `from_nanos` but accepts `u128` |
| `s.as_chunks::<N>()` | (also `as_array::<N>()` in 1.93: slice → fixed-size array ref) |
| `fmt::from_fn(\|f\| ...)` | `Display` value from closure, no new type needed |
| `dq.pop_front_if(\|x\| ...)` / `pop_back_if(...)` | Conditional pop from `VecDeque` |
| `cell.get()` on `LazyCell`/`LazyLock` | `Option<&T>` without forcing init |
| `LazyCell::force_mut(&mut cell)` | Force init, return `&mut T` |
| `iter.next_if_map(\|x\| ...)` | Peek + transform; advance only if `Some` |
| `v.element_offset(&v[i])` | Index of element by reference |
| `f64::consts::EULER_GAMMA` / `GOLDEN_RATIO` | New float constants |
