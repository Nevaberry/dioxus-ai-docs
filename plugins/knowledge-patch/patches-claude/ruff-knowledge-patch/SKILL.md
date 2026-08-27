---
name: ruff-knowledge-patch
description: Ruff
version: "0.16.0"
license: MIT
metadata:
  author: Nevaberry
---


# Ruff Knowledge Patch

Load this skill when upgrading Ruff, changing lint or formatter configuration,
integrating Ruff with an editor or CI, or consuming machine-readable output.

Start with the migration checks, then open the matching topic reference. Treat
preview as opt-in and pin settings that must not change as defaults advance.

## Reference index

| Reference | Topics |
| --- | --- |
| [CLI, server, analysis, and distribution](references/cli-server-analysis-and-distribution.md) | CLI exit and output behavior, language server, dependency graphs, containers, binaries, source builds |
| [Formatting and syntax](references/formatting-and-syntax.md) | Stable and preview formatter styles, syntax validation, Python targets, Markdown formatting |
| [Lint rules](references/lint-rules.md) | Stable and preview rules, changed rule behavior, defaults, import and typing checks |
| [Migration and configuration](references/migration-and-configuration.md) | Renamed, recoded, deprecated, and removed rules; target inference; configuration discovery and inheritance |
| [Suppressions and fixes](references/suppressions-and-fixes.md) | `noqa`, `ruff: ignore`, range suppressions, fix availability, and safety classifications |

## Breaking-change checklist

Before changing the pinned Ruff version:

1. Pin `target-version` when the project cannot accept evolving Python syntax
   assumptions.
2. Pin `lint.select` when the project depends on a fixed default rule set,
   especially when enabling preview.
3. Search configuration, `noqa`, and other suppression comments for renamed,
   recoded, deprecated, or removed rule codes.
4. Run formatting separately; review f-strings, `match`, assertions, lambdas,
   method chains, stubs, and Markdown blocks.
5. Audit human-readable and JSON parsers; locations are not always populated.
6. Reassess every enabled unsafe fix; several fixes change classification
   based on operand types, comments, or the surrounding expression.
7. Check editor settings and server logs independently from command-line
   behavior.
8. For Ruff builds, verify container bases, Rust, artifacts, and source builds.

## High-impact migrations

### Pin the lint selection

The default and preview selections have expanded substantially and are not
strict supersets of earlier selections. A project that expects the traditional
Pyflakes and pycodestyle selection should state it explicitly:

```toml
[tool.ruff.lint]
select = ["E4", "E7", "E9", "F"]
```

Do not infer that every formerly implicit rule remains selected. Read
[Lint rules](references/lint-rules.md) for the exact default-selection changes
and the stable-rule lists.

### Pin Python semantics

Use the real minimum supported Python version rather than relying on fallback
behavior:

```toml
[tool.ruff]
target-version = "py312"
```

This controls version-gated syntax and influences lint and formatting choices.
Syntax diagnostics can use a different fallback from ordinary lint-rule
application when no target is configured. Extended configurations are resolved
before Ruff falls back to a default.

### Migrate rule identifiers deliberately

Rule codes have been split, moved, deprecated, and removed. Update all of the
following together:

- `select`, `extend-select`, `ignore`, and per-file ignores;
- inline and file-level suppression comments;
- editor filters and CI annotations;
- scripts that call `ruff rule` or parse diagnostics.

The most migration-sensitive changes include the `UP007`/`UP045` split,
`RUF025` moving to `RUF037`, `RUF035` moving to `S704`, Airflow rule-code
reorganization, and the removal of `S320`, `PD901`, and `UP038`. Exact behavior
and staging are in
[Migration and configuration](references/migration-and-configuration.md).

### Expect formatter diffs

Stable formatter styles have incorporated earlier preview changes. Upgrades
can alter f-string quoting and layout, assertion wrapping, `match` patterns,
single-manager `with` statements, lambdas, fluent method chains, stub spacing,
and Markdown Python blocks.

Run a formatter-only change before mixing an upgrade with semantic edits:

```console
ruff format --check .
ruff format .
```

Use `--exit-non-zero-on-format` only when the intended contract is "write the
changes, then fail if anything changed." See
[Formatting and syntax](references/formatting-and-syntax.md).

