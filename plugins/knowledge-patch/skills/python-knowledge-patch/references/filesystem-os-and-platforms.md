# Filesystems, operating systems, and platforms

Use this reference for path handling, process and low-level OS APIs, memory mapping, environments and locale, and platform-specific behavior.

## Filesystems and paths

### Windows filesystem semantics (Python 3.13)
On Windows, `os.path.isabs()` no longer treats a path beginning with exactly one slash or backslash as absolute. `os.mkdir()` and `os.makedirs()` now honor mode `0o700` by applying access control (other mode values remain ignored), which also makes `tempfile.mkdtemp()` private by default.

### Changed recursive glob behavior (Python 3.13)
`Path.glob()` and `Path.rglob()` patterns ending in `**` now return both files and directories; add a trailing slash to retain the old directories-only result. Their new `recurse_symlinks` keyword controls whether recursive wildcard expansion follows symlinks.

### Path text newline handling and symlink loops (3.13.0)
`Path.read_text()` accepts a `newline` parameter. `Path.resolve()` treats symlink loops like other errors: strict mode raises `OSError`, while non-strict mode does not raise.

### Deep directory comparisons (3.13.0)
`filecmp.dircmp` can request non-shallow comparisons, matching the deep-comparison option already available on `filecmp.cmp()`.

### Missing-but-symlink-free real paths (Python 3.14)
`os.path.realpath(path, strict=os.path.ALLOW_MISSING)` permits nonexistent components but re-raises other errors, producing a path whose existing portion is fully resolved and symlink-free.

### Cached path type information (Python 3.14)
`Path.info` implements the new `pathlib.types.PathInfo` protocol and caches file-type/stat queries; paths yielded by `iterdir()` begin with type information obtained during the directory scan.

### Trailing-dot path suffixes (3.14.0)
`pathlib` treats a final dot as a suffix, bringing its splitting behavior in line with `os.path.splitext()`.

```python
assert PurePath("archive.tar.").suffixes == [".tar", "."]
```

### Broader `pathlib` error suppression (3.14.0)
`Path.exists()` and the `Path.is_*()` predicates now suppress every `OSError`, not just a selected set, and return `False`; use `Path.stat()` when the underlying failure must remain visible.

### Platform-specific hard-link semantics (3.14.0)
On Linux, `os.link()` now follows symlinks by default and when `follow_symlinks=True`. Windows rejects `follow_symlinks=True`, while macOS can reject `follow_symlinks=False` when `linkat()` is unavailable.

### Timestamp and time-zone path semantics (3.15.0b3)
On Windows, `time.gmtime()`, `time.localtime()`, and related `datetime` APIs accept negative timestamps; `datetime.now()` uses half-even rounding like `fromtimestamp()`. `zoneinfo.reset_tzpath()` converts `PathLike` entries to strings, rejects other types, and reports a relative path with `ValueError`.

## OS processes and low-level APIs

### Process-aware CPU counts and overrides (Python 3.13)
`os.process_cpu_count()` reports logical CPUs usable by the current process, and it now drives default worker counts in `compileall`, `concurrent.futures`, and `multiprocessing`. Both it and `os.cpu_count()` can be overridden with `PYTHON_CPU_COUNT` or `-X cpu_count` to impose a CPU count without changing application code.

### Linux timer file descriptors (Python 3.13)
`os` now exposes Linux timerfds through `timerfd_create()`, `timerfd_settime()`/`timerfd_settime_ns()`, `timerfd_gettime()`/`timerfd_gettime_ns()`, and the `TFD_*` flags.

### Unified `getpass.getuser()` failures (Python 3.13)
`getpass.getuser()` now raises `OSError` for every failure to retrieve a username, replacing the platform-dependent `ImportError` or `KeyError` cases.

### Expanded platform process and terminal APIs (3.13.0)
POSIX builds add `os.posix_openpt()`, `grantpt()`, `unlockpt()`, and `ptsname()`, while macOS gains `os.waitid()`. Windows gains `os.fchmod()`, file-descriptor support in `os.chmod()`, `os.lchmod()` and `follow_symlinks` handling, and multiprocessing pools may exceed 62 processes.

### Broader `fcntl` buffers and interruption handling (3.14.0)
`fcntl.fcntl()` accepts arbitrary bytes-like objects rather than only `bytes`. `fcntl.ioctl()` now retries `EINTR` automatically and releases the GIL for system calls made with large bytes-like objects.

### New low-level platform constants (3.15.0b3)
`os` adds `NODEV`; qualifying Linux builds also expose `RWF_ATOMIC` (Linux 6.11+) and `RWF_DONTCACHE` (Linux 6.14+). Socket support adds `IPV6_HDRINCL`, Linux `SO_PASSRIGHTS`, and missing ISO-TP constants, while `resource` gains `RLIMIT_NTHR`, `RLIMIT_UMTXP`, `RLIMIT_PIPEBUF`, `RLIMIT_THREADS`, `RLIM_SAVED_CUR`, and `RLIM_SAVED_MAX` where supplied by the platform.

