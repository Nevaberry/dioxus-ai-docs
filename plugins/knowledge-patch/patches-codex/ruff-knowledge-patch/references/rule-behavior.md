# Rule Behavior

## Typing and annotation behavior

`RET503` understands functions annotated to return `typing.Never` (0.9.0).
`TC008` preview behavior applies `quoted-type-alias` more eagerly inside
`TYPE_CHECKING` blocks but ignores it in stubs. Preview `PLW1641` also ignores
`eq-without-hash` in stubs (0.9.0).

Any local variable named `TYPE_CHECKING` is recognized as a type-checking
guard. Legacy `if 0:` and `if False:` guards are no longer recognized; use a
local `TYPE_CHECKING` variable (0.10.0-guide).

`PYI019` more accurately detects custom `TypeVar`s that can be replaced by
`Self`, and its diagnostic spans the entire function header. `N803` ignores
arguments of functions decorated with `typing.override` (0.10.0).

`UP024` recognizes `resource.error` as a deprecated alias for `OSError`.
`UP035` rewrites `get_type_hints()` only for Python 3.13 and newer (0.11.0).

`PYI019` checks string annotations. `UP007` and `UP045` do not fix
`Optional[None]`. The stable `UP007`/`UP045` split means explicit selections,
ignores, and suppressions may need `UP045` (0.12.0).

Preview `UP043` runs in stub files. `UP008` only applies when the `__class__`
cell exists (0.13.0).

`UP045` applies to string arguments of `typing.cast` (0.14.0).

Bandit import checks `S401` through `S415` allow imports under
`TYPE_CHECKING`. `TC001` through `TC003` avoid strict behavior when
`lint.future-annotations` is enabled. Preview `F811` finds annotated
redeclarations and duplicate imports under `TYPE_CHECKING`. `PYI033`, now named
`legacy-type-comment`, also runs on Python files (0.15.0).

`FA102` recognizes more PEP 585-compatible APIs, including APIs from
`collections.abc`. `UP019` recognizes `typing_extensions.Text` as well as
`typing.Text` (0.16.0).

## Imports, paths, and security

`E402` ignores `pytest.importorskip` between import statements (0.9.0).

`PLE1310` applies to objects known to be `str` or `bytes`. `PLW1508` detects
invalidly typed defaults passed to `os.environ.get`, and `FURB169` recognizes
`type(expr) is type(None)` even when `expr` is not a name (0.10.0).

First-party import classification checks a module's full path against the
configured project root or roots, which can move nested modules between import
sections (0.11.0).

`EXE003` accepts `uv run` shebangs. `S308` accepts raw strings. `S603` treats
`str`, `list[str]`, and tuples of string literals as trusted input. `S608`
skips expressionless f-strings (0.11.0).

`S310` resolves local string-literal bindings. `S508` and `S509` understand the
recommended API in newer PySNMP versions (0.16.0).

## Pytest and testing behavior

`PT006` applies to `pytest.parametrize` calls outside decorators and calls that
use keyword arguments (0.9.0).

`PT012` and `PT031` allow a `for` statement with an empty body inside
`pytest.raises` and `pytest.warns` context managers (0.10.0).

`PT019` no longer recommends `usefixtures` for `parametrize` values, and
`FAST003` accepts class dependencies (0.11.0).

Pytest-style checks also include `pytest_asyncio` fixtures (0.15.0).

## Classes, functions, and control flow

`A005` ignores stub files. `RUF008` and `RUF009` support `attrs`, and `PYI006`
applies to non-stub files (0.9.0).

`__new__` methods are no longer flagged by `N804`; `PLW0211` handles them.
`FURB169` recognizes non-name expressions in `type(expr) is type(None)` checks
(0.10.0).

`RUF005` covers slices, and `FURB171` covers `set` and `frozenset` calls.
`PERF401` can replace list-constructor calls with comprehensions (0.11.0).

`FURB129` has an always-safe `readlines-in-for` fix. `SIM108` may simplify a
conditional expression further to `or`. `FBT001` includes annotations that
contain `bool`, such as `bool | int` and `Optional[bool]` (0.12.0).

`B017` checks direct calls to unittest and pytest exception assertions, not
only context-manager forms. `PGH005` covers `AsyncMock` methods such as
`not_awaited`, and `SIM117` is always safe (0.13.0).

`B006` recognizes additional definitely mutable defaults involving tuples,
generators, and assignment expressions. `B901` catches `yield` embedded in
other statements. `PLW0133` detects subclasses of built-in exceptions, and
`PIE794` detects duplicate declared class fields (0.14.0).

`A003` finds built-in attribute shadowing in decorators, defaults, and other
attribute definitions. `SIM910` accepts more dictionary-key expression forms.
`UP008` is safe when it preserves comments, and `UP043` runs on stubs before
Python 3.13 (0.15.0).

`BLE001` is suppressed when an exception is logged through logging methods
other than `critical`, `error`, or `exception` (0.16.0).

`B008` treats `range` as immutable. `RET504` avoids a false positive when a
variable is read in a `finally` clause (0.16.1).

## Strings, names, and diagnostics

`PLE2502` detects U+061C ARABIC LETTER MARK. `EM101` checks byte strings in
exception messages. `COM812` and `COM819` check PEP 695 type-parameter-list
trailing commas (0.13.0).

`RUF065` covers more eager logging conversions while excluding nonsimple
`str()` calls and complex conversion specifiers. `FURB105` detects empty
f-strings, and `RUF052` detects more dummy-variable uses (0.14.0).

`RUF019` considers f-string interpolation a possible side effect (0.15.0).

`INT001`, `INT002`, and `INT003` recognize more common `gettext` patterns,
including assignment to `builtins._` (0.16.0).

Preview `RUF065` avoids a false positive for unpacked arguments. `D214`,
`D405`, and `D413` skip section detection inside reStructuredText directive
bodies (0.16.1).

## Framework-specific behavior

Airflow checks cover `DatasetEvent`, `Param`, removed `DAG.create_dagrun`, the
deprecated `DAG(concurrency=...)` argument, and invalid positional arguments to
`HookLineageCollector.create_asset` and `Asset` or `Dataset` (0.14.0).

`DJ001` applies to annotated Django fields (0.14.0).

## Other stabilized and corrected behavior

`UP015` highlights only the redundant mode argument rather than the full
`open` call, so an existing `noqa` may need to move. `PT012` and `PT031` accept
empty-body loops in their context managers. `PLW1508`, `PYI019`, and `PLE1310`
have the expanded behavior described above (0.10.0).

`RUF060` recursively checks empty collections. `FAST003` accepts class
dependencies, and `PT019` excludes parametrized values as described above
(0.11.0).

Ruff treats `ty:` comments as pragma comments (0.12.0).

`PLC0414` does not apply to `__init__.py`, avoiding a conflict with a proposed
`F401` fix. Preview `RUF060` correctly handles empty f-strings (0.13.0).

`ERA001` ignores `ruff:disable` and `ruff:enable` control comments (0.14.0).

`SIM905` can fix `split(maxsplit=...)` without an explicit separator, and
`PYI016` recognizes duplicates involving `typing.Optional` (0.15.0).
