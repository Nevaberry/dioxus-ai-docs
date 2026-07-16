# Data, I/O, and serialization

Use this reference for configuration and databases, serialization, compression and archives, streams and codecs, and structured-data formats.

## Databases and configuration

### Unnamed configuration-file sections (Python 3.13)
`configparser.ConfigParser(allow_unnamed_section=True)` now accepts top-level key-value pairs before any named INI section.

### SQLite-backed `dbm` by default (Python 3.13)
The new `dbm.sqlite3` backend is now the default backend selected by `dbm`; select a backend explicitly when the implementation or storage format must remain fixed.

### Explicit SQLite connection cleanup (Python 3.13)
An unclosed `sqlite3.Connection` now emits `ResourceWarning`, so connections should be closed explicitly or managed with cleanup that actually calls `close()`.

### SQLite call-convention deprecations (Python 3.13)
Passing more than one positional argument to `sqlite3.connect()` or `Connection()` is deprecated, with the remaining parameters becoming keyword-only in 3.15. Conversely, the leading arguments to `create_function()` and `create_aggregate()`, and callback arguments to the authorizer, progress, and trace methods, are becoming positional-only.

### SQLite dump filtering and CLI editing (3.13.0)
`sqlite3.Connection.iterdump()` accepts a keyword-only `filter` for selecting database objects to dump. The `python -m sqlite3` shell now enables readline editing.

### Invalid configuration continuations (3.13.0)
`ConfigParser.read()` and `read_file()` raise `ParsingError` when an indented continuation follows a key that had no value.

### Safer configuration writes (Python 3.14)
`ConfigParser.write()` raises `InvalidWriteError` for keys containing delimiters or beginning like a section header, preventing it from emitting a file that it could parse differently or not read back.

### Stricter `pathlib` and SQLite calls (Python 3.14)
`Path` rejects ignored extra keywords, and `PurePath.relative_to()` and `is_relative_to()` no longer join extra positional arguments onto the comparison path. SQLite statements with named placeholders now require a mapping; supplying a sequence raises `ProgrammingError`.

### Unnamed sections through the mapping API (3.15.0b3)
After enabling unnamed-section parsing, a `ConfigParser` can create that section through mapping access using the `configparser.UNNAMED_SECTION` key.

```python
parser[configparser.UNNAMED_SECTION] = {"setting": "value"}
```

### SQLite cursor and shell behavior (3.15.0b3)
`sqlite3.Cursor.arraysize` rejects negative values, and `fetchmany()` correctly enforces the requested maximum row count. The SQLite shell completes keywords and database object names, while `sqlite3.SQLITE_KEYWORDS` exposes SQLite's keyword set to applications.

## Serialization and object storage

### Safer `marshal` handling (Python 3.13)
The new `allow_code=False` argument on `marshal` module functions prevents both serialization and deserialization of version-dependent code objects.

### Pickle protocol default (Python 3.14)
`pickle` now writes protocol 5 by default, so callers needing compatibility with runtimes that cannot read it must choose an older protocol explicitly; serialization failures also carry notes identifying the failing object path.

### Marshal format 5 slices (3.14.0)
`marshal` can now serialize `slice` objects, and the marshal format version is 5.

```python
payload = marshal.dumps(slice(1, 10, 2))
restored = marshal.loads(payload)
```

### Immutable JSON decoding (Python 3.15 preview)
`json.load()` and `loads()` accept `array_hook`, complementing the object hooks with control over decoded arrays. Combining `object_pairs_hook=frozendict` and `array_hook=tuple` produces a recursively immutable representation.

```python
value = json.loads(text, object_pairs_hook=frozendict, array_hook=tuple)
```

### Serialization and shelf customization (Python 3.15 preview)
`pickle` can serialize private methods and nested classes. `shelve` accepts custom serialization and deserialization functions, and both shelves and the `dbm.dumb`/`dbm.sqlite3` backends expose `reorganize()` to reclaim space from deleted entries.

