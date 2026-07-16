# Documentation, Tests, and Formatting

Use this reference for rustdoc, doctest execution, libtest flags, rustfmt migration, and compiler-emitted path behavior. Edition-specific doctest aggregation and style-edition changes are in [edition-2024.md](edition-2024.md).

## Doctest target selection and execution

### Target-aware ignores

Rustdoc code blocks accept target-specific ignore attributes such as `ignore-x86_64` from 1.88.0. Use `ignore-*` only when the example truly cannot run for that target; keep ordinary `ignore` for examples that should never be tested.

### External run tools

Stable `--test-runtool` and `--test-runtool-arg` options select an external executable and arguments for running doctests from 1.88.0. This supports emulators such as QEMU without wrapping rustdoc itself.

### Cross-compiled doctests

`cargo test --doc --target <triple>` runs doctests from 1.89.0 instead of skipping them. Cargo uses the target's configured runner, so an upgrade can expose cross-target failures that were previously hidden.

The crate-level `#![doc(test(attr(...)))]` configuration is accepted on all targets from 1.89.0.

## Libtest command-line changes

- Positional `--logfile` is deprecated from 1.86.0.
- `--nocapture` is deprecated in favor of `--no-capture` from 1.88.0.

Update CI scripts before making warnings fatal.

## Rustdoc search

### Raw-pointer queries

Type-based search accepts raw-pointer forms such as `*const u8 ->` from 1.91.0. Functions using raw pointers also display correct signatures in search results.

### Partial identifiers

Search terms need only be valid as part of an identifier from 1.92.0, so a query may begin with a digit. When a trait item appears, corresponding impl items are hidden to leave space for more relevant inherent methods.

## Rustdoc attributes and Markdown

### Strict attribute validation

`#![doc(document_private_items)]` was removed in 1.93.0. Missing, unexpected, or wrongly typed values for the following attributes trigger deny-by-default `rustdoc::invalid_doc_attributes`:

- `html_favicon_url`
- `html_logo_url`
- `html_playground_url`
- `issue_tracker_base_url`
- `html_no_source`

### Deprecation-note Markdown

Deprecation notes use ordinary Markdown rendering from 1.96.0 rather than special preformatted output. A multiline note may collapse onto one line; add the normal two trailing spaces before a newline when a forced line break is intended.

## Rustdoc output and path remapping

Rustdoc stabilizes `--emit` and `--remap-path-prefix` in 1.97.0.

From 1.94.0, compiler-emitted paths preserve their original relative spelling and respect `--remap-path-prefix`. Cargo diagnostics for local path dependencies and workspace members therefore use relative rather than absolute paths. Do not write tooling that assumes diagnostics always carry absolute filesystem paths.

`rustc --remap-path-scope` is separately stable from 1.95.0 and controls where remapping affects paths embedded in binaries.

## Point-release tool fixes

Rust 1.93.1 fixes a keyword-recovery compiler crash that particularly affected rustfmt and a false positive in `clippy::panicking_unwrap`. It also repairs the distributed `wasm32-wasip2` file-descriptor leak described in the target reference.

## Rustfmt 2024 behavior

Rustfmt's parsing edition and style edition can be selected independently. The 2024 style changes layout and import sorting intentionally; follow the migration guidance in [edition-2024.md](edition-2024.md) and isolate broad formatting churn when reviewing semantic changes.
