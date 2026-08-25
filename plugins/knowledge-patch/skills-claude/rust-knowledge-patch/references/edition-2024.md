# Rust 2024 Edition

This reference consolidates the `edition-2024` and
`edition-2024-supplemental` batches, plus edition-specific changes from
`1.85.0`, `1.88.0`, and `1.91.0`.

## Migration workflow and blind spots

The edition is selected with `edition = "2024"` in `Cargo.toml`. Run
`cargo fix --edition`; it is driven by the `rust-2024-compatibility` lint
group. Individual migration lints can be enabled with `#![warn(...)]` while a
crate remains on edition 2021.

`cargo fix` has two important blind spots:

- Macro bodies use the defining crate's edition. An exported `macro_rules!`
  macro never invoked in its own crate is not exercised by migration lints and
  may break callers after the bump—for example, one expanding `let dyn = 1;` or
  relying on `$x:pat` not matching `A | B`. Test exported macros inside the
  defining crate before migrating.
- Doctests are not edited. Run `cargo test` after the edition bump and pin an
  example with an `edition2018` code-fence tag if it cannot yet migrate.

Individual Cargo targets may override the package edition, allowing staged
migration:

```toml
[[bin]]
name = "my-binary"
edition = "2018"
```

`cargo fix --edition` defaults to `--all-targets`; use its target-selection
flags with per-target editions. Trying a future edition before stabilization
requires `cargo-features = ["edition20xx"]` before `[package]` and nightly.

## Unsafe boundaries

### Foreign blocks and items

Foreign blocks require `unsafe extern`. Items inside may be `safe` or
`unsafe`; an unqualified item defaults to unsafe. The item qualifiers work in
all editions since 1.82.

```rust
unsafe extern "C" {
    pub safe fn sqrt(x: f64) -> f64;
    pub unsafe fn strlen(p: *const std::ffi::c_char) -> usize;
    pub fn free(p: *mut core::ffi::c_void);
    pub safe static IMPORTANT_BYTES: [u8; 256];
}
```

Migration lint: `missing_unsafe_on_extern`.

### Unsafe attributes

`no_mangle`, `export_name`, and `link_section` must use `unsafe(...)` because
they can break linking even on otherwise safe code.

```rust
// SAFETY: no other global function uses this name.
#[unsafe(no_mangle)]
pub fn example() {}

#[unsafe(export_name = "loop")]
fn arduino_loop() {}
```

Migration lint: `unsafe_attr_outside_unsafe`.

### Unsafe operations inside unsafe functions

An `unsafe fn` body is not implicitly an unsafe block. Put each unsafe
operation in an explicit `unsafe { ... }`; `unsafe_op_in_unsafe_fn` warns by
default.

```rust
unsafe fn get_unchecked<T>(x: &[T], i: usize) -> &T {
    unsafe { x.get_unchecked(i) }
}
```

### Environment mutation

`std::env::set_var`, `std::env::remove_var`, and deprecated
`CommandExt::before_exec` are unsafe functions in edition 2024. Environment
mutation is unsound if another thread may be running; there is no general safe
replacement, so audit rather than blindly wrap each call.

```rust
// SAFETY: this point in startup is single-threaded.
unsafe { std::env::set_var("FOO", "123") };
```

Migration lint: `deprecated_safe_2024`.

### References to mutable statics

`static_mut_refs` is deny-by-default. It covers explicit and implicit
references, including `println!("{NUMS:?}")` and `NUMS.len()`. Prefer an
atomic, `Mutex<T>`, `OnceLock`/`LazyLock`, or a `Sync` wrapper around
`UnsafeCell`; where a mutable static is unavoidable, form `&raw const` or
`&raw mut` instead of first creating `&mut STATE as *mut _`. There is no
automatic migration.

```rust
static mut STATE: GlobalState = GlobalState::new();
unsafe { example_ffi(&raw mut STATE) };
```

