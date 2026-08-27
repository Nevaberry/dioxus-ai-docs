# CLI, server, analysis, and distribution

Use this reference for command behavior, machine output, editor integrations,
dependency graphs, containers, release artifacts, and source builds.

## CLI behavior and output

### Format and fail

Since 0.11.0, `ruff format --exit-non-zero-on-format` writes formatting changes
and returns a nonzero status when it modifies files:

```console
ruff format --exit-non-zero-on-format .
```

This differs from a check-only command because the working tree is changed.

### Watch output

In 0.15.0, `ruff check --watch` respects `--output-format` and defaults to the
`full` format.

### Fix diffs and format-check output

In 0.16.0-guide, `ruff check` and `ruff format --check` include fix diffs in
human-readable output. Scripts that scrape logs should not assume the earlier
shape. `ruff format --check` also accepts linter output formats, including CI
annotation formats:

```console
ruff format --check --output-format github .
```

### Nullable JSON fields

Also in 0.16.0-guide, JSON output can use `null` for `filename`, `location`,
`end_location`, `fix.edits[].location`, and `fix.edits[].end_location`. These
values replace placeholder empty strings or row-1/column-1 locations. JSON
schemas and consumers must make every listed field nullable.

## Language server

### Logging and code actions

In 0.9.0, server logging is controlled only by `logLevel`, which defaults to
`info`. The LSP `trace` setting no longer toggles logging. Code-action requests
ignore diagnostics produced by other sources.

In 0.10.0, `ruff.printDebugInformation` no longer produces logging output.

### Formatter backend and file coverage

The 0.13.0 server can use `uv` as an alternative formatter backend.

Preview Markdown formatting in 0.15.0 is also supported by the language server.
Configured extension mappings participate in later server handling.

In 0.16.1, the server lints TOML files, correctly indexes excluded nested Ruff
workspaces, and handles unknown enumeration values in LSP messages without
failing.

### Human-readable rule names

In 0.15.0 preview, LSP hovers and code actions prefer human-readable rule names.
The 0.16.1 preview option can opt out and retain code-oriented names while
leaving other preview features on.

## Dependency-graph analysis

Since 0.11.0, `ruff analyze graph` accepts a virtual environment, allowing it
to resolve imports from that environment.

In 0.14.0, dependency analysis can skip imports inside `TYPE_CHECKING` blocks.
Graphs work with Jupyter notebooks and use configured `src` directories when
resolving imports.

Use the same environment, source roots, and guard conventions as the project to
avoid graph classifications that differ from runtime or lint behavior.

## Container images

In 0.10.0-guide, `ruff:alpine` moves from Alpine 3.20 to 3.21, and the
`ruff:alpine3.20` image stops receiving updates.

In 0.15.0:

- `ruff:alpine` moves to Alpine 3.23;
- `ruff:debian` and `ruff:debian-slim` use Debian 13 “Trixie”; and
- deployment assumptions based on the prior base images should be retested.

## Binaries, WASM, and releases

Ruff 0.14.12 was published on PyPI without a corresponding GitHub release or
tag because of a WASM publishing issue. Version 0.14.13 has identical contents
and is the follow-up. Release mirroring must tolerate that missing tag.

In 0.15.0, release binaries no longer include big-endian `ppc64`, and WASM
artifacts are no longer attached to GitHub releases. Consumers of those
artifacts need a different distribution path or supported target.

## Source builds

Source distributions stop pinning the release Rust toolchain in 0.12.0: they no
longer contain `rust-toolchain.toml`. Downstream packagers may use a toolchain
compatible with Ruff's minimum supported Rust version rather than the higher
release-build toolchain.

In 0.15.0, source builds require Rust 1.91 or newer. Reconcile this minimum with
distribution toolchains before upgrading build recipes.
