---
name: rust-knowledge-patch
description: "Rust changes since training cutoff (latest: 1.94.0) — 2024 edition, trait upcasting, async closures, let chains, naked functions, new std APIs. Load before working with Rust."
license: MIT
metadata:
  author: Nevaberry
  version: "1.94.0"
---

# Rust 1.85–1.94 Knowledge Patch

Claude's baseline knowledge covers Rust through ~1.84. This skill provides features from 1.85 (February 2025) onwards.

## Quick Reference

### Rust 2024 Edition (1.85+)

| Change | Migration |
|--------|-----------|
| `unsafe extern` blocks required | Add `unsafe` before `extern "C"` |
| Unsafe attributes: `no_mangle`, `export_name` | Wrap in `unsafe(...)` |
| `unsafe_op_in_unsafe_fn` warns | Add `unsafe {}` blocks inside `unsafe fn` |
| `static mut` refs denied | Use `addr_of!()` / `addr_of_mut!()` |
| `set_var`/`remove_var` are unsafe | Wrap in `unsafe {}` |
| `gen` is reserved keyword | Rename identifiers |
| `expr` fragment matches `const {}`, `_` | Use `expr_2021` for old behavior |
| Prelude: `Future`, `IntoFuture`, `AsyncFn*` | May shadow imports |
| `Box<[T]>` iterates by value | Check `into_iter()` usage |
| MSRV-aware resolver default | Cargo respects `rust-version` |

See `references/edition-2024.md` for full migration guide with code examples.

### Key Language Features

| Feature | Since | Example |
|---------|-------|---------|
| Async closures | 1.85 | `async \|\| { ... }` with `AsyncFn` bounds |
| Trait upcasting | 1.86 | `&dyn Sub` → `&dyn Super` implicit coercion |
| Let chains | 1.88 | `if let Some(x) = a && x > 0 { }` (2024 ed.) |
| Naked functions | 1.88 | `#[unsafe(naked)]` + `naked_asm!` |
| Const generic `_` | 1.89 | `[false; _]` infers const from context |
| `#[repr(u128)]` | 1.89 | 128-bit enum discriminants |
| Safe `#[target_feature]` | 1.86 | No `unsafe` needed within same feature |
| `use<...>` in traits | 1.87 | `-> impl Sized + use<Self>` |

See `references/language-features.md` for async closures, trait upcasting, let chains, naked functions, inline asm.

### Collections & Iterators

| API | Since | Purpose |
|-----|-------|---------|
| `get_disjoint_mut` | 1.86 | Multiple `&mut` to distinct elements |
| `Vec::pop_if` | 1.86 | Conditional pop |
| `Vec::extract_if` | 1.87 | Drain + filter (replaces `drain_filter`) |
| `VecDeque::pop_front_if` | 1.93 | Conditional front/back pop |
| `HashMap::extract_if` | 1.88 | Drain matching entries |
| `array_windows` | 1.94 | Fixed-size sliding windows on slices |
| `as_chunks::<N>()` | 1.88 | View slice as array chunks |
| `as_array::<N>()` | 1.93 | Slice → fixed-size array ref |
| Tuple `collect()` | 1.85 | Fan out into multiple collections |
| `core::iter::chain` | 1.91 | Free function `chain(a, b)` |
| `core::array::repeat` | 1.91 | `[T; N]` from `Clone` (non-`Copy`) |

See `references/collections.md` for usage examples and signatures.

### I/O, Sync & Concurrency

| API | Since | Purpose |
|-----|-------|---------|
| `std::io::pipe()` | 1.87 | Anonymous pipes, integrates with `Command` |
| `File::lock` / `try_lock` | 1.89 | Cross-platform advisory file locking |
| `OnceLock::wait()` | 1.86 | Block until initialized |
| `RwLockWriteGuard::downgrade` | 1.92 | Write → read lock without gap |
| `LazyCell`/`LazyLock` `DerefMut` | 1.89 | Mutate lazy values |
| `LazyCell::get()` | 1.94 | Check initialized without forcing |

See `references/io-sync.md` for full examples.

### Formatting & Strings

