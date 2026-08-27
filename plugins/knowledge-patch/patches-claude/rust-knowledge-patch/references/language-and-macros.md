# Language, Traits, Macros, and Diagnostics

## Traits, closures, and opaque types

### Coherence and trait objects

Coherence uses the next-generation trait solver (`1.84.0`). Rare impl pairs
that were previously accepted can now report conflicting implementations.

A trait object can drop its principal trait while retaining an auto trait:

```rust
let x: Box<dyn std::fmt::Debug + Send> = Box::new(1);
let y: Box<dyn Send> = x;
```

Trait upcasting is stable (`1.86.0`): a `dyn Trait` coerces to a
`dyn Supertrait` behind references, smart pointers, or raw pointers. This lets
a subtrait of `Any` upcast and use `Any`'s downcasting methods without adding a
custom conversion method or a `downcast-rs`-style crate. Unsafe code must still
never fabricate a raw trait object with an invalid vtable.

```rust
trait Trait: Supertrait {}
trait Supertrait {}

fn upcast(x: &dyn Trait) -> &dyn Supertrait { x }
```

An impl for an unsized type no longer has to implement a trait method whose
declaration has `Self: Sized` (`1.87.0`). Multiple bounds on one associated
item are accepted in generic bounds (`1.92.0`), but not in trait objects:

```rust
fn f(it: impl Iterator<Item: Clone, Item: std::fmt::Debug>) {}
```

### Async closures

`async || {}` and `AsyncFn`, `AsyncFnMut`, and `AsyncFnOnce` are stable and in
every edition's prelude (`1.85.0`). Unlike `|| async {}`, an async closure's
returned future may borrow from the closure captures. The traits also express
higher-ranked async callbacks that `Fn(&u8) -> Fut` cannot:

```rust
async fn run(_: impl for<'a> AsyncFn(&'a u8)) {}
async fn callback(_: &u8) {}
run(callback);
```

### Precise opaque-type capture

Trait return-position `impl Trait` accepts `use<...>` (`1.87.0`). Because an
RPITIT desugars to a generic associated type, every type and const parameter in
scope, including `Self`, must be listed. Lifetimes may be omitted, allowing the
opaque result to avoid capturing a method lifetime:

```rust
trait Foo {
    fn method<'a>(&'a self) -> impl Sized;
    fn precise<'a>(&'a self) -> impl Sized + use<Self>;
}
```

Edition-specific implicit capture is covered in
[edition-2024.md](edition-2024.md).

### Closure and pattern capture changes

Capture analysis follows patterns more precisely (`1.94.0`). A non-`move`
closure may move only a matched field and borrow the rest where it previously
moved the whole variable. This can produce new borrow errors and shift `Drop`
timing.

Matching a single-variant `#[non_exhaustive]` enum reads its discriminant
(`1.95.0`), which can change what a closure captures. Pattern bindings are
lowered in written order (`1.91.0`), correcting binding drop order. Drop
checking also became stricter for `let`-`else` bindings, and coroutine captures
must be drop-live.

## Conditions, patterns, and inference

### Const-generic inference

`generic_arg_infer` is stable in `1.89.0`: `_` may be inferred as a const
generic argument just as it can for a type argument:

```rust
pub fn all_false<const LEN: usize>() -> [bool; LEN] {
    [false; _]
}
```

It remains forbidden where an item signature or item type is declared, such
as `[bool; _]` in a return type or constant declaration.

### Match-arm `if let` guards

Match guards may use `if let` and let chains (`1.95.0`). Bindings from the
guard are visible in the arm body, but guard patterns do not contribute to
exhaustiveness, so a catch-all arm remains necessary.

```rust
match value {
    Some(x) if let Ok(y) = compute(x) => println!("{x}, {y}"),
    _ => {}
}
```

### Never-type and const behavior

Never-type coercion applies inside tuple expressions (`1.96.0`). Constants of
type `ManuallyDrop` work as patterns again, restoring behavior regressed in
`1.94.0`.

A constant whose final value references mutable or external memory is accepted
(`1.90.0`), but cannot be used as a pattern. Const evaluation errors when
initializing a static writes to that same static. From `1.95.0`, const blocks
do not influence whether a fallible expression is implicitly const-promoted.

### Parsing and matching changes

`..EXPR` parses after unary `!`, `-`, and `*` (`1.87.0`), which can change how
macros match those tokens. Tuple struct and tuple variant constructors now
carry temporary lifetime extension through their arguments (`1.89.0`), so
`Wrap(&String::from("hi"))` and `Some(&String::from("hi"))` can bind safely.
`format_args!()` can likewise be bound to a variable.

## Configuration macros and macro scope

### Boolean cfg predicates

