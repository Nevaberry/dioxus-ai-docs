# Language, Traits, Macros, and Diagnostics

Use this reference for cross-edition compiler behavior, type-system changes, pattern and macro compatibility, and lint-driven upgrade failures.

## Traits, coherence, and opaque types

### Coherence and trait objects

- Trait-implementation overlap uses the next-generation trait solver (1.84.0). An upgrade can newly report `conflicting implementations` for previously accepted unsound overlap, or accept impl sets whose non-overlap the older solver could not establish.
- A trait-object coercion may discard its non-auto principal trait while retaining auto traits (1.84.0):

  ```rust
  fn keep_only_send(value: &(dyn std::fmt::Display + Send)) -> &dyn Send {
      value
  }
  ```

- Trait-object upcasting is stable through references, smart pointers such as `Arc`, and raw pointers (1.86.0). Raw objects must carry valid vtables even temporarily.
- An impl for an unsized type may omit a required method whose `Self: Sized` bound cannot hold (1.87.0).

### Precise capture and associated types

- Trait methods may constrain return-position `impl Trait` capture with `use<...>` (1.87.0). For example, `fn value<'a>(&'a self) -> impl Sized + use<Self>` may depend on `Self` without capturing `'a`.
- Impls with `?Sized` bounds on recursive types containing associated-type projections can newly fail and may require refactoring (1.89.0).
- The same associated item may be bounded more than once in a generic trait bound, but not in a trait object (1.92.0): `Iterator<Item: Copy, Item: Send>`.
- Associated-item bounds are preferred over equivalent where-clause bounds when proving that the associated type is `Sized` or implements an auto trait (1.92.0).
- A downstream crate may no longer implement `DerefMut` for `Pin<LocalType>` (1.92.0); redesign code that used such an impl.
- Return-position `impl Trait` types in traits are rejected when their visibility is too private for the exposed interface (1.96.0).
- `Eq::assert_receiver_is_total_eq` is deprecated, and a manual impl that defines it receives a future-compatibility warning (1.95.0).

## Inference, lifetimes, captures, and drop order

### Const-generic and array inference

- `_` may be an inferred const-generic argument when context determines it (1.89.0), including `[false; _]`. It remains invalid in item signatures such as declared function return types or const item types.
- Array-repeat `Copy` requirements now affect inference only at the end of type checking (1.89.0).
- Generic const parameter defaults are type-checked, and more ill-typed const-generic arguments are rejected (1.88.0 and 1.96.0).
- Array coercions can provide fewer inference constraints, so affected expressions may require explicit types (1.95.0).

### Lifetime spelling and extension

- `mismatched_lifetime_syntaxes` warns when elision connects input and output lifetimes but the signature spells the two sides inconsistently (1.89.0). For example, prefer `Iter<'_, u8>` over `Iter<u8>` when tied to an elided input; this lint supersedes `elided_named_lifetimes`.
- Temporary lifetime extension passes through tuple-struct and tuple-variant constructors (1.89.0), allowing a borrowed temporary to live for the enclosing `let`:

  ```rust
  struct Wrapped<'a>(&'a String);
  let value = Wrapped(&String::from("temporary"));
  ```

- Temporary extension no longer reaches arguments of `pin!` and formatting macros when the macro call itself is in a non-extending position (1.92.0).
- Lifetime bounds are checked for types mentioning only type parameters (1.95.0); add correct bounds rather than relying on their former omission.

### Patterns, captures, and destruction

- Pattern bindings are lowered in written order, and primary-binding order determines drop order (1.91.0). Test code whose destructors have visible side effects.
- Pattern-aware closure capture can move one field while borrowing another rather than moving the whole variable (1.94.0). This may expose borrow errors or change destruction timing.
- Matching a single-variant `#[non_exhaustive]` enum now reads its discriminant (1.95.0), which can make a closure capture a value it did not capture before.
- Struct-field shorthand patterns using the accidentally accepted `mut ref` or `mut ref mut` combinations are feature-gated again (1.95.0).
- Never values are always coerced in tuple expressions (1.96.0).
- Some `#[repr(Int)]` enums with fields of uninhabited zero-sized types have corrected layouts (1.96.0); do not infer language-level guarantees from the former layout.
- The encoding of some enums without an explicit representation changed (1.97.0). Treat unspecified layout as non-contractual.

### Const promotion and evaluation compatibility