### Treat machine output as a versioned interface

JSON consumers must allow nullable filenames, diagnostic locations, and edit
locations. Human-readable check output can include fix diffs, and format-check
output supports linter-style output formats. Validate parsers and wrappers
against actual output rather than placeholder assumptions.

## Configuration quick reference

### Prevent fixes from importing `typing_extensions`

```toml
[tool.ruff.lint]
typing-extensions = false
```

Use this when generated changes must stay within the standard library or the
project's declared dependencies.

### Permit future-import insertion

```toml
[tool.ruff.lint]
future-annotations = true
```

This can let typing-related fixes insert `from __future__ import annotations`,
move imports under `TYPE_CHECKING`, use PEP 604 syntax on older targets, or
unquote annotations. Review module-level import changes.

### Map custom Markdown extensions

```toml
[tool.ruff]
extension = { qmd = "markdown" }
```

Extension mappings affect discovery, code-block language selection, and server
handling. Formatting Markdown may now occur without preview, so include
documentation changes in upgrade review.

### Preserve code-oriented names in preview

Preview output can prefer human-readable rule names. When integrating tools
that require rule codes, use the preview option that opts out of
human-readable names and test editor and CLI output together.

## Suppression quick reference

Ruff accepts a line-end or preceding-line `ruff: ignore` comment:

```python
import math  # ruff: ignore[F401]

# ruff: ignore[F401]
import os
```

Keep the canonical space after the colon. Block `ruff:disable` and
`ruff:enable` suppressions are stable, while logical-line and file-level forms,
human-readable names, and migration checks may still depend on preview.

Unified suppression parsing recognizes more valid comments but reports some
malformed comments that older parsing tolerated. File-level suppressions also
participate in blanket- and unused-suppression checks. See
[Suppressions and fixes](references/suppressions-and-fixes.md).

## Fix-safety workflow

Never equate "a fix exists" with "the fix is semantics-preserving." For an
upgrade or a new rule selection:

1. Run checks without fixes and save the diagnostic set.
2. Apply safe fixes first.
3. Review files containing comments, type-sensitive expressions, generators,
   context managers, path operations, and string conversions.
4. Apply unsafe fixes in small groups with tests.
5. Re-run Ruff and the project's test suite after each group.

Many classifications are conditional: a fix may be safe only for integers,
booleans, literals, comment-free expressions, typing-only contexts, or a
particular call shape. The exhaustive changes are cataloged in
[Suppressions and fixes](references/suppressions-and-fixes.md).

## Preview discipline

Preview is a bundle of evolving parser, formatter, rule, default-selection,
suppression, and output behavior. Enabling it for one feature can expose other
changes. Keep these controls explicit:

- `preview` itself;
- `target-version`;
- `lint.select` and ignores;
- formatter and Markdown extension settings;
- whether output uses codes or human-readable rule names;
- whether unsafe fixes are allowed.

When a preview diagnostic becomes stable, remove workarounds only after
checking whether its code, default selection, fix safety, or scope also changed.

## Language-server checks

Server logging is controlled by the dedicated log-level setting, not LSP trace.
Code actions ignore diagnostics from other sources. Debug-information commands
and formatter-backend choices have changed, and the server now covers Markdown
and TOML in more situations.

When command-line and editor results differ, compare:

- the resolved workspace root and nested workspace exclusions;
- target and inherited configuration;
- discovered extensions and file types;
- server formatter backend;
- diagnostic source and code-action ownership;
- log-level configuration.

Read [CLI, server, analysis, and distribution](references/cli-server-analysis-and-distribution.md) for complete integration notes.

## Dependency analysis

Dependency graphs can resolve imports from a supplied virtual environment,
skip imports guarded by `TYPE_CHECKING`, analyze notebooks, and use configured
source roots. Pass the same environment and source layout used by the project;
otherwise graph classification can differ from lint and runtime behavior.

## Verification after an upgrade

Run the project's normal commands, plus focused checks appropriate to the
features in use:

```console
ruff check .
ruff format --check .
ruff analyze graph .
```

Also inspect editor diagnostics, output fixtures, containers, and source builds.
A clean lint run does not validate formatter, server, schema, or packaging.
