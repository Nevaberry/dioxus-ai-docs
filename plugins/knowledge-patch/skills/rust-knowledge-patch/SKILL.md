---
name: rust-knowledge-patch
description: Rust 1.84.0–1.97.0 compatibility. Use for Rust work.
license: MIT
version: 1.97.0
metadata:
  author: Nevaberry
---

# Rust Knowledge Patch

Baseline: Rust through 1.84.x (2021 Edition); covers 1.84.0–1.97.0, Rust 2024 Edition, Cargo additions, and relevant point-release compatibility notes.

## Reference index

| Reference | Topics |
| --- | --- |
| [edition-2024.md](references/edition-2024.md) | Edition migration, syntax, match ergonomics, temporary scope, unsafe requirements, resolver 3, doctests, rustfmt |
| [language-and-macros.md](references/language-and-macros.md) | Traits, opaque types, inference, patterns, macros, name resolution, lints, newly rejected code |
| [safety-ffi-and-low-level.md](references/safety-ffi-and-low-level.md) | Raw pointers, provenance, pinning, atomics, allocation, FFI, ABIs, intrinsics, inline assembly |
| [standard-library.md](references/standard-library.md) | Collections, iterators, ranges, I/O, paths, text, numerics, const stabilization, behavior contracts |
| [cargo.md](references/cargo.md) | Configuration, builds, workspaces, publishing, lockfiles, registries, cache, metadata, environment variables |
| [targets-and-toolchains.md](references/targets-and-toolchains.md) | Linkers, symbol mangling, WebAssembly, target tiers, platform baselines, LLVM, native linking |
| [docs-tests-and-formatting.md](references/docs-tests-and-formatting.md) | Rustdoc, doctests, libtest, rustfmt, diagnostic path handling |

## Apply this patch

1. Identify the crate edition, MSRV, compilation targets, panic strategy, and whether Cargo or rustc is invoked directly.
2. Check the breaking-change sections below before adopting new APIs.
3. Read only the topic references relevant to the task; they hold the complete compatibility details and stable API inventory.
4. Preserve an older MSRV unless the requested change intentionally raises it. New syntax, APIs, Cargo keys, and TOML 1.1 forms require the corresponding toolchain.
5. For unsafe, FFI, linker, or custom-target work, validate the target-specific preconditions instead of relying on host behavior.

## Breaking changes and migrations

### Rust 2024 is a semantic migration

- Run `cargo fix --edition`, then review every edit; several migrations insert syntax without proving safety or lifetime intent.
- Declare foreign blocks as `unsafe extern`, wrap `no_mangle`, `export_name`, and `link_section` as unsafe attributes, and put unsafe operations inside explicit blocks even within an `unsafe fn`.
- Replace references to `static mut` with synchronization or tightly scoped raw-pointer access.
- Audit never-type fallback, return-position `impl Trait` capture, boxed-slice `.into_iter()`, match ergonomics, `if let` scrutinee temporaries, and tail-expression temporary destruction.
- Review macro match order because 2024 `expr` fragments accept const blocks and `_`; use `expr_2021` only when the old grammar is required.
- Rename `gen` identifiers or use `r#gen`; separate guarded-string `#` tokens with whitespace.
- Expect resolver 3 for 2024 packages, but configure it explicitly in a virtual workspace.
- Read [edition-2024.md](references/edition-2024.md) before changing a crate's edition.

### Compiler acceptance changed

- Trait overlap uses the next-generation solver (1.84.0), so upgrades may reject previously accepted unsound impl sets or accept newly provable disjoint sets.
- Never-type fallback lints become deny-by-default in 1.92.0 when building the affected crate directly.
- Pattern capture, binding, and destruction order changed in several releases; code with visible destructor effects or partial moves needs focused tests.
- Macro expansions with trailing semicolons, missing fragment specifiers, invalid export attributes, unsupported ABI strings, and several formerly tolerated syntactic forms now warn or fail.
- Custom JSON target specifications require nightly options as of 1.95.0.
- WebAssembly unresolved symbols fail linking as of 1.96.0; declare intentional imports explicitly.
- Read [language-and-macros.md](references/language-and-macros.md) and [targets-and-toolchains.md](references/targets-and-toolchains.md) during upgrade triage.

### ABI, linking, and symbol behavior changed

- `wasm32-unknown-unknown` switched to the standards-compliant C ABI in 1.89.0; do not mix objects built under the old and new conventions.
- `x86_64-unknown-linux-gnu` uses LLD by default from 1.90.0; opt out with `-Clinker-features=-lld` only for a confirmed incompatibility.
- Linux `panic=abort` builds retain unwind tables from 1.92.0 unless `-C force-unwind-tables=no` is set.
- Stable rustc emits v0 Rust symbols by default from 1.97.0; update debuggers, profilers, and backtrace expectations.
- The layouts of types without an explicit representation remain non-contractual; 1.96.0 and 1.97.0 include observable layout corrections or changes.
- Read [safety-ffi-and-low-level.md](references/safety-ffi-and-low-level.md) before altering FFI or unsafe code.

