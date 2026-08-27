# Filesystems, Data, and Encoding

## Confined path resolution

### Rooted filesystem operations (1.24-guide)

`os.OpenRoot` opens a trusted directory as `*os.Root`. Operations accept
relative names, permit contained `..` components and symlinks, and reject
traversal escaping the root. This avoids the symlink check/use race in lexical
validation followed by a separate open.

```go
root, err := os.OpenRoot(baseDirectory)
if err != nil {
	return err
}
defer root.Close()

file, err := root.Open(untrustedFilename)
```

Available root methods include `Create`, `Lstat`, `Mkdir`, `Open`, `OpenFile`,
`OpenRoot`, `Remove`, and `Stat`; rename and symlink creation are not included.
Use `os.OpenInRoot(baseDirectory, name)` for one-shot access rather than
`os.Open(filepath.Join(baseDirectory, name))`.

Platform limits matter:

- Unix roots follow the directory across rename or deletion and prevent
  symlink escape, but do not block traversal through bind or other mounts.
- Windows roots reject reserved device names and hold a handle that prevents
  root rename or deletion.
- `GOOS=js` uses name checks and remains vulnerable to symlink TOCTOU races.
- WASI protection depends on its implementation; Plan 9 can provide only
  lexical checks because it has no symlinks.

## Links, archives, and filesystem tests

### Tar ownership and Windows reparse points (1.23.0)

If input to `archive/tar.FileInfoHeader` implements `FileInfoNames`, its methods
supply `Uname` and `Gname` rather than platform owner lookup.

On Windows, `Stat` reports AF_UNIX reparse points as `ModeSocket`, mount points
are not `ModeSymlink`, and other non-symlink reparse points are `ModeIrregular`.
`EvalSymlinks` does not follow mount points. It and `Readlink` no longer
normalize volume names to drive letters. The `winsymlink` and
`winreadlinkvolume` compatibility settings default to 1.

### Structured `fstest` failures (1.23.0)

`testing/fstest.TestFS` returns an error with `Unwrap() []error`; locate
individual failures with `errors.Is` and `errors.As`.

### Symlink-aware filesystem interfaces (1.25.0)

`io/fs.ReadLinkFS` standardizes symlink reading. `os.DirFS`, `os.Root.FS`, and
`fstest.MapFS` implement it. `tar.Writer.AddFS` and `os.CopyFS` preserve links
from supporting filesystems. `fstest.TestFS` validates `ReadLinkFS` and does
not follow symlinks while walking.

## Windows and process handles

### Asynchronous files (1.25.0)

`os.NewFile` integrates Windows overlapped handles with the runtime completion
port. Reads and writes no longer block an OS thread, and deadlines work unless
the handle already belongs to a different completion port.

### Native flags and controlled process access (1.26.0)

`os.Process.WithHandle` provides controlled access to a pidfd on Linux 5.4+
or a Windows Handle. On Windows, `os.OpenFile` accepts compatible native flag
combinations such as `FILE_FLAG_OVERLAPPED` and `FILE_FLAG_SEQUENTIAL_SCAN`.

## JSON, images, compression, and hashes

### JSON v2 rollout (1.25.0, 1.27.0)

The former `GOEXPERIMENT=jsonv2` gate exposed `encoding/json/v2` and the
lower-level `encoding/json/jsontext`. Those packages are now available and v2
rejects invalid UTF-8 strings and duplicate object names by default.

The existing `encoding/json` API now uses the v2 backend while preserving
marshal and unmarshal behavior apart from possible error-text changes.
`GOEXPERIMENT=nojsonv2` temporarily restores the old implementation.

### Cloneable and extendable hashes (1.25.0)

`hash.XOF` represents arbitrary-length-output hashes such as SHAKE, while
`hash.Cloner` copies hash state. Standard-library `hash.Hash` implementations
are cloneable, including SHA-3 implementations and `maphash.Hash`.

### JPEG and DEFLATE output changes (1.26.0, 1.27.0)

The replacement JPEG encoder and decoder are more accurate but can change
encoded bytes. A new DEFLATE-family implementation can likewise produce bytes
different from earlier releases, including through packages built on it.
Golden tests, caches, and protocols should compare decoded content or otherwise
tolerate non-canonical encodings.