- Expressions containing fallible operations are no longer implicitly promoted when promotion eligibility would require evaluating a const block (1.95.0).
- Typed const-evaluation copies handle padding more consistently (1.95.0), which can rarely reject a const or static when bytes from part of a pointer would enter padding.
- A static initializer that writes to the same static is rejected during const evaluation (1.90.0).

## Conditions, patterns, and configuration syntax

### Match guards

Match arms may bind a pattern with an `if let` guard (1.95.0). Bindings from the arm pattern and guard are available in the body; guard patterns do not contribute to exhaustiveness.

```rust
match value {
    Some(x) if let Ok(y) = compute(x) => println!("{x}, {y}"),
    _ => {}
}
```

### `cfg_select!`

`cfg_select!` expands the first true `cfg` arm, with `_` as a fallback, for either items or expressions (1.95.0).

```rust
cfg_select! {
    unix => { fn platform() -> &'static str { "unix" } }
    target_pointer_width = "32" => { fn platform() -> &'static str { "32-bit" } }
    _ => { fn platform() -> &'static str { "other" } }
}
```

### Forwarding expressions to `cfg`

An `expr` metavariable captured by `macro_rules!` can be forwarded as a `cfg` predicate (1.96.0):

```rust
macro_rules! cfg_item {
    ($condition:expr, $item:item) => {
        #[cfg($condition)]
        $item
    };
}
cfg_item!(unix, fn platform_only() {});
```

### Pattern assertions

`assert_matches!` and `debug_assert_matches!` display the value with `Debug` on failure (1.96.0). They are not in the prelude; import them from `core` or `std`.

## Declarative and procedural macros

### Edition and parsing behavior

- When an external crate's exported `macro_rules!` macro defines another declarative macro, the nested macro body uses the defining crate's edition (1.85.0), not the consuming crate's edition.
- Open-beginning ranges can be parsed after unary `!`, `-`, or `*`, potentially changing macro matching (1.87.0).
- Standard macros such as `assert_eq!` and `vec!` accept `const { ... }` expressions (1.87.0).

### Rejected or changed macro constructs

- Macro calls inside `#![crate_name]` are rejected (1.87.0).
- Procedural macros cannot observe expanded `cfg(true)` attributes (1.87.0).
- Some invalid pasted-token declarative macros must be rewritten, often by capturing a `tt` fragment (1.87.0).
- `missing_fragment_specifier` is an unconditional error (1.89.0).
- `semicolon_in_expressions_from_macros` is deny-by-default for expression-position expansions ending in `;` (1.91.0), ahead of a hard error.
- `invalid_macro_export_arguments` is deny-by-default, and malformed `#[macro_export(...)]` is reported in dependencies (1.92.0).
- Invalid numeric suffixes in field positions and shebangs inside `--cfg` or `--check-cfg` are rejected (1.91.0).
- An expression-context `include!(...)` no longer strips a leading shebang from its input (1.94.0).

### Prelude and import ambiguity

- Standard-library macros arrive through the prelude instead of injected `#[macro_use]` (1.94.0). A same-named glob import can become ambiguous and require an explicit import.
- Ambiguous glob reexports are visible across crate boundaries (1.94.0).
- Ambiguity between `core::panic!` and `std::panic!` is reported by `ambiguous_panic_imports` (1.94.0).
- Path-segment keywords may be imported when renamed, but `use $crate::{self};` without renaming is rejected (1.95.0).
- Ambiguously glob-imported traits receive `ambiguous_glob_imported_traits`, and derive helper attributes conflicting with built-in attributes receive a future-compatibility warning (1.95.0).

## Lints and diagnostic policy

### Lint-level semantics

- An inner `#[deny(...)]` under an outer `#[forbid(...)]` is a harmless no-op rather than an attempted weakening (1.84.0).
- `rustc --check-cfg` no longer declares `test` automatically (1.85.0). Direct compiler invocations must pass `--check-cfg=cfg(test)`; Cargo still declares it.
- `unknown_or_malformed_diagnostic_attributes` is a group containing the individually configurable `unknown_diagnostic_attributes`, `misplaced_diagnostic_attributes`, `malformed_diagnostic_attributes`, and `malformed_diagnostic_format_literals` (1.90.0).
- Impls and impl items inherit `dead_code` levels from their corresponding traits and trait items (1.94.0).
- `unused_visibilities` warns on visibility applied to `const _` declarations (1.94.0).
- The allow-by-default `dead_code_pub_in_binary` finds unused public items in binary crates (1.97.0).

### Function, pointer, and expression diagnostics