## Opaque-type capture

Return-position `impl Trait` in edition 2024 implicitly captures every
in-scope generic parameter, including lifetimes. This matches RPITIT and
`async fn`; earlier bare functions and inherent methods captured a lifetime
only when it appeared syntactically in the bounds.

```rust
fn f_implicit(_: &()) -> impl Sized {}
// Edition 2021: equivalent to `impl Sized + use<>`.
// Edition 2024: equivalent to `impl Sized + use<'_>`.
```

The all-edition `use<...>` bound states the capture set, and `use<>` captures
nothing:

```rust
fn capture<'a, T>(x: &'a (), y: T) -> impl Sized + use<'a, T> { (x, y) }
fn no_capture<'a>(_: &'a ()) -> impl Sized + use<> {}
```

In-scope parameters include outer-impl generics, `for<'a>` binder lifetimes,
and the anonymous type parameter created by argument-position `impl Trait`.
That anonymous parameter is the case the migration lint cannot rewrite: name it
before putting it in `use<...>`.

Replace the `Captures<(&'a (), T)>` trick and the outlives trick
(`impl Sized + 'a` plus a gratuitous `T: 'a`) with `use<'a, T>` in any edition,
or rely on implicit capture in edition 2024. Migration lint:
`impl_trait_overcaptures`.

## Temporary scopes and drop order

### `if let` scrutinees

Scrutinee temporaries now drop when the then-block ends or before entering
`else`, rather than after the entire `if let`. This can release an `RwLock`
read guard before the else branch tries to write.

To preserve the old lifetime, rewrite to `match`, whose scrutinee temporary
lives through the expression. The `if_let_rescope` migration lint makes this
rewrite, so review it: preserving old semantics may preserve an existing
deadlock.

From `1.91.0`, this edition rule also applies to temporaries created by `pin!`,
`format_args!`, `write!`, and `writeln!` in an `if let` scrutinee. A separate
future-incompatibility lint warns about further shortening that lands later.

### Tail expressions

Temporaries in a block, function, or closure tail expression drop at that
block's end, before its locals, instead of extending outward. This permits:

```rust
fn f() -> usize {
    let c = RefCell::new("..");
    c.borrow().len()
}
```

It rejects code that relied on extension, such as
`let x = { &String::from("1234") }.len();`. Lift the block into a `let` to
re-enable temporary lifetime extension. The `tail_expr_drop_order` lint warns
only where a non-trivial `Drop` is involved and has no semantics-preserving
automatic rewrite.

## Never-type fallback

When the compiler cannot infer the type to which `!` coerces, edition 2024
falls back to `!` rather than `()`. Typical failures include a generic `f()?`,
`panic!()` in a closure with a trait-constrained return type, and an
inference-dependent branch paired with `return`.

```rust
f::<()>()?;
run(|| -> () { panic!() });
() = if true { Default::default() } else { return };
```

`never_type_fallback_flowing_into_unsafe` is deny-by-default;
`dependency_on_unit_never_type_fallback` provides an advance warning before
migration. Both become deny-by-default on every edition in `1.92.0`, so code
on earlier editions can start failing. They remain lints and can be allowed.
When an affected crate is compiled as a dependency Cargo warns instead of
failing; the denial applies when that crate is built directly.

## Patterns, conditions, and iteration

### Match ergonomics reservations

In an inherited non-move binding mode, explicit `mut`, `ref`, and `ref mut`
bindings are rejected, as are `&`/`&mut` patterns that reset that mode. For
example, `let [ref x] = &[()];` no longer compiles; bind through the reference
or match the value. Migration lint: `rust_2024_incompatible_pat`.

### Let chains

As of `1.88.0`, `if` and `while` conditions may join `let` expressions and
boolean conditions with `&&`. Bindings are visible in later links and the body,
and patterns may be refutable or irrefutable. This remains an error in edition
2021 regardless of compiler version because it depends on the new `if let`
temporary scope.

