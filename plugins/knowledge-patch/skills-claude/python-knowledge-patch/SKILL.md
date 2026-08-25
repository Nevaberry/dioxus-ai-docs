---
name: python-knowledge-patch
description: Python
version: 3.14
license: MIT
metadata:
  author: Nevaberry
---


# Python Knowledge Patch

Use this skill when updating Python applications, libraries, tooling, native
extensions, embedded runtimes, or CPython builds whose behavior depends on
recent language and standard-library changes.

Confirm the exact interpreter and maintenance release before applying an item.
Open the topic reference that matches the code under review; the quick
reference below emphasizes compatibility failures, changed defaults, and the
most broadly useful additions.

## Reference index

| Reference | Topics |
| --- | --- |
| [Language and runtime](references/language-and-runtime.md) | Syntax, built-ins, object behavior, text, numbers, garbage collection, removals |
| [Typing and introspection](references/typing-and-introspection.md) | Annotations, ASTs, frames, signatures, type expressions, symbols |
| [Concurrency and asyncio](references/concurrency-and-asyncio.md) | Threads, queues, multiprocessing, task groups, subinterpreters, free-threading |
| [Data, I/O, and serialization](references/data-io-and-serialization.md) | Configuration, SQLite, archives, compression, structured data, streams |
| [Networking and security](references/networking-and-security.md) | TLS, HTTP, URLs, email, protocol parsing and validation |
| [Filesystems, OS, and platforms](references/filesystem-os-and-platforms.md) | Paths, descriptors, memory maps, resources, locale, operating systems |
| [Tooling, debugging, and testing](references/tooling-debugging-and-testing.md) | Imports, REPLs, profiling, pdb, logging, warnings, tests, packaging |
| [C API and extensions](references/c-api-and-extensions.md) | Extension compatibility, references, types, modules, embedding, Stable ABI |
| [Build and distribution](references/build-and-distribution.md) | Configure controls, JIT, toolchains, artifacts, cross-builds, installers |

## Compatibility first

### Runtime and language behavior

- `functools.partial` stored directly on a class emits `FutureWarning`; wrap it
  in `staticmethod()` when non-binding behavior is intended.
- Optimized builds reject the same invalid syntax as ordinary builds. Do not
  rely on `-O` to remove an invalid write to `__debug__`, `await`, or async
  comprehension.
- Generator-expression iteration is deferred until the generator runs. Code
  that expects a source error at construction must force iteration explicitly.
- `Path.exists()` and `Path.is_*()` suppress every `OSError`; use `stat()` when
  permissions, encoding, or other failures must remain observable.
- `\B` now matches empty input as the inverse of `\b`. Use `(?!\A\Z)\B` when
  empty strings must remain excluded.
- Copying or pickling `itertools` iterators is no longer supported.
- Garbage-collector behavior depends on the maintenance release: do not infer
  the collector design from the feature release alone.

### Removed and deprecated call patterns

- Pass a mapping for SQLite named placeholders. Sequences now raise
  `ProgrammingError`.
- Use `sqlite_version` and `sqlite_version_info`; the module's `version` and
  `version_info` attributes are removed.
- Prefer `subprocess` to `os.popen()` and `os.spawn*()`, `Path.as_uri()` to
  `PurePath.as_uri()`, and normal file opening to `codecs.open()`.
- Replace `pkgutil.get_loader()` / `find_loader()`, `pty.master_open()` /
  `slave_open()`, and the legacy `URLopener` classes before upgrading.
- Name `sqlite3.connect()` options after the database; pass function and
  callback registration arguments positionally.
- Use `os.path.isreserved()` instead of `PurePath.is_reserved()`, modern loader
  APIs instead of `load_module()`, and class or mapping forms for `NamedTuple`
  and `TypedDict` construction.
- Stop depending on `CodeType.co_lnotab`, the private `sre_*` modules, CGI
  support in `http.server`, or removed WAVE marker methods.
- Avoid legacy false query-string inputs; normalize them before parsing.

### Changed defaults and failure modes

- `gzip.compress()` produces reproducible output by default with `mtime=0` and
  OS byte 255. Pass `mtime=None` when wall-clock timestamps are desired.
- Pickle protocol 5 is the default. Select an older protocol explicitly when
  older consumers must read the data.
- Unclosed `GzipFile` and `NamedTemporaryFile` instances emit
  `ResourceWarning`; use explicit ownership and closure.
- Nonblocking text reads and `hashlib.file_digest()` may raise
  `BlockingIOError` instead of returning empty/spurious data.
- Email header assignment validates field names, and generators reject unsafe
  or non-EAI output instead of flattening it inaccurately.
- `ConfigParser` refuses keys that would not round-trip through its output.
- `QueueListener.start()` raises if already started; use it as a context
  manager for paired startup and shutdown.
