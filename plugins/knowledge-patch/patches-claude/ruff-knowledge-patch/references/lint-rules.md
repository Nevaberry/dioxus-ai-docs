# Lint rules

Use this reference to decide whether a rule is stable, understand its changed
scope, or evaluate preview rules. Configuration migrations and fix safety are
documented in their dedicated references.

## Stable rule availability

### Core correctness, style, and modernization

- Stable since 0.9.0: `A005` (`stdlib-module-shadowing`, renamed from
  `builtin-module-shadowing`), `A006` (`builtin-lambda-argument-shadowing`),
  `FURB188` (`slice-to-remove-prefix-or-suffix`), `PLR1716`
  (`boolean-chained-comparison`), `RUF032` (`decimal-from-float-literal`),
  `RUF033` (`post-init-default`), and `RUF034` (`useless-if-else`).
- Stable since 0.10.0: `B911` (`batched-without-explicit-strict`), `C420`
  (`unnecessary-dict-comprehension-for-iterable`), `DTZ901`
  (`datetime-min-max`), `PLC1802` (`len-test`), `PLW1507`
  (`shallow-copy-environ`), `RUF040` (`invalid-assert-message-literal-argument`),
  `RUF041` (`unnecessary-nested-literal`), `RUF046`
  (`unnecessary-cast-to-int`), `RUF048` (`map-int-version-parsing`), `RUF051`
  (`if-key-in-dict-del`), and `SIM905` (`split-static-string`).
- Stable since 0.12.0: `FURB122` (`for-loop-writes`), `FURB132`
  (`check-and-remove-from-set`), `FURB157` (`verbose-decimal-constructor`),
  `FURB162` (`fromisoformat-replace-z`), `FURB166` (`int-on-sliced-str`),
  `PLR1733` (`unnecessary-dict-index-lookup`), `PLW0177` (`nan-comparison`),
  `PLW1641` (`eq-without-hash`), `RUF028`
  (`invalid-formatter-suppression-comment`), `RUF049` (`dataclass-enum`),
  `RUF053` (`class-with-mixed-type-vars`), `RUF057` (`unnecessary-round`), and
  `RUF058` (`starmap-zip`).
- Stable since 0.13.0: `ASYNC116` (`long-sleep-not-forever`), `FURB116`
  (`f-string-number-format`), `RUF043` (`pytest-raises-ambiguous-pattern`),
  `RUF059` (`unused-unpacked-variable`), and `UP050`
  (`useless-class-metaclass-type`).
- Stable since 0.15.0: `B912` (`map` without explicit `strict`), `FURB110`
  (`if` expression instead of `or`), `FURB171` (single-item membership test),
  `PLC0207` (missing `maxsplit`), `PLW0108` (unnecessary lambda), `RUF037`
  (empty iterable in `deque`), `RUF060` (membership in an empty collection),
  `RUF064` (non-octal permissions), `RUF102` (invalid rule code), `RUF103`
  (invalid suppression), `RUF104` (unmatched suppression), and `UP042`
  (replace string enum).
- Stable since 0.16.0: `FURB164` (`unnecessary-from-float`), `FURB192`
  (`sorted-min-max`), `ISC004`
  (`implicit-string-concatenation-in-collection-literal`), `PLE0304`
  (`invalid-bool-return-type`), `PLR0917` (`too-many-positional-arguments`),
  `PLR1708` (`stop-iteration-return`), `RUF036`
  (`none-not-at-end-of-union`), `RUF063`
  (`access-annotations-from-class-dict`), and `RUF068`
  (`duplicate-entry-in-dunder-all`).

### Typing, imports, paths, and APIs

- Stable since 0.10.0: `PTH208` (`os-listdir`), `PTH210`
  (`invalid-pathlib-with-suffix`), `TC006` (`runtime-cast-value`), `TC007`
  (`unquoted-type-alias`), and `UP044` (`non-pep646-unpack`).
- Stable since 0.12.0: `PLC0415` (`import-outside-top-level`), `UP045`
  (`non-pep604-annotation-optional`), `UP046` (`non-pep695-generic-class`),
  `UP047` (`non-pep695-generic-function`), and `UP049`
  (`private-type-parameter`).
- Stable since 0.13.0: `PTH211` (`os-symlink`), `PYI059`
  (`generic-not-last-base-class`), and `PYI061` (`redundant-none-literal`).

### Testing, logging, security, async, and frameworks

- Stable since 0.10.0: `FAST003` (`fast-api-unused-path-parameter`), `LOG015`
  (`root-logger-call`), and `S704` (`unsafe-markup-use`).
- Stable since 0.12.0: `LOG014` (`exc-info-outside-except-handler`), `PT028`
  (`pytest-parameter-with-default-argument`), `PT030`
  (`pytest-warns-too-broad`), and `PT031`
  (`pytest-warns-with-multiple-statements`).
