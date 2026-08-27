# Suppressions and fixes

Use this reference when suppression parsing changes, when migrating to
`ruff: ignore`, or when deciding whether to apply an autofix.

## Suppression parsing and diagnostics

### Unified `noqa` parsing

In 0.10.0-guide, file-level and inline suppression comments use the same,
more robust parser. More valid forms are recognized, but some malformed forms
that previously worked now produce errors. Normalize comments rather than
depending on permissive legacy parsing.

Since 0.11.0, stable `PGH004` detects blanket file-level `noqa` comments as well
as blanket inline comments. `RUF100` detects unused file-level `noqa` directives
that name specific codes.

Ruff 0.14.0 preview validates `ruff:disable` / `ruff:enable` ranges, reports
invalid or unmatched comments, consolidates diagnostics for matched pairs, and
lets `RUF100` find unused ranges. `ERA001` ignores these control comments.
`--add-noqa` can attach a reason to generated suppressions.

Block `ruff:disable` / `ruff:enable` becomes stable in 0.15.0. Preview adds
`#ruff:file-ignore`, `#ruff:ignore`, nested logical-line suppressions,
human-readable names in suppressions and selectors, and `--add-ignore`.
Preview rules `RUF105`, `RUF106`, and `RUF201` migrate `noqa` to `ruff:ignore`,
codes to names in `ruff:ignore`, and configuration selectors to names.

### Stable `ruff: ignore`

In 0.16.0, Ruff accepts `ruff: ignore` at the end of a diagnostic line or on the
preceding line. Use the canonical space after the colon:

```python
import math  # ruff: ignore[F401]

# ruff: ignore[F401]
import os
```

## Stable fix additions and corrections

In 0.9.0, fixes for `PYI041` (`redundant-numeric-union`) and `PYI016`
(`duplicate-union-members`) become stable. `FURB171` is unsafe
when its right-hand side is a string. `RUF046` adds parentheses when removing
`int(...)` would otherwise alter semantics.

In 0.10.0, fixes or improvements for `PLR1714`
(`repeated-equality-comparison`), `SIM103` (`needless-bool`), and `PYI018`
(`unused-private-type-var`) become stable. `UP015` narrows its diagnostic to
the redundant `open` mode argument, so an existing `noqa` may need to move.

In 0.11.0, `E712` and `ISC003` gain autofixes, the `SIM117` fix is enabled in
preview, `PERF401` can replace list constructors with comprehensions, and
`PERF403` gains a fix.

Stable 0.12.0 behavior makes the `FURB129` (`readlines-in-for`) fix always safe
and lets `SIM108` further reduce a conditional expression to `or`.

In 0.13.0, the `SIM117` fix becomes always safe.

In 0.15.0, `SIM905` fixes `split(maxsplit=...)` without an explicit separator,
and `UP008` has a safe fix when comments are preserved.

## Conditional and unsafe fixes

### Operand, inheritance, and comment sensitivity

Since 0.11.0, fixes are unsafe:

- for `FURB161`, except with integers and booleans;
- for `FURB116`, except with number literals;
- for `FURB180` when the class has bases;
- for `PIE804` when the dictionary contains comments; and
- for `PLR1730`, `UP004`, `UP010`, and `UP050` when they delete comments.

Airflow module-move fixes are unsafe. The expanded behavior for `PERF401`,
`PERF403`, `E712`, `ISC003`, and preview `SIM117` should be reviewed separately
from availability.

### Call shapes and optional annotations

In 0.12.0, `FURB163` is unsafe for `log2`, `log10`, `*args`, or when it deletes comments.
`UP007` and `UP045` offer no fix for `Optional[None]`.

### Type-changing, path, and comment-removing fixes

In 0.14.0, fixes for `B905` and `B912` become unsafe. `PTH104`, `PTH105`, `PTH109`, and
`PTH115` are unsafe when changing the return or expression type, including in
compound statements. `FURB192` is always unsafe.

The following fixes are unsafe when they remove comments:

- `B009`, `B010`, `B013`, `B014`, `B033`;
- `SIM910`, `SIM911`;
- `UP007`, `UP039`, `UP041`, `UP045`;
- `FURB105`, `FURB116`, `FURB136`, `FURB140`, `FURB145`, `FURB154`,
  `FURB157`, `FURB164`, `FURB181`, `FURB188`; and
- `RUF019`, `RUF020`.

### Typing contexts and removed fixes

In 0.15.0, fixes for `UP017`, `UP020`, `UP033`, `FURB110`, and `RUF010` are unsafe when
they delete comments. `RUF036` is limited to typing contexts and its fix is
unsafe outside typing-only code. `PTH101` is unsafe for a class attribute
annotated as `int`; `EXE004` and `PYI061` fixes in Python files are unsafe.

The `NPY201` fix for `np.in1d` is removed. `PT006` receives no fix when
`argnames` or `argvalues` are ambiguous.

### Preview safety corrections

In 0.16.1 preview, `PT018` fixes are safe by default and unsafe only when comments are
present; `PT022` fixes are unsafe. `FURB105` is unsafe when removing unknown
separators. `UP040`, `UP046`, and `UP047` skip their fix when a defaulted
`TypeVar` comes before a non-defaulted one.

Corrected fixes in 0.16.1 include NFKC normalization of `C408` keyword names
and parenthesizing `yield` arguments in `FURB192`.

## Review workflow

Classify fixes by actual operands and context, not only by rule code. Apply
safe fixes first, then separately review changes involving comments, typing
contexts, expression types, constructors, paths, generators, or imports. Run
the project's tests after unsafe fix groups.
