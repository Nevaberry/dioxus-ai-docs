# Filesystems, Data, and Encoding

## Confined and symlink-aware filesystems

### Traversal-resistant filesystem roots (`1.24-guide`)

`os.OpenRoot` opens a directory as an `*os.Root`. Its operations resolve
relative names while rejecting `..` or symlink traversal that would escape the
root. Contained `..` components and symlinks remain valid, making this stronger
than lexical sanitization and immune to the check/use race of pre-validating a
path.

```go
root, err := os.OpenRoot(baseDirectory)
if err != nil {
	return err
}
defer root.Close()

file, err := root.Open(untrustedFilename)
```

The initial API provides `Create`, `Lstat`, `Mkdir`, `Open`, `OpenFile`,
`OpenRoot`, `Remove`, and `Stat`, but not rename or symlink creation.
`os.OpenInRoot(baseDirectory, untrustedFilename)` is the safe one-shot form.

### Platform limits of `os.Root` (`1.24-guide`)

On Unix, a root follows its directory through rename or deletion and blocks
symlink escape, but does not stop traversal through mount points. Windows roots
reject reserved device names and retain a handle that prevents renaming or
deleting the root. `GOOS=js` uses name checks vulnerable to symlink TOCTOU
races; WASI protection depends on its implementation, and Plan 9 is lexical
because it has no symlinks.

### Symlink-aware filesystem operations (`1.25.0`)

`io/fs.ReadLinkFS` standardizes reading links. `os.DirFS`, `os.Root.FS`, and
`fstest.MapFS` implement it. `tar.Writer.AddFS` and `os.CopyFS` preserve links
from supporting filesystems. `fstest.TestFS` validates the interface and no
longer follows links during its walk.

## File metadata, handles, and filesystem tests

### Overriding tar owner names (`1.23.0`)

When input to `archive/tar.FileInfoHeader` implements `FileInfoNames`, its
methods supply `Uname` and `Gname` instead of platform-dependent owner lookup.

### Windows reparse-point behavior (`1.23.0`)

On Windows, `Stat` marks AF_UNIX reparse points as `ModeSocket`; mount points
are no longer `ModeSymlink`, and other non-symlink reparse points are
`ModeIrregular`. `EvalSymlinks` no longer follows mount points. It and
`Readlink` stop normalizing volumes to drive letters. The compatibility
settings `winsymlink` and `winreadlinkvolume` both default to 1 for 1.23.

### Structured `fstest` errors (`1.23.0`)

`testing/fstest.TestFS` returns an error with `Unwrap() []error`, allowing
individual failures to be found with `errors.Is` and `errors.As`.

### Windows asynchronous file handles (`1.25.0`)

`os.NewFile` integrates overlapped handles with the runtime completion port.
Reads and writes no longer block an OS thread, and deadlines work unless the
handle already belongs to another completion port.

### Native process and Windows file controls (`1.26.0`)

`os.Process.WithHandle` provides controlled access to a pidfd on Linux 5.4+ or
a Handle on Windows. On Windows, `os.OpenFile` accepts combinations of native
flags such as `FILE_FLAG_OVERLAPPED` and `FILE_FLAG_SEQUENTIAL_SCAN`.

## JSON, hashes, images, compression, and identifiers

### Experimental JSON v2 (`1.25.0`)

Building with `GOEXPERIMENT=jsonv2` exposes `encoding/json/v2` and
`encoding/json/jsontext`, and switches `encoding/json` to the new backend while
preserving marshal and unmarshal behavior apart from possible error-text
changes.

### Cloneable and extendable hashes (`1.25.0`)

`hash.XOF` represents arbitrary-length-output hashes such as SHAKE, while
`hash.Cloner` copies hash state. Every standard-library `hash.Hash`
implementation is cloneable, including SHA-3 and `maphash.Hash` through their
new clone methods.

### JPEG output changes (`1.26.0`)

The replacement JPEG encoder and decoder are more accurate but can produce
different bytes. Update golden tests and caches that compare encoded bytes.

### JSON v2 becomes the standard backend (`1.27.0`)

`encoding/json/v2` and `encoding/json/jsontext` are available. V2 rejects
invalid UTF-8 strings and duplicate object names by default. The existing
`encoding/json` API uses the v2 backend while preserving marshal and unmarshal
behavior apart from possible error-text changes.
`GOEXPERIMENT=nojsonv2` temporarily restores the old implementation.

### Standard UUID support (`1.27.0`)

The `uuid` package generates and parses UUIDs.

### Changed DEFLATE-family output (`1.27.0`)

The new compression implementation can produce bytes different from 1.26 for
DEFLATE and packages built on it. Golden tests, caches, and protocols should
compare decoded content or otherwise tolerate the change.
