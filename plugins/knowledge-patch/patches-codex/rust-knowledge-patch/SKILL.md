---
name: rust-knowledge-patch
description: Rust
version: "1.97.0"
license: MIT
metadata:
  author: Nevaberry
---


# Rust Knowledge Patch

Use this skill when upgrading, reviewing, or debugging Rust code, Cargo workflows, platform support, documentation, tests, or formatting.

## Reference index

| Reference | Topics |
| --- | --- |
| [edition-2024.md](references/edition-2024.md) | Edition migration, iterator and temporary semantics, opaque capture, patterns, unsafe extern blocks, manifests, doctests, rustfmt |
| [language-and-macros.md](references/language-and-macros.md) | Traits, opaque types, inference, patterns, macros, lints, name resolution, newly rejected code |
| [safety-ffi-and-low-level.md](references/safety-ffi-and-low-level.md) | Raw pointers, provenance, pinning, allocation, FFI, ABIs, intrinsics, assembly, symbol and layout behavior |
| [standard-library.md](references/standard-library.md) | Collections, iterators, ranges, I/O, paths, text, numerics, const stabilization, behavior contracts |
| [cargo.md](references/cargo.md) | Configuration, builds, workspaces, packaging, publishing, lockfiles, registries, cache, metadata, environment variables |
| [targets-and-toolchains.md](references/targets-and-toolchains.md) | Linkers, WebAssembly, target tiers, platform baselines, LLVM, native linking, host queries |
| [docs-tests-and-formatting.md](references/docs-tests-and-formatting.md) | Rustdoc, doctests, libtest, rustfmt, diagnostics and path remapping |

## Apply this patch

1. Read the crate's `rust-version`, edition, targets, panic strategy, and Cargo/rustc invocation path.
2. Preserve the existing MSRV unless the task explicitly raises it.
3. Check breaking changes before adopting new APIs or syntax.
4. Open only the topic references relevant to the work; they carry the complete compatibility inventory.
5. Test target-specific, FFI, linker, unsafe, and const-evaluation assumptions on the actual toolchain and target.
6. If the project is newer than the frontmatter version, treat this guidance as potentially stale and trust manifests, code, compiler output, and tests.

## Breaking changes and migrations

### Upgrade affected 1.97.0 builds to 1.97.1

Rust 1.97.1 fixes an LLVM optimization miscompilation whose underlying issue affects releases back to 1.87. Upgrade affected users rather than relying on the generated-IR behavior from 1.97.0.

### Treat Rust 2024 as a semantic migration

- Run `cargo fix --edition`, then review every edit.
- Boxed-slice method-call `.into_iter()` consumes the box and yields owned elements; use `.iter()` for borrowing.
- Never-type fallback remains `!`; constrain generic results that relied on `()`.
- Tail-expression and some `if let` temporaries drop earlier.
- Return-position `impl Trait` captures every in-scope lifetime unless a precise `use<...>` bound says otherwise.
- Make pattern prefixes explicit before using `mut`, `ref`, `ref mut`, `&`, or `&mut`.
- Declare foreign blocks `unsafe extern`; mark imports `safe` only when every call is valid.
- Replace legacy manifest spellings, align workspace-inherited default features, review combined doctests and nested includes, and pin rustfmt's `style_edition` when needed.

Read [edition-2024.md](references/edition-2024.md) before changing an edition.

### Compiler acceptance and inference changed

- Direct builds fail on the never-type migration lints from 1.92.0; fix type inference rather than broadly allowing them.
- Macro matchers require fragment specifiers, expression-position expansions cannot end in semicolons, and invalid `macro_export` arguments can fail builds.
- Unsupported ABIs, several invalid low-level attributes, uninhabited statics, custom JSON targets on stable, and newly rejected path or pattern forms require source changes.
- Pattern binding, closure capture, tuple-constructor temporary extension, const promotion, and never coercion changes can alter borrowing, drop order, or inference.
- Standard macros now resolve through the prelude, so glob imports can create ambiguities.

Use [language-and-macros.md](references/language-and-macros.md) for the exact lint, syntax, and release behavior.

### ABI, linker, symbol, and layout assumptions changed

- Rebuild every side of a `wasm32-unknown-unknown` C ABI boundary after the 1.89.0 ABI change.
- WebAssembly unresolved symbols fail linking from 1.96.0; declare imports or explicitly restore the old linker flag.
- `x86_64-unknown-linux-gnu` uses LLD by default from 1.90.0.
- Linux `panic=abort` emits unwind tables from 1.92.0 unless disabled.
- Stable rustc emits v0 Rust symbols by default from 1.97.0.
- Never rely on the observed encoding of a type without an explicit representation; enum layouts changed in 1.96.0 and 1.97.0 edge cases.

