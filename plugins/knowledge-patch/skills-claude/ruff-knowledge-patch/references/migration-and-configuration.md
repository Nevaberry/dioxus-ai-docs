# Migration and configuration

Use this reference for version-sensitive configuration, renamed or removed
rules, Python-target behavior, discovery, and upgrade planning.

## Python target inference and defaults

### Inference timing

The announced inference of Python from `requires-python` did **not** ship in
`0.10.0-guide`; it first ships in 0.11.0. Do not diagnose 0.10 behavior as if
that inference were already active.

In 0.15.0, Ruff resolves the full chain of `extend`ed configurations before it
falls back to its default Python version. A target inherited from an extended
file can therefore win over the fallback.

### Different fallbacks for syntax and rules

Since 0.12.0, regular checks include version-related and CPython compile-time
syntax errors. With no `target-version`, version-related syntax checks assume
the latest supported Python, then 3.13, while ordinary lint behavior still
defaults to the minimum supported Python, then 3.9. Pin the real project target
to avoid this split fallback.

Ruff advances its default and latest baselines for Python 3.14 in 0.14.0.
Projects relying on implicit versions can therefore see different parsing,
lint, or formatting decisions. Preview also accepts `py315`:

```toml
[tool.ruff]
preview = true
target-version = "py315"
```

## Rule-code migrations

### Renames, splits, and moves

- In 0.9.0, `A005` is named `stdlib-module-shadowing`, replacing
  `builtin-module-shadowing`; it also ignores stub files.
- Preview in 0.9.0 splits `UP007`: it retains `Union` handling, while new
  `UP045` handles `Optional`. This split becomes stable in 0.12.0, so update
  explicit selections, ignores, and `noqa` comments to include `UP045` where
  intended.
- Preview in 0.9.0 moves `RUF025` to `RUF037`.
- The `unsafe-markup-use` rule moves from `RUF035` to `S704` in
  0.10.0-guide; `S704` is stable in 0.10.0. Update selectors and suppressions.
- Airflow preview rules are reorganized in 0.11.0: former `AIR301` becomes
  `AIR002`, former `AIR302` becomes `AIR301`, and former `AIR303` becomes
  `AIR302`. Checks are also split into `AIR311` and `AIR312`, with some
  `AIR312` checks later returning to `AIR302`. Update every explicit selector,
  ignore, and suppression. Autofixes cover these rules, but module-move fixes
  are unsafe.

### Deprecations and removals

- `UP038` (`non-pep604-isinstance`) and `S320`
  (`suspicious-xmle-tree-usage`) are deprecated in 0.10.0.
- `S320` is removed in 0.12.0. `pandas-df-variable-name` is deprecated there.
- In 0.13.0-guide, selecting a group or prefix no longer activates deprecated
  rules; a deprecated rule must be selected by its exact code. The remaining
  deprecated rules `PD901` (`pandas-df-variable-name`) and `UP038` are then
  removed and no longer run.

Search `select`, `extend-select`, `ignore`, per-file ignores, suppressions,
editor settings, and scripts for all affected identifiers.

## Default rule selection

Preview mode expands from 59 stable-default rules to 412 rules beginning in
0.15.0 (specifically 0.15.2). It is mostly, but not completely, a superset. It
initially omits `E401`, `E402`, `E701`–`E703`, `E711`–`E714`, `E721`, `E731`,
`E741`–`E743`, `F403`, `F405`, `F406`, and `F722`; later 0.15.6 removes a few
more rules from preview defaults.

The expanded stable default in 0.16.0-guide enables 413 rules rather than 59.
It is primarily an expansion but is not a strict superset: 18 opinionated
pycodestyle and Pyflakes rules stop being enabled implicitly. Pin a fixed
selection when CI must remain stable:

```toml
[tool.ruff.lint]
select = ["E4", "E7", "E9", "F"]
```

## Lint option migrations

### `flake8-builtins`

In 0.10.0, `lint.flake8-builtins.strict-checking` changes its default from
`true` to `false`. The `builtins-`-prefixed option names are deprecated in favor
of unprefixed names; for example, replace `builtins-allowed-modules` with
`allowed-modules`.

### Type-checking guards

In 0.10.0-guide, any local variable named `TYPE_CHECKING` is recognized as a
type-checking guard. Legacy `if 0:` and `if False:` guards are no longer
recognized; migrate them to a local `TYPE_CHECKING` variable.

To prevent generated fixes from importing `typing_extensions`, set
`lint.typing-extensions` to false (since 0.11.0):

```toml
[tool.ruff.lint]
typing-extensions = false
```

With `lint.future-annotations = true` in 0.13.0-guide, fixes for `TC001`,
`TC002`, `TC003`, `RUF013`, and `UP037` can insert
`from __future__ import annotations`. This can move more imports under
`TYPE_CHECKING`, use PEP 604 unions before Python 3.10, or unquote annotations:

```toml
[tool.ruff.lint]
future-annotations = true
```

In 0.15.0 preview, `UP006`, `UP007`, and `UP045` fixes may also insert that
future import. Bandit import rules `S401`–`S415` allow guarded imports, while
`TC001`–`TC003` avoid strict behavior when future annotations are enabled.

### Import classification and conventions

Since 0.11.0, isort checks a module's full path against the configured project
root or roots when classifying first-party imports. Nested modules can move
between import sections. The same release makes `numpy.typing as npt` a default
`flake8-import-conventions` alias, so `ICN001` recognizes it without custom
configuration.

In 0.15.0, import sorting gains configurable section-heading comments.

## Configuration discovery and extensions

The macOS fallback at
`~/Library/Application Support/ruff/ruff.toml` is removed in 0.13.0-guide. Put
user configuration in the XDG location, normally `~/.config/ruff/ruff.toml`.

Preview in 0.14.0 discovers `*.pyw` by default.

Preview Markdown support in 0.15.0 discovers `.md` files by default from
0.15.5. `.qmd` loses its implicit special case and must be mapped:

```toml
[tool.ruff]
extension = { qmd = "markdown" }
```

Configured extensions affect discovery, code-block language selection, and
later language-server handling. Markdown formatting becomes default behavior in
0.16.0-guide rather than requiring preview.

## Human-readable rule names

In 0.15.0 preview, suppressions and selectors can use human-readable rule
names. Preview output, LSP hovers, and code actions prefer those names;
`ruff rule` accepts them, and unknown selectors warn rather than fail. Preview
rules `RUF105`, `RUF106`, and `RUF201` migrate `noqa` to `ruff:ignore`, codes to
names in `ruff:ignore`, and configuration selectors to names.

The 0.16.1 preview option can opt out of human-readable names, allowing an
integration to retain code-oriented output while using other preview behavior.

## Release and environment notes

The `ruff:alpine` image moves from Alpine 3.20 to 3.21 in 0.10.0-guide;
`ruff:alpine3.20` stops receiving updates. In 0.15.0, `ruff:alpine` advances to
Alpine 3.23 and `ruff:debian` / `ruff:debian-slim` use Debian 13 “Trixie.”

Version 0.14.12 was published to PyPI without a GitHub release or tag after a
WASM publishing issue; 0.14.13 has identical contents and is its follow-up.
Account for that if release automation assumes every PyPI version has a tag.
