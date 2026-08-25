# Formatting and syntax

Use this reference when an upgrade changes formatter output, syntax errors, or
file types selected for formatting.

## Stable formatter styles

### 2025 style

Ruff 0.9.0 uses the stabilized 2025 formatter style. Upgrades can produce diffs
in all of these cases:

- expressions inside f-string elements are formatted; inner strings can use
  alternate quotes, while hexadecimal casing in debug expressions is kept;
- quote style is chosen per literal in an implicitly concatenated f-string,
  and an implicit concatenation is joined into one literal when it fits;
- the `ISC001` incompatibility warning is removed;
- an `assert` message is preferably parenthesized instead of breaking the
  assertion expression;
- overlong `if` guards in `match` cases are automatically parenthesized, and
  `match` patterns are formatted more consistently;
- unnecessary parentheses around return type annotations are removed;
- an opening parenthesis stays on the same line as `if` in a comprehension
  whose condition begins with a comment;
- a single-context-manager `with` is formatted more consistently on Python
  3.8 and older; and
- docstring code blocks correctly account for width when
  `max-doc-code-line-length = "dynamic"`.

The formatter changes again in 0.10.0-guide: it no longer adds unnecessary
parentheses to a single-manager `with` statement with a trailing comment.

### 2026 style

The preview formatter behavior from the 0.14 series becomes the stable 2026
style in 0.15.0. Stable output can now:

- remove parentheses around multiple exception types on Python 3.14+;
- permit newlines after function headers without docstrings;
- avoid extra parentheses around long `match` patterns with `as` captures;
- format fluent method chains;
- keep lambda parameters on one line while parenthesizing an expanded body,
  while preserving parentheses required by the lambda body;
- omit extra spaces between escaped quotes and closing triple quotes; and
- enforce blank lines before decorated classes in stub files.

Ruff 0.15.9 also adds the `nested-string-quote-style` formatter option.

## F-strings and parser compatibility

Ruff 0.12.0 avoids placing a line break after a format specifier in a
multiline f-string. Python 3.13.4 made that break a syntax error, so upgrading
can change these f-strings even without other style changes.

Preview in 0.11.0 accepts `py314`, including deferred-annotation behavior and
Python 3.14's unparenthesized exception tuples. By 0.11.13, parser and formatter
support includes template strings:

```toml
[tool.ruff]
target-version = "py314"
```

Preview in 0.15.0 supports Python 3.15 lazy imports and PEP 798 star-unpacking
of comprehensions, validates lazy-import syntax, and preserves `lazy` during
import sorting. `TID254` can require or ban lazy imports, another preview check
detects eager evaluation of lazy imports, and `RUF017` uses starred unpacking
on Python 3.15+.

## Syntax validation

Preview checks in 0.11.0 report compile-time errors including:

- duplicate parameters or type parameters;
- invalid `match` patterns;
- illegal starred expressions and invalid annotations;
- module-level `nonlocal`; and
- assignment to or deletion of `__debug__`.

They version-gate PEP 701 f-strings, parenthesized context managers, starred
annotations and indexes, tuple unpacking in `for` iterators, and
unparenthesized exception tuples. If no Python version applies to a
version-related preview diagnostic, Ruff uses the latest supported version.

In 0.12.0, these checks become regular checks. They include CPython compiler
errors such as placing an irrefutable `match` pattern before the final case.
With no target configured, version-related syntax checks assume Python 3.13,
while other lint behavior assumes Python 3.9. Pin `target-version` to the
project's actual baseline.

Ruff 0.14.0 advances its implicit default and latest baselines for Python 3.14
and accepts Python 3.15 as a preview target. This can change syntax, rule, and
format decisions even if configuration did not otherwise change.

## Preview formatter corrections

In 0.11.0 preview, Ruff no longer adds trailing whitespace to a docstring after
an escaped quote. It also formats `match` cases using `[]` and `_` consistently.

The 0.14.0 preview behavior removes exception-tuple parentheses on Python
3.14+, permits header newlines, changes long `match` patterns, introduces fluent
chains, and revises lambda layout as described above. Later fixes preserve
parentheses required for lambda semantics.

## Markdown formatting

Preview formatting in 0.15.0 processes labeled Python blocks in Markdown,
including `pycon` and Quarto language markers, but leaves unlabeled blocks
untouched. The language server supports the same behavior. Markdown discovery
starts by default in preview in 0.15.5, and `.qmd` must be explicitly mapped:

```toml
[tool.ruff]
extension = { qmd = "markdown" }
```

In 0.16.0-guide, Python blocks in Markdown are formatted by default without a
preview opt-in. Include documentation files in formatter-diff review.

## Formatting commands

Since 0.11.0, this command writes changes but returns nonzero if it changes any
files:

```console
ruff format --exit-non-zero-on-format .
```

In 0.16.0-guide, `ruff format --check` supports linter output formats such as
`github` and `gitlab`:

```console
ruff format --check --output-format github .
```

Check-output changes can include fix diffs, so wrappers should not assume the
older human-readable shape.
