# Language and Core Library

## Iteration and templates

### Function-range iterator protocol (`1.23-guide`)

`for range` accepts functions of the forms `func(func() bool)`,
`func(func(V) bool)`, and `func(func(K, V) bool)`. The iterator calls its
`yield` argument for each item and must stop as soon as `yield` returns false;
an early loop exit makes the compiler-provided `yield` return false.

The `iter` package names the one- and two-value forms `iter.Seq[V]` and
`iter.Seq2[K, V]`; there is no `Seq0`. Container APIs conventionally expose an
`All` method returning one of these types.

### Converting push iterators to pull iterators (`1.23-guide`)

`iter.Pull` converts an `iter.Seq[V]` into `next func() (V, bool)` and a
`stop` function, which is especially useful when consuming sequences in
lockstep. Call `stop` whenever consumption can end before `next` reports false;
deferring it unconditionally is the simplest safe pattern.

### Iterator APIs in `slices` and `maps` (`1.23-guide`)

`slices` provides `All`, `Values`, `Collect`, `AppendSeq`, `Backward`,
`Sorted`, `SortedFunc`, `SortedStableFunc`, and `Chunk` for iterator production
and consumption. `maps` provides iterator-based `All`, `Keys`, `Values`,
`Collect`, and `Insert`. For example, `slices.Sorted(maps.Keys(m))` collects a
map's keys into a sorted slice.

### Enabling the language feature (`1.23-guide`)

Range over functions requires language version 1.23 or later. Update the module
with `go get go@1.23`, change only its directive with
`go mod edit -go=1.23`, or isolate the syntax in a file guarded by
`//go:build go1.23`.

### Template `else with` (`1.23.0`)

`text/template` accepts `else with`, avoiding a nested `with` when selecting a
fallback value:

```gotemplate
{{with .Primary}}
  {{.}}
{{else with .Fallback}}
  {{.}}
{{else}}
  unavailable
{{end}}
```

### Iterator ranges in templates (`1.24.0`)

`text/template` accepts `range` over iterator functions and integer values.

### Reflection iterators (`1.26.0`)

`reflect.Type` has `Fields`, `Methods`, `Ins`, and `Outs` iterators.
`reflect.Value` has `Fields` and `Methods`; value iteration yields both field
or method metadata and its corresponding `Value`.

## Generics, expressions, and literals

### Initialized pointers with `new` (`1.26.0`)

`new` accepts an expression and returns a pointer to a new variable initialized
with that value. This makes optional pointer fields possible without a
temporary:

```go
person := Person{Age: new(yearsSince(born))}
```

### Self-referential generic constraints (`1.26.0`)

A generic type may refer to itself in its own type-parameter list, permitting
F-bounded constraints:

```go
type Adder[A Adder[A]] interface {
	Add(A) A
}
```

### Generic methods (`1.27.0`)

Methods on non-parameterized receiver types may declare their own type
parameters. Methods on parameterized types still cannot add type parameters,
and generic methods cannot implement interface methods.

```go
type Store struct{}

func (Store) Identity[T any](value T) T { return value }
```

### Broader struct-literal keys (`1.27.0`)

A struct literal key may use any field selector valid for the struct type, not
only a directly declared top-level field.

### Function-value type inference (`1.27.0`)

Type inference applies whenever a generic function is assigned or converted to
a matching function type:

```go
func identity[T any](value T) T { return value }
var intIdentity func(int) int = identity
```

## Errors, time, and cancellation

### Wrapped `driver.Valuer` errors (`1.23.0`)

Errors returned by `database/sql/driver.Valuer` are wrapped by `DB.Query`,
`DB.Exec`, and `DB.QueryRow`, so callers can inspect the original cause with
`errors.Is` or `errors.As`.

### Strict time-zone offsets (`1.23.0`)

`time.Parse` and `time.ParseInLocation` reject out-of-range time-zone offsets.

### Immediate nil-pointer checks (`1.25.0`)

Dereferencing a possibly nil result before checking its accompanying error now
panics at the dereference, as the language requires, correcting delayed checks
present since 1.21. Check the error immediately after the call.

### Type-safe error extraction (`1.26.0`)

`errors.AsType[E]` returns a type-safe matched error value and a boolean:

```go
if pathErr, ok := errors.AsType[*os.PathError](err); ok {
	fmt.Println(pathErr.Path)
}
```

### Signal cancellation causes (`1.26.0`)

`signal.NotifyContext` records an error identifying the received signal as the
context's cancellation cause, available through `context.Cause`.

## Source analysis and generated positions

### Source-analysis APIs (`1.25.0`)

`ast.PreorderStack` traverses with the enclosing-node stack,
`token.FileSet.AddExistingFiles` assembles a set from existing files, and
`types.Var.Kind` plus `types.LookupSelection` expose variable classification
and selections. AST package-merging APIs and `parser.ParseDir` are deprecated.

### Source-tooling APIs and literal positions (`1.26.0`)

`ast.ParseDirective` parses conventional comments such as `//go:generate`, and
`token.File.End` returns a file's end position. `ast.BasicLit.ValueEnd` records
the exact literal end; tools changing `ValuePos` must also update or clear
`ValueEnd` to avoid formatting differences.

### Relative `//line` paths (`1.27.0`)

Relative filenames in `//line` and `/*line*/` directives resolve against the
directory containing the directive's source file. Generators should make paths
relative to the generated source file's directory.

## Regular expressions and Unicode

### Unicode category matching (`1.25.0`)

`regexp/syntax` accepts `Any`, `ASCII`, `Assigned`, `Cn`, `LC`, and long
category aliases. Names are matched case-insensitively while spaces,
underscores, and hyphens are ignored. `unicode.CategoryAliases` exposes aliases,
and category `C` includes the newly exposed unassigned-code-point category
`Cn`.

### Unicode 17 (`1.27.0`)

The `unicode` package and system-wide Unicode support use Unicode 17 rather
than Unicode 15.
