# Formatting and Syntax

## Stable formatter behavior

The 2025 stable formatter style includes all of these behaviors (0.9.0):

- format expressions inside f-string elements, choose alternate quotes for
  strings inside f-strings, and preserve hexadecimal case in debug expressions;
- choose quote style per literal in an implicitly concatenated f-string;
- join an implicitly concatenated string into one literal when it fits on one
  line;
- no longer emit the `ISC001` incompatibility warning;
- prefer parentheses around an `assert` message instead of breaking the
  assertion expression;
- automatically parenthesize overlong `if` guards in `match` cases and format
  `match` patterns consistently;
- remove unnecessary parentheses around return type annotations;
- keep the opening parenthesis on the same line as `if` in a comprehension when
  its condition starts with a comment;
- consistently format single-context-manager `with` statements on Python 3.8
  and older; and
- account for docstring-code-block width when
  `max-doc-code-line-length = "dynamic"`.

The formatter stopped adding unnecessary parentheses around a one-context
manager `with` statement with a trailing comment (0.10.0-guide).

The 2026 stable style incorporates the preview formatter work from the 0.14
series. It also permits omitting extra spaces between escaped quotes and a
closing triple quote, and enforces blank lines before decorated classes in stub
files. The `nested-string-quote-style` option was added later in that series
(0.15.0).

## F-string correctness

Preview formatting stopped adding trailing whitespace to a docstring after an
escaped quote. It also made `case []` and `case _` formatting consistent
(0.11.0).

The formatter avoids a line break after a format specifier in a multiline
f-string because Python 3.13.4 made that break a syntax error (0.12.0).

## Preview formatter behavior

For Python 3.14 and newer, preview formatting removes parentheses around
multiple exception types. It permits newlines after function headers without
docstrings and avoids extra parentheses around long `match` patterns with `as`
captures (0.14.0).

Preview also adds fluent method-chain formatting. Lambda parameters stay on one
line while an expanded body is parenthesized; later corrections preserve
parentheses required by the lambda body (0.14.0).

## Markdown formatting

Preview formatting processes labeled Python blocks in Markdown, including
`pycon` and Quarto language markers, while leaving unlabeled blocks unchanged.
Markdown files became preview-discovered by default, and `.qmd` must be mapped
explicitly (0.15.0):

```toml
[tool.ruff]
extension = { qmd = "markdown" }
```

Python code blocks in Markdown are now formatted by default without a preview
opt-in (0.16.0-guide).

## Syntax validation

Preview checks validate compile-time errors including (0.11.0):

- duplicate parameters or type parameters;
- invalid `match` patterns;
- illegal starred expressions and invalid annotations;
- module-level `nonlocal`; and
- assignment to or deletion of `__debug__`.

Preview also version-gates PEP 701 f-strings, parenthesized context managers,
starred annotations and indexes, tuple unpacking in `for` iterators, and
unparenthesized exception tuples. If no Python version applies to a
version-sensitive syntax diagnostic, it uses the latest supported Python
(0.11.0).

These checks moved into regular linting, including CPython compiler errors such
as an irrefutable `match` case appearing before the final case (0.12.0). When
`target-version` is unset, version-related syntax checks assume the latest
supported Python, then 3.13, while other lint behavior defaults to the minimum
supported Python, then 3.9.

## Python 3.14 support

`py314` is accepted as a target. Preview understands deferred annotations and
Python 3.14 unparenthesized exception tuples. Parser and formatter support for
template strings arrived later in the same series (0.11.0):

```toml
[tool.ruff]
target-version = "py314"
```

Implicit default and latest Python-version settings later advanced for Python
3.14. Preview also accepts `py315` (0.14.0):

```toml
[tool.ruff]
preview = true
target-version = "py315"
```

## Python 3.15 preview syntax

Preview parsing supports lazy imports and PEP 798 star-unpacking of
comprehensions. It validates lazy-import syntax and preserves the `lazy`
keyword during import sorting. `TID254` can require or ban lazy imports, a
separate preview check finds lazy imports that are evaluated eagerly, and
`RUF017` uses starred unpacking on Python 3.15 and newer (0.15.0).
