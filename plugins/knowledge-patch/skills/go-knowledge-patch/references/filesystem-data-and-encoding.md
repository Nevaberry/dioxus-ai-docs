# Filesystems, Data, and Encoding

Batch coverage: `1.23.0`, `1.24-guide`, `1.25.0`, `1.26.0`.

## Contents

- [Traversal-resistant roots](#traversal-resistant-roots)
- [Symbolic links and filesystem testing](#symbolic-links-and-filesystem-testing)
- [Windows filesystem behavior](#windows-filesystem-behavior)
- [Tar ownership](#tar-ownership)
- [JSON v2 experiment](#json-v2-experiment)
- [JPEG output](#jpeg-output)

## Traversal-resistant roots

### `os.Root`

`os.OpenRoot` opens a directory as an `*os.Root`. Root operations resolve relative names while rejecting `..` or symbolic-link traversal that would escape the directory. Contained `..` components and symlinks remain valid. This is stronger than lexical sanitization and avoids the check/use race created by validating a path before opening it.

```go
root, err := os.OpenRoot(baseDirectory)
if err != nil {
	return err
}
defer root.Close()

file, err := root.Open(untrustedFilename)
```

The original API provides `Create`, `Lstat`, `Mkdir`, `Open`, `OpenFile`, `OpenRoot`, `Remove`, and `Stat` methods on `Root`, but no rename or symlink-creation methods. Use `os.OpenInRoot(baseDirectory, untrustedFilename)` for a one-shot open instead of `os.Open(filepath.Join(baseDirectory, untrustedFilename))`.

### Platform limits

- On Unix, a root follows its directory across rename or deletion and prevents symlink escape. It does not prevent traversal through mount points such as bind mounts.
- On Windows, roots reject reserved device names and hold a handle that prevents renaming or deleting the root.
- On `GOOS=js`, roots use name-based checks and remain vulnerable to symlink TOCTOU races.
- On WASI, protection is only as strong as the implementation.
- On Plan 9, roots use lexical checks because the platform has no symlinks.

## Symbolic links and filesystem testing

### Standard link interface and copying

`io/fs.ReadLinkFS` standardizes symbolic-link reads. `os.DirFS`, `os.Root.FS`, and `fstest.MapFS` implement it. `tar.Writer.AddFS` and `os.CopyFS` preserve links when the source filesystem supports the interface.

`fstest.TestFS` validates `ReadLinkFS` and no longer follows symbolic links during its walk.

### Structured `fstest` errors

`testing/fstest.TestFS` returns an error with `Unwrap() []error`. Use `errors.Is` and `errors.As` to inspect individual filesystem failures.

## Windows filesystem behavior

### Reparse points

On Windows, `Stat` reports AF_UNIX reparse points as `ModeSocket`. It no longer reports mount points as `ModeSymlink`; other non-symlink reparse points are `ModeIrregular`.

`EvalSymlinks` no longer follows mount points. Both `EvalSymlinks` and `Readlink` stop normalizing volumes to drive letters. The `winsymlink` and `winreadlinkvolume` compatibility settings both default to 1 for Go 1.23.

### Asynchronous handles

`os.NewFile` integrates overlapped handles with the runtime completion port. Reads and writes do not block an OS thread, and deadlines are available unless the handle already belongs to another completion port.

`os.OpenFile` accepts combinations of native Windows flags including `FILE_FLAG_OVERLAPPED` and `FILE_FLAG_SEQUENTIAL_SCAN`.

## Tar ownership

When input to `archive/tar.FileInfoHeader` implements `FileInfoNames`, its methods populate `Uname` and `Gname` instead of using platform-dependent owner lookup.

## JSON v2 experiment

Building with `GOEXPERIMENT=jsonv2` exposes `encoding/json/v2` and the lower-level `encoding/json/jsontext` package:

```sh
GOEXPERIMENT=jsonv2 go test ./...
```

The experiment also switches `encoding/json` to the new implementation while preserving marshal and unmarshal behavior, apart from possible changes to error text.

## JPEG output

The replacement JPEG encoder and decoder are more accurate but may produce different bytes for the same image. Update golden tests and caches that compare encoded JPEG bytes exactly.
