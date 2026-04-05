---
name: go-knowledge-patch
description: "Go changes since training cutoff (latest: 1.26) — new() with values, self-referential generics, errors.AsType, reflect iterators, go fix modernizers. Load before working with Go."
version: "1.26.0"
license: MIT
metadata:
  author: Nevaberry
---

# Go Knowledge Patch

Covers Go 1.26 (2026-02-10). Claude Opus 4.6 knows Go through 1.22. It is **unaware** of any features below.

## Index

| Topic | Reference | Key features |
|---|---|---|
| Language features | [references/language-features.md](references/language-features.md) | `new(value)`, self-referential generic constraints |
| Standard library | [references/stdlib-additions.md](references/stdlib-additions.md) | `errors.AsType`, `slog.NewMultiHandler`, `reflect` iterators, `testing.T.ArtifactDir`, `bytes.Buffer.Peek` |
| Tooling | [references/tooling.md](references/tooling.md) | `go fix` modernizers, `//go:fix inline` directive |

---

## Quick Reference

### Language Changes (1.26)

| Feature | Description |
|---|---|
| `new(expr)` | `new` accepts initial value: `new(30)` returns `*int` pointing to 30 |
| Self-referential generics | `type Adder[A Adder[A]] interface { Add(A) A }` |

### New Standard Library APIs (1.26)

| API | Description |
|---|---|
| `errors.AsType[T](err)` | Generic type-safe `errors.As`, returns `(T, bool)` |
| `bytes.Buffer.Peek(n)` | Return next n bytes without advancing |
| `slog.NewMultiHandler(h...)` | Fan-out to multiple log handlers |
| `reflect.Value.Fields()` | Iterator over struct fields (also `Methods`, `Ins`, `Outs`) |
| `testing.T.ArtifactDir()` | Directory for test output files (`-artifacts` flag) |
| `os/signal.NotifyContext` | Now sets cancel cause with signal info |

---

## `new()` with Initial Value — 1.26

`new` can now take an expression operand, returning a pointer to a variable initialized with that value. Especially useful for optional pointer fields:

```go
type Person struct {
	Name string `json:"name"`
	Age  *int   `json:"age,omitempty"`
}

p := Person{Name: "Alice", Age: new(30)} // *int pointing to 30
```

---

## `errors.AsType` — Generic Type-Safe Error Matching — 1.26

```go
// Old: requires a variable declaration
var pathErr *fs.PathError
if errors.As(err, &pathErr) { /* use pathErr */
}

// New: type-safe, no pre-declaration needed
if val, ok := errors.AsType[*fs.PathError](err); ok { /* use val */
}
```

---

## Self-Referential Generic Constraints — 1.26

Generic types may now refer to themselves in their own type parameter list:

```go
type Adder[A Adder[A]] interface {
    Add(A) A
}

func Sum[A Adder[A]](x, y A) A { return x.Add(y) }
```
