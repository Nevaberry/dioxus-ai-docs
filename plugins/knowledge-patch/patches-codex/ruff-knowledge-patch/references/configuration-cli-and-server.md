# Configuration, CLI, and Server

## Target-version resolution

The announced inference of Python version from `requires-python` when
`target-version` is unset did not ship in 0.10.0; it first shipped in 0.11.0
(0.10.0-guide).

Ruff resolves the complete chain of `extend`ed configuration files before
falling back to a default Python version. A `target-version` inherited from an
extended file therefore takes effect instead of an earlier default fallback
(0.15.0).

Ruff advanced its implicit default and latest Python-version settings for
Python 3.14. Pin the project version when behavior must remain fixed (0.14.0):

```toml
[tool.ruff]
target-version = "py312"
```

## Typing-related fix configuration

Disable generated imports from `typing_extensions` with (0.11.0):

```toml
[tool.ruff.lint]
typing-extensions = false
```

When `lint.future-annotations` is enabled, fixes for `TC001`, `TC002`, `TC003`,
`RUF013`, and `UP037` may insert `from __future__ import annotations`. This can
move more imports under `TYPE_CHECKING`, use PEP 604 unions before Python 3.10,
or unquote more annotations (0.13.0-guide):

```toml
[tool.ruff.lint]
future-annotations = true
```

In preview, fixes for `UP006`, `UP007`, and `UP045` may also insert the future
import (0.15.0).

## Plugin-specific options

For `flake8-builtins`, `lint.flake8-builtins.strict-checking` now defaults to
`false`, not `true`. Options formerly prefixed with `builtins-` are deprecated;
for example, replace `builtins-allowed-modules` with `allowed-modules`
(0.10.0).

Import sorting recognizes `numpy.typing as npt` as a default
`flake8-import-conventions` alias, so `ICN001` accepts it without custom alias
configuration (0.11.0). Import sorting also supports configurable
section-heading comments (0.15.0).

## Formatting command behavior

`ruff format --exit-non-zero-on-format` writes formatting changes but returns a
non-zero exit code when it changed files (0.11.0):

```console
ruff format --exit-non-zero-on-format .
```

`ruff format --check` accepts the linter's output formats, including the
`github` and `gitlab` CI annotation formats (0.16.0-guide):

```console
ruff format --check --output-format github .
```

Both `ruff check` and `ruff format --check` include fix diffs in their output.
Update wrappers that consume the human-readable text (0.16.0-guide).

## Watch mode

`ruff check --watch` respects `--output-format` and defaults to `full`
(0.15.0).

## JSON compatibility

JSON consumers must accept `null` for all of these diagnostic fields rather
than relying on empty strings or row-1/column-1 placeholders
(0.16.0-guide):

- `filename`;
- `location` and `end_location`; and
- `fix.edits[].location` and `fix.edits[].end_location`.

## Language-server logs and code actions

Server logging is controlled solely by `logLevel`, which defaults to `info`.
The LSP `trace` value no longer turns logging on or off. Code-action requests
ignore diagnostics emitted by other sources (0.9.0).

`ruff.printDebugInformation` no longer produces logging output (0.10.0).

The Ruff server can use `uv` as an alternative formatter backend (0.13.0).

The language server supports Markdown formatting and configured extension
mapping (0.15.0). It later added TOML linting, correct indexing for excluded
nested Ruff workspaces, and graceful handling of unknown enumeration values in
LSP messages (0.16.1).

## Human-readable names in integrations

Preview output, LSP hovers, and code actions prefer human-readable rule names,
and `ruff rule` accepts them. Unknown selectors warn instead of failing
(0.15.0).

Preview mode provides an option to opt out of human-readable names, which lets
integrations retain code-oriented names while using other preview behavior
(0.16.1).
