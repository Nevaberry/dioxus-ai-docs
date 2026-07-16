# Rust 2024 Edition

Use this reference when migrating an existing crate, reviewing edition-sensitive code, or selecting the Cargo resolver and formatting style. The core edition batch is `edition-2024`; later supplemental migration details are grouped with it.

## Migration workflow

Set the crate's `edition`, run `cargo fix --edition`, and review the result before compiling under the new edition. Automatic edits preserve compilation where possible but cannot prove unsafe preconditions, intended temporary lifetimes, macro rule priority, global symbol uniqueness, or formatting policy.

## Syntax and pattern grammar

### Guarded-string token reservation

The edition reserves one or more `#` immediately before a string literal and two or more consecutive `#` characters. Inputs such as `m!(#"text"#)` and `m!(###)` no longer parse; insert whitespace to keep the tokens separate. Use `rust_2024_guarded_string_incompatible_syntax` or `cargo fix --edition` to find cases.

### `gen` keyword reservation

`gen` is reserved for future generator blocks. Rename existing identifiers or write them as raw identifiers such as `r#gen`; `keyword_idents_2024` supports migration.

### `let` chains

Top-level `let` expressions may be operands of an `&&` chain in `if` and `while`, interleaved with boolean conditions. They cannot be parenthesized or joined by `||`.

```rust
if let Some(first) = iter.next()
    && *first > 0
    && let Some(second) = iter.next()
{
    use_pair(first, second);
}
```

### Fully explicit patterns after match ergonomics

After a pattern elides a reference and changes the default binding mode away from `move`, explicit `mut`, `ref`, `ref mut`, `&`, and `&mut` are rejected. Make the reference prefix fully explicit. The `rust_2024_incompatible_pat` lint and `cargo fix --edition` can rewrite affected patterns.

```rust
let &[ref x, mut y] = &[(), ()];
```

### Broader macro `expr` fragments

`$e:expr` now matches const blocks and `_`, which can change which declarative-macro arm wins. The compatibility rewrite to `expr_2021` preserves the old grammar; keep `expr` when the broader matching behavior is intended.

```rust
macro_rules! evaluate {
    ($value:expr) => { consume($value) };
    (const $value:expr) => { consume_const($value) };
}
```

## Iteration, inference, and opaque types

### Boxed-slice iteration

`Box<[T]>` has implemented `IntoIterator` since Rust 1.80, but earlier editions hide it from method-call lookup. In 2024, `boxed.into_iter()` consumes the box and yields `T`; use `boxed.iter()` for `&T`. Direct `for value in boxed` yields owned values in every edition on compilers with the implementation.

### Never-type fallback

An unconstrained never-to-any coercion falls back to `!`, not `()`. Specify unit where code relied on implicit unit inference, particularly generic `f()?` calls or panicking closures. `never_type_fallback_flowing_into_unsafe` is deny-by-default in this edition.

```rust
f::<()>()?;
run(|| -> () { panic!() });
```

### Return-position `impl Trait` capture

Without a `use<...>` bound, a return-position opaque type captures every in-scope type, const, and lifetime parameter, including parameters on an outer `impl`. A newly captured lifetime can prevent an otherwise independent value from being `'static`. Use precise capture to preserve non-capture; name an argument-position `impl Trait` parameter before listing it.

```rust
fn value<'a, T>(_: &'a (), value: T) -> impl Sized + use<T> { value }
```

## Temporary scope and destruction order

### `if let` scrutinees

Scrutinee temporaries live through the successful arm but drop before `else`, permitting resources such as read locks to be reacquired there. Rewrite to `match` when the pre-2024 lifetime through both arms is intentional. The `if_let_rescope` lint identifies affected expressions.

From 1.91.0, temporaries produced by `pin!`, `format_args!`, `write!`, and `writeln!` in an `if let` scrutinee consistently obey this shortened scope.

### Tail expressions

Temporaries in a function, closure, or block tail may drop at that block's end before local bindings. This can make `c.borrow().len()` valid as a function tail when `c` is a local `RefCell`, but makes `{ &String::from("1234") }.len()` invalid. Introduce a local when the inner value must live longer. `tail_expr_drop_order` warns for nontrivial destructors but has no automatic rewrite.

## Unsafe and foreign interfaces

### Unsafe foreign blocks and items

