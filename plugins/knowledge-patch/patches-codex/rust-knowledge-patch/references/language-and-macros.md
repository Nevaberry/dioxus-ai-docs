# Language, Traits, Macros, and Diagnostics

## Traits, coercions, and opaque types

- **Lint nesting (since 1.84.0):** `#[deny(lint)]` nested under `#[forbid(lint)]` is accepted as a no-op; the outer prohibition still applies.
- **Trait-object weakening (since 1.84.0):** a coercion may discard a non-auto principal trait while retaining auto traits, such as coercing `&(dyn Display + Send)` to `&dyn Send`.
- **Unsized implementations (since 1.87.0):** an impl for an unsized type may omit a required method whose bounds include `Self: Sized`.
- **Associated-item bounds (since 1.92.0):** repeated bounds for one associated item are accepted except in trait objects. Associated-type item bounds take precedence over where-clause bounds when proving auto traits and `Sized`.
- **Downstream `Pin` impls (since 1.92.0):** a downstream crate may no longer implement `DerefMut` directly for `Pin<LocalType>`; remove or redesign such impls.
- **RPITIT visibility (since 1.96.0):** return-position `impl Trait` in traits errors when its hidden types are too private.

## Inference, temporaries, and const evaluation

- **Const-generic inference (since 1.89.0):** `_` may stand for an inferred const-generic argument in expressions, but remains forbidden in item signatures.
- **Lifetime syntax lint (since 1.89.0):** `mismatched_lifetime_syntaxes` warns when elision connects input and output lifetimes written in different syntax categories. Spell a hidden output lifetime as `'_`; this supersedes `elided_named_lifetimes`.
- **Tuple-constructor extension (since 1.89.0):** temporary lifetime extension in a `let` initializer passes through tuple-struct and tuple-variant constructors.
- **Constants referencing mutable/external memory (since 1.90.0):** such references may appear in a constant's final value, but that constant cannot be used as a pattern.
- **Self-writing statics (since 1.90.0):** const evaluation rejects a static initializer that writes to the same static.
- **Macro-argument lifetimes (since 1.92.0):** arguments of non-extended `pin!` and formatting macros no longer receive incidental temporary lifetime extension; bind borrowed temporaries first.
- **Const promotion (since 1.95.0):** const blocks are no longer evaluated to decide whether enclosing fallible expressions can be implicitly promoted. Typed const-evaluation copies handle padding more consistently and can rarely reject pointer bytes that reach padding.
- **Array inference (since 1.95.0):** array coercions may contribute fewer constraints, so code relying on them can need explicit types.
- **Never coercions (since 1.96.0):** tuple expressions now consistently apply never-type coercions.
- **Const-generic checking (since 1.96.0):** const-generic argument types are checked in more positions.
- **Float inference (since 1.97.0):** using `f32: From<{float}>` to constrain an otherwise unconstrained float produces a future-compatibility warning.

## Patterns, captures, and imports

- **Open-beginning ranges (since 1.87.0):** `..EXPR` is accepted directly after unary `!`, `-`, and `*`; macro matching around these token sequences can change.
- **Binding and drop order (since 1.91.0):** bindings are lowered in written order, and primary-binding order determines destruction order. Test destructuring with visible `Drop` effects.
- **Precise closure capture (since 1.94.0):** pattern capture is more precise. A non-`move` closure may move one field and borrow another instead of moving the whole value, changing borrow errors and drop timing.
- **Path-keyword aliases (since 1.95.0):** path-segment keywords can be imported when renamed, such as `use crate as root`; unrenamed `use $crate::{self};` is rejected.
- **`if let` guards (since 1.95.0):** match guards may bind patterns with `if let`; those patterns do not contribute to exhaustiveness.
- **Non-exhaustive discriminants (since 1.95.0):** matching a single-variant `#[non_exhaustive]` enum now reads its discriminant and can change closure capture.
- **Struct self-imports (since 1.96.0):** `use S::{self as Other}` is rejected because a `{self}` import requires a module parent.
- **Path and pattern syntax (since 1.97.0):** generic arguments on module path segments are rejected even for generic enum-variant reexports, and tuple-index shorthand is rejected in struct patterns.

## Configuration and built-in macros

- **Raw cfg identifiers (since 1.85.0):** Cargo cfg expressions accept keyword-shaped names as raw identifiers such as `r#gen`; bare keywords warn for future incompatibility.
- **Checked `test` cfg (since 1.85.0):** direct `rustc --check-cfg` users must register `test` explicitly with `--check-cfg=cfg(test)`; Cargo registers it in this release.
- **Const-block macro arguments (since 1.87.0):** standard macros such as `assert_eq!` and `vec!` accept `const { ... }` expressions.
- **Boolean cfg predicates (since 1.88.0):** `cfg(true)` and `cfg(false)` work in `cfg`, `cfg_attr`, `cfg!`, and Cargo target tables, replacing empty `all()`/`any()` tricks.
- **Stored `format_args!` (since 1.89.0):** formatted arguments containing placeholders may be bound to a variable for later use, subject to normal borrow lifetimes.
- **`$crate` construction (since 1.90.0):** `proc_macro::Ident::new` accepts `$crate`.
- **Prelude macro resolution (since 1.94.0):** standard macros arrive through the prelude instead of injected `#[macro_use]`. Same-named glob imports can become ambiguous; explicitly import the intended macro. `ambiguous_panic_imports` also covers affected `no_std` code glob-importing `std`.
- **Compile-time selection (since 1.95.0):** `cfg_select!` expands the first matching item or expression arm and supports `_` as fallback.
- **Forwarded cfg expressions (since 1.96.0):** macros may forward an `expr` metavariable into `cfg`.
- **Pattern assertions (since 1.96.0):** import `assert_matches!` or `debug_assert_matches!` from `core` or `std`; failures render the value with `Debug`.

