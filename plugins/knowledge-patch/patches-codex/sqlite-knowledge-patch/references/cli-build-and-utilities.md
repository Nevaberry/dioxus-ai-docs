# CLI, Builds, and Utilities

Use this reference for shell automation, output compatibility, Tcl behavior,
build systems, WASM, bundled utility programs, and platform support.

## Shell invocation and output

### Control-character escaping (3.50.0)

The CLI suppresses most raw control characters. `.dump` represents special
characters with `unistr()` unless escape mode is disabled, so restoring such a
dump requires `unistr()` support when escaping remains enabled.

### Existing-database and display behavior (3.51.0)

Startup and `.open` accept `--ifexists`. `.imposter` is read-only, works with
`VACUUM`, and no longer needs `--unsafe-testing`. `.width` is capped at 30,000,
`.timer` reports microseconds, and `box` and `column` modes account for
double-wide characters.

```text
sqlite3 --ifexists existing.db
.open --ifexists existing.db
```

### QRF and interactive defaults (3.53.0)

The Query Result Formatter library formats results for fixed-pitch displays
and is available through the Tcl interface's `format` method. Interactive
shells default to Unicode box output and right-justify numbers in tabular
modes; batch sessions retain the legacy format.

### Script arguments and one-shot controls (3.53.0)

An existing non-empty `*.sql` or `*.txt` argument executes as a script. An
unquoted trailing semicolon on a dot-command is ignored. `.timer once` times
only the next SQL statement, and `.progress --timeout S` interrupts statements
after `S` seconds.

```text
sqlite3 app.db setup.sql
.timer once
.progress --timeout 5
```

### `.indexes` pattern change (3.53.0)

`.indexes PATTERN` now matches index names rather than names of indexed tables.
Update shell scripts that rely on the older result set.

## Build systems and provenance

### Canonical-source Autosetup (3.48.0)

The canonical-source `configure` script uses Autosetup rather than GNU
Autoconf. Most targets need only a C compiler and `make` or `nmake`; Tcl is
still needed for tests and Tcl-based accessories such as `sqlite3_analyzer`.
At this point the amalgamation tarball's build system was still unchanged.

### Amalgamation Autosetup (3.49.0)

The precompiled amalgamation tarball's main `configure` script also uses
Autosetup. The deprecated TEA subdirectory continues to use Autotools.

### Installation and console compatibility (3.47.0, 3.49.0)

Version 3.47.1 restores `DESTDIR` handling in `make install`.
`SQLITE_USE_STDIO_FOR_CONSOLE` is removed. Windows command-line builds can
define `SQLITE_USE_W32_FOR_CONSOLE_IO` to use Win32 console APIs without
changing the SQLite core.

### Source provenance and WASM width (3.51.0)

`SQLITE_SCM_BRANCH`, `SQLITE_SCM_TAGS`, and `SQLITE_SCM_DATETIME` expose the
source check-in branch, tags, and timestamp. Non-canonical 64-bit WASM builds
can be made with `make`; canonical WASM builds remain 32-bit.

## Tcl interface

### Tcl version support (3.47.0)

The interface supports Tcl 9. Tcl 8.5 and later are expected to keep working,
but that compatibility is no longer guaranteed.

### Dictionary rows and `NULL` (3.51.0)

Tcl `eval -asdict` presents each row as a dictionary. A Tcl user-defined
function may use `break` to return SQL `NULL`.

## Utilities

### CLI extensions and analysis tools (3.47.0)

The CLI includes `median()`, `percentile()`, `percentile_cont()`, and
`percentile_disc()` extension functions plus the `.www` command. The release
also introduces experimental `sqlite3_rsync`. `sqlite3_analyzer` reports
`WITHOUT ROWID` statistics separately, and `sqldiff` no longer creates an empty
database when its second path is missing. Version 3.47.1 fixes Windows line
endings in `sqlite3_rsync.exe`.

### `sqlite3_rsync` transport behavior (3.50.0, 3.53.0)

`sqlite3_rsync` no longer requires WAL mode and uses less bandwidth when source
and replica are similar. On macOS it searches `$HOME/bin`, `/usr/local/bin`,
and `/opt/homebrew/bin` for the remote executable. Use 3.50.1 or later because
3.50.0 can omit the replica's last page. Version 3.53.0 adds `-p` and `--port`
for selecting the port.

## Platform support

### Windows RT (3.53.0)

Windows RT is no longer supported.