- Direct function-pointer comparison triggers `unpredictable_function_pointer_comparisons` (1.85.0); use `std::ptr::fn_addr_eq` for deliberate address comparison. From 1.89.0, the lint also reaches comparisons generated by external macros.
- `double_negations` warns on forms such as `--x`, which are two negations rather than decrement (1.86.0).
- `dangerous_implicit_autorefs` warns when dereferencing a raw pointer causes an implicit autoref (1.88.0) and becomes deny-by-default in 1.89.0.
- `invalid_null_arguments` detects null passed where the called operation requires non-null (1.88.0).
- Ignoring `[T; N]::map` warns (1.89.0).
- `function_casts_as_integer` and `const_item_interior_mutations` warn by default, while `deref_nullptr` is deny-by-default (1.93.0).
- `uninhabited_static` is deny-by-default and is reported in dependencies (1.96.0).
- Depending on `f32: From<{float}>` to infer an otherwise unconstrained float receives a future-compatibility warning (1.97.0).

### Never type and must-use behavior

- Never-type future-compatibility warnings are reported in dependencies from 1.89.0.
- `never_type_fallback_flowing_into_unsafe` and `dependency_on_unit_never_type_fallback` are deny-by-default when building the affected crate directly (1.92.0). Cargo only warns when the crate is a dependency; projects can explicitly allow them.
- `unused_must_use` does not warn for `Result<(), E>` or `ControlFlow<B, ()>` when `E` or `B` is uninhabited, such as `!` or `Infallible` (1.92.0).
- From 1.97.0, `Result<T, Uninhabited>` and `ControlFlow<Uninhabited, T>` are treated like `T` for must-use checking, so only the payload's requirement controls the warning.

### Attribute and identifier diagnostics

- Rust identifiers use Unicode 17, and lifetime identifiers are NFC-normalized (1.94.0).
- Code-generation attributes on body-free trait methods receive a future-compatibility warning because they currently have no effect (1.94.0).
- Name-resolution deprecation lints are deny-by-default and are reported in dependencies (1.91.0).
- Bare `...` parameters outside foreign blocks are future-incompatible, and keyword cfg predicates are rejected (1.93.0).
- Meaningless `#[test]` placement, malformed `#[should_panic]` and `#[link]`, trait modifiers on inherent impls, `static` closures, and relaxed associated-type bounds such as `TraitRef<AssocTy: ?Sized>` are rejected (1.91.0 and 1.93.0).
- Empty `export_name`, malformed `link` or `link_name` parameters, and invalid Mach-O `link_section` specifiers are rejected (1.97.0).

## Newly enforced type and syntax rules

- `ptr_cast_add_auto_to_object` and order-dependent trait objects became hard errors; associated types on `dyn` types are no longer deduplicated (1.87.0).
- Formatting width and precision are capped at 16 bits on every target (1.87.0).
- `#[bench]` without `#![feature(custom_test_frameworks)]`, some always-true-pattern borrow cases, and vector values passed through an ABI without the required target feature are rejected (1.88.0).
- Unsupported ABI strings are rejected everywhere, including function-pointer trait impls (1.90.0).
- `proc_macro_derive` arguments are validated even when the attribute is on the crate root (1.90.0).
- Coroutine captures must be drop-live, and `let-else` bindings receive stricter drop checking (1.91.0).
- A cast may no longer freely change lifetime bounds on a `dyn` type, and well-formedness is checked before where-clause normalization (1.94.0).
- Struct imports such as `use S::{self as Other};` and unsizing into `Pin<Foo>` when `Foo` lacks `Deref` are rejected (1.96.0).
- Generic arguments on module path segments and tuple-index shorthand in struct patterns are rejected (1.97.0).

## Removed or deprecated compiler surfaces

- The unstable `-Zpolymorphize` flag was removed (1.85.0).
- The no-op crate attributes `#![no_start]` and `#![crate_id]` were removed, and casting a fieldless enum with `Drop` to an integer is a hard error (1.86.0).
- `wasm_c_abi` became a hard error in 1.86.0; `wasm-bindgen` must be at least 0.2.89.
- `std::intrinsics::drop_in_place` was removed (1.89.0). The accidentally stable intrinsic entries `copy`, `copy_nonoverlapping`, and `write_bytes` are proper intrinsics, cannot coerce to function pointers, and add no debug assertions against undefined behavior.
- Constants and functions in `std::char` are deprecated in favor of primitive `char` APIs (1.97.0).
