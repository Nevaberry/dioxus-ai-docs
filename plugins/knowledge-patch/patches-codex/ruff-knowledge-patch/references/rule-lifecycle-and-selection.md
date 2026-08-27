# Rule Lifecycle and Selection

## Default selection

The default selection expanded from 59 to 413 rules. It is primarily broader,
but it is not a strict superset: 18 opinionated pycodestyle and Pyflakes rules
are no longer implicitly selected (0.16.0-guide). Pin policy explicitly when a
project needs stable selection.

Preview had previously expanded to 412 enabled rules. Its initial selection
omitted `E401`, `E402`, `E701` through `E703`, `E711` through `E714`, `E721`,
`E731`, `E741` through `E743`, `F403`, `F405`, `F406`, and `F722`; later patch
releases removed a few more from preview defaults (0.15.0).

To retain the former common defaults explicitly:

```toml
[tool.ruff.lint]
select = ["E4", "E7", "E9", "F"]
```

## Stable rule promotions

These rules no longer require preview (0.9.0):

- `A005` (`stdlib-module-shadowing`, renamed from
  `builtin-module-shadowing`) and `A006` (`builtin-lambda-argument-shadowing`);
- `FURB188` (`slice-to-remove-prefix-or-suffix`);
- `PLR1716` (`boolean-chained-comparison`); and
- `RUF032` (`decimal-from-float-literal`), `RUF033` (`post-init-default`), and
  `RUF034` (`useless-if-else`).

These rules became stable in 0.10.0:

- `B911` (`batched-without-explicit-strict`), `C420`
  (`unnecessary-dict-comprehension-for-iterable`), `DTZ901`
  (`datetime-min-max`), `FAST003` (`fast-api-unused-path-parameter`), and
  `LOG015` (`root-logger-call`);
- `PLC1802` (`len-test`), `PLW1507` (`shallow-copy-environ`), `PTH208`
  (`os-listdir`), and `PTH210` (`invalid-pathlib-with-suffix`);
- `RUF040` (`invalid-assert-message-literal-argument`), `RUF041`
  (`unnecessary-nested-literal`), `RUF046` (`unnecessary-cast-to-int`),
  `RUF048` (`map-int-version-parsing`), and `RUF051`
  (`if-key-in-dict-del`); and
- `S704` (`unsafe-markup-use`), `SIM905` (`split-static-string`), `TC006`
  (`runtime-cast-value`), `TC007` (`unquoted-type-alias`), and `UP044`
  (`non-pep646-unpack`).

These rules became stable in 0.12.0:

- `FURB122` (`for-loop-writes`), `FURB132`
  (`check-and-remove-from-set`), `FURB157` (`verbose-decimal-constructor`),
  `FURB162` (`fromisoformat-replace-z`), and `FURB166`
  (`int-on-sliced-str`);
- `LOG014` (`exc-info-outside-except-handler`), `PLC0415`
  (`import-outside-top-level`), `PLR1733`
  (`unnecessary-dict-index-lookup`), `PLW0177` (`nan-comparison`), and
  `PLW1641` (`eq-without-hash`);
- `PT028` (`pytest-parameter-with-default-argument`), `PT030`
  (`pytest-warns-too-broad`), and `PT031`
  (`pytest-warns-with-multiple-statements`);
- `RUF028` (`invalid-formatter-suppression-comment`), `RUF049`
  (`dataclass-enum`), `RUF053` (`class-with-mixed-type-vars`), `RUF057`
  (`unnecessary-round`), and `RUF058` (`starmap-zip`); and
- `UP045` (`non-pep604-annotation-optional`), `UP046`
  (`non-pep695-generic-class`), `UP047` (`non-pep695-generic-function`), and
  `UP049` (`private-type-parameter`).

These rules became stable in 0.13.0:

- Airflow rules `AIR002`, `AIR301`, `AIR302`, `AIR311`, and `AIR312`;
- `ASYNC116` (`long-sleep-not-forever`), `FURB116`
  (`f-string-number-format`), and `PTH211` (`os-symlink`);
- `PYI059` (`generic-not-last-base-class`) and `PYI061`
  (`redundant-none-literal`); and
- `RUF043` (`pytest-raises-ambiguous-pattern`), `RUF059`
  (`unused-unpacked-variable`), and `UP050`
  (`useless-class-metaclass-type`).

These rules became stable in 0.15.0:

- `ASYNC212` (blocking `httpx` call), `ASYNC240` (blocking path method),
  `ASYNC250` (blocking `input`), and `B912` (`map` without explicit `strict`);
- `FURB110` (`if` expression instead of `or`), `FURB171` (single-item
  membership test), `PLC0207` (missing `maxsplit`), and `PLW0108`
  (unnecessary lambda);
- `RUF037` (empty iterable in `deque`), `RUF060` (membership in an empty
  collection), `RUF061` (legacy `pytest.raises`), and `RUF064` (non-octal
  permissions); and
- `RUF102` (invalid rule code), `RUF103` (invalid suppression), `RUF104`
  (unmatched suppression), and `UP042` (replace string enum).

These rules became stable in 0.16.0:

- `AIR303` (`airflow3-incompatible-function-signature`), `CPY001`
  (`missing-copyright-notice`), `FURB164` (`unnecessary-from-float`), and
  `FURB192` (`sorted-min-max`);
- `ISC004` (`implicit-string-concatenation-in-collection-literal`), `LOG004`
  (`log-exception-outside-except-handler`), `PLE0304`
  (`invalid-bool-return-type`), and `PLR0917`
  (`too-many-positional-arguments`); and
