# Standard Library Updates

## `errors.AsType` — Generic Type-Safe Error Matching (1.26)

Replaces the two-step `errors.As` pattern with a single generic call:

```go
// Before
var pathErr *fs.PathError
if errors.As(err, &pathErr) {
	use(pathErr)
}

// After — no separate variable needed
if pe, ok := errors.AsType[*fs.PathError](err); ok {
	use(pe)
}
```

Returns `(T, bool)` — the matched error and whether the match succeeded.

## `bytes.Buffer.Peek` (1.26)

`Peek(n)` returns the next n bytes from the buffer without advancing the read position.

```go
var buf bytes.Buffer
buf.WriteString("hello world")
preview := buf.Peek(5) // []byte("hello"), buffer unchanged
```

## `log/slog.NewMultiHandler` (1.26)

Creates a handler that fans out log records to multiple handlers. `Enabled` returns true if any sub-handler is enabled for the given level.

```go
h := slog.NewMultiHandler(jsonHandler, textHandler)
logger := slog.New(h)
```

## `reflect` Iterator Methods (1.26)

New iterator methods on `Type` and `Value` that work with range-over-func:

### Type iterators

- `Type.Fields()` — iterates struct fields
- `Type.Methods()` — iterates method set
- `Type.Ins()` — iterates function input parameters
- `Type.Outs()` — iterates function output parameters

### Value iterators

`Value.Fields()` and `Value.Methods()` yield both type info and the corresponding value:

```go
for sf, v := range reflect.ValueOf(s).Fields() {
	fmt.Println(sf.Name, v)
}
```

## `testing.T.ArtifactDir` (1.26)

Returns a directory where tests can write output artifacts (screenshots, debug dumps, etc.). Use the `-artifacts` flag with `go test` to persist them; otherwise they are cleaned up after the test completes.

```go
func TestFoo(t *testing.T) {
	dir := t.ArtifactDir()
	os.WriteFile(filepath.Join(dir, "debug.png"), data, 0644)
}
```

Run with persistence:

```bash
go test -artifacts ./testdata/artifacts ./...
```