`cfg(true)` and `cfg(false)` are accepted in `#[cfg]`, `#[cfg_attr]`, `cfg!`,
and Cargo `[target]` tables (`1.88.0`). `#[cfg(false)]` is the direct way to
compile an item out, replacing the easy-to-reverse `cfg(any())` idiom.

### `cfg_select!`

`cfg_select!` is a prelude macro selecting the first matching arm
(`1.95.0`). It works in item and expression positions and uses bare predicates,
`=>`, and `_`, not the `cfg-if` crate's `if`/`else if` syntax.

```rust
let platform = cfg_select! {
    windows => "windows",
    _ => "not windows",
};
```

`assert_matches!` and `debug_assert_matches!` stabilize in `1.96.0`. They are
not in the prelude; import them from `core` or `std`. A failed assertion prints
the value's `Debug` form, unlike `assert!(matches!(...))`.

### Forwarding cfg expressions

From `1.96.0`, `cfg` accepts an `expr` metavariable, so a captured expression
can be forwarded into a cfg predicate.

`proc_macro::Ident::new` accepts the special name `"$crate"` from `1.90.0`.
`proc_macro::TokenStream` implements `Extend` directly for `Group`, `Ident`,
`Punct`, and `Literal`, not only `TokenTree`, from `1.92.0`.

### Standard macros and imports

Standard-library macros come through the prelude rather than an injected
`#[macro_use] extern crate std` (`1.94.0`). A glob import defining a same-named
macro now conflicts with the prelude and is an error; add an explicit import to
disambiguate. The `panic` case is softened to the `ambiguous_panic_imports`
warning, commonly affecting `no_std` crates that glob-import `std` and bring
both `core::panic!` and `std::panic!` into scope.

Standard macros such as `assert_eq!` and `vec!` accept `const { ... }` arguments
(`1.87.0`).

## Attributes and diagnostics

### Diagnostic attributes

Library authors can mark an impl `#[diagnostic::do_not_recommend]` (`1.85.0`)
to keep it from being suggested as the path through an otherwise distracting
blanket impl.

`unknown_or_malformed_diagnostic_attributes` became a lint group (`1.90.0`),
containing `unknown_diagnostic_attributes`,
`misplaced_diagnostic_attributes`, `malformed_diagnostic_attributes`, and
`malformed_diagnostic_format_literals`. This permits allowing only unknown
newer attributes while retaining other validation:

```rust
#![allow(unknown_diagnostic_attributes)]
```

`Eq::assert_receiver_is_total_eq` is deprecated in `1.95.0`. Delete a manual
definition and leave an empty `impl Eq for T {}`; defining the marker method
now produces a future-compatibility warning.

### Function addresses

Function-pointer equality is unreliable because the backend may merge or
duplicate functions. `unpredictable_function_pointer_comparisons` warns by
default (`1.85.0`); use `std::ptr::fn_addr_eq`.

Casting a function item directly to an integer triggers
`function_casts_as_integer` (`1.93.0`). Cast through an explicit function
pointer first, such as `my_fn as fn() -> u32 as usize`.

### Lifetime syntax

`mismatched_lifetime_syntaxes` warns by default (`1.89.0`) when one lifetime is
written in inconsistent syntax categories between inputs and outputs. Hidden,
visible-elided, and named lifetimes should match; for example, write
`std::slice::Iter<'_, u8>` when returning an iterator borrowing an elided slice
input. This lint is narrower than `elided_lifetimes_in_paths` and supersedes
`elided_named_lifetimes`.

### Interior mutation and visibility

`const_item_interior_mutations` warns (`1.93.0`) when code mutates an
interior-mutable `const`, because each use creates a fresh copy and discards the
mutation. Use a static for shared state.

`unused_visibilities` warns (`1.94.0`) on meaningless visibility such as
`pub const _: () = ();`. The allow-by-default `dead_code_pub_in_binary` lint
reports unused public items in binary crates (`1.97.0`). Impls and impl items
inherit the `dead_code` level of the trait item they implement (`1.94.0`).

### Pointer-related lints

`dangling_pointers_from_locals` warns when a function returns a raw pointer to
its local, and `integer_to_ptr_transmutes` warns on integer-to-pointer
transmute (`1.91.0`). Use `ptr::with_exposed_provenance` for an intentionally
exposed address or a plain `as` cast as directed by that lint.

`dangerous_implicit_autorefs` first warned in `1.88.0` and became
deny-by-default in `1.89.0`; it catches implicit autoref of a raw-pointer
deref. `invalid_null_arguments` was also promoted from Clippy in `1.88.0`.
`deref_nullptr` is deny-by-default from `1.93.0`.

## Newly rejected forms and future incompatibilities

### Macros and attributes

