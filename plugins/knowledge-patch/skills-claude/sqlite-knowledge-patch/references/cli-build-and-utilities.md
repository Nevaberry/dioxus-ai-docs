# CLI, Builds, and Utilities

## Configure and build systems

### Canonical-source builds (since 3.48.0)

The canonical-source `configure` script uses Autosetup instead of GNU
Autoconf. Most targets require only a C compiler plus `make` or `nmake`. The
amalgamation tarball's build system is unchanged at that point. Tcl remains
required for tests and Tcl-based accessory programs such as
`sqlite3_analyzer`.

### Amalgamation-tarball builds (since 3.49.0)

The precompiled amalgamation tarball's main `configure` script also uses
Autosetup instead of Autotools, completing the build-system change. The
deprecated TEA subdirectory still uses Autotools.

### Installation (3.47.1)

The `make install` target once again honors `DESTDIR`.

## Tcl support and behavior

SQLite 3.47.0 supports Tcl 9. Tcl 8.5 and later are expected to continue
working, but that compatibility is no longer guaranteed.

As of 3.51.0, Tcl `eval -asdict` supplies each row as a dictionary. A Tcl
user-defined function may `break` to return SQL `NULL`.

## Bundled build features and provenance

As of 3.51.0:

- `SQLITE_SCM_BRANCH`, `SQLITE_SCM_TAGS`, and `SQLITE_SCM_DATETIME` expose
  the source check-in's branch, tags, and timestamp.
- The amalgamation contains `carray` and `percentile`, but they remain
  disabled unless built with `SQLITE_ENABLE_CARRAY` or
  `SQLITE_ENABLE_PERCENTILE`.
- Non-canonical 64-bit WASM builds can be produced with `make`; canonical
  builds remain 32-bit.

## CLI functions and utility programs

### Aggregate extensions and utility behavior

- The CLI adds the `median()`, `percentile()`, `percentile_cont()`, and
  `percentile_disc()` extension functions and the `.www` command.
- The release adds the experimental `sqlite3_rsync` program.
- `sqlite3_analyzer` reports `WITHOUT ROWID` statistics separately.
- `sqldiff` no longer creates an empty database when its second path is
  absent.
- Version 3.47.1 fixes Windows line endings in `sqlite3_rsync.exe`.

### `sqlite3_rsync` behavior (since 3.50.0)

`sqlite3_rsync` no longer requires WAL mode and uses less bandwidth when the
source and replica are already similar. On macOS, the remote executable can
be found in `$HOME/bin`, `/usr/local/bin`, or `/opt/homebrew/bin`. Use 3.50.1
or later because 3.50.0 can omit the replica's final page.

As of 3.53.0, `sqlite3_rsync` supports `-p` and `--port` to select a port.

## CLI control-character escaping

As of 3.50.0, the CLI avoids emitting most control characters directly.
`.dump` encodes special characters with `unistr()` unless escape mode is off.
A dump containing such values consequently requires `unistr()` support when
restored unless that escaping is disabled.

## Shell behavior and display

### Startup, imposter, width, timing, and display controls

- As of 3.51.0, `--ifexists` is accepted at startup and by `.open`.
- As of 3.51.0, `.imposter` is read-only and usable with `VACUUM` without
  `--unsafe-testing`.
- As of 3.51.0, `.width` is capped at 30,000.
- As of 3.51.0, `.timer` reports values in microseconds.
- As of 3.51.0, `box` and `column` modes handle double-wide characters.

```text
sqlite3 --ifexists existing.db
.open --ifexists existing.db
```

### Query Result Formatter and output defaults (since 3.53.0)

The Query Result Formatter library formats query results for fixed-pitch
displays and is exposed through the Tcl interface's `format` method.
Interactive CLI sessions default to Unicode box output and right-justify
numbers in tabular modes. Batch sessions retain the legacy format.

### Scripts and one-shot controls (since 3.53.0)

A non-empty `*.sql` or `*.txt` file named as a command-line argument is
executed as a script. An unquoted trailing semicolon on a dot-command is
ignored. `.timer once` times only the next SQL statement, and
`.progress --timeout S` interrupts statements after `S` seconds.

```text
sqlite3 app.db setup.sql
.timer once
.progress --timeout 5
```

### `.indexes` pattern matching (since 3.53.0)

The `.indexes PATTERN` argument matches index names instead of names of
indexed tables. This can change existing shell-script results.

## Windows build and platform support

`SQLITE_USE_STDIO_FOR_CONSOLE` was removed in 3.49.0. Windows
command-line-tool builds can define `SQLITE_USE_W32_FOR_CONSOLE_IO` to use
Win32 console APIs without affecting the SQLite core.

Windows RT is no longer supported as of 3.53.0.