Declare every foreign block `unsafe extern`. Items may be explicitly `safe` or `unsafe`; an unqualified declaration remains unsafe. Marking an item safe commits the block author to the correctness of its foreign signature.

```rust
unsafe extern "C" {
    pub safe fn sqrt(value: f64) -> f64;
    pub unsafe fn strlen(value: *const core::ffi::c_char) -> usize;
    pub fn free(value: *mut core::ffi::c_void);
}
```

### Unsafe attributes

Write `no_mangle`, `export_name`, and `link_section` as `#[unsafe(...)]`. Migration can wrap the attribute but cannot verify symbol uniqueness, ABI expectations, or section invariants.

```rust
// SAFETY: this is the program's only definition of `device_loop`.
#[unsafe(export_name = "device_loop")]
pub fn run() {}
```

### Unsafe operations inside unsafe functions

`unsafe_op_in_unsafe_fn` warns by default. An unsafe function makes calling it unsafe but does not justify every unsafe operation in its body; wrap each operation in an explicit block or deliberately configure the lint.

```rust
unsafe fn get_unchecked<T>(values: &[T], index: usize) -> &T {
    unsafe { values.get_unchecked(index) }
}
```

### Mutable statics

`static_mut_refs` is deny-by-default and includes implicit borrows from formatting or method calls. Prefer an immutable static containing an atomic, lock, `OnceLock`, or `LazyLock`. If global reasoning is unavoidable, form `&raw const` or `&raw mut` pointers and confine unsafe access.

### Environment and pre-exec mutation

`std::env::set_var`, `std::env::remove_var`, and deprecated Unix `CommandExt::before_exec` require unsafe calls. Mutate the environment only when no other thread can run; migrate `before_exec` to the also-unsafe `pre_exec` when appropriate. The `deprecated_safe_2024` rewrite inserts blocks but cannot prove these conditions.

## Prelude and method resolution

`std::future::Future` and `IntoFuture` enter the prelude. Their methods can conflict with another in-scope trait; `rust_2024_prelude_collisions` migrates affected calls to fully qualified syntax such as `<_ as MyPoller>::poll(value)`.

## Cargo behavior

### Resolver 3

For a normal 2024 package, Cargo implies resolver 3 and `resolver.incompatible-rust-version = "fallback"`, making dependency selection aware of Rust-version compatibility. The resolver is workspace-global; a virtual workspace has no package edition from which to infer it and must opt in.

```toml
[workspace]
resolver = "3"
```

### Manifest spelling

The edition rejects `[project]` in favor of `[package]` and the underscore aliases `default_features`, `crate_type`, `proc_macro`, `dev_dependencies`, and `build_dependencies` in favor of hyphenated forms. `cargo fix --edition` updates these spellings.

### Inherited dependency defaults

A member may specify `default-features = false` on a `{ workspace = true }` dependency only when the matching `[workspace.dependencies]` entry also disables defaults. The previously ineffective member-only form is now an error; another workspace member can still enable defaults through feature unification.

## Doctests and included documentation

Rustdoc attempts to compile compatible doctests from a 2024 crate into one executable, though each test still runs in a separate process. It separates `compile_fail` blocks, explicit-edition blocks, crate or global attributes, and macros that use `$crate`. Add the `standalone_crate` code-block tag when generated locations or `type_name` paths must remain isolated.

When `#[doc = include_str!(...)]` includes Markdown that itself uses `include!`, `include_str!`, or `include_bytes!`, resolve nested paths relative to the Markdown file rather than the Rust source. Adjust old paths manually.

## Rustfmt style edition

Formatting style can be selected independently of parsing edition. `--edition 2024` selects both; `--style-edition 2024` or the following setting changes only formatting:

```toml
# rustfmt.toml
style_edition = "2024"
```

The 2024 style intentionally changes comment alignment and accidental formatting inside comments, long strings, array patterns, impl generics, complex return types, nested tuple access, macro calls, attributed `let`-`else`, and several match, closure, and where-clause layouts. Running `cargo fmt` applies the migration; isolate this churn as a formatting-only change when useful.

Sorting is identifier-aware: it ignores `r#`, so `r#async` sorts as `async`; it uses Unicode lexicographic order and compares numeric suffixes naturally, placing names such as `NonZeroU8`, `NonZeroU16`, `NonZeroU32`, and `NonZeroU64` in numeric order.

These supplemental migration details correspond to `edition-2024-supplemental`.
