# Lints & Diagnostics (1.84–1.94)

## `missing_abi` — Warn by Default in 1.86

`extern {}` blocks and `extern fn` without explicit ABI now warn. Fix: add `"C"` explicitly.

```rust
// Before (now warns):
extern "C" {
    fn foo();
}
extern "C" fn bar() {}

// After:
extern "C" {
    fn foo();
}
extern "C" fn bar() {}
```

## `dangling_pointers_from_locals` — Warn by Default in 1.91

Warns when a raw pointer to a local variable escapes the function (dangling after return). The borrow checker doesn't track raw pointers, so this was silently UB.

```rust
// Warns: raw pointer to local will dangle
fn f() -> *const u8 {
    let x = 0u8;
    &x as *const u8  // dangling after return
}

fn g() -> *const u8 {
    let x = 0u8;
    &raw const x    // same warning
}

// Fix: return the value, use Box/static, or redesign the API
```

## `mismatched_lifetime_syntaxes` — Warn by Default in 1.89

Warns when a function input lifetime uses `&` elision but the output type hides that lifetime (e.g. `Iter<T>` instead of `Iter<'_, T>`).

```rust
// Before (now warns):
fn items(scores: &[u8]) -> std::slice::Iter<u8> { scores.iter() }
fn get(v: &Vec<String>) -> std::slice::Iter<String> { v.iter() }

// After:
fn items(scores: &[u8]) -> std::slice::Iter<'_, u8> { scores.iter() }
fn get(v: &Vec<String>) -> std::slice::Iter<'_, String> { v.iter() }
```

## `#[diagnostic::do_not_recommend]` — 1.85

Hint to suppress a blanket impl from appearing in compiler error suggestions. Doesn't change semantics.

```rust
// Without: compiler suggests "implement Foo to satisfy Bar"
// With: that suggestion is suppressed
#[diagnostic::do_not_recommend]
impl<T: Foo> Bar for T {}
```

## Never-Type Lints — Deny by Default in 1.92 (Breaking)

`never_type_fallback_flowing_into_unsafe` and `dependency_on_unit_never_type_fallback` are now deny-by-default. These flag code that will break when `!` (never type) is fully stabilized.

```rust
// These previously compiled but now error:
// - Patterns that fall back from ! to () in unsafe code
// - Code depending on unit fallback behavior for diverging expressions

// To suppress while you fix:
#[allow(never_type_fallback_flowing_into_unsafe)]
#[allow(dependency_on_unit_never_type_fallback)]
fn foo() { ... }
```

**Action:** Fix the flagged code rather than suppressing — these will become hard errors when `!` is fully stabilized.

## `cfg` on `asm!` Lines — 1.93

Individual lines within `asm!`, `global_asm!`, and `naked_asm!` blocks can have `#[cfg(...)]`.

```rust
asm!(
    "nop",
    #[cfg(target_feature = "sse2")]
    "movaps xmm0, xmm0",
    #[cfg(target_feature = "sse2")]
    a = const 123,
);

// Previously required duplicating the entire asm! block for conditional lines
```
