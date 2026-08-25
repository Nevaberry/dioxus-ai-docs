---
name: ruff-knowledge-patch
description: Ruff
version: 0.16.0
license: MIT
metadata:
  author: Nevaberry
---


# Ruff Knowledge Patch

Use this skill when configuring, upgrading, integrating, or debugging Ruff.
Start with the quick references below, then open the topic reference that
matches the task. Treat project configuration, installed behavior, and test
results as authoritative when they differ from this guidance.

## Reference index

| Reference | Topics |
| --- | --- |
| [Analysis, Discovery, and Distribution](references/analysis-discovery-and-distribution.md) | Dependency graphs, file discovery, containers, release artifacts, and source builds |
| [Configuration, CLI, and Server](references/configuration-cli-and-server.md) | Target versions, configuration inheritance, command output, JSON, watch mode, and language-server behavior |
| [Fixes and Safety](references/fixes-and-safety.md) | Fix availability, safety classifications, comment preservation, and semantic hazards |
| [Formatting and Syntax](references/formatting-and-syntax.md) | Stable and preview formatting, syntax validation, Markdown, f-strings, and Python-version parsing |
| [Rule Behavior](references/rule-behavior.md) | Changed diagnostics, expanded detection, special cases, and preview rules |
| [Rule Lifecycle and Selection](references/rule-lifecycle-and-selection.md) | Stable, preview, deprecated, removed, and recoded rules; defaults and suppressions |

## Upgrade triage

Check these changes first when an upgrade creates a large or surprising diff:

1. Pin `target-version` to the project's actual Python version. Implicit
   Python-version defaults have changed, and syntax validation may use a
   different default from ordinary lint-rule application.
2. Pin `lint.select` if the project relies on an established rule set. The
   default selection is now far larger and is not a strict superset of the old
   defaults.
3. Expect `ruff format` to process labeled Python blocks in Markdown by
   default. Map nonstandard extensions explicitly.
4. Review deprecated or removed rule codes, Airflow code migrations, the
   `UP007`/`UP045` split, and the `RUF025` to `RUF037` move.
5. Review autofixes classified as unsafe before applying them in bulk,
   especially fixes that remove comments or change expression types.
6. Update integrations that parse human-readable output or JSON. Check output
   includes diffs, and several JSON location fields are nullable.

## Quick reference: default rule expansion

Ruff enables 413 rules by default. This is primarily an expansion from 59,
but 18 opinionated pycodestyle and Pyflakes rules are no longer implicit.
Projects that need a fixed policy should configure it rather than inherit the
moving default:

```toml
[tool.ruff.lint]
select = ["E4", "E7", "E9", "F"]
```

Preview defaults had already expanded substantially and changed during the
preceding release series. Do not assume preview is simply stable selection
plus experimental rules; inspect effective settings when migrating.

## Quick reference: suppression migration

Ruff accepts `ruff: ignore` on a diagnostic line or the preceding line. Keep a
space after the colon in the canonical spelling:

```python
import math  # ruff: ignore[F401]

# ruff: ignore[F401]
import os
```

Block `ruff:disable` and `ruff:enable` ranges are stable. Preview mode also has
file-level, logical-line, and nested logical-line suppression forms, plus
human-readable rule names. See the lifecycle reference before converting a
large suppression set: preview includes migration checks and a generated
ignore command, and selector behavior differs from older code-only workflows.

File-level and inline `noqa` use a unified parser. Malformed forms that used to
work can now error. `PGH004` checks blanket file-level `noqa`, while `RUF100`
can report unused file-level and range suppressions.

## Quick reference: formatting scope

`ruff format` now formats Python code blocks in Markdown without requiring
preview. Labeled blocks include `python`, `pycon`, and Quarto markers;
unlabeled blocks remain untouched. If Quarto files should be formatted, map
their extension explicitly:

```toml
[tool.ruff]
extension = { qmd = "markdown" }
```

Formatter style has changed in two large steps. Expect diffs involving
f-strings, implicit concatenation, assertions, `match`, context managers,
method chains, lambdas, escaped triple quotes, and decorated classes in stubs.
Review formatting changes separately from semantic lint fixes.