### Pinning and pointer assumptions need review

- `pin!(&mut_value)` no longer performs a dereference coercion in 1.97.0; make the intended pointee explicit.
- Raw-reference formation through a raw pointer and to a union field is safe, but dereferencing the result still requires valid unsafe reasoning.
- Debug null-pointer checks are not soundness checks and disappear when debug assertions are disabled.
- Use exposed-provenance APIs rather than integer transmutation when reconstructing pointers.

### Cargo workflows changed

- Cargo may automatically clean unused cache data from 1.88.0; disable it when old Cargo installations share entries that newer Cargo cannot observe.
- `cargo publish --workspace` publishes in dependency order but is not atomic (1.90.0).
- `cargo publish` no longer leaves a local `.crate`; use `cargo package` when that artifact is required.
- Published crates always include `Cargo.lock`, while `cargo package --exclude-lockfile` explicitly omits it from a package archive.
- Lockfile v4 is the default; declare the actual `package.rust-version` to preserve compatibility with Cargo older than 1.78.
- `build.build-dir`, `resolver.lockfile-path`, configuration `include`, target-specific `rustdocflags`, and `build.warnings` solve distinct build-layout and policy needs.
- Use registry credential providers instead of command-line publish tokens.
- Read [cargo.md](references/cargo.md) before changing CI, packaging, registry, or workspace automation.

## High-value language features

### Traits and opaque types

- Trait-object upcasting to a supertrait is stable from 1.86.0 for references, smart pointers, and raw pointers with valid vtables.
- Trait return-position `impl Trait` supports precise `use<...>` capture from 1.87.0.
- Associated types may repeat bounds from 1.92.0, and associated-item bounds now guide auto-trait and `Sized` reasoning.

```rust
trait Super {}
trait Sub: Super {}

fn upcast(value: &dyn Sub) -> &dyn Super {
    value
}

trait Value {
    fn value<'a>(&'a self) -> impl Sized + use<Self>;
}
```

### Conditions, patterns, and configuration

- Edition 2024 supports `let` chains in `if` and `while`; 1.95.0 adds `if let` match guards.
- `cfg_select!` chooses the first matching item or expression arm from 1.95.0.
- `assert_matches!` and `debug_assert_matches!` provide pattern failures with `Debug` output from 1.96.0; import them explicitly.

```rust
match value {
    Some(x) if let Ok(y) = compute(x) => use_pair(x, y),
    _ => {}
}
```

### Ranges and slices

- `array_windows` yields overlapping `&[T; N]` windows from 1.94.0.
- `core::range` introduces copyable range values whose iterator types implement iteration; range syntax still constructs legacy `core::ops` ranges.
- Use `RangeBounds` in public APIs that should accept both range families.

```rust
use core::range::Range;

#[derive(Clone, Copy)]
struct Span(Range<usize>);
```

## High-value library features

### Multi-borrowing and extraction

- Slices and `HashMap` support checked and unchecked disjoint mutable access from 1.86.0.
- `Vec`, `LinkedList`, `BTreeMap`, and `BTreeSet` have stable `extract_if` variants across 1.87.0 and 1.91.0.
- `File` has portable shared/exclusive locking operations from 1.89.0; `RwLockWriteGuard::downgrade` is stable from 1.92.0.

### Process and allocation primitives

- `std::io::pipe()` integrates anonymous pipes with `Command` and `Stdio` from 1.87.0; drain output before waiting to avoid a full-pipe deadlock.
- `Box<MaybeUninit<T>>::write`, slice-wide `MaybeUninit` operations, zeroed smart-pointer allocation, and raw-parts decomposition cover common staged-initialization and ownership-transfer tasks.
- `std::fmt::from_fn` creates a display value backed by a formatting callback from 1.93.0.

### Const evaluation

- Releases 1.84.0–1.97.0 make many pointer, pinning, numeric, collection-view, string, path, cell, slice, formatting, and character operations const-capable.
- Check [standard-library.md](references/standard-library.md) for the exact method and minimum release instead of assuming the runtime-stable API is const-stable.

## Target and documentation checks

- Query the host triple with `rustc --print host-tuple`, or use Cargo's portable `host-tuple` target where supported.
- Review target tier changes before assuming rustup artifacts, host tools, or test guarantees.
- Cross-target doctests now run through configured runners; target-specific failures that were previously skipped may surface.
- Rustdoc target ignores, external doctest runners, search improvements, attribute validation, and emitted-path remapping are detailed in [docs-tests-and-formatting.md](references/docs-tests-and-formatting.md).

## Covered batches

Included versioned batches: 1.84.0, edition-2024, 1.85.0, 1.86.0, 1.87.0, 1.88.0, 1.89.0, 1.90.0, 1.91.0, 1.92.0, 1.93.0, 1.94.0, 1.95.0, 1.96.0, and 1.97.0. Cargo and Rust 2024 supplemental additions are integrated by topic.
