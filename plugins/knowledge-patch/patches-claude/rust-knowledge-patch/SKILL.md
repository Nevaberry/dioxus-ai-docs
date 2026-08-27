---
name: rust-knowledge-patch
description: Rust
version: "1.97.0"
license: MIT
metadata:
  author: Nevaberry
---


# Rust Knowledge Patch

Use this patch when changing Rust source, Cargo configuration, edition settings,
unsafe or FFI code, platform targets, documentation tests, or compiler policy.

## Reference index

| Reference | Topics |
| --- | --- |
| [edition-2024.md](references/edition-2024.md) | Edition migration, unsafe requirements, capture and temporary scopes, patterns, macros, doctests, rustfmt |
| [language-and-macros.md](references/language-and-macros.md) | Traits, closures, opaque types, inference, patterns, macros, name resolution, lints, rejected code |
| [safety-ffi-and-low-level.md](references/safety-ffi-and-low-level.md) | Pointer provenance, pinning, allocation, atomics, FFI, ABIs, intrinsics, inline assembly |
| [standard-library.md](references/standard-library.md) | Collections, iterators, ranges, I/O, paths, text, numerics, const APIs, behavior contracts |
| [cargo.md](references/cargo.md) | Resolution, configuration, builds, workspaces, publishing, lockfiles, registries, cache, environment variables |
| [targets-and-toolchains.md](references/targets-and-toolchains.md) | Linkers, symbol mangling, WebAssembly, target tiers, platform baselines, LLVM, native linking |
| [docs-tests-and-formatting.md](references/docs-tests-and-formatting.md) | Rustdoc, doctests, libtest, rustfmt, source locations, diagnostics, path remapping |

## Apply this patch

1. Identify the crate edition, declared `rust-version`, compilation targets,
   panic strategy, and whether the build invokes Cargo or rustc directly.
2. Check the declared MSRV before adopting versioned syntax, APIs, Cargo keys,
   or TOML forms.
3. Check the breaking-change sections below before adopting newer APIs, then
   read the topic reference that covers the affected subsystem.
4. For unsafe, FFI, linker, or custom-target work, validate the target-specific
   requirements instead of relying on host behavior.

## Breaking changes and migrations

### Treat the 2024 edition as a semantic migration

- Run `cargo fix --edition`, then review its edits. It does not update doctests
  or uninvoked exported macro bodies, and some rewrites preserve old behavior
  rather than choosing the desired new behavior.
- Write `unsafe extern` blocks; mark explicitly safe foreign items `safe`.
  Wrap `no_mangle`, `export_name`, and `link_section` in `unsafe(...)`, and put
  unsafe operations inside explicit blocks even within an `unsafe fn`.
- Audit calls to `std::env::set_var`, `std::env::remove_var`, and deprecated
  `CommandExt::before_exec`; they are unsafe in this edition and have no general
  safe replacement.
- Replace references to `static mut` with raw references or synchronization;
  implicit references such as formatting or method calls are denied too.
- Audit return-position `impl Trait` capture, never-type fallback, boxed-slice
  `.into_iter()`, match ergonomics, `if let` scrutinee temporaries, and
  tail-expression destruction order.
- Review macro match order because `expr` accepts const blocks and `_`; retain
  `expr_2021` only where the narrower grammar is intentional.
- Rename `gen` identifiers or use `r#gen`, and separate guarded-string `#`
  tokens with whitespace.
- Resolver v3 is the default for edition 2024.
- Read [edition-2024.md](references/edition-2024.md) before changing a crate's
  edition.

### Compiler acceptance and observable behavior changed

- Coherence uses the next-generation trait solver from 1.84.0, so some impl
  pairs previously accepted can become conflicting.
- Never-type fallback lints are deny-by-default on every edition from 1.92.0
  when the affected crate is built directly.
- Pattern capture, binding, and destruction behavior changed. Add focused tests
  when partial moves or visible destructor effects matter.
- Trailing semicolons in macro expansions, missing fragment specifiers,
  malformed attributes, unsupported ABI strings, invalid export/link
  attributes, and several formerly tolerated syntax forms now warn or fail.
- Custom JSON target specifications require nightly options from 1.95.0.
- WebAssembly unresolved symbols fail linking from 1.96.0; either declare the
  import explicitly or intentionally pass the linker opt-out flag.
- Read [language-and-macros.md](references/language-and-macros.md) and
  [targets-and-toolchains.md](references/targets-and-toolchains.md) during
  upgrade triage.

### ABI, linking, and symbol expectations changed

- `wasm32-unknown-unknown` adopted the standards-compliant C ABI in 1.89.0;
  rebuild both sides and do not mix objects made under the old convention.
- `x86_64-unknown-linux-gnu` uses LLD by default from 1.90.0. Disable the `lld`
  linker feature only for confirmed BFD-specific requirements.
- Linux `panic=abort` builds retain unwind tables from 1.92.0 unless
  `-Cforce-unwind-tables=no` is set.
- Stable rustc emits v0 Rust symbols by default from 1.97.0. Update debuggers,
  profilers, demanglers, and backtrace expectations.