- Stable since 0.13.0: Airflow `AIR002`, `AIR301`, `AIR302`, `AIR311`, and
  `AIR312`.
- Stable since 0.15.0: `ASYNC212` (blocking `httpx` call), `ASYNC240`
  (blocking path method), `ASYNC250` (blocking `input`), and `RUF061` (legacy
  `pytest.raises`).
- Stable since 0.16.0: `AIR303`
  (`airflow3-incompatible-function-signature`), `CPY001`
  (`missing-copyright-notice`), and `LOG004`
  (`log-exception-outside-except-handler`).

## Changed stable diagnostic scope

### Functions, classes, and expressions

- `RET503` understands functions annotated with `typing.Never` since 0.9.0.
- Since 0.10.0, `N804` does not flag `__new__`; `PLW0211` handles it instead.
  `PLE1310` applies to objects known to be `str` or `bytes`. `FURB169`
  recognizes `type(expr) is type(None)` even when `expr` is not a name.
- `SIM108` can simplify a conditional expression further to `or` since
  0.12.0.
- Since 0.13.0, `B017` checks direct unittest and pytest exception-assertion
  calls, `COM812` and `COM819` cover PEP 695 type-parameter trailing commas,
  `EM101` checks byte-string exception messages, `PLE2502` detects U+061C, and
  `UP008` runs only when the `__class__` cell exists. Preview `RUF060`
  correctly handles empty f-strings.
- Expanded 0.14.0 behavior lets `B006` recognize more guaranteed-mutable
  defaults involving tuples, generators, and assignment expressions;
  `FURB105` finds empty f-strings; `B901` catches `yield` embedded in other
  statements; `RUF052` catches more dummy-variable uses; `PLW0133` recognizes
  subclasses of built-in exceptions; `UP045` covers string arguments of
  `typing.cast`; and `PIE794` finds duplicated declared class fields.
- Stable 0.15.0 behavior expands `A003` to attribute definitions in decorators,
  default arguments, and elsewhere; `SIM910` accepts more dictionary-key
  expressions.
- Corrections in 0.16.1 make `B008` treat `range` as immutable and prevent
  `RET504` from firing when a variable is read in a `finally` clause.

### Typing, stubs, and import behavior

- Since 0.9.0, `A005` ignores stubs; `RUF008` and `RUF009` support `attrs`;
  and `PYI006` applies to non-stub files.
- Since 0.10.0, `PYI019` more accurately finds custom `TypeVar`s replaceable by
  `Self`, spans the full function header, and `N803` ignores arguments of
  functions decorated with `typing.override`.
- Since 0.11.0, `EXE003` accepts `uv run` shebangs, `RUF005` covers slices,
  `FURB171` covers `set` and `frozenset`, `UP024` recognizes `resource.error`
  as an alias of `OSError`, and `UP035` rewrites `get_type_hints()` only on
  Python 3.13+.
- Since 0.12.0, `FBT001` covers annotations containing `bool`, including
  `bool | int` and `Optional[bool]`; Ruff treats `ty:` comments as pragmas; and
  `PYI019` checks string annotations. The `UP007` / `UP045` split is stable.
- In 0.13.0, preview `UP043` runs in stubs. Stable behavior makes `PLC0414`
  skip `__init__.py`, avoiding conflict with a suggested `F401` fix.
- Stable 0.15.0 behavior recognizes `typing.Optional` duplicates in `PYI016`
  and runs `UP043` on stubs before Python 3.13. Preview `F811` finds annotated
  redeclarations and duplicate imports under `TYPE_CHECKING`; `PYI033`, named
  `legacy-type-comment`, also runs on Python files; `FURB189` permits subclasses
  of built-ins in stubs.
- Stable 0.16.0 behavior expands `FA102` to more PEP 585-compatible
  `collections.abc` APIs and makes `UP019` recognize both
  `typing_extensions.Text` and `typing.Text`.

### Testing and framework behavior

- Since 0.9.0, `PT006` covers `pytest.parametrize` calls outside decorators and
  calls using keywords; `E402` permits `pytest.importorskip` between imports.
- Since 0.10.0, `PT012` and `PT031` permit empty-bodied `for` statements within
  `pytest.raises` and `pytest.warns`; `PLW1508` finds invalidly typed defaults
  passed to `os.environ.get`.
- Since 0.11.0, `PT019` does not suggest `usefixtures` for `parametrize`
  values, `FAST003` accepts class dependencies, and `S608` skips expressionless
  f-strings.
- Since 0.13.0, `PGH005` covers `AsyncMock` methods such as `not_awaited`.
- Airflow checks expand in 0.14.0 to `DatasetEvent`, `Param`, removed
  `DAG.create_dagrun`, deprecated `DAG(concurrency=...)`, and invalid positional
  arguments to `HookLineageCollector.create_asset` and `Asset` / `Dataset`.
- `DJ001` applies to annotated Django fields since 0.14.0.
- Preview checks in 0.15.0 include `pytest_asyncio` fixtures.

