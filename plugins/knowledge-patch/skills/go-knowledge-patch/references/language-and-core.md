# Language and Core Library

Batch coverage: `1.23-guide`, `1.23.0`, `1.24.0`, `1.25.0`, `1.26.0`.

## Contents

- [Function iterators](#function-iterators)
- [Templates](#templates)
- [Language changes](#language-changes)
- [Errors and reflection](#errors-and-reflection)
- [Parsing and matching](#parsing-and-matching)

## Function iterators

### Push-iterator protocol

A `for range` loop over a function accepts exactly these iterator shapes:

```go
func(func() bool)
func(func(V) bool)
func(func(K, V) bool)
```

The iterator calls `yield` for every item and must stop when it returns false. An early loop exit causes the compiler-provided `yield` to return false.

The `iter` package names the one- and two-value forms `iter.Seq[V]` and `iter.Seq2[K, V]`; there is no `Seq0`. Container APIs conventionally expose an `All` method:

```go
func (s *Set[E]) All() iter.Seq[E] {
	return func(yield func(E) bool) {
		for value := range s.m {
			if !yield(value) {
				return
			}
		}
	}
}

for value := range set.All() {
	fmt.Println(value)
}
```

Range-over-function syntax requires language version 1.23 or later. Select it with `go get go@1.23`, change only the directive with `go mod edit -go=1.23`, or isolate the syntax in a file guarded by `//go:build go1.23`.

### Pull iteration

`iter.Pull` converts `iter.Seq[V]` to `next func() (V, bool)` and a `stop` function, which is useful for consuming multiple sequences in lockstep. Call `stop` whenever iteration might end before `next` returns false; unconditional `defer` is the simplest safe pattern.

```go
next, stop := iter.Pull(seq)
defer stop()
for value, ok := next(); ok; value, ok = next() {
	use(value)
}
```

### `slices` and `maps`

Use the iterator-aware `slices` APIs `All`, `Values`, `Collect`, `AppendSeq`, `Backward`, `Sorted`, `SortedFunc`, `SortedStableFunc`, and `Chunk`. Use `maps.All`, `Keys`, `Values`, `Collect`, and `Insert` for map iteration and collection.

```go
keys := slices.Sorted(maps.Keys(m))
```

## Templates

`text/template` accepts `else with`, avoiding a nested fallback `with`:

```gotemplate
{{with .Primary}}
  {{.}}
{{else with .Fallback}}
  {{.}}
{{else}}
  unavailable
{{end}}
```

Template `range` also accepts iterator functions and integer values.

## Language changes

### Initialized pointers with `new`

The built-in `new` accepts an expression and returns a pointer to a new variable initialized with that expression's value. Use it for optional pointer fields without a temporary.

```go
person := Person{Age: new(yearsSince(born))}
```

### Self-referential generic constraints

A generic type may refer to itself in its own type-parameter list, enabling F-bounded interfaces:

```go
type Adder[A Adder[A]] interface {
	Add(A) A
}
```

### Immediate nil-pointer checks

Nil checks that had been delayed by compiler behavior now occur at the dereference point required by the language. Code that dereferences a possibly nil result before checking its accompanying error can therefore panic earlier. Check the error immediately after the call.

## Errors and reflection

### Wrapped `driver.Valuer` errors

`DB.Query`, `DB.Exec`, and `DB.QueryRow` wrap errors returned by `database/sql/driver.Valuer`. Use `errors.Is` or `errors.As` to inspect the original cause.

### Type-safe wrapped-error extraction

`errors.AsType[E]` is a generic form of `errors.As` that returns the matched value and a boolean.

```go
if pathErr, ok := errors.AsType[*os.PathError](err); ok {
	fmt.Println(pathErr.Path)
}
```

### Reflection iterators

`reflect.Type` provides `Fields`, `Methods`, `Ins`, and `Outs` iterators. `reflect.Value` provides `Fields` and `Methods`; value iteration yields both field or method metadata and the corresponding `Value`.

## Parsing and matching

### Time-zone offsets

`time.Parse` and `time.ParseInLocation` reject time-zone offsets that are out of range rather than accepting them.

### Unicode categories in regular expressions

`regexp/syntax` recognizes `Any`, `ASCII`, `Assigned`, `Cn`, `LC`, and long category aliases. Category names are case-insensitive and ignore spaces, underscores, and hyphens. `unicode.CategoryAliases` exposes the aliases, and category `C` now includes the exposed unassigned-code-point category `Cn`.