```rust
if let Channel::Stable(v) = release_info()
    && let Semver { major, minor, .. } = v
    && major == 1
    && minor == 88
{ /* ... */ }
```

### Boxed-slice iteration

Method-call syntax `boxed_slice.into_iter()` yields `T` rather than `&T`.
Use `.iter()` to retain borrowed iteration. The `boxed_slice_into_iter` lint is
warn-by-default in all editions.

## Prelude and macro grammar

### Prelude collisions

`Future` and `IntoFuture` join the prelude. A custom trait method such as
`poll` can become ambiguous on a type that also implements `Future`; use fully
qualified syntax. Migration lint: `rust_2024_prelude_collisions`.

```rust
<_ as MyPoller>::poll(&core::pin::pin!(async {}));
```

### Expression fragments

`expr` macro fragments also match `const { ... }` and `_`. `expr_2021`
preserves the narrower grammar. The
`edition_2024_expr_fragment_specifier` lint rewrites `expr` to `expr_2021`, but
usually retain `expr` unless a newly matched input would shadow a later rule.

```rust
macro_rules! example {
    ($e:expr) => { "first rule" };
    (const $e:expr) => { "second rule" };
}
```

`missing_fragment_specifier` is a hard error: every `macro_rules!`
metavariable needs a fragment kind.

### Reserved identifiers and tokens

`gen` is reserved; change identifiers to `r#gen`. Migration lint:
`keyword_idents_2024`.

Guarded strings—one or more `#` immediately followed by a string literal—and
two or more consecutive `#` characters are reserved. Macro inputs such as
`demo!(#"foo"#)` or `demo!(###)` must insert whitespace to keep tokens
separate. Migration lint: `rust_2024_guarded_string_incompatible_syntax`.

Raw lifetimes can be written as `'r#ident` since edition 2021, which lets a
`'gen` lifetime migrate to `'r#gen`. In editions 2015/2018, the same characters
tokenize separately; when moving macro input to 2021+, `my_macro!('r#foo)` may
need to become `my_macro!('r# foo)`.

## Cargo manifest migration

- The `[project]` table is removed; use `[package]`.
- Underscore dependency-key spellings such as `default_features` are removed;
  use `default-features`.
- On a workspace-inherited dependency, a member's
  `default-features = false` is an error if the workspace declaration enables
  default features. Put the setting in `[workspace.dependencies]`.
- Resolver v3 is the edition default.

## Doctests

Edition 2024 combines doctests into one executable. `1.85.0` silently fell
back to per-doctest compilation because of a bug; `1.85.1` restores combining
and can expose tests that passed only while isolated.

Use the `standalone_crate` code-fence tag when a doctest must remain its own
crate. Rustdoc already separates `compile_fail` and `edition*` tests, tests with
crate-level attributes such as `#![feature(...)]` or `global_allocator`, and
macros using `$crate`. It cannot detect code observing its own source position
or module path, such as `Location::caller().line()` or `type_name`; test these
after migration.

For `#![doc = include_str!("../README.md")]`, `include!`, `include_str!`, and
`include_bytes!` inside README doctests resolve relative to the Markdown file,
not the Rust source. This path change has no automatic migration.

## Formatting style edition

Rustfmt's `style_edition` is separate from the language edition and defaults to
the crate edition. It can also be selected in `rustfmt.toml` or with
`--style-edition`:

```toml
style_edition = "2024"
```

The 2024 style sorts raw identifiers by the name without `r#`, sorts embedded
integers in version order, and sorts lowercase module names after uppercase
type names in `use` lists. It also collapses some single-expression blocks,
formats tuple-field access without a separating space, adds a block around a
closure whose only expression is a loop, changes indentation around comments
and impl generics, removes blank lines from `where` clauses, and adds
semicolons to `return`/`break`/`continue` in match-arm blocks. Budget for a
large formatting-only change.
