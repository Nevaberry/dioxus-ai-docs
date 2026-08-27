---
name: python-knowledge-patch
description: Python
version: "3.14"
license: MIT
metadata:
  author: Nevaberry
---


# Python Knowledge Patch

Use this skill when changing Python applications, libraries, tooling, native
extensions, embedding code, builds, or distribution automation. Start with the
migration checks below, then open the topic reference that owns the affected
API. Confirm the exact interpreter and maintenance release before applying
version-dependent behavior.

## Reference index

| Reference | Topics |
| --- | --- |
| [Language and runtime](references/language-and-runtime.md) | Execution semantics, built-ins, object behavior, text, numerics, garbage collection, and Python-level migrations |
| [Typing and introspection](references/typing-and-introspection.md) | ASTs, annotations, type expressions, signatures, frames, symbols, and runtime metadata |
| [Concurrency and asyncio](references/concurrency-and-asyncio.md) | Threads, processes, asyncio, subinterpreters, free-threading, and concurrent iterators |
| [Data, I/O, and serialization](references/data-io-and-serialization.md) | Configuration, archives, compression, SQLite, structured formats, streams, and codecs |
| [Networking and security](references/networking-and-security.md) | TLS, HTTP, URLs, email, sockets, protocol limits, parsers, and defensive validation |
| [Filesystems, OS, and platforms](references/filesystem-os-and-platforms.md) | Paths, descriptors, memory maps, resources, locales, virtual environments, and platform behavior |
| [Tooling, debugging, and testing](references/tooling-debugging-and-testing.md) | Startup, imports, profiling, monitoring, pdb, logging, CLI parsing, tests, IDLE, and Tk |
| [C API and extensions](references/c-api-and-extensions.md) | Ownership, errors, types, module initialization, embedding, free-threading, Stable ABI, and migrations |
| [Build and distribution](references/build-and-distribution.md) | Configure requirements, JIT controls, artifacts, cross-builds, installers, and platform targets |

## Migration-first quick reference

### Check maintenance releases, not only minor versions

- Python 3.14.0 through 3.14.4 use the two-generation incremental garbage
  collector. Python 3.14.5 and later return to the 3.13 generational design.
- Python 3.13.3 briefly forwarded arbitrary task-creation keywords through a
  contract that broke established custom task factories. Guard workarounds by
  the 3.13 maintenance release; 3.13.4 and later restore compatibility while
  retaining the keyword channel.
- Windows and macOS runtime availability also changes by maintenance release;
  verify the installer and platform floor before publishing support claims.

### Remove obsolete Python APIs before upgrading

- Replace `pkgutil.get_loader()` and `find_loader()`, `pty.master_open()` and
  `slave_open()`, and `URLopener` or `FancyURLopener` before Python 3.14.
- Import resource ABCs from `importlib.resources.abc`, not `importlib.abc`.
- Python 3.15 removes CGI serving, the legacy `sre_*` modules,
  `PurePath.is_reserved()`, `code.co_lnotab`, old loader `load_module()`
  definitions, and other deprecated entry points. Use the complete removal
  lists in the language and tooling references.
- Copying, deep-copying, or pickling `itertools` iterator objects is no longer
  supported in Python 3.14.

### Make call styles explicit

- Pass `sqlite3.connect()` options after the database by keyword; these become
  keyword-only in Python 3.15. Pass the name/count/callable arguments of
  SQLite function registration, aggregates, and handler setters positionally.
- Named SQLite placeholders require a mapping in Python 3.14; a sequence raises
  `ProgrammingError`.
- `functools.reduce()` accepts `initial=`, while `function=` and `sequence=`
  are deprecated and become errors in Python 3.16.
- Pass a string to `complex()` positionally. Avoid a complex value in either
  the `real` or `imag` component.
- A `functools.partial` stored directly on a class emits `FutureWarning`; wrap
  it in `staticmethod()` when non-binding behavior is intended.

```python
class Handler:
    parse = staticmethod(functools.partial(parse, strict=True))

con = sqlite3.connect("app.db", timeout=10)
con.create_function("slug", 1, slug)
```

### Audit changed defaults and failure modes

- `gzip.compress()` uses `mtime=0` and an OS byte of 255 by default, and pickle
  protocol 5 is the default. Choose older behavior explicitly for consumers
  that require it.
- Unclosed `gzip.GzipFile` and `tempfile.NamedTemporaryFile` objects can emit
  `ResourceWarning`; use context managers for owned resources.
- `Path.exists()` and `Path.is_*()` suppress every `OSError`. Use `stat()` when
  callers must distinguish absence from permission or I/O failures.
- Text reads on nonblocking streams and `hashlib.file_digest()` can raise
  `BlockingIOError` instead of returning misleading data.
- `ConfigParser.write()` rejects keys that cannot round-trip, and email header
  generation rejects unsafe names, folds, and delimiters.
- On Python 3.15, implicit text encoding is UTF-8. Request
  `encoding="locale"` when locale-dependent behavior is intentional.