## Compression and archives

### Compressed-file mode values changed (Python 3.13)
`gzip.GzipFile.mode` is now the string `'rb'` or `'wb'` rather than integer `1` or `2`, and a readable object from `zipfile.ZipFile.open()` now reports `'rb'` rather than `'r'`.

### ZIP64 imports (Python 3.13)
`zipimport` now supports importing from ZIP64 archives rather than only classic-size ZIP files.

### Uncached tar streaming (3.13.0)
`tarfile` has a stream mode that reads an archive without caching information for all of its members, reducing retained state for one-pass processing.

### Public ZIP compression level (3.13.0)
`ZipInfo.compress_level` is the public spelling of the formerly protected `_compresslevel` attribute; the old name remains as a compatibility property.

### Zstandard and the `compression` namespace (Python 3.14)
The new `compression.zstd` module handles Zstandard data, and `tarfile`, `zipfile`, and `shutil` understand Zstandard archives. `compression.gzip`, `.bz2`, `.lzma`, and `.zlib` are now the preferred re-export paths, although their original top-level modules are not deprecated.

### Hardened tar extraction filters (Python 3.14)
`tarfile.data_filter()` now normalizes symbolic-link targets, and filters are reapplied when links fall back to copied members or directory attributes are fixed up. Rejected members remain rejected even at `errorlevel=0`, and a rejected link fallback can raise `LinkFallbackError`.

### Reproducible ZIP timestamps (Python 3.14)
`ZipFile.writestr()` now respects `SOURCE_DATE_EPOCH`, allowing generated ZIP archives to participate in reproducible-build timestamp control.

### Reproducible gzip compression by default (3.14.0)
`gzip.compress()` now defaults `mtime` to `0`, making its output reproducible. Pass `mtime=None` when the header should contain the current time.

```python
stable = gzip.compress(data)
dated = gzip.compress(data, mtime=None)
```

### Streaming XZ compression presets (3.14.0)
`tarfile.open()` accepts `preset` with streaming XZ write mode.

```python
with tarfile.open("archive.tar.xz", mode="w|xz", preset=6) as archive:
    archive.add("payload")
```

### Archive compression defaults and timestamps (3.15.0b3)
The default `compressionlevel` for `gzip` and gzip-compressed `tarfile` output is 6 rather than 9. `tarfile.open(..., mtime=...)` controls the gzip header timestamp for `.tar.gz` output, enabling reproducible archives.

### Decompressors become unusable after fatal errors (3.15.0b3)
After libbz2 reports a decompression error, a `BZ2Decompressor` cannot be reused; callers must create a new decompressor instead of retrying on potentially invalid internal state.

### Zstandard-compressed ZIP imports (3.15.0b3)
`zipimport` can import modules from ZIP entries compressed with Zstandard, extending Zstandard archive support beyond explicit `zipfile` access.

## Streams, binary data, and codecs

### Restored tree-capable `importlib.resources` helpers (Python 3.13)
The functional `importlib.resources` helpers such as `open_binary()`, `read_text()`, and `path()` accept multiple path components to address resource trees, with text encoding and errors now keyword-only. These helpers are no longer scheduled for removal; `contents()` remains deprecated but likewise has no removal plan.

### Unicode arrays use a fixed-width type code (Python 3.13)
`array.array('w')` stores Unicode characters as `Py_UCS4`; the platform-dependent `'u'`/`wchar_t` code now warns at runtime and is scheduled for removal in 3.16.

### I/O cleanup and read-after-write behavior (3.13.0)
`IOBase` finalizers now report `close()` failures through `sys.unraisablehook` even outside development or debug mode. `BufferedRandom.read1()` flushes the underlying write buffer before reading.

### Copyable codec descriptors (3.13.0)
`codecs.CodecInfo` objects can now be shallow-copied, deep-copied, and pickled; codec stream objects still reject copying and pickling with `TypeError`.

### Time-zone-aware property lists (3.13.0)
`plistlib` load and dump APIs accept `aware_datetime` to work with aware datetime values.

