# Documentation, Tests, and Formatting

## Doctest compilation and execution

### Combined edition-2024 doctests

Edition 2024 combines doctests into one executable. `1.85.0` accidentally fell
back to separate compilation; `1.85.1` restores combining and can reveal tests
that passed only in isolation.

Use a `standalone_crate` code-fence tag when a doctest must be compiled as its
own crate. Rustdoc already separates `compile_fail` and `edition*` tests,
tests with crate-level attributes, and macros using `$crate`; it cannot detect
code depending on its source line or generated module path. Run doctests after
migration because `cargo fix --edition` does not edit them. Full migration
details are in [edition-2024.md](edition-2024.md).

### Cross-target doctests

`doctest-xcompile` is stable from `1.89.0`. Consequently,
`cargo test --doc --target <other>` runs doctests through the target's Cargo
runner instead of silently skipping them.

From `1.88.0`, an `ignore-<target>` code-block info attribute skips a doctest
on a matching target. Rustdoc also accepts `--test-runtool` and
`--test-runtool-arg` to execute doctests through a wrapper such as qemu.

### Include paths in Markdown-backed docs

For docs loaded with `#![doc = include_str!("../README.md")]`, edition-2024
doctest calls to `include!`, `include_str!`, and `include_bytes!` resolve
relative to the Markdown file rather than the Rust source. This is not
automatically migrated.

At the language level, `include!` in expression position no longer strips a
leading shebang from the included file (`1.94.0`), so such an include may stop
compiling.

## Test harness changes

Libtest deprecates `--nocapture` in favor of `--no-capture` (`1.88.0`).

`#[bench]` outside `#![feature(custom_test_frameworks)]` becomes a hard error in
`1.88.0`. A meaningless `#[test]` placement, such as on a struct or trait
method, becomes an error in `1.93.0`, including when rustdoc processes it.

`#![reexport_test_harness_main]` was accidentally stable and is gated again in
`1.96.0`.

## `cfg(test)` validation

Rustc removes `test` from its built-in `--check-cfg` list in `1.85.0`.
Tools invoking rustc directly must pass `--check-cfg=cfg(test)` to avoid
`unexpected_cfgs` warnings. Cargo passes it unconditionally, so ordinary Cargo
builds are unaffected.

## Procedural macro source locations

Stable `proc_macro::Span` source-location methods arrive in `1.88.0`:

- `line()` and `column()` return `usize`;
- `start()` and `end()` return collapsed `Span` values rather than a stable
  `LineColumn` type;
- `file()` returns a rendered-path `String`;
- `local_file()` returns `Option<PathBuf>` and is `None` when there is no real
  local source, including remapped paths.

These methods no longer require nightly or a `proc-macro2` fallback.

## Rustdoc attributes and output

`#![doc(test(attr(...)))]` may be placed on a module rather than only the crate
root from `1.89.0`, allowing scoped doctest attributes.

From `1.93.0`, malformed crate-level attributes such as `html_logo_url` and
`issue_tracker_base_url` trigger deny-by-default
`rustdoc::invalid_doc_attributes`. `#![doc(document_private_items)]` is removed;
use the CLI flag.

Rustdoc renders deprecation notes as ordinary Markdown from `1.96.0` rather
than preformatted text. Multi-line notes may collapse onto one line unless the
source ends lines with two spaces.

Rustdoc stabilizes `--emit` and `--remap-path-prefix` in `1.97.0`.

## Compiler diagnostic paths

Diagnostic paths preserve their original relative or absolute form and honor
`--remap-path-prefix` from `1.94.0`. Path dependencies and workspace members
therefore appear as relative paths in downstream diagnostics where applicable;
tools parsing compiler output must accept that change.

Rustc `--remap-path-scope` (`1.95.0`) restricts prefix remapping to selected
outputs such as `macro`, `diagnostics`, `debuginfo`, or `object`; the default
remains all outputs.

## Rustfmt style editions

Rustfmt's formatting style edition is independent of the language edition. It
defaults to the crate edition and is configurable through `style_edition` in
`rustfmt.toml` or `--style-edition`.

The 2024 style changes sorting of raw identifiers, identifiers with numbers,
and `use` lists, plus block collapsing, tuple-field spacing, loop-closure
braces, comment and generic indentation, blank lines in `where` clauses, and
semicolons on control-flow expressions in match-arm blocks. Expect a broad
format-only diff; exact migration examples are in
[edition-2024.md](edition-2024.md).

## Point-release fixes affecting tools

- `1.93.1` fixes a parser ICE frequently triggered by rustfmt and a
  `clippy::panicking_unwrap` false positive on field access through implicit
  dereference.
- `1.94.1` fixes a Clippy ICE in `match_same_arms` and removes methods that were
  mistakenly added to the unsealed Windows `OpenOptionsExt` trait.

## Output-sensitive behavior

Raw-pointer `Debug` output includes pointer metadata from `1.87.0`, and format
width and precision are capped at 16 bits. Snapshot tests relying on the old
text must be updated.

Linker stderr from successful links is visible through `linker_messages` from
`1.97.0`; it is not escalated by `-Dwarnings` or Cargo `build.warnings`.