## Memory mappings and resources

### Controlling `mmap` descriptor ownership (Python 3.13)
On Unix, `mmap.mmap(..., trackfd=False)` prevents the mapping from duplicating and retaining the supplied file descriptor.

### File-like `mmap` positioning (3.13.0)
`mmap.mmap` now has `seekable()`, and `seek()` returns the new absolute position, making mappings conform better to seekable file-like interfaces.

### Expanded OS and memory-mapping controls (Python 3.15 preview)
Linux builds expose `os.statx()`, and `os.makedirs(..., parent_mode=...)` plus `Path.mkdir(..., parents=True, parent_mode=...)` can set a distinct mode on intermediate directories. Windows now supports `mmap(..., trackfd=False)` without duplicating the supplied handle, Linux 5.17 or newer can label anonymous mappings with `mmap.set_name()`, and unsupported platforms omit `mmap.resize()` instead of exposing a method that fails with `SystemError`.

### More complete `mmap` synchronization and sizing (3.15.0b3)
`mmap.flush()` accepts a `flags` argument to control synchronization behavior. `mmap.size()` returns the size of anonymous mappings on both Unix and Windows, while mappings created with `trackfd=False` raise `ValueError` because no backing descriptor is retained.

### Resource-limit value handling (3.15.0b3)
`resource.getrlimit()` returns large finite limits as positive integers rather than wrapping them negative, and `setrlimit()` accepts such values while rejecting negative values other than `RLIM_INFINITY`.

## Environments, startup, and locale

### UTF-8-first `.pth` decoding (Python 3.13)
`site` now decodes `.pth` files as UTF-8 first and falls back to the locale encoding only when UTF-8 decoding fails.

### Virtual-environment SCM ignore files (Python 3.13)
The `venv` CLI now creates supported SCM ignore files (Git by default) unless `--without-scm-ignore-files` is passed, while `EnvBuilder` and `venv.create()` expose the feature as an opt-in API.

### Multi-value locale results (3.14.0)
`locale.nl_langinfo(locale.ALT_DIGITS)` returns up to 100 symbols in one semicolon-separated string, and `locale.ERA` likewise returns all era-description segments rather than only the first one.

### Virtual-environment prefixes without `site` (3.14.0)
Launching a virtual environment with `-S` no longer makes its prefix values fall back to the base installation: `sys.prefix` and `sys.base_prefix` point to the virtual environment even when `site` is disabled.

### Locale modifiers and restored locale discovery (Python 3.15 preview)
`locale.setlocale()` accepts language codes containing `@` modifiers and `getlocale()` preserves those modifiers instead of stripping them. `locale.getdefaultlocale()` is no longer deprecated.

### Virtual-environment directory separation (Python 3.15 preview)
On POSIX platforms whose `sys.platlibdir` is not `lib`, virtual environments now create the platform-library directories instead of a `lib64 -> lib` symlink. Pure-Python and platform-library installation paths therefore no longer necessarily share one physical directory.

## Platform and user-interface behavior

### Typed Tkinter callback arguments (3.13.0)
`tkinter.wantobjects` now defaults to `2`, so callback arguments are converted according to their Tcl representation into Python values such as integers, floats, bytes, and tuples instead of always being strings.

### Predictable Tk text counts (3.13.0)
`Text.count(..., return_ints=True)` always returns a single count as an integer rather than a one-tuple or `None`; the default otherwise preserves the older return convention.

### Expanded Tk window and image APIs (3.13.0)
`wm_attributes()` accepts names without a leading dash, accepts keyword assignments, and can return a dictionary with `return_python_dict=True`. `PhotoImage` adds `read()`, `data()`, `copy_replace()`, and richer copy/write options, while widgets add `after_info()`.

### Android and iOS platform identity (3.13.0)
Android now reports `sys.platform == "android"` and exposes device and OS details through `platform.android_ver()`. The build system adds Android support plus iOS framework targets, an iOS platform guide, and a loader for extension modules stored in framework directories.

### Stable FreeBSD platform identifier (Python 3.14)
`sys.platform` is now always `freebsd` on FreeBSD rather than embedding the major release as values such as `freebsd13`; code matching version-suffixed platform identifiers must be updated.

### Extended Tk text searching (3.15.0b3)
`tkinter.Text.search()` supports the Tcl `-nolinestop` and `-strictlimits` modes, and `Text.search_all()` exposes `-all` and `-overlap` searches that return every matching position.

### Capability-based curses APIs (3.15.0b3)
The curses mouse interface and the `set_escdelay()`/`set_tabsize()` functions plus `ESCDELAY`/`TABSIZE` variables are detected by capabilities rather than ncurses-only macros, making them available with implementations such as NetBSD curses and PDCurses when supported.