## Declarative and procedural macro compatibility

- **Defining-crate edition (since 1.85.0):** when an exported macro expands to define another `macro_rules!`, the inner macro uses the external defining crate's edition, not the consumer's.
- **Invalid constructs rejected (since 1.87.0):** macros in `#![crate_name]`, attributes on `..` in struct patterns, order-dependent trait objects, and `ptr_cast_add_auto_to_object` cases are errors. Repeated associated-type bindings on `dyn` types are not deduplicated, and flattened `format_args!` is disallowed in const contexts.
- **ABI strings in pointer types (since 1.87.0):** unsupported ABI strings on function pointers warn even when they occur in dependencies.
- **Expansion visibility (since 1.87.0):** procedural macros no longer observe expanded `cfg(true)` attributes. Declarative macros depending on the old pasted-token representation can fail; match the relevant input as `tt` where appropriate.
- **Span locations (since 1.88.0):** `proc_macro::Span` exposes stable `line`, `column`, `start`, `end`, `file`, and `local_file`.
- **Fragment specifiers (since 1.89.0):** every metavariable matcher needs an explicit fragment kind; `missing_fragment_specifier` is an unconditional error.
- **Expression semicolons (since 1.91.0):** `semicolon_in_expressions_from_macros` is deny-by-default when an expression-position `macro_rules!` expansion ends in `;`, ahead of a hard error.
- **Export arguments (since 1.92.0):** `invalid_macro_export_arguments` is deny-by-default and reported in dependencies.

## Lints and newly rejected code

- **Missing ABI (since 1.86.0):** `missing_abi` warns for bare `extern {}` and `extern fn`; omission still means `"C"`, but spell it explicitly.
- **Double negation (since 1.86.0):** `double_negations` warns on `--x`, which is two negations, not decrement.
- **Hard compatibility errors (since 1.86.0):** `wasm_c_abi` is a hard error; use `wasm-bindgen` 0.2.89 or newer. Integer casts of fieldless enums implementing `Drop` also error, and `#![no_start]`/`#![crate_id]` are removed.
- **Raw-pointer diagnostics (since 1.88.0):** `dangerous_implicit_autorefs` warns when a raw-pointer dereference forms an implicit reference and was scheduled to become deny-by-default in the next release; `invalid_null_arguments` catches invalid null arguments.
- **Custom test attributes (since 1.88.0):** `#[bench]` without `#![feature(custom_test_frameworks)]` is a hard error.
- **Diagnostic lint group (since 1.90.0):** configure `unknown_diagnostic_attributes`, `misplaced_diagnostic_attributes`, `malformed_diagnostic_attributes`, and `malformed_diagnostic_format_literals` separately or through `unknown_or_malformed_diagnostic_attributes`.
- **Unsupported ABIs (since 1.90.0):** unsupported `extern "abi"` strings are rejected in all positions, including trait impls for function-pointer types.
- **Pointer escape and transmute lints (since 1.91.0):** `dangling_pointers_from_locals` and `integer_to_ptr_transmutes` warn by default. Name-resolution deprecation lints are deny-by-default and reported in dependencies.
- **Never-type migration (since 1.92.0):** `never_type_fallback_flowing_into_unsafe` and `dependency_on_unit_never_type_fallback` are deny-by-default for direct builds. Dependency builds produce Cargo warnings; fix inference instead of relying on `allow`.
- **Low-level defaults (since 1.93.0):** `function_casts_as_integer` warns on direct function-item-to-integer casts; `const_item_interior_mutations` warns on mutation of interior-mutable const values; `deref_nullptr` is deny-by-default; out-of-range `repr(C)` enum discriminants warn for future incompatibility.
- **Trait lint inheritance (since 1.94.0):** impls and their items inherit `dead_code` levels from the matching trait/items. `unused_visibilities` warns on visibility attached to anonymous `const _`.
- **Unicode identifiers (since 1.94.0):** Unicode data is version 17 and lifetime identifiers are NFC-normalized.
- **Cross-crate diagnostics (since 1.94.0):** casts may not freely change lifetime bounds on `dyn` types, expression-position `include!` no longer strips a leading shebang, and ambiguous glob reexports are visible across crate boundaries. Codegen attributes on body-free trait methods warn because they have no effect.
- **Upgrade checks (since 1.95.0):** lifetime bounds involving only type parameters and more visibility-related ambiguous imports are checked. Future warnings cover ambiguously glob-imported traits, derive helpers conflicting with built-ins, and manual `Eq::assert_receiver_is_total_eq`; accidental `mut ref` and `mut ref mut` shorthand patterns are feature-gated again.
- **Uninhabited statics (since 1.96.0):** `uninhabited_static` is deny-by-default and reported in dependencies.
- **Other 1.96.0 rejections:** unsizing into `Pin<Foo>` requires `Foo: Deref`, and `#![reexport_test_harness_main]` is feature-gated again.
- **Uninhabited results (since 1.97.0):** `unused_must_use` treats `Result<T, Uninhabited>` and `ControlFlow<Uninhabited, T>` like `T`. `dead_code_pub_in_binary` is an allow-by-default lint for unused public binary-crate APIs.
