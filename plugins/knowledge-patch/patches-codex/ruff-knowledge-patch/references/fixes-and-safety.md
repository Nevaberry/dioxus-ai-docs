# Fixes and Safety

## General fix policy

Ruff's safety classifications are contextual. A fix that is safe for one
expression may be unsafe for another because it deletes comments, changes a
type, alters evaluation, or depends on typing-only semantics. Review unsafe
fixes before applying them in bulk.

## Semantic-preservation corrections

The `FURB171` fix is unsafe when its right-hand side is a string. The `RUF046`
fix parenthesizes its argument when removing an `int` call would otherwise
change meaning (0.9.0).

Fixes for `PYI041` (`redundant-numeric-union`) and `PYI016`
(`duplicate-union-members`) are stable (0.9.0).

Stable fixes or fix improvements became available for `PLR1714`
(`repeated-equality-comparison`), `SIM103` (`needless-bool`), and `PYI018`
(`unused-private-type-var`) (0.10.0).

The following fixes expanded or became available (0.11.0):

- `RUF005` covers slices, and `FURB171` covers `set` and `frozenset` calls;
- `PERF401` can replace list-constructor calls with comprehensions;
- `PERF403`, `E712`, and `ISC003` have fixes; and
- the existing `SIM117` fix is enabled in preview.

The `FURB129` `readlines-in-for` fix is always safe, and `SIM108` may further
simplify a conditional expression to `or` (0.12.0). The `SIM117` fix later
became always safe (0.13.0).

`UP008` has a safe fix when it preserves comments (0.15.0).

## Comment-removing fixes

The fixes for `PLR1730`, `UP004`, `UP010`, and `UP050` are unsafe when they
delete comments (0.11.0).

Fixes for all of the following became unsafe when they would remove comments
(0.14.0):

- `B009`, `B010`, `B013`, `B014`, and `B033`;
- `SIM910` and `SIM911`;
- `UP007`, `UP039`, `UP041`, and `UP045`;
- `FURB105`, `FURB116`, `FURB136`, `FURB140`, `FURB145`, `FURB154`,
  `FURB157`, `FURB164`, `FURB181`, and `FURB188`; and
- `RUF019` and `RUF020`.

The same condition applies to `UP017`, `UP020`, `UP033`, `FURB110`, and
`RUF010` (0.15.0).

## Type- and value-sensitive fixes

These fixes are unsafe only outside their narrower safe cases (0.11.0):

- `FURB161`, except for integers and booleans;
- `FURB116`, except for numeric literals;
- `FURB180`, when the class has bases; and
- `PIE804`, when the dictionary contains comments.

The `FURB163` fix is unsafe for `log2`, `log10`, `*args`, or when it would
delete comments. `UP007` and `UP045` do not offer a fix for `Optional[None]`
(0.12.0).

Fixes for `B905` and `B912` are unsafe. `PTH104`, `PTH105`, `PTH109`, and
`PTH115` fixes are unsafe when they can change return or expression types,
including inside compound statements. The `FURB192` fix is always unsafe
(0.14.0).

`RUF036` is limited to typing contexts, and its fix is unsafe outside
typing-only code. The `PTH101` fix is unsafe for a class attribute annotated as
`int`. The `EXE004` fix and `PYI061` fixes in Python files are unsafe
(0.15.0).

## Availability restrictions

The `NPY201` fix for `np.in1d` was removed. `PT006` receives no fix when
`argnames` or `argvalues` is ambiguous (0.15.0).

In preview, `PT018` fixes are safe unless comments are present, while `PT022`
fixes are unsafe. `FURB105` fixes are unsafe when they remove unknown
separators. `UP040`, `UP046`, and `UP047` skip their fix when a defaulted
`TypeVar` precedes a non-defaulted one (0.16.1).

## Corrected fix output

The `C408` fix NFKC-normalizes keyword names, and the `FURB192` fix
parenthesizes `yield` arguments (0.16.1).

## Future-import insertion

With `lint.future-annotations = true`, fixes for `TC001`, `TC002`, `TC003`,
`RUF013`, and `UP037` may insert `from __future__ import annotations`
(0.13.0-guide). Preview fixes for `UP006`, `UP007`, and `UP045` may also insert
the import (0.15.0). Treat that as a module-level semantic edit, not a local
text replacement.
