# Language and Core Library

## Iterators and templates

### Function-range protocol and adapters (1.23-guide)

Go permits `for range` over `func(func() bool)`, `func(func(V) bool)`, and
`func(func(K, V) bool)`. The iterator calls `yield` for each element and must
stop when it returns false; an early loop exit makes the compiler-provided
`yield` return false. `iter.Seq[V]` and `iter.Seq2[K, V]` name the one- and
two-value forms; there is no `Seq0`.

`iter.Pull` converts `iter.Seq[V]` to `next func() (V, bool)` and `stop`.
Always call `stop` when consumption might finish early; `defer stop()` is the
safest default for lockstep or partial consumption.

Iterator-producing and consuming helpers include:

- `slices.All`, `Values`, `Collect`, `AppendSeq`, `Backward`, `Sorted`,
  `SortedFunc`, `SortedStableFunc`, and `Chunk`.
- `maps.All`, `Keys`, `Values`, `Collect`, and `Insert`.

For example, `slices.Sorted(maps.Keys(m))` collects sorted map keys. The module
or source file must select language version 1.23 or later. Use
`go get go@1.23`, `go mod edit -go=1.23`, or isolate syntax behind
`//go:build go1.23`.

### Template control flow and ranges (1.23.0, 1.24.0)

`text/template` accepts `else with`, avoiding nested fallback blocks:

```gotemplate
{{with .Primary}}
  {{.}}
{{else with .Fallback}}
  {{.}}
{{else}}
  unavailable
{{end}}
```

Templates can also range over iterator functions and integer values.

## Language syntax and inference

### Initialized pointers and recursive constraints (1.26.0)

`new(expression)` allocates a variable initialized from the expression and
returns its pointer, which removes temporary variables for optional fields:

```go
person := Person{Age: new(yearsSince(born))}
```

A generic type may refer to itself in its type-parameter list, enabling
F-bounded constraints:

```go
type Adder[A Adder[A]] interface {
	Add(A) A
}
```

### Generic methods and broader inference (1.27.0)

A method on a non-parameterized receiver may declare its own type parameters:

```go
type Store struct{}

func (Store) Identity[T any](value T) T { return value }
```

Parameterized receiver types still cannot add method type parameters, and a
generic method cannot implement an interface method.

Struct literal keys may use any field selector valid for the struct type, not
only directly declared top-level fields. Type inference also applies when a
generic function is assigned or converted to a matching function type:

```go
func identity[T any](value T) T { return value }
var intIdentity func(int) int = identity
```

## Errors, time, and signals

### Wrapped errors and stricter parsing (1.23.0)

Errors returned by `database/sql/driver.Valuer` are wrapped by `DB.Query`,
`DB.Exec`, and `DB.QueryRow`; inspect their cause with `errors.Is` or
`errors.As`.

`time.Parse` and `time.ParseInLocation` reject out-of-range time-zone offsets.

### Immediate nil checks (1.25.0)

Dereferencing a possibly nil result before checking its accompanying error now
panics at the required dereference point. Check the error immediately after the
call.

### Type-safe extraction and signal causes (1.26.0)

`errors.AsType[E]` returns a matched error value and a boolean:

```go
if pathErr, ok := errors.AsType[*os.PathError](err); ok {
	fmt.Println(pathErr.Path)
}
```

`signal.NotifyContext` records an error identifying the received signal as the
context cancellation cause; retrieve it with `context.Cause`.

## Reflection, source positions, and text

### Source inspection APIs (1.25.0, 1.26.0)

`ast.PreorderStack` traverses with the enclosing-node stack;
`token.FileSet.AddExistingFiles` builds a file set from existing files; and
`types.Var.Kind` plus `types.LookupSelection` expose variable classification
and method or field selections. Deprecated source APIs include AST
package-merging helpers and `parser.ParseDir`.

`ast.ParseDirective` parses conventional directive comments such as
`//go:generate`. `token.File.End` returns a file's end position.
`ast.BasicLit.ValueEnd` records a literal's exact end; tools that change
`ValuePos` must update or clear `ValueEnd` to avoid formatting differences.

### Reflection iterators (1.26.0)

`reflect.Type` provides `Fields`, `Methods`, `Ins`, and `Outs` iterators;
`reflect.Value` provides `Fields` and `Methods`. Value iteration yields both
the field or method metadata and its corresponding `Value`.

### Relative line directives (1.27.0)

Relative filenames in `//line` and `/*line*/` directives resolve against the
directory containing the source file with the directive. Generators should
make paths relative to the generated file, not the process working directory.

### Regular-expression categories (1.25.0)

`regexp/syntax` accepts `Any`, `ASCII`, `Assigned`, `Cn`, `LC`, and long Unicode
category aliases. Names are case-insensitive and ignore spaces, underscores,
and hyphens. `unicode.CategoryAliases` exposes aliases, and `C` includes the
unassigned-code-point category `Cn`.

### Unicode and UUID APIs (1.27.0)

The `unicode` package and system-wide tables use Unicode 17 rather than
Unicode 15. The new `uuid` package generates and parses UUIDs.
