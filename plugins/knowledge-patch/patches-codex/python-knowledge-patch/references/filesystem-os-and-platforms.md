# Filesystems, operating systems, and platforms

## Paths and links

### Path probing and suffixes

`Path.exists()` and the `Path.is_*()` predicates suppress every `OSError` in
Python 3.14; call `Path.stat()` when the failure must remain observable. A
trailing dot is now a suffix, so `PurePath("foo.bar.").suffixes` is
`[".bar", "."]`.

### Parent modes and missing-path resolution

Python 3.15 adds `parent_mode` to `os.makedirs()` and
`Path.mkdir(parents=True)` for intermediate directories. Linux exposes
`os.statx()`. `os.path.realpath(strict=os.path.ALLOW_MISSING)` permits missing
components, re-raises other failures, and guarantees the resolved portion is
free of symlinks.

### Hard-link symlink behavior

`os.link()` follows symlinks by default on Linux. Windows rejects
`follow_symlinks=True`; macOS can reject `follow_symlinks=False` when `linkat()`
is unavailable.

### Time-zone search paths

In Python 3.15.0b3, `zoneinfo.reset_tzpath()` accepts `PathLike` values after
`os.fspath()` conversion and reports relative paths with `ValueError`.

## File descriptors and memory maps

### Unix descriptor APIs

Linux builds expose `timerfd_create()`, floating-point and nanosecond timer get
and set functions, and `TFD_NONBLOCK`, `TFD_CLOEXEC`, `TFD_TIMER_ABSTIME`, and
`TFD_TIMER_CANCEL_ON_SET`. Unix `mmap.mmap(..., trackfd=False)` avoids
duplicating the supplied descriptor.

### File-like mappings

`mmap.mmap` implements `seekable()`, and `seek()` returns the new absolute
position instead of `None`.

### Nonblocking digest and descriptor I/O

`hashlib.file_digest()` raises `BlockingIOError` when a nonblocking stream has
no data instead of incorporating spurious null bytes. `fcntl.fcntl()` accepts
any bytes-like object. `fcntl.ioctl()` retries `EINTR` and releases the GIL for
large bytes-like arguments.

### Mapping labels, tracking, and resize availability

Python 3.15 gives Windows `mmap.mmap()` a `trackfd=False` option. Linux mappings
can be labeled with `set_name()` on supporting kernels. On platforms without a
resize syscall, `mmap.resize` is absent instead of failing with `SystemError`.

In 3.15.0b3, `mmap.flush(flags=...)` selects synchronization behavior. `size()`
returns the size of anonymous mappings on Unix and Windows; a mapping created
with `trackfd=False` raises `ValueError` when the backing size is unavailable.

## Resources, locale, and process state

### Resource limit behavior and constants

`resource.RLIM_INFINITY` is always positive in Python 3.15, and old negative
spellings are deprecated. In 3.15.0b3, supported systems can expose
`RLIMIT_NTHR`, `RLIMIT_UMTXP`, `RLIMIT_PIPEBUF`, `RLIMIT_THREADS`,
`RLIM_SAVED_CUR`, and `RLIM_SAVED_MAX`. Other low-level additions include
`os.NODEV`, `os.RWF_DONTCACHE`, `os.RWF_ATOMIC`, `socket.IPV6_HDRINCL`, and
additional ISO-TP socket constants.

### Locale modifiers and discovery

`setlocale()` accepts `@` modifiers, and `getlocale()` preserves them in the
returned language code. `locale.getdefaultlocale()` is no longer deprecated.
Remember that `locale.nl_langinfo()` can temporarily change process-wide
`LC_CTYPE` and affect concurrent locale-sensitive threads.

### Timestamp semantics

Python 3.15.0b3 supports negative timestamps on Windows in `time.gmtime()`,
`time.localtime()`, and relevant datetime functions. `datetime.now()` uses the
same half-even rounding as `fromtimestamp()`.

### Environment-clearing audit

`os.environ.clear()` emits the `os._clearenv` audit event in Python 3.15.0b3.

## Platforms and environments

### Platform identification

Python 3.14 requires Windows 10 and exposes every Windows code page as a
`cpXXX` codec. On FreeBSD, `sys.platform` is always `"freebsd"` without a
release suffix. `platform.libc_ver()` can identify musl on Alpine Linux.

### Virtual-environment directory separation

On POSIX systems where `sys.platlibdir != "lib"`, Python 3.15 virtual
environments create a real platform-library directory rather than a
`lib64 -> lib` symlink. Purelib and platlib no longer share one directory.

### Capability-based curses APIs

Python 3.15.0b3 exposes mouse APIs such as `getmouse()` and `BUTTON*`, plus
`set_escdelay()`, `set_tabsize()`, `ESCDELAY`, and `TABSIZE`, according to actual
curses capabilities rather than ncurses-only macros. They are available with
NetBSD curses or PDCurses when those implementations support them.
