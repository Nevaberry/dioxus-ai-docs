# I/O, formatting, compression, and networking

## Concrete reader and writer interfaces

Zig 0.15.1 deprecates generic `std.io` streams in favor of non-generic
`std.Io.Reader` and `std.Io.Writer`. Caller-provided buffers live in the interface.
An old writer can temporarily bridge with `old_writer.adaptToNewApi(&.{})`.

```zig
var buffer: [1024]u8 = undefined;
var file_writer = std.fs.File.stdout().writer(&buffer);
const stdout: *std.Io.Writer = &file_writer.interface;
try stdout.print("{s}\n", .{"hello"});
try stdout.flush();
```

The reader provides peeking, delimiter-taking, discarding, and file-transfer
operations. The writer provides splatting and file transfer.

## File I/O

In 0.15.1, file I/O moved to concrete `File.Reader` and `File.Writer` interfaces.
They track size, position, seek failures, and positional-versus-streaming access;
pass them rather than bare handles for seeking or transfer.

- `fs.Dir.copyFile` no longer reports `error.OutOfMemory`.
- `fs.Dir.atomicFile` requires a `write_buffer`, and `fs.AtomicFile` exposes a
  `Writer`.
- The old `File.writeFileAll*` APIs were removed.
- `posix.sendfile` was replaced by `File.Reader.sendFile`.
- No-buffer `File.reader` and `File.writer` are now `deprecatedReader` and
  `deprecatedWriter`.

## Formatting

### Explicit custom formatting

Since 0.15.1, `{f}` invokes a value's `format` method, `{any}` bypasses it, and
plain `{}` is ambiguous for values that define custom formatting. A `format`
method receives only the value and `*std.Io.Writer`, and returns
`std.Io.Writer.Error!void`. Use `std.fmt.Alt` or a wrapper value when context needs
an alternate representation.

```zig
const Value = struct {
    number: u32,
    pub fn format(value: @This(), writer: *std.Io.Writer) std.Io.Writer.Error!void {
        try writer.print("{d}", .{value.number});
    }
};
```

### Specifiers and alignment

New 0.15.1 specifiers include `{t}` for an enum tag or error name and `{b64}` for
standard Base64. Integer specifiers can call a custom `formatNumber`. Width and
alignment now count bytes/ASCII rather than Unicode code points.

### Removed helpers and renamed wrappers

The 0.15.1 replacements are:

| Old API | Current API |
|---|---|
| `CountingWriter` | `Writer.Discarding`, `Writer.Allocating`, or `Writer.fixed` |
| `BufferedWriter` | A buffer passed directly to a writer |
| `std.fmt.Formatter` | `std.fmt.Alt` |
| `std.fmt.format` | `Writer.print` |
| Old escape helpers | `std.ascii.hexEscape` or `std.zig.fmtString` |
| Slice hex wrappers | `{x}` or `{X}` |
| Size wrappers | `{B}` or `{Bi}` |
| Duration wrappers | `{D}` |

`SeekableStream`, `BitReader`, `BitWriter`, `LimitedReader`, and `BufferedReader`
were removed.

## Flate

Flate was reorganized in 0.15.1. Initialize
`std.compress.flate.Decompress` with a reader, format (`.zlib` or `.gzip`), and
window buffer, then consume its `reader`. An empty buffer is suitable when
immediately piping with `streamRemaining`. Standard-library flate compression was
removed.

```zig
var window: [std.compress.flate.max_window_len]u8 = undefined;
var decompress: std.compress.flate.Decompress = .init(reader, .zlib, &window);
const decompressed: *std.Io.Reader = &decompress.reader;
```

## HTTP and TLS

In 0.15.1, `std.http.Server` and `std.crypto.tls.Client` accept `std.Io.Reader`
and `std.Io.Writer` rather than depending directly on `std.net`.

The HTTP client sequence is `request`, `sendBodiless`, `receiveHead`, then
`response.reader(buffer)`. Inspect or copy response headers before creating the
body reader, because that operation invalidates strings in `response.head`.
