# Filesystems, operating systems, and platforms

## Descriptors and memory mappings

### Unix descriptor APIs (`whatsnew-3.13`)

Linux exposes `timerfd_create()`, float and nanosecond timer get/set functions,
and `TFD_NONBLOCK`, `TFD_CLOEXEC`, `TFD_TIMER_ABSTIME`, and
`TFD_TIMER_CANCEL_ON_SET`. On Unix, `mmap.mmap(..., trackfd=False)` avoids
duplicating the supplied file descriptor.

### Mapping controls (`whatsnew-3.15`, `3.15.0b3`)

Windows `mmap.mmap()` adds `trackfd=False`; Linux mappings can be labeled with
`set_name()`. Where no resize syscall exists, `mmap.resize` is absent rather
than raising `SystemError`.

In 3.15.0b3, `mmap.flush(flags=...)` selects synchronization behavior.
`size()` reports anonymous-mapping size on Unix and Windows. A mapping created
with `trackfd=False` raises `ValueError` when backing size is unavailable.

## Paths and file operations

### Path probing and suffixes (`3.14.0`)

`Path.exists()` and `Path.is_*()` suppress all `OSError`; use `Path.stat()` to
observe failures. A trailing dot counts as a suffix, so
`PurePath("foo.bar.").suffixes` is `[".bar", "."]`.

### Hard links and symlinks (`3.14.0`)

`os.link()` follows symlinks by default on Linux. Windows rejects
`follow_symlinks=True`; macOS may reject `follow_symlinks=False` when
`linkat()` is unavailable.

### Creation and resolution (`whatsnew-3.15`)

`os.makedirs()` and `Path.mkdir(parents=True)` accept `parent_mode` for
intermediate directories. Linux exposes `os.statx()`. Use
`os.path.realpath(strict=os.path.ALLOW_MISSING)` to allow missing components
while re-raising other errors and guaranteeing a symlink-free resolved prefix.

### Safer moves and archive paths (`3.15.0b3`)

On Windows, `shutil.unpack_archive()` skips ZIP members with drive prefixes.
`shutil.move()` resolves symlinks before deciding whether a destination is
inside its source.

## Resources, environment, and locale

### Resource-limit semantics (`whatsnew-3.15`)

`resource.RLIM_INFINITY` is always positive; negative legacy spellings are
deprecated.

### Resource and platform constants (`3.15.0b3`)

Where available, `resource` exposes `RLIMIT_NTHR`, `RLIMIT_UMTXP`,
`RLIMIT_PIPEBUF`, `RLIMIT_THREADS`, `RLIM_SAVED_CUR`, and `RLIM_SAVED_MAX`.
Low-level additions include `os.NODEV`, `os.RWF_DONTCACHE`, `os.RWF_ATOMIC`,
`socket.IPV6_HDRINCL`, and more ISO-TP socket constants.

### Locale behavior (`whatsnew-3.15`)

`setlocale()` accepts `@` modifiers and `getlocale()` preserves them in the
language code. `locale.getdefaultlocale()` is no longer deprecated.

### Environment audit event (`3.15.0b3`)

`os.environ.clear()` emits the `os._clearenv` audit event.

### Capability-based curses APIs (`3.15.0b3`)

Mouse functions such as `getmouse()` and `BUTTON*`, plus `set_escdelay()`, `set_tabsize()`,
`ESCDELAY`, and `TABSIZE`, are exposed by actual curses capability rather than
ncurses-only macros. They are available with implementations such as NetBSD
curses and PDCurses when supported.

## Platform and environment layouts

### Platform identification (`3.14.0`)

Python requires Windows 10, and all Windows code pages are available as
`cpXXX` codecs. FreeBSD uses the unsuffixed `sys.platform == "freebsd"`.
`platform.libc_ver()` can identify musl on Alpine Linux.

### Virtual-environment directories (`whatsnew-3.15`)

On POSIX systems where `sys.platlibdir != "lib"`, virtual environments create
a real platform-library directory instead of `lib64 -> lib`; purelib and
platlib no longer share one directory.

### Timestamp and time-zone paths (`3.15.0b3`)

Windows accepts negative timestamps in `time.gmtime()`, `time.localtime()`, and
related `datetime` APIs. `datetime.now()` uses half-even rounding like
`fromtimestamp()`. `zoneinfo.reset_tzpath()` accepts `PathLike` through
`os.fspath()` and raises `ValueError` for relative paths.