- Enum layouts without explicit `repr` are not stable contracts; observable
  layout changes occurred again in 1.97.0.
- Read [safety-ffi-and-low-level.md](references/safety-ffi-and-low-level.md)
  before altering FFI or unsafe code.

### Pinning and pointer assumptions need review

- `pin!(&mut_value)` no longer deref-coerces in 1.97.0; make the intended
  pointee explicit with a reborrow or `Pin::new`/`Pin::as_mut`.
- Forming a raw reference through a raw pointer or to a union field is safe,
  but dereferencing the result still needs valid unsafe reasoning.
- Debug null-pointer checks disappear when debug assertions are disabled and
  are never a soundness guarantee.
- Prefer exposed- or strict-provenance APIs over integer transmutation when
  reconstructing or tagging pointers.

### Cargo workflows and policy changed

- Resolver v3 can prefer dependency versions compatible with declared
  `rust-version`; use the configuration override for latest-dependency CI.
- Automatic cache collection can remove stale downloads. Disable it when Cargo
  versions predating access-time tracking share the cache.
- `cargo publish --workspace` publishes in dependency order but is not atomic.
- `cargo publish` does not reliably leave a local `.crate`; run `cargo package`
  when the archive is required.
- Published packages always include `Cargo.lock`;
  `cargo package --exclude-lockfile` skips lockfile verification when creating
  a local package.
- `build.build-dir`, `resolver.lockfile-path`, configuration `include`,
  target-specific `rustdocflags`, and `build.warnings` address separate build
  layout and policy needs.
- Prefer prompts, stdin, environment variables, or registry credential
  providers over command-line tokens.
- Read [cargo.md](references/cargo.md) before changing CI, packaging, registry,
  or workspace automation.

## High-value language features

### Async closures, traits, and opaque types

- `async || {}` and the `AsyncFn*` traits support futures borrowing closure
  captures and higher-ranked async callbacks (1.85.0).
- Trait-object upcasting to a supertrait is stable for references, smart
  pointers, and raw pointers (1.86.0); raw trait-object pointers still require
  a valid vtable.
- Trait return-position `impl Trait` supports precise `use<...>` capture
  (1.87.0). Every in-scope type and const parameter, including `Self`, must be
  named; lifetimes may be omitted from the capture set.

```rust
trait Super {}
trait Sub: Super {}

fn upcast(value: &dyn Sub) -> &dyn Super { value }

trait Value {
    fn value<'a>(&'a self) -> impl Sized + use<Self>;
}
```

### Conditions, configuration, and patterns

- Edition 2024 supports `let` chains in `if` and `while` from 1.88.0.
- Match arms support `if let` guards from 1.95.0; guard patterns do not
  contribute to exhaustiveness.
- `cfg_select!` selects the first matching item or expression arm from 1.95.0.
- `assert_matches!` and `debug_assert_matches!` are stable from 1.96.0, print
  the failed value with `Debug`, and require an explicit import.

```rust
match value {
    Some(x) if let Ok(y) = compute(x) => use_pair(x, y),
    _ => {}
}
```

### Ranges and slices

- `array_windows` yields overlapping `&[T; N]` windows from 1.94.0.
- `core::range` provides copyable range values with separate iterator types;
  range syntax still constructs legacy `core::ops` ranges.
- Prefer `RangeBounds` in public APIs that should accept both range families.

```rust
use core::range::Range;

#[derive(Clone, Copy)]
struct Span(Range<usize>);
```

## High-value library features

### Multi-borrowing, extraction, and locking

- Slices and `HashMap` support checked and unchecked disjoint mutable access
  from 1.86.0.
- `Vec`, `LinkedList`, `HashMap`, `HashSet`, `BTreeMap`, and `BTreeSet` have
  distinct `extract_if` signatures; check whether the type accepts a range.
- `File` provides advisory shared/exclusive locking from 1.89.0.
- `RwLockWriteGuard::downgrade` atomically produces a read guard from 1.92.0.

### Process, allocation, and formatting primitives

- `std::io::pipe()` integrates anonymous pipes with `Command` and `Stdio` from
  1.87.0. Drop/move every writer and drain output before waiting to avoid a
  full-pipe deadlock.
- `Box<MaybeUninit<T>>::write`, zeroed smart-pointer allocation, slice-wide
  `MaybeUninit` operations, and raw-parts decomposition cover staged
  initialization and ownership transfer; callers of `assume_init` must assert
  the zeroed representation is valid.
- `std::fmt::from_fn` creates a `Display` and `Debug` value backed by a
  formatting callback from 1.93.0.

## Target and documentation checks

- Query the host with `rustc --print host-tuple`, or use Cargo's portable
  `host-tuple` target where supported.
- Check target tiers before assuming rustup artifacts, host tools, or test-suite
  guarantees.
- Cross-target doctests can run through the configured runner; tests previously
  skipped may now fail.
- Rustdoc target ignores, standalone doctests, external runners, emitted-path
  remapping, and formatting changes are detailed in
  [docs-tests-and-formatting.md](references/docs-tests-and-formatting.md).