### Strings, logging, security, and internationalization

- Since 0.11.0, `S308` accepts raw strings and `S603` trusts `str`,
  `list[str]`, and tuples of string literals.
- Expanded 0.14.0 `RUF065` coverage finds more eager logging conversions while
  excluding complex specifiers and `str()` calls that are not simple
  conversions.
- Stable 0.16.0 behavior suppresses `BLE001` when exceptions are logged through
  methods other than `critical`, `error`, or `exception`; recognizes more
  common `gettext` patterns in `INT001`, `INT002`, and `INT003`, including assignment to
  `builtins._`; resolves local string-literal bindings in `S310`; and supports
  the newer PySNMP API in `S508` and `S509`.
- Preview `RUF065` in 0.16.1 avoids a false positive for unpacked arguments.
  `D214`, `D405`, and `D413` skip section detection inside reStructuredText
  directive bodies.

## Preview rule set by developer concern

### Correctness and control flow

- The 0.9.0 preview set adds `B903` (`class-as-data-structure`) and `RUF049`
  for a class that is both an enum and a dataclass. It also splits `UP007`
  (`Union`) from new `UP045` (`Optional`) and moves `RUF025` to `RUF037`.
- Preview in 0.11.0 adds `RUF102` (`invalid-rule-code`), `RUF060`
  (`in-empty-collection`, later with recursive empty-collection checking),
  `PLC0207` (`missing-maxsplit-arg`), `UP050`
  (`useless-class-metaclass-type`), and `PTH211` (`os.symlink` to
  `Path.symlink_to`).
- Preview in 0.12.0 adds `RUF061` for calls to `pytest.raises`, `pytest.warns`,
  and `pytest.deprecated_call` outside context managers.
- Preview in 0.14.0 adds `PLR1708` (raising `StopIteration` from a generator),
  `ISC004` (implicit string concatenation in collections), `RUF067` (non-empty
  initialization modules), and `RUF068` (duplicate `__all__` entries):

```python
items = ["left" "right"]  # ISC004
__all__ = ["run", "run"]  # RUF068
```

- General preview additions in 0.15.0 are `RUF069` (float equality), `PLR1712`
  (swapping through a temporary), `RUF070` (assignment immediately before
  `yield`), `B043` (constant-name `delattr`), `RUF071`
  (`os.path.commonprefix`), `RUF050` (unnecessary `if`), `RUF072` (useless
  `finally`), `RUF073` (percent-formatting an f-string), `PLW0717` (too many
  `try` statements), `RUF074` (incorrect decorator order), `RUF075` (fallible
  context manager), and `ASYNC119` (`yield` in a context manager implemented as
  an async generator).

### Documentation, classes, typing, and formatting

- Preview 0.9.0 behavior applies `TC008` (`quoted-type-alias`) more eagerly in
  `TYPE_CHECKING` but ignores it in stubs; `PLW1641` also ignores stubs.
- Preview in 0.14.0 adds `DOC102` (`docstring-extraneous-parameter`), which finds documented parameters missing
  from signatures, including NumPy-style comma-separated entries, and `RUF066`,
  which finds unnecessary class properties while honoring
  `lint.pydocstyle.property-decorators`.
- Preview in 0.15.0 adds `D420` (docstring section order), `D421` (property
  docstring starting with a verb), and `UP051` (deprecated `abc` decorators).
  `RUF019` treats f-string interpolation as a possible side effect.

### Airflow workflows

Preview 0.15.0 adds `AIR321` for Airflow 3.1 imports; `AIR003` and `AIR304` for
parse-time or runtime-varying DAG values; `AIR201` for XCom pulls in template
strings; `AIR004` for branch tasks used as short-circuit tasks; and `AIR202` for
implicit multiple outputs.

## Fix-bearing rule behavior

Availability does not imply safety; consult
[Suppressions and fixes](suppressions-and-fixes.md) before applying fixes.

- Stable fixes or improvements include `PYI041` and `PYI016` (0.9.0),
  `PLR1714`, `SIM103`, and `PYI018` (0.10.0), `FURB129` and `SIM108` (0.12.0),
  and `SIM117` (0.13.0).
- Since 0.11.0, `PERF401` can replace list constructor calls with
  comprehensions, `PERF403` has a fix, `E712` and `ISC003` have autofixes, and
  the `SIM117` fix is available in preview.
- Stable 0.15.0 behavior lets `SIM905` fix `split(maxsplit=...)` without an
  explicit separator and gives `UP008` a safe fix when comments are preserved.
- Preview 0.15.0 adds an `E402` fix. The `NPY201` fix for `np.in1d` is removed,
  and ambiguous `PT006` `argnames` / `argvalues` receive no fix.
- Fix corrections in 0.16.1 NFKC-normalize `C408` keyword names and
  parenthesize `yield` arguments for `FURB192`.