- `PLR1708` (`stop-iteration-return`), `RUF036`
  (`none-not-at-end-of-union`), `RUF063`
  (`access-annotations-from-class-dict`), and `RUF068`
  (`duplicate-entry-in-dunder-all`).

## Deprecated, removed, and recoded rules

`unsafe-markup-use` moved from `RUF035` to `S704`; update selectors,
suppression comments, and integrations (0.10.0-guide).

`UP038` (`non-pep604-isinstance`) and `S320`
(`suspicious-xmle-tree-usage`) were deprecated (0.10.0). `S320` was later
removed, and `PD901` (`pandas-df-variable-name`) was deprecated (0.12.0).

Deprecated rules stopped being activated by selecting a group or prefix; they
had to be selected by exact code. The remaining deprecated rules `PD901` and
`UP038` were then removed (0.13.0-guide).

`UP007` now handles `Union`, while `UP045` handles `Optional`. `RUF025` moved
to `RUF037` (0.9.0). The split became stable in 0.12.0, so update explicit
selection, ignores, and `noqa` comments.

## Airflow rule migration

Airflow 3 preview codes were reorganized: old `AIR301` moved to `AIR002`, old
`AIR302` moved to `AIR301`, and old `AIR303` moved to `AIR302`. Additional
checks were split into `AIR311` and `AIR312`, with some `AIR312` checks later
moved back to `AIR302` (0.11.0). Update exact selects, ignores, and suppressions.
Autofixes cover these rules, but module-move fixes are unsafe.

## Suppression parsing and checks

File-level and inline `noqa` comments share one robust parser. More valid
suppression forms are recognized, while malformed forms that previously worked
can error (0.10.0-guide).

`PGH004` stably detects blanket file-level `noqa`, not only blanket inline
comments. `RUF100` detects unused file-level `noqa` directives that name rule
codes (0.11.0).

Preview validates `ruff:disable` and `ruff:enable` ranges, reports invalid or
unmatched controls, and consolidates diagnostics for matching pairs. `RUF100`
also reports unused ranges. `ERA001` ignores the control comments, and
`--add-noqa` can add a reason to generated suppressions (0.14.0).

Block `ruff:disable` and `ruff:enable` suppressions are stable. Preview adds
`#ruff:file-ignore`, `#ruff:ignore` logical-line suppressions, nested
logical-line suppressions, human-readable names in suppressions and selectors,
and `--add-ignore` (0.15.0).

Preview rules `RUF105`, `RUF106`, and `RUF201` migrate `noqa` to `ruff:ignore`,
codes to names in `ruff:ignore`, and configuration selectors to names,
respectively. Preview output, LSP hovers, and code actions prefer readable
names; `ruff rule` accepts them, and unknown selectors warn instead of fail
(0.15.0).

`ruff: ignore` is now supported after a diagnostic line or on the line before
it. The canonical form includes a space after the colon (0.16.0):

```python
import math  # ruff: ignore[F401]

# ruff: ignore[F401]
import os
```

## Preview rule additions

Preview added `B903` (`class-as-data-structure`) and `RUF049` for a class that
is both an enum and a dataclass (0.9.0).

Preview added `RUF102` (`invalid-rule-code`), `RUF060`
(`in-empty-collection`, later extended to recursive empty collections),
`PLC0207` (`missing-maxsplit-arg`), `UP050`
(`useless-class-metaclass-type`), and `PTH211` for replacing `os.symlink` with
`Path.symlink_to` (0.11.0).

Preview added `RUF061`, which detects `pytest.raises`, `pytest.warns`, and
`pytest.deprecated_call` calls not used as context managers (0.12.0).

Preview added these rules in 0.14.0:

- `DOC102` (`docstring-extraneous-parameter`), including NumPy-style
  comma-separated parameter entries;
- `PLR1708` (`stop-iteration-return`);
- `RUF066` (unnecessary class properties), honoring configured
  `lint.pydocstyle.property-decorators`;
- `ISC004` (implicit string concatenation in collections);
- `RUF067` (non-empty initialization modules); and
- `RUF068` (duplicate entries in `__all__`).

Preview added these general rules in 0.15.0:

- `RUF069` (float equality), `D420` (docstring section order), `PLR1712`
  (temporary-variable swap), `RUF070` (assignment before `yield`), `B043`
  (constant-name `delattr`), and `RUF071` (`os.path.commonprefix`);
- `RUF050` (unnecessary `if`), `RUF072` (useless `finally`), `RUF073`
  (percent-formatting an f-string), `PLW0717` (too many `try` statements),
  `RUF074` (incorrect decorator order), and `RUF075` (fallible context manager);
  and
- `ASYNC119` (yield in an async-generator context manager), `D421` (property
  docstring beginning with a verb), and `UP051` (deprecated `abc` decorators).

Airflow preview additions include `AIR321` for Airflow 3.1 imports; `AIR003`
and `AIR304` for parse-time or runtime-varying DAG values; `AIR201` for XCom
pulls in template strings; `AIR004` for branch tasks used as short-circuit
tasks; and `AIR202` for implicit multiple outputs (0.15.0).

## Preview-only behavior changes

Preview `UP043` runs in stubs, `RUF060` handles empty f-strings correctly, and
`UP008` runs only when the `__class__` cell exists (0.13.0).

Preview adds an `E402` fix and permits `FURB189` subclasses of built-ins in
stubs (0.15.0).
