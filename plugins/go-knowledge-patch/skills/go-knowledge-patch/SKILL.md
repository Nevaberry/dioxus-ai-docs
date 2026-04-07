---
name: go-knowledge-patch
description: "Go changes since training cutoff (latest: 1.26.0) — new(expr) builtin, errors.AsType, self-referential generics, reflect iterators, go fix modernizer. Load before working with Go."
license: MIT
version: "1.26.0"
metadata:
  author: Nevaberry
---

# Go 1.23+ Knowledge Patch

Claude's baseline knowledge covers Go through 1.22. This skill provides features from 1.23 (2024) onwards.

## Quick Reference

### Language Changes (1.26)

| Feature | Syntax |
|---------|--------|
| Pointer from expression | `new(42)`, `new(yearsSince(born))` |
| Self-referential generics | `type Adder[A Adder[A]] interface { Add(A) A }` |

See `references/language-changes.md` for details and migration patterns.

### Standard Library (1.26)

| Package | Addition | Purpose |
|---------|----------|---------|
| `errors` | `AsType[T](err)` | Generic type-safe error matching |
| `bytes` | `Buffer.Peek(n)` | Read next n bytes without advancing |
| `log/slog` | `NewMultiHandler(h...)` | Fan out to multiple log handlers |
| `reflect` | `Type.Fields()`, `.Methods()`, `.Ins()`, `.Outs()` | Iterator methods on types |
| `reflect` | `Value.Fields()`, `.Methods()` | Iterator methods yielding type+value |
| `testing` | `T.ArtifactDir()` | Directory for test output artifacts |

See `references/stdlib-updates.md` for full API details and examples.

### Tooling (1.26)

| Command | Purpose |
|---------|---------|
| `go fix ./...` | Rewritten modernizer — updates code to current idioms |
| `//go:fix inline` | Directive for custom API migration rules |

See `references/tooling.md` for modernizer details.

## Reference Files

| File | Contents |
|------|----------|
| `language-changes.md` | `new(expr)`, self-referential generic constraints |
| `stdlib-updates.md` | errors.AsType, bytes.Buffer.Peek, slog.NewMultiHandler, reflect iterators, testing artifacts |
| `tooling.md` | `go fix` modernizers, `//go:fix inline` directive |

## Critical Knowledge

### `new(expr)` Replaces ptr() Helpers (1.26)

The most common impact — eliminates the ubiquitous `ptr[T any](v T) *T` helper:

```go
// Before: needed a helper or temp variable
func ptr[T any](v T) *T { return &v }
p := ptr(42)

// After: built-in
p := new(42)
p := new(yearsSince(born)) // useful for optional struct fields
```

### `errors.AsType` — No More Temp Variables (1.26)

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

### Reflect Iterators (1.26)

Range over struct fields, method sets, and function signatures:

```go
for sf, v := range reflect.ValueOf(s).Fields() {
	fmt.Println(sf.Name, v)
}
```
