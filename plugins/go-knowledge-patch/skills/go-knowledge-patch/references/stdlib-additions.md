# Go Standard Library Additions (1.26)

## `errors.AsType` — Generic Type-Safe Error Matching

```go
// Old: requires a variable declaration
var pathErr *fs.PathError
if errors.As(err, &pathErr) { /* use pathErr */
}

// New: type-safe, no pre-declaration needed
if val, ok := errors.AsType[*fs.PathError](err); ok { /* use val */
}
```

## `bytes.Buffer.Peek`

`Peek(n)` returns the next n bytes without advancing the buffer.

## `log/slog.NewMultiHandler`

Fan-out handler that dispatches to multiple handlers:

```go
h := slog.NewMultiHandler(jsonHandler, textHandler)
logger := slog.New(h)
```

## `reflect` Iterator Methods

`Type.Fields()`, `Type.Methods()`, `Type.Ins()`, `Type.Outs()` and `Value.Fields()`, `Value.Methods()` return iterators:

```go
for sf, v := range reflect.ValueOf(s).Fields() {
    fmt.Println(sf.Name, v)
}
```

## `testing.T.ArtifactDir`

Returns a directory for writing test output files. Use `-artifacts` flag with `go test` to persist them:

```go
func TestScreenshot(t *testing.T) {
    dir := t.ArtifactDir() // writes "=== ARTIFACTS TestScreenshot /path/..."
    saveScreenshot(filepath.Join(dir, "page.png"))
}
```

## `os/signal.NotifyContext` Cancel Cause

`NotifyContext` now sets a cancel cause indicating which signal was received (works with `context.Cause`).
