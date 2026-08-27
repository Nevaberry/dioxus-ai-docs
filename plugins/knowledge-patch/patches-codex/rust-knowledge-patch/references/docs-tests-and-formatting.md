# Documentation, Tests, and Formatting

## Libtest command-line changes

- The libtest `--logfile` option is deprecated since 1.86.0.
- The `--nocapture` spelling is deprecated since 1.88.0; use `--no-capture`.

## Targeted and cross-compiled doctests

### Target ignores and runners

Since 1.88.0, rustdoc supports target-name `ignore-*` attributes for doctests. Stable `--test-runtool` and `--test-runtool-arg` execute doctests through an emulator or other runner.

Since 1.89.0, `cargo test --doc --target <triple>` actually runs cross-target doctests through the target's configured runner. Tests previously skipped can therefore surface target-specific failures.

### Edition 2024 compilation model

Compatible Edition 2024 doctests normally compile into a shared binary but still execute in separate processes. Use `standalone_crate` for examples depending on generated crate structure, source positions, or type names. Nested doctest includes and other migration details are in [edition-2024.md](edition-2024.md).

## Rustdoc attributes and rendered Markdown

- Since 1.93.0, `#![doc(document_private_items)]` is removed; request private items through rustdoc or Cargo command-line options.
- Also since 1.93.0, malformed `html_favicon_url`, `html_logo_url`, `html_playground_url`, `issue_tracker_base_url`, and `html_no_source` trigger deny-by-default `rustdoc::invalid_doc_attributes`.
- Since 1.96.0, deprecation notes render as normal Markdown. Multiline source can collapse into one line unless it uses Markdown's two-trailing-spaces hard break.

## Paths, remapping, and output

- Since 1.94.0, compiler-emitted paths preserve their original relativeness and `--remap-path-prefix`; downstream diagnostics can show local Cargo dependency paths as relative.
- Since 1.95.0, stable rustc's `--remap-path-scope` selects the output scopes in which paths are remapped.
- Since 1.97.0, rustdoc's `--emit` and `--remap-path-prefix` flags are stable, enabling stable-toolchain artifact selection and embedded-path remapping.

## Test binary discovery

Since 1.94.0, Cargo sets `CARGO_BIN_EXE_<crate>` in an integration test's runtime environment. Prefer `std::env::var` when the test needs the built executable path at runtime.

## Formatting

Rustfmt's Edition 2024 `style_edition` can be pinned independently of parsing. Put `style_edition = "2024"` in `rustfmt.toml`, or pass `--style-edition 2024`, so direct editor runs and `cargo fmt` agree.