### Harden archives, URLs, and protocols

- Tar extraction filters are reapplied during link fallback and directory
  fixups; rejected members stay rejected even at `errorlevel=0`.
- `ZipFile.writestr()` honors `SOURCE_DATE_EPOCH`. Python 3.15 reproducible ZIP
  timestamps use UTC, and gzip and gzip-tar compression default to level 6.
- Use the file-URL conversion controls deliberately: scheme requirements,
  authority resolution, and query/fragment removal can change results.
- HTTP clients can bound response headers; later behavior also bounds chunked
  trailers and limits interim responses. Treat those limits as security
  controls, not incidental parser details.
- Protocol code should expect stricter validation of control characters in
  URLs, cookies, WSGI, HTTP tunnels, POP3, and related fields.

### Review native-extension ownership and synchronization

- `PyModule_Add()` always steals the supplied reference, including on failure.
- Prefer strong-reference getters such as `PyDict_GetItemRef()`,
  `PyList_GetItemRef()`, `PyImport_AddModuleRef()`, and `PyWeakref_GetRef()`;
  release the returned references.
- Use `PyObject_HasAttrWithError()` or `PyMapping_HasKeyWithError()` when a
  failed lookup must not be suppressed.
- Include system headers directly; `Python.h` no longer provides several of
  them transitively.
- `PyDict_Next()` does not lock in free-threaded builds. Hold one critical
  section around the complete iteration.
- Reference-count equality is not a safe uniqueness test with borrowed operand
  stack references. Use the appropriate `PyUnstable_Object_Is*Referenced()`
  helper.
- `Py_Finalize()` deletes interned strings. Embedders that reinitialize must
  release extension-held interned references during shutdown.

## High-value capabilities

### Lazy imports and immutable values

Python 3.15 adds module-scope lazy imports. Loading occurs when the imported
name is first used; star imports, future imports, `try` blocks, and nested
declarations are excluded.

```python
lazy import json
lazy from pathlib import Path

payload = json.loads('{"answer": 42}')
```

- Global lazy-import behavior is controlled by `-X lazy_imports=all`,
  `PYTHON_LAZY_IMPORTS`, and the `sys` filter APIs.
- `frozendict` is immutable, insertion ordered, and hashable only when all
  contents are hashable. Accept general mappings through
  `collections.abc.Mapping`.
- `sentinel` creates identity-stable markers that can participate in type
  expressions and can be pickleable when importable by name.
- Comprehensions and generator expressions accept `*` and `**` unpacking.

### Profiling and live diagnostics

- `profiling.tracing` is the deterministic profiler and
  `profiling.sampling` is an attachable sampler; `cProfile` remains an alias,
  while the pure-Python `profile` module is deprecated.
- Sampling supports wall, CPU, GIL, and exception time; async reconstruction;
  flame graphs, pstats, heatmaps, and compact replayable captures.
- Pdb can attach to a same-version process with `-p PID`; use
  `await pdb.set_trace_async()` inside coroutines.
- Asyncio exposes process task inspection and in-process call-graph capture.
- Native diagnostics can include operating-system thread names and C stacks.

### Safer structured data and binary handling

- `json.load()` and `loads()` accept `array_hook`; pair `tuple` with a
  `frozendict` object-pairs hook for deeply immutable decoded data.
- `bytearray.take_bytes()` removes a prefix and returns it as `bytes` without
  copying.
- `tomllib` accepts TOML 1.1 syntax, including multiline inline tables,
  trailing commas, new escapes, and time values without seconds.
- Base encoders and decoders add explicit padding, wrapping, ignored-character,
  and canonical controls. Canonical decoding rejects noncanonical padding.
- `zlib.adler32_combine()` and `crc32_combine()` combine checksums without
  replaying the original inputs.

### Concurrency and isolation

- `asyncio.TaskGroup.cancel()` directly cancels a task group.
- `threading.serialize_iterator`, `synchronized_iterator()`, and
  `concurrent_tee()` are supported tools for shared iteration.
- Free-threaded builds define documented concurrent-iteration guarantees for
  range and selected `itertools` iterators.
- Query isolated-interpreter support through
  `sys.implementation.supports_isolated_interpreters` before relying on it.
- Context-manager decorators now keep their context active across returned
  generators, async generators, and awaited coroutines.

## Upgrade workflow

1. Record the exact Python version, build mode, ABI, operating system, and
   installer source.
2. Search for removed and deprecated Python and C APIs before adapting new
   behavior.
3. Audit defaults affecting serialization, encoding, archive metadata, path
   errors, parser limits, and task factories.
4. Exercise nonblocking streams, malformed protocol input, resource cleanup,
   interpreter shutdown, and extension imports with warnings visible.
5. For free-threaded builds, review extension declarations, critical sections,
   iterator sharing, warning/context inheritance, and packaging support.
6. Open every applicable topic reference; the quick reference intentionally
   prioritizes migration risk rather than API completeness.
