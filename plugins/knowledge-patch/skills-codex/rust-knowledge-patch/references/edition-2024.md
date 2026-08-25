# Rust 2024 Edition

## Iteration, fallback, and temporary scope

### Boxed-slice iteration (`edition-2024`)

`Box<[T]>::into_iter()` in method-call syntax now consumes the box and yields `T`. In older editions that syntax deliberately resolves through the slice and yields `&T`, even though `Box<[T]>` implements `IntoIterator` everywhere. Use `.iter()` to retain borrowing; the `boxed_slice_into_iter` migration lint can rewrite affected calls.

### Never-type fallback (`edition-2024`)

An unconstrained never-to-any coercion falls back to `!`, not `()`. Generic `f()?` calls and panicking closures that relied on unit need an explicit type. `dependency_on_unit_never_type_fallback` finds unit dependencies, while `never_type_fallback_flowing_into_unsafe` is deny-by-default.

```rust
fn run() -> Result<(), ()> {
    f::<()>()?;
    Ok(())
}
```

### Tail expressions and `if let` scrutinees (`edition-2024`, 1.91.0)

A block tail's temporaries drop at the end of that block, before its local bindings. This can make borrow-guard tails compile, but can invalidate references that depended on extension into an enclosing expression. The `tail_expr_drop_order` lint flags nontrivial destructor cases but cannot rewrite them. Temporaries from `pin!`, `format_args!`, `write!`, and `writeln!` in an `if let` scrutinee likewise use the shorter Edition 2024 scope as of 1.91.0. Bind a value first when a longer lifetime is intentional.

## Opaque capture and patterns

### Return-position `impl Trait` capture (`edition-2024-supplemental`)

Without `use<...>`, a return-position opaque type implicitly captures every in-scope lifetime, in addition to type and const parameters captured in older editions. `impl_trait_overcaptures` can usually insert a precise bound preserving old behavior; argument-position `impl Trait` may first need conversion to a named type parameter.

```rust
fn detached<'a, T>(_: &'a (), value: T) -> impl Sized + use<T> {
    value
}
```

### Explicit pattern prefixes (`edition-2024-supplemental`)

Binding annotations `mut`, `ref`, and `ref mut`, and reference patterns `&` and `&mut`, are permitted only while the pattern prefix is fully explicit. Use `rust_2024_incompatible_pat` to rewrite affected patterns into cross-edition syntax.

```rust
let &[ref first, mut second] = &[(), ()];
```

## Unsafe foreign declarations

### Foreign blocks are explicitly unsafe (`edition-2024-supplemental`)

Declare every foreign block as `unsafe extern`. An imported function or static may be marked `safe` only when its declaration makes every call valid. Unmarked items remain unsafe by default, and automated migration cannot validate signatures.

```rust
use core::ffi::c_void;

unsafe extern "C" {
    pub safe fn sqrt(value: f64) -> f64;
    pub fn free(pointer: *mut c_void);
}
```

## Cargo manifest migration

### Canonical spellings (`edition-2024-supplemental`)

Manifests reject `[project]` and underscore aliases including `default_features`, `crate_type`, `proc_macro`, `dev_dependencies`, and `build_dependencies`. Use `[package]` and hyphenated keys; `cargo fix --edition` updates them.

### Workspace dependency defaults (`edition-2024-supplemental`)

A member dependency with `workspace = true` may set `default-features = false` only when the corresponding entry in `[workspace.dependencies]` also disables defaults. A member-local attempt is an error when the workspace omits the setting or enables defaults.

```toml
[workspace.dependencies]
regex = { version = "1.10.4", default-features = false }
```

## Doctests and formatting

### Combined doctests (`edition-2024-supplemental`)

Rustdoc normally compiles compatible doctests into one binary while running them as separate processes. Add the `standalone_crate` tag when a case depends on generated crate layout, source lines, or type names. Cases such as `compile_fail`, explicit-edition, and crate-attribute examples are already separated.

````rust
//! ```standalone_crate
//! let location = std::panic::Location::caller();
//! assert!(location.line() > 0);
//! ```
````

### Nested include paths (`edition-2024-supplemental`)

Inside documentation loaded with `#[doc = include_str!(...)]`, doctest uses of `include!`, `include_str!`, and `include_bytes!` resolve relative to the Markdown file rather than the Rust source file. There is no automatic path migration.

### Rustfmt style edition (`edition-2024-supplemental`)

Rustfmt defaults its style edition to the parsing edition. Pin `style_edition = "2024"` in `rustfmt.toml`, or pass `--style-edition 2024`, when direct editor runs must match `cargo fmt` independently of the crate edition.