## Quick reference: Python-version behavior

Always prefer an explicit target:

```toml
[tool.ruff]
target-version = "py312"
```

Syntax validation reports compiler errors during regular checks. If no target
is configured, version-related syntax checks can assume the latest supported
Python while other lint behavior uses the minimum supported Python. An
inherited target from an `extend` chain is resolved before Ruff falls back to
its default.

Python 3.14 is supported as a target. Preview supports Python 3.15 syntax,
including lazy imports and starred unpacking in comprehensions, and retains
the `lazy` keyword during import sorting.

## Quick reference: CI and machine output

Use format-and-fail when a job should write changes but still fail if it made
any:

```console
ruff format --exit-non-zero-on-format .
```

`ruff format --check` accepts linter output formats:

```console
ruff format --check --output-format github .
```

Check-mode output includes fix diffs. Treat human-readable output as display
text, not a stable parser protocol. In JSON, accept `null` for `filename`,
top-level start and end locations, and fix-edit start and end locations.

## Quick reference: fix policy

Safe and unsafe classifications have become more context-sensitive. Before
automating fixes:

- enable unsafe fixes only with review;
- preserve comments unless the rule explicitly guarantees it;
- watch for changes to expression or return types in pathlib rewrites;
- inspect typing rewrites that may insert a future import;
- do not expect every diagnostic to have a fix; some ambiguous or
  order-dependent cases deliberately skip one; and
- use the detailed safety matrix in [Fixes and Safety](references/fixes-and-safety.md).

With `lint.future-annotations = true`, fixes for selected typing rules can add
`from __future__ import annotations` at module scope:

```toml
[tool.ruff.lint]
future-annotations = true
```

Set `lint.typing-extensions = false` when generated fixes must not import from
`typing_extensions`.

## Quick reference: server integrations

Server logging is controlled only by `logLevel`, whose default is `info`; LSP
`trace` does not toggle logging. `ruff.printDebugInformation` no longer emits
logging output. Code-action requests ignore diagnostics from other sources.

The server can use `uv` as its formatter backend. It also formats Markdown,
lints TOML, indexes excluded nested Ruff workspaces, and tolerates unknown LSP
enumeration values. Preview users who need code-oriented names can opt out of
human-readable names.

## Task workflow

### Upgrading Ruff

1. Read the installed and target versions from the project manifest or lock.
2. Open the lifecycle reference and update removed, deprecated, or recoded
   selectors and suppressions.
3. Compare configured rule selection with current stable or preview defaults.
4. Open the formatting reference and run formatting in a clean worktree.
5. Open the safety reference before applying fixes.
6. Validate CI output parsers and editor integrations.

### Investigating a changed diagnostic

1. Identify the rule code and whether preview is enabled.
2. Check lifecycle status and any code migration.
3. Check the rule-behavior reference for new coverage or exemptions.
4. Check the configured target version and file type.
5. Reproduce with the project's effective configuration.
6. If accepting a fix, check its current safety conditions.

### Stabilizing automation

1. Pin `target-version` and `lint.select`.
2. Choose a machine-readable output format.
3. Make JSON fields nullable in the consumer schema.
4. Decide whether Markdown and mapped extensions belong in the format scope.
5. Decide whether preview human-readable names are acceptable.
6. Test watch, check, format-check, and language-server paths separately.

### Building dependency graphs

Use `ruff analyze graph` with a virtual environment when imports must resolve
against installed dependencies. Graph analysis can ignore imports under
`TYPE_CHECKING`, works with notebooks, and honors configured `src` directories.

## Verification checklist

- Confirm the effective target Python version.
- Confirm stable versus preview mode.
- Confirm the effective selected and ignored rules.
- Search configuration and suppressions for removed or migrated codes.
- Review formatter diffs in Python, stub, Markdown, and mapped-extension files.
- Review unsafe fixes and comment-removing edits.
- Exercise CI parsers against current text and JSON output.
- Exercise editor formatting, linting, code actions, and log settings.
- Keep project behavior and tests above general guidance when they conflict.