Read [safety-ffi-and-low-level.md](references/safety-ffi-and-low-level.md) and [targets-and-toolchains.md](references/targets-and-toolchains.md) before changing interop or build infrastructure.

### Pointer and pinning assumptions need review

- Forming `&raw` through a raw pointer or to a union field is safe, but dereferencing remains subject to the full unsafe contract.
- Debug null checks are diagnostics, not soundness guarantees; read/write validity generally excludes null.
- Prefer exposed-provenance APIs to integer-to-pointer transmutes.
- `pin!(x)` no longer dereference-coerces `&mut T`; express the intended pinned place explicitly.
- Bind temporaries before passing borrowed values to `pin!` or formatting macros when their lifetime matters.

### Cargo workflows changed

- Automatic cache cleanup can remove old entries; disable it when pre-1.78 Cargo installations share the cache.
- `cargo publish --workspace` is dependency ordered but non-atomic.
- Publishing does not leave a `.crate`; use `cargo package` when the archive is required.
- `cargo package --exclude-lockfile` omits the lockfile, while normal package behavior may include it.
- `build.build-dir`, `resolver.lockfile-path`, configuration `include`, target `rustdocflags`, and `build.warnings` address different concerns.
- Keep target cleaning scoped, use explicit package/workspace selectors, and avoid ambiguous relative install roots.

Read [cargo.md](references/cargo.md) before changing CI, configuration, packaging, registries, or workspaces.

## High-value language and macro features

### Traits and coercions

- Trait-object coercions can discard the principal trait while retaining auto traits from 1.84.0.
- Unsized implementations may omit required methods constrained by `Self: Sized` from 1.87.0.
- Associated items accept repeated bounds outside trait objects from 1.92.0, and item bounds take precedence in auto-trait and `Sized` reasoning.

```rust
trait Inspect {
    fn sized_only(&self) where Self: Sized;
}

impl Inspect for [u8] {}
```

### Conditions, configuration, and assertions

- `cfg(true)` and `cfg(false)` work in compiler and Cargo predicates from 1.88.0.
- `cfg_select!` chooses the first matching item or expression arm from 1.95.0.
- Match guards accept `if let` from 1.95.0, but guard patterns do not affect exhaustiveness.
- `assert_matches!` and `debug_assert_matches!` are stable from 1.96.0 and require an explicit import.

```rust
use std::assert_matches;

assert_matches!(Some(4), Some(1..=6));
```

### Ranges and patterns

- `array_windows` yields overlapping fixed-size slice windows from 1.94.0.
- The stable `core::range` family grows across 1.95.0 and 1.96.0; its iterable range values implement `IntoIterator`, and range syntax still creates legacy `core::ops` ranges.
- Use `RangeBounds` in public APIs intended to accept both range families.

## High-value library features

### Collections and mutable insertion

- Hash collections provide `extract_if` from 1.88.0; B-tree collections add it in 1.91.0.
- Slices provide fixed-width chunks, borrowed split-off operations, UTF-8 boundary adjustment, and fixed-size overlapping windows.
- Rust 1.95.0 adds insertion methods that return mutable references for `Vec`, `VecDeque`, and `LinkedList`.

### Initialization, allocation, and ownership transfer

- Zeroed `Box`, `Rc`, and `Arc` allocation returns `MaybeUninit`; call `assume_init` only for valid all-zero representations.
- `MaybeUninit` slice and array APIs support whole-buffer initialization and storage conversion.
- `Vec::into_raw_parts` and `String::into_raw_parts` transfer pointer, length, and capacity without freeing.
- `Layout` has stable composition and dangling-pointer helpers for allocator work.

### I/O, locking, and formatting

- `File` has shared/exclusive locking operations from 1.89.0.
- `RwLockWriteGuard::downgrade` atomically converts a write guard to a read guard from 1.92.0.
- `std::fmt::from_fn` creates formatting values without a dedicated wrapper type from 1.93.0 and is const-capable from 1.95.0.
- Unix stream writes suppress broken-pipe signals; Windows socket shutdown now yields `BrokenPipe` on a subsequent write.

### Const evaluation

Many pointer, pinning, numeric, slice, string, path, cell, formatting, and collection-view operations became const-capable. Check [standard-library.md](references/standard-library.md) for exact API names and minimum releases; runtime stability does not imply const stability.

## Target, toolchain, and documentation checks

- Query the host with `rustc --print host-tuple`, or use Cargo's portable `host-tuple` target.
- Review target tiers and platform baselines before assuming artifacts, host tools, tests, or native libraries.
- External LLVM minimums rise across these releases; match the compiler version before custom-building rustc.
- Cross-target doctests run through configured runners, so failures previously skipped can surface.
- Rustdoc target ignores, output controls, stricter attributes, deprecation Markdown, path remapping, and combined Edition 2024 doctests are detailed in [docs-tests-and-formatting.md](references/docs-tests-and-formatting.md).
