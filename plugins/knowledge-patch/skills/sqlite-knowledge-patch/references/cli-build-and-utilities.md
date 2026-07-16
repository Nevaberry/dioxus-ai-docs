# CLI, Builds, and Utilities

## Interactive and batch output

Since 3.53.0, interactive shell sessions default to Unicode box output and right-align numbers in tabular modes. Batch sessions retain the legacy output format. The Query Result Formatter library supplies fixed-pitch query formatting and is also exposed by the Tcl interface's `format` method.

Other display behavior since 3.51.0:

- `box` and `column` modes account for double-wide characters.
- `.timer` reports microseconds.
- `.width` values are capped at 30,000.

The shell avoids writing most raw control characters as of 3.50.0. `.dump` encodes special characters with `unistr()` unless `--escape` mode is disabled.

## Shell scripting and dot-commands

As of 3.53.0:

- An existing, non-empty command-line file with a `*.sql` or `*.txt` name is executed as a script.
- An unquoted trailing semicolon on a dot-command is ignored.
- `.timer once` times only the next statement.
- `.progress --timeout S` interrupts a statement after `S` seconds.
- `.indexes PATTERN` matches index names rather than indexed table names and accepts additional options. Update scripts that relied on table-name matching.

Startup and `.open` accept `--ifexists` since 3.51.0. `.imposter` is read-only, works with `VACUUM`, and no longer requires `--unsafe-testing`.

The `.www` command and the shell's `median()`, `percentile()`, `percentile_cont()`, and `percentile_disc()` extension functions arrived in 3.47.0.

## Canonical-source and amalgamation builds

- Starting in 3.48.0, the canonical source tree's `./configure` uses Autosetup rather than GNU Autoconf. Common build targets need only a C compiler and `make`/`nmake`; tests and Tcl-based accessories such as `sqlite3_analyzer` still require Tcl. The `sqlite3-autoconf-NNNNNNN.tar.gz` build was not changed in that release.
- Starting in 3.49.0, the main `configure` script in the precompiled amalgamation tarball also uses Autosetup. The deprecated TEA subdirectory still depends on Autotools.
- The 3.47.1 `make install` target again honors `DESTDIR`.
- Custom JavaScript/WASM builds can select 64-bit WASM through normal `make` starting in 3.51.0, while canonical builds remain 32-bit.

## Windows build targets

`SQLITE_USE_STDIO_FOR_CONSOLE` was removed in 3.49.0 because it was nonfunctional. Windows command-line tools can define `SQLITE_USE_W32_FOR_CONSOLE_IO` to use Win32 console APIs; this option does not affect the SQLite core.

Windows RT ceased to be supported in 3.53.0.

## Tcl integration

The SQLite Tcl interface supports Tcl 9 as of 3.47.0. Tcl 8.5 and later are expected to keep working but are no longer guaranteed.

Since 3.51.0, Tcl `eval -asdict` returns row data as a dict instead of an array. A Tcl-defined SQL function may use `break` to return SQL `NULL`.

## `sqlite3_rsync`

The experimental `sqlite3_rsync` utility appeared in 3.47.0; 3.47.1 corrects Windows line endings in `sqlite3_rsync.exe`.

Since 3.50.0 it no longer requires WAL mode, transfers less data when databases are already similar, and on macOS searches `$HOME/bin`, `/usr/local/bin`, and `/opt/homebrew/bin` for the remote executable. Use 3.50.1 or later because 3.50.0 could omit the replica's final page.

Since 3.53.0, `-p` / `--port` selects the remote port.

## Analyzer and diff utilities

`sqlite3_analyzer` reports `WITHOUT ROWID` table statistics separately as of 3.47.0. `sqldiff` no longer creates an empty database when its second database path does not exist.