| API | Since | Purpose |
|-----|-------|---------|
| `fmt::from_fn` | 1.93 | `Display` from closure |
| `format_args!()` in `let` | 1.89 | Storable in variables |
| `str::from_utf8()` inherent | 1.87 | `s.from_utf8()` method |
| `OsStr::display()` | 1.87 | Lossy display for OS strings |
| `str::ceil_char_boundary` | 1.91 | Nearest valid UTF-8 boundary |

### Numeric & Primitive APIs

| API | Since | Purpose |
|-----|-------|---------|
| `cast_signed()` / `cast_unsigned()` | 1.87 | Type-safe sign casting |
| `is_multiple_of()` | 1.87 | Cleaner than `x % n == 0` |
| `strict_add/sub/mul/...` | 1.91 | Always-panic on overflow |
| `carrying_add` / `borrowing_sub` | 1.91 | Extended-precision arithmetic |
| `midpoint(a, b)` | 1.85 | Average without overflow |
| `unbounded_shl/shr` | 1.87 | Shift saturating to 0/sign |
| `Result::flatten()` | 1.89 | Like `Option::flatten` |

See `references/new-apis.md` for Path, Memory, Cell, and other stabilized APIs.

### Allocation & Memory

| API | Since | Purpose |
|-----|-------|---------|
| `Box::new_zeroed()` | 1.92 | Zero-initialized `MaybeUninit` alloc |
| `Vec::into_raw_parts` | 1.93 | Decompose vec into `(ptr, len, cap)` |
| `MaybeUninit::assume_init_ref` | 1.93 | Safe(r) access to initialized values |
| `NonNull::from_ref/from_mut` | 1.89 | Safe constructors from references |
| `&raw` on union fields (safe) | 1.92 | No `unsafe` for raw pointer to union field |

### Cargo

| Feature | Since | Detail |
|---------|-------|--------|
| `build.build-dir` | 1.91 | Separate dir for build artifacts |
| Config `include` | 1.94 | Include other `.cargo/config.toml` files |

## Reference Files

| File | Contents |
|------|----------|
| `edition-2024.md` | Full 2024 edition migration guide |
| `language-features.md` | Async closures, trait upcasting, let chains, naked fns, asm, target_feature |
| `collections.md` | get_disjoint_mut, extract_if, pop_if, array_windows, as_chunks, tuple collect |
| `io-sync.md` | Pipes, file locking, OnceLock, RwLock downgrade, LazyCell/LazyLock |
| `new-apis.md` | Numeric, Path, formatting, Cell, MaybeUninit, other stabilized APIs |

## Critical Examples

### Let Chains (2024 Edition)

```rust
if let Some(user) = get_user()
    && let Role::Admin(level) = user.role
    && level > 3
{
    grant_access(user);
}
```

### Trait Upcasting

```rust
trait Base: std::any::Any {}
fn downcast(x: &dyn Base) -> Option<&ConcreteType> {
    let any: &dyn std::any::Any = x; // implicit upcast
    any.downcast_ref()
}
```

### Multiple Mutable References

```rust
let v = &mut [1, 2, 3, 4, 5];
let [a, c] = v.get_disjoint_mut([0, 2]).unwrap();
*a += *c;
```

### Anonymous Pipes with Command

```rust
let (mut recv, send) = std::io::pipe()?;
let mut child = Command::new("cmd")
    .stdout(send.try_clone()?)
    .stderr(send)
    .spawn()?;
let mut output = Vec::new();
recv.read_to_end(&mut output)?;
child.wait()?;
```

### Display from Closure

```rust
fn format_list(items: &[i32]) -> impl std::fmt::Display + '_ {
    std::fmt::from_fn(move |f| {
        for (i, item) in items.iter().enumerate() {
            if i > 0 { write!(f, ", ")?; }
            write!(f, "{item}")?;
        }
        Ok(())
    })
}
```

### Array Windows

```rust
fn has_palindrome_pair(s: &str) -> bool {
    s.as_bytes()
        .array_windows()
        .any(|[a1, b1, b2, a2]| (a1 != b1) && (a1 == a2) && (b1 == b2))
}
```
