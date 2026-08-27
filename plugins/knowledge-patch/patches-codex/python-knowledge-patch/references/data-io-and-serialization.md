# Data, I/O, and serialization

## Configuration and structured data

### Unnamed configuration sections

`ConfigParser(allow_unnamed_section=True)` accepts top-level key-value pairs
before any section heading. In Python 3.15.0b3, mapping access can create
`UNNAMED_SECTION`; writing multiline values normalizes CR, CRLF, and LF input
to LF followed by a tab.

### ConfigParser write validation

Python 3.14 rejects keys whose serialized form could not be parsed back
accurately. `ConfigParser.write()` raises `configparser.InvalidWriteError`
instead of emitting a corrupt configuration.

### Property-list datetimes

`plistlib` accepts `aware_datetime` to load and dump timezone-aware `datetime`
values.

### CSV record boundaries

`csv.writer()` always quotes or escapes carriage returns and newlines,
regardless of its configured `lineterminator`, so embedded line breaks cannot
be emitted ambiguously.

### TOML 1.1

Python 3.15 `tomllib` accepts TOML 1.1 while retaining TOML 1.0 behavior.
Inline tables may span lines and have trailing commas, basic strings support
`\xHH` and `\e`, and time values may omit seconds.

### Immutable JSON and custom shelves

`json.load()` and `loads()` accept `array_hook`; using `array_hook=tuple` with
`object_pairs_hook=frozendict` produces deeply immutable decoded data. Pickle
can serialize private methods and nested classes, and `shelve` accepts custom
serialization and deserialization functions.

### Floating-point WAVE data

Python 3.15 supports `WAVE_FORMAT_IEEE_FLOAT`. Readers and writers expose
`getformat()`, writers expose `setformat()`, and `setparams()` accepts a
seven-item tuple containing the format while retaining six-item PCM tuples.

## SQLite

### Call-style migration

All `sqlite3.connect()` and `Connection()` parameters after the database become
keyword-only in Python 3.15. Conversely, name/count/callable arguments for
`create_function()` and `create_aggregate()`, plus callback arguments to handler
setters, become positional-only.

```python
con = sqlite3.connect("app.db", timeout=10)
con.create_function("slug", 1, slug)
con.set_trace_callback(trace)
```

### Binding and version inspection

Python 3.14 raises `ProgrammingError` when a sequence is supplied for named SQL
placeholders; pass a mapping. `sqlite3.version` and `version_info` are removed;
inspect the runtime library through `sqlite_version` and
`sqlite_version_info`.

### Cursor and shell behavior

In Python 3.15.0b3, `sqlite3.Cursor.arraysize` rejects negative values and
`fetchmany()` honors the maximum row count. The SQLite shell adds color and
completion for keywords, tables, indexes, triggers, views, columns, functions,
and schemas. `sqlite3.SQLITE_KEYWORDS` exposes the keyword set.

## Streams and binary data

### Nonblocking text input

Text reads from nonblocking streams may raise `BlockingIOError` when bytes are
not immediately available. `io.Reader` and `io.Writer` are simple structural
interfaces for code that only needs read or write behavior.

### Archive stream mode values

`gzip.GzipFile.mode` reports `'rb'` or `'wb'` rather than `1` or `2`, and a
readable stream from `ZipFile.open()` reports `'rb'` rather than `'r'`. Compare
against the new string values.

### Memory-bounded tar reading

`tarfile` has a stream mode that reads archives without caching metadata for
their members, reducing memory use for large archives.

### Complex binary formats

Python 3.14 `struct` adds `F` and `D` format characters for C float-complex and
double-complex values, with matching `ctypes` scalar types when the compiler and
libffi support them. Python 3.15 adds half-float `e` and complex `Zf` and `Zd`
array type codes, changes `array.typecodes` from `str` to `tuple`, and supports
`Zf` and `Zd` in `memoryview`. `ctypes` complex `_type_` codes become `Zf`,
`Zd`, and `Zg`; the one-letter `struct` codes are soft-deprecated for the
two-letter forms.

### Copy-free bytearray extraction

`bytearray.take_bytes(n=None)` removes up to `n` leading bytes and returns them
as `bytes` without copying, replacing `bytes(buffer[:n]); del buffer[:n]`.

### Base encoding controls

Python 3.15 base encoders and decoders add combinations of `padded`, `wrapcol`,
`ignorechars`, and `canonical`. Canonical decoding rejects nonzero padding bits
and other noncanonical forms. `urlsafe_b64decode()` does not require padding
unless `padded=True`. `binascii` adds Base32 and Base85-family support plus
alphabet and formatting controls.

## Compression, archives, and serialization

### Reproducible ZIP metadata

`ZipFile.writestr()` honors `SOURCE_DATE_EPOCH`, and `ZipInfo._for_archive()`
resolves the defaults that `writestr()` will apply to a metadata object.

### Serialization defaults (`3.14.0`)

`gzip.compress()` defaults `mtime` to `0` and writes an OS byte of 255, making
output reproducible by default. Pickle protocol 5 is now the default; pass an
older protocol explicitly when older readers need it.

### Explicit temporary and compressed-file closure

An unclosed `gzip.GzipFile` or `tempfile.NamedTemporaryFile` emits
`ResourceWarning` when garbage-collected. Use a context manager when the
current scope owns the resource.

### Archive compression defaults and timestamps

In Python 3.15.0b3, gzip and gzip-compressed tar archives default to compression
level 6 rather than 9. `tarfile.open()` accepts `mtime=` for gzip headers, and
reproducible ZIP writes use UTC instead of local time.

### Checksum composition

`zlib.adler32_combine()` and `zlib.crc32_combine()` combine Adler-32 and CRC-32
checksums in Python 3.15.0b3.

### Failed BZ2 decompressors

After libbz2 reports a decompression error, that `BZ2Decompressor` is terminal
and cannot be called again through invalid state.

### Zstandard ZIP imports

`zipimport` can import entries compressed with Zstandard in Python 3.15.0b3.