### Nonblocking text I/O and structural protocols (Python 3.14)
Text reads from a nonblocking stream may now raise `BlockingIOError` when bytes are not immediately available. `io.Reader` and `io.Writer` provide simpler structural typing protocols than `typing.IO`, `TextIO`, and `BinaryIO`.

### Complete Windows code-page codecs (3.14.0)
On Windows, every system code page is now available through its `cpXXX` codec name rather than only the previously enumerated subset.

### More unclosed-resource warnings (3.14.0)
Garbage-collecting an unclosed `tempfile.NamedTemporaryFile` or deleting an unclosed `gzip.GzipFile` now emits `ResourceWarning`, so both should be closed explicitly or used as context managers.

### Copy-free bytearray extraction (Python 3.15 preview)
`bytearray.take_bytes(n=None)` transfers the first `n` bytes into a `bytes` object and removes them from the mutable buffer without copying; omitting `n` drains the whole buffer.

```python
buffer = bytearray(b"header\npayload")
line = buffer.take_bytes(buffer.find(b"\n") + 1)
```

### Extended binary format codes (Python 3.15 preview)
`array` and `memoryview` support complex-float formats `Zf` and `Zd`, while `array` additionally supports the IEEE-754 half-float code `e`; `array.typecodes` is now a tuple because codes may contain two characters. The old `struct` complex codes `F` and `D` are soft-deprecated in favor of `Zf` and `Zd`, and the corresponding `ctypes` scalar `_type_` values now use `Zf`, `Zd`, and `Zg`.

### Configurable and stricter base encodings (Python 3.15 preview)
The `base64` encoders and decoders gain controls including `padded`, `wrapcol`, `ignorechars`, and `canonical`; canonical decoding rejects nonzero padding bits and other noncanonical spellings. `urlsafe_b64decode()` no longer requires input padding by default, so use `padded=True` to retain strict padding, and accepting `+` or `/` alongside an alternative alphabet is deprecated.

Low-level `binascii` now supplies Base32, Ascii85, Base85, and Z85 conversion functions and matching padding, wrapping, alphabet, ignored-character, and canonical controls.

### Floating-point WAVE files (Python 3.15 preview)
`wave` reads and writes `WAVE_FORMAT_IEEE_FLOAT`, adds explicit `getformat()`/`setformat()` accessors, accepts seven-element parameter tuples containing the format while retaining six-element PCM tuples, and writes the required `fact` chunk for non-PCM output.

## Structured data and parsing

### XML parser flushing and iterator cleanup (Python 3.13)
ElementTree's `XMLParser` and `XMLPullParser` and the SAX Expat parser now expose `flush()`, while low-level Expat parsers expose `GetReparseDeferralEnabled()` and `SetReparseDeferralEnabled()` to control Expat 2.6 reparse deferral. The iterator returned by `ElementTree.iterparse()` now has `close()` for explicit cleanup.

### CSV quoting and space delimiters (3.13.0)
`csv.writer()` always quotes or escapes carriage returns and newlines regardless of the configured line terminator. With a space delimiter and `skipinitialspace=True`, it quotes empty fields or raises if the active quoting mode cannot represent them.

### Structured TOML decode errors (3.14.0)
`tomllib.TOMLDecodeError` exposes `msg`, `doc`, `pos`, `lineno`, and `colno`; constructing it with arbitrary free-form arguments is deprecated.

```python
try:
    tomllib.loads(text)
except tomllib.TOMLDecodeError as error:
    print(error.lineno, error.colno, error.msg)
```

### TOML 1.1 parsing (Python 3.15 preview)
`tomllib` now accepts TOML 1.1 while preserving TOML 1.0 behavior: inline tables may span lines and have trailing commas, basic strings gain `\xHH` and `\e` escapes, and seconds are optional in times and datetimes.

```toml
point = {
  x = 1,
  y = 2,
}
alarm = 14:15
```
