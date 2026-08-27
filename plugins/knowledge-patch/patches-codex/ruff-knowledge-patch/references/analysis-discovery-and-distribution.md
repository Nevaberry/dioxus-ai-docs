# Analysis, Discovery, and Distribution

## Dependency-graph analysis

`ruff analyze graph` accepts a virtual environment so imports can resolve from
that environment (since 0.11.0).

Graph analysis can skip imports inside `TYPE_CHECKING` blocks, works with
Jupyter notebooks, and uses configured `src` directories for import resolution
(since 0.14.0).

## File discovery and extension mapping

Preview discovery includes `*.pyw` by default (since 0.14.0).

Preview formatting discovers Markdown files by default and formats labeled
Python blocks, including `pycon` and Quarto language markers. Unlabeled blocks
are not formatted. The former implicit `.qmd` special case was removed; map it
when needed (0.15.0):

```toml
[tool.ruff]
extension = { qmd = "markdown" }
```

Configured extensions participate in discovery, code-block language selection,
and server handling. Markdown formatting later became the non-preview default
(0.16.0-guide).

## Configuration locations and workspace indexing

Ruff no longer searches `~/Library/Application Support/ruff/ruff.toml` for
macOS user configuration. Use the XDG location, normally
`~/.config/ruff/ruff.toml` (0.13.0-guide).

The language server correctly indexes excluded nested Ruff workspaces and also
lints TOML files (0.16.1).

## Container images

The floating `ruff:alpine` image moved from Alpine 3.20 to Alpine 3.21, and
`ruff:alpine3.20` stopped receiving updates (0.10.0-guide).

It later moved to Alpine 3.23. The `ruff:debian` and `ruff:debian-slim` images
use Debian 13 “Trixie” (0.15.0).

Pin a distro-specific tag when the base OS is part of the deployment contract;
do not assume a floating image retains its former packages or ABI.

## Source builds and published artifacts

Source distributions stopped including `rust-toolchain.toml`, allowing
downstream packagers to choose a toolchain compatible with Ruff's minimum Rust
version rather than the release-build toolchain (0.12.0).

Source builds now require Rust 1.91 or newer. Release binaries no longer include
big-endian `ppc64`, and WASM artifacts are no longer attached to GitHub releases
(0.15.0).

Version 0.14.12 was published to PyPI without a GitHub release or tag because of
a WASM publishing issue. Version 0.14.13 has identical contents and is the
follow-up release (0.14.0).
