# Data, I/O, and serialization

## Configuration and structured data

### Unnamed configuration sections (`whatsnew-3.13`, `3.15.0b3`)

`ConfigParser(allow_unnamed_section=True)` accepts top-level key/value pairs
before a section heading. In 3.15.0b3, mapping access can create
`UNNAMED_SECTION`; writing multiline values normalizes CR, CRLF, and LF to LF
followed by a tab.

### ConfigParser write validation (`3.14.0`)

`ConfigParser` raises `configparser.InvalidWriteError` instead of writing a key
whose serialized form could not be parsed back accurately.

### Timezone-aware property lists (`3.13.0`)

Pass `aware_datetime=True` to `plistlib` to load and dump timezone-aware
`datetime` values.

### TOML 1.1 (`whatsnew-3.15`)

`tomllib` accepts TOML 1.1 while preserving TOML 1.0 behavior. Inline tables
may span lines and end with trailing commas, basic strings accept `\xHH` and
`\e`, and time values may omit seconds.

### JSON, pickle, and shelf hooks (`whatsnew-3.15`)

`json.load()` and `loads()` accept `array_hook`; combining `array_hook=tuple`
with `object_pairs_hook=frozendict` yields deeply immutable decoded data.
Pickle serializes private methods and nested classes. `shelve` accepts custom
serialization and deserialization functions.

## SQLite and database behavior

### SQLite call-style migration (`whatsnew-3.13`)

All `sqlite3.connect()` and `Connection()` parameters after the database become
keyword-only in 3.15. Conversely, name/count/callable arguments for
`create_function()` and `create_aggregate()`, and callback arguments for
handler setters, become positional-only:

```python
con = sqlite3.connect("app.db", timeout=10)
con.create_function("slug", 1, slug)
con.set_trace_callback(trace)
```

### Named bindings and version inspection (`whatsnew-3.14`)

A sequence supplied for named SQL placeholders raises `ProgrammingError`; pass
a mapping. `sqlite3.version` and `version_info` are removed; inspect the
runtime library with `sqlite_version` and `sqlite_version_info`.

### Cursor and shell behavior (`3.15.0b3`)

`sqlite3.Cursor.arraysize` rejects negative values, and `fetchmany()` honors
the maximum row count. The SQLite shell adds color and completion for keywords,
tables, indexes, triggers, views, columns, functions, and schemas;
`sqlite3.SQLITE_KEYWORDS` exposes the keyword set.

## Streams, descriptors, and binary formats

### Archive stream mode values (`whatsnew-3.13`)

`gzip.GzipFile.mode` reports `'rb'` or `'wb'` instead of `1` or `2`. A readable
stream from `ZipFile.open()` reports `'rb'` instead of `'r'`; update comparisons.

### File-like memory mappings (`3.13.0`)

`mmap.mmap` implements `seekable()`, and `seek()` returns the new absolute
position rather than `None`.

### CSV record boundaries (`3.13.0`)

`csv.writer()` always quotes or escapes CR and LF regardless of the configured
`lineterminator`, preventing ambiguous embedded record boundaries.

### Nonblocking text and digest I/O (`whatsnew-3.14`, `3.14.0`)

Text reads from nonblocking streams may raise `BlockingIOError` when bytes are
not available. `hashlib.file_digest()` likewise raises `BlockingIOError`
instead of incorporating spurious NUL bytes. `fcntl.fcntl()` accepts any
bytes-like object; `fcntl.ioctl()` retries `EINTR` and releases the GIL for
large bytes-like arguments.

### Complex binary formats (`whatsnew-3.14`)

`struct` adds `F` and `D` for C float-complex and double-complex values.
Matching ctypes complex scalar types exist when compiler and libffi support is
available. See the language reference for the later two-letter migration.

### Copy-free bytearray extraction (`whatsnew-3.15`)

`bytearray.take_bytes(n=None)` removes up to `n` leading bytes and returns them
as `bytes` without copying, replacing `bytes(buffer[:n]); del buffer[:n]`.

### Floating-point WAVE (`whatsnew-3.15`)

`wave` supports `WAVE_FORMAT_IEEE_FLOAT`. Readers and writers add `getformat()`,
writers add `setformat()`, and `setparams()` accepts a seven-item tuple that
includes format while retaining six-item PCM tuples.

### Checksum composition (`3.15.0b3`)

`zlib.adler32_combine()` and `zlib.crc32_combine()` combine independently
calculated Adler-32 and CRC-32 checksums.

### Failed BZ2 decompressors (`3.15.0b3`)

Once libbz2 reports a decompression error, that `BZ2Decompressor` is terminal;
do not call it again through invalid internal state.

## Archives and reproducibility

### Memory-bounded tar reading (`3.13.0`)

Tarfile stream mode reads an archive without caching metadata for all members,
reducing memory consumption for large archives.

### Hardened tar extraction (`whatsnew-3.14`)

Extraction filters normalize symlink targets and are reapplied when links fall
back to copied members and during directory fixups. A rejected member is never
extracted merely because `errorlevel` is zero. Link substitution failures can
raise `LinkFallbackError`.

### Reproducible ZIP timestamps (`whatsnew-3.14`)

`ZipFile.writestr()` honors `SOURCE_DATE_EPOCH`. `ZipInfo._for_archive()`
resolves the defaults that `writestr()` will apply to a metadata object.

### Serialization defaults (`3.14.0`)

`gzip.compress()` defaults `mtime` to zero and writes OS byte 255, making output
reproducible. Pickle protocol 5 is the default; select an older protocol
explicitly for older readers.

### Explicit compressed and temporary-file closure (`3.14.0`)

An unclosed `gzip.GzipFile` or `tempfile.NamedTemporaryFile` emits
`ResourceWarning` when collected. Use a context manager when the current scope
owns the object.

### Compression defaults and timestamps (`3.15.0b3`)

The default gzip level used by `gzip` and gzip-compressed tar archives is 6
rather than 9. `tarfile.open()` accepts `mtime=` for gzip headers, and
reproducible ZIP writes use UTC rather than local time.

### Zstandard ZIP imports (`3.15.0b3`)

`zipimport` imports modules from ZIP members compressed with Zstandard.

## XML and HTML

### Expat control and cleanup (`whatsnew-3.13`)

For Expat 2.6 reparse deferral, ElementTree and SAX parsers have `flush()`;
raw expat parsers have `GetReparseDeferralEnabled()` and
`SetReparseDeferralEnabled()`. The iterator from `ElementTree.iterparse()` has
`close()` for explicit cleanup.

### XML validation and defenses (`whatsnew-3.15`)

`xml.is_valid_name()` and `xml.is_valid_text()` validate XML names and document
text. Expat parser objects expose controls for allocation-amplification and
billion-laughs protections.

### HTML5 parsing and serialization (`3.15.0b3`)

`HTMLParser` follows HTML5 rules for tag whitespace, repeated `=`, comments,
CDATA, raw-text elements, and abruptly terminated constructs. ElementTree's
HTML serializer leaves raw-text content unescaped, omits the `plaintext`
closing tag, and accepts empty attributes represented by `None`.

## Encodings

### Configurable and strict base encodings (`whatsnew-3.15`)

Base encoders and decoders add combinations of `padded`, `wrapcol`,
`ignorechars`, and `canonical`. Canonical decoding rejects nonzero padding bits
and other noncanonical forms. `urlsafe_b64decode()` does not require padding
unless `padded=True`. `binascii` adds Base32 and Base85-family support plus
alphabet and formatting controls.