- A missing `macro_rules!` fragment specifier is a hard error in edition 2024.
- A macro expansion ending in `;` in expression position is deny-by-default as
  `semicolon_in_expressions_from_macros` from `1.91.0`, including through
  dependencies, and is scheduled to become a hard error.
- Malformed `#[should_panic]` and `#[link]` attributes are errors (`1.91.0`);
  `ill_formed_attribute_input` also reports future breakage in dependencies.
- Deprecation lints emitted during name resolution are deny-by-default in
  `1.91.0` and are reported through dependencies.
- `invalid_macro_export_arguments` is deny-by-default and reported through
  dependencies (`1.92.0`).
- A meaningless `#[test]` placement is an error, including in rustdoc
  (`1.93.0`). Keywords cannot serve as cfg predicates.
- Malformed crate-level doc attributes trigger deny-by-default
  `rustdoc::invalid_doc_attributes`; `#![doc(document_private_items)]` was
  removed in favor of the rustdoc CLI flag (`1.93.0`).
- Repeating `export_name`, `link_name`, or `link_section` on one item uses the
  first occurrence (`1.96.0`). Empty `export_name`, invalid `link_name` and
  `link(name)` arguments, and invalid Mach-O `link_section` values are errors
  (`1.97.0`).
- Applying both `no_mangle` and `export_name` to one item warns (`1.85.0`).
- Codegen attributes on trait methods without bodies get a future-compatibility
  warning because they have no effect (`1.94.0`).
- Derive helper attributes shadowing built-ins get a future-incompatibility
  warning (`1.95.0`).

### Imports and name resolution

- Ambiguous glob re-exports error across crates (`1.94.0`).
- `use $crate::{self};` is rejected, while renaming a path-segment keyword,
  such as `use $crate as name;`, is accepted (`1.95.0`).
- `ambiguous_glob_imported_traits` warns when a trait arrives through
  conflicting glob imports (`1.95.0`); more visibility-related ambiguous
  imports are errors.
- `use S::{self as Other};` is rejected when `S` is a struct because `{self}`
  requires a module parent (`1.96.0`).
- Generic arguments are forbidden on a module path segment even when the module
  re-exports a generic enum variant (`1.97.0`).

### Patterns, types, and impls

- Casting away or freely changing a `dyn` lifetime bound is forbidden
  (`1.94.0`). Where-clauses are checked for well-formedness before
  normalization.
- Trait-impl modifiers on inherent impls, `static` closures, relaxed bounds in
  associated-type-bound position, invalid numeric suffixes in tuple-index or
  field-name positions, and shebangs in `--cfg`/`--check-cfg` arguments are
  rejected (`1.91.0`).
- Lifetime bounds on types mentioning only type parameters are checked
  (`1.95.0`). `mut ref` and `mut ref mut` in struct-pattern shorthand are
  feature-gated again; `irrefutable_let_patterns` does not fire on let chains.
- `use S::{self as Other};` module-parent restrictions, more const-generic type
  checking, and privacy checking of trait RPIT underlying types land in
  `1.96.0`.
- Tuple-index shorthand patterns such as `Foo { 0, 1 }` are syntax errors in
  `1.97.0`.
- A fieldless enum implementing `Drop` cannot be cast to an integer
  (`cenum_impl_drop_cast`, hard error in `1.86.0`).
- Downstream crates cannot implement `DerefMut` for `Pin<LocalType>` from
  `1.92.0`.
- Unsize coercion into `Pin<Foo>` is removed when `Foo` does not implement
  `Deref` (`1.96.0`).

### Other compatibility lints

- `missing_abi` warns on `extern` declarations without an explicit ABI from
  `1.86.0`.
- `double_negations` catches `--x` as a likely decrement typo (`1.86.0`).
- A borrow-checker correction around always-true patterns rejects some code
  accepted before `1.88.0`.
- `ControlFlow` is `#[must_use]` from `1.87.0`.
- `unused_must_use` ignores `Result<(), E>` and `ControlFlow<E, ()>` when `E`
  is uninhabited (`1.92.0`). From `1.97.0`, it looks through an uninhabited
  branch to the other value and fires exactly when that value is itself
  `#[must_use]`.
- Repr-C enum discriminants outside `c_int`/`c_uint` and transparent reprs that
  ignore a repr-C field gain future-compatibility warnings (`1.93.0`).
- `uninhabited_static` is deny-by-default and reported for dependencies
  (`1.96.0`).
- `varargs_without_pattern` is reported for dependencies, and using
  `f32: From<{float}>` to constrain an otherwise ambiguous literal warns for
  future incompatibility (`1.97.0`).
- Hidden `f64` methods deprecated since 1.0 are removed in `1.97.0`.
