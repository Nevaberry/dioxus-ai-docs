# Removals

## Dead batteries (3.13, PEP 594)

19 modules removed from stdlib. All raise `ImportError` on Python 3.13+:

| Module | Replacement |
|--------|-------------|
| `aifc` | `standard-aifc` (PyPI) |
| `audioop` | `audioop-lts` (PyPI) |
| `cgi` | `urllib.parse.parse_qs()` (GET), `multipart` pkg (POST) |
| `cgitb` | `standard-cgitb` (PyPI) |
| `chunk` | `standard-chunk` (PyPI) |
| `crypt` | `hashlib`, `bcrypt`, `argon2-cffi` |
| `imghdr` | `filetype`, `puremagic`, `python-magic` |
| `mailcap` | `mimetypes` module |
| `msilib` | — |
| `nis` | — |
| `nntplib` | `pynntp` (PyPI) |
| `ossaudiodev` | `pygame` (PyPI) |
| `pipes` | `subprocess` + `shlex.quote()` |
| `sndhdr` | `filetype`, `puremagic`, `python-magic` |
| `spwd` | `python-pam` (PyPI) |
| `sunau` | `standard-sunau` (PyPI) |
| `telnetlib` | `telnetlib3` (PyPI) |
| `uu` | `base64` module |
| `xdrlib` | `standard-xdrlib` (PyPI) |

## Other removals (3.13)

| Removed | Replacement |
|---------|-------------|
| `2to3` / `lib2to3` | — |
| `tkinter.tix` | — |
| `locale.resetlocale()` | `locale.setlocale(locale.LC_ALL, "")` |
| `typing.io` / `typing.re` namespaces | Import from `typing` directly |
| `TypedDict("TD", x=int)` keyword syntax | Class syntax or `TypedDict("TD", {"x": int})` |
| `unittest.findTestCases()` | `TestLoader.loadTestsFromModule()` |
| `unittest.makeSuite()` | `TestLoader.loadTestsFromTestCase()` |
| `unittest.getTestCaseNames()` | `TestLoader.getTestCaseNames()` |
| `pathlib.Path` as context manager | Was no-op since 3.9 |
| `re.template()` / `re.TEMPLATE` | — (was undocumented) |

## Behavior changes (3.13)

| Change | Impact |
|--------|--------|
| Docstring whitespace stripping | Compiler strips common leading whitespace; may affect `doctest` |
| `pathlib.Path.glob("**")` returns files AND dirs | Add trailing `/` for dirs only: `glob("**/")` |
| `gzip.GzipFile.mode` returns string | Now `'rb'`/`'wb'` instead of int `1`/`2` |

## Removals (3.14)

| Removed | Replacement |
|---------|-------------|
| `ast.Num`, `ast.Str`, `ast.Bytes`, `ast.NameConstant`, `ast.Ellipsis` | `ast.Constant` |
| `ast.Constant.n`, `ast.Constant.s` | `ast.Constant.value` |
| `asyncio` child watcher classes | — (no longer needed) |
| `asyncio.get_event_loop()` auto-creation | `asyncio.run()` or `asyncio.Runner` |
| `pkgutil.get_loader()`, `find_loader()` | `importlib.util.find_spec()` |
| `pty.master_open()`, `slave_open()` | `pty.openpty()` |
| `sqlite3.version` | `sqlite3.sqlite_version` |
| `itertools` copy/pickle/deepcopy | — (removed) |
| `urllib.request.URLopener`, `FancyURLopener` | `urllib.request.urlopen()` |

## Breaking behavior changes (3.14)

| Change | Impact |
|--------|--------|
| `asyncio.get_event_loop()` raises `RuntimeError` | Must use `asyncio.run()` |
| `multiprocessing` default → `'forkserver'` on Linux | May cause pickling errors; use `get_context('fork')` |
| `int()` no longer delegates to `__trunc__()` | Must implement `__int__()` or `__index__()` |
| `NotImplemented` in bool context → `TypeError` | Was deprecated since 3.9 |
| `functools.partial` is method descriptor | Wrap in `staticmethod()` for classes |
| `pickle` default protocol → 5 | Was 4 |
| `types.UnionType` == `typing.Union` | `repr(Union[int, str])` → `"int \| str"` |
| Incremental GC: 2 generations | `gc.collect(1)` does an increment, not gen-1 collection |
| SyntaxWarning in `finally` (PEP 765) | `return`/`break`/`continue` in `finally` now warns |
