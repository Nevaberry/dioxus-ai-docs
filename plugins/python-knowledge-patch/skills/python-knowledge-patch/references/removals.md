# Removals, Breaking Changes, and Deprecations

## Breaking Changes — Python 3.14

### asyncio.get_event_loop() Raises RuntimeError

No longer implicitly creates an event loop when none exists:

```python
# BROKEN in 3.14:
loop = asyncio.get_event_loop()
loop.run_until_complete(main())

# FIX — use asyncio.run():
asyncio.run(main())

# FIX — for multiple sequential async calls:
with asyncio.Runner() as runner:
    runner.run(op_one())
    blocking_code()
    runner.run(op_two())
```

### multiprocessing Default Start Method

On Linux/Unix (not macOS), default changed from `'fork'` to `'forkserver'`. See [concurrency.md](concurrency.md) for migration details.

### int() No Longer Delegates to __trunc__()

Classes must implement `__int__()` or `__index__()` for `int()` conversion. `__trunc__()` alone no longer works.

### pickle Default Protocol 5

Default protocol version changed from 4 to 5. Protocol 5 supports out-of-band data buffers. Files pickled with protocol 5 can't be read by Python < 3.8.

### NotImplemented in Boolean Context

`bool(NotImplemented)` now raises `TypeError` (was `DeprecationWarning` since 3.9).

## Removed APIs — Python 3.14

### asyncio
- Child watcher classes removed: `SafeChildWatcher`, `FastChildWatcher`, `MultiLoopChildWatcher`, `PidfdChildWatcher`, `ThreadedChildWatcher`, `AbstractChildWatcher`
- `get_child_watcher()` / `set_child_watcher()` on policies

### ast
- `ast.Num`, `ast.Str`, `ast.Bytes`, `ast.NameConstant`, `ast.Ellipsis` — use `ast.Constant`
- `ast.Constant.n` and `.s` — use `.value`
- Custom `visit_Num`, `visit_Str`, etc. on `NodeVisitor` subclasses no longer called — use `visit_Constant`

### Other Removals
- `itertools` iterator copy/deepcopy/pickle support
- `pkgutil.get_loader()` and `find_loader()`
- `urllib.request.URLopener` and `FancyURLopener` — use `urlopen()`
- `pty.master_open()` and `slave_open()` — use `pty.openpty()`
- `sqlite3.version` and `version_info` — use `sqlite_version`

## Key Deprecations — Python 3.14

### Removal in 3.16
- `asyncio.iscoroutinefunction()` — use `inspect.iscoroutinefunction()`
- `asyncio` policy system (`AbstractEventLoopPolicy`, `get_event_loop_policy()`, `set_event_loop_policy()`) — use `asyncio.run(loop_factory=...)` instead
- `codecs.open()` — use `open()`

### Other Deprecations
- `argparse.FileType` — handle file opening after parsing
- `os.popen()` and `os.spawn*` — use `subprocess`
- `pathlib.PurePath.as_uri()` (removal in 3.19) — use `pathlib.Path.as_uri()`