- Query-string, URL, cookie, WSGI, HTTP, POP3, IMAP, and archive handling has
  stricter input validation. Keep malformed-input tests in compatibility runs.

### Asyncio, processes, and free-threading

- Guard custom task factories by exact maintenance release: the 3.13.3
  keyword-forwarding behavior was corrected in 3.13.4.
- `Thread.join()` waits for the underlying operating-system thread to exit.
- Unix asyncio servers remove their socket path when closed.
- `SharedMemory(track=False)` opts out of resource-tracker cleanup; tracker
  leaks now produce a nonzero tracker exit.
- Free-threaded builds change warning-context and thread-context inheritance.
  Test both GIL-enabled and free-threaded configurations when relevant.
- Hold one critical section around an entire `PyDict_Next()` traversal;
  per-step locking is not sufficient.
- Prefer supported iterator serialization/synchronization helpers when sharing
  generators across concurrent callers.
- Use direct task-group cancellation when the target runtime provides it,
  instead of injecting a task whose only purpose is to raise.

## High-value additions

### Safer structured data and I/O

- `ConfigParser(allow_unnamed_section=True)` accepts top-level keys; newer
  mapping access can also create `UNNAMED_SECTION`.
- `importlib.resources` helpers accept nested path components. Pass text
  `encoding` and `errors` by keyword.
- Tar streaming can avoid caching every member. Tar extraction filters also
  harden symlink fallback and directory fixups.
- `ZipFile.writestr()` honors `SOURCE_DATE_EPOCH`, and `ZipInfo._for_archive()`
  resolves the metadata defaults that will be written.
- `io.Reader` and `io.Writer` are structural protocols for simple stream APIs.
- TOML 1.1 users should open the data reference for exact parsing changes.

### Runtime features to gate by interpreter

- `Fraction` accepts any object implementing `as_integer_ratio()`.
- Three-argument `pow()` can dispatch to `__rpow__()`.
- `super` objects can be copied and pickled.
- `datetime` and `time` ISO parsing accepts `24:00`.
- Newer runtimes add explicit lazy imports, immutable built-in mappings,
  identity-stable sentinels, unpacking comprehensions, generic `slice`, and
  copy-free `bytearray.take_bytes()`; never emit their syntax or built-ins for
  an older interpreter.
- Newer typing surfaces include `TypeForm`, closed or extensible `TypedDict`,
  richer type aliases, and bounded or variant `TypeVarTuple` declarations.

### Debugging and observability

- Pdb supports packaged and module targets, live process attachment, and async
  breakpoints; use the exact same runtime version for attachment.
- `sys.monitoring` exposes richer exception events, including per-code
  enablement in newer runtimes.
- Native thread names and C stacks can appear in `faulthandler` output.
- Asyncio can expose live task trees and in-process call graphs.
- The `profiling` package adds deterministic tracing plus an attachable sampling
  profiler with async-aware, process, flame-graph, and replay workflows.
- `-X importtime=2` includes cached imports, and `-X perf_jit` enables enhanced
  Linux perf integration.

### C extensions and embedding

- Declare free-threaded support with `Py_mod_gil` for multi-phase modules or
  `PyUnstable_Module_SetGIL()` for single-phase modules. Undeclared modules may
  re-enable the GIL.
- `PyModule_Add()` always steals the passed reference. Prefer new `*Ref()`
  lookup helpers when ownership must be explicit.
- Use error-preserving attribute and mapping lookup APIs when lookup failures
  must propagate instead of reaching `sys.unraisablehook()`.
- Include every system header directly; `Python.h` no longer supplies several
  platform headers transitively.
- Replace removed trashcan macros, ambiguous iteration, private integer and
  Unicode builders, and direct representation access with their public APIs.
- Limited-API reference-count and type macros are opaque. Never use
  `Py_REFCNT(obj) == 1` as a uniqueness test for borrowed stack references.
- Release extension-held interned strings before finalization when an embedder
  can reinitialize the runtime.
- Newer free-threaded Stable ABI and slot/export APIs require separate artifact
  planning; keep ordinary and free-threaded wheels distinct when unsupported
  APIs are used.

## Upgrade workflow

1. Confirm the exact executable, ABI, maintenance release, GIL mode, operating
   system, and extension build configuration.
2. Search first for removals, keyword/positional migration warnings, iterator
   serialization, old loader APIs, legacy SQLite usage, and private C APIs.
3. Audit changed defaults in serialization, text encoding, query parsing,
   archives, process startup, warning handling, and argument parsing.
4. Open the matching topic reference and trace every affected call site;
   preview-only syntax and APIs require an explicit runtime gate.
5. Run tests with warnings and `ResourceWarning` visible. Exercise malformed
   input, nonblocking I/O, shutdown, finalization, interpreter reinitialization,
   and free-threaded imports where applicable.
6. For binary extensions, test Limited/Stable API claims, ownership on every
   error path, GIL declarations, and wheel tags on every supported platform.
