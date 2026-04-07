# Language Changes

## `new` Accepts an Expression Argument (1.26)

`new(expr)` creates a pointer to the value of `expr`. This eliminates the common `ptr()` helper pattern used throughout Go codebases.

```go
// Before: needed a helper or temp variable
func ptr[T any](v T) *T { return &v }
p := ptr(42)

// After: built-in
p := new(42)
p := new(yearsSince(born)) // useful for optional struct fields
```

### Common use cases

Setting optional struct fields inline:

```go
req := &Request{
	Timeout: new(5 * time.Second),
	Retries: new(3),
}
```

## Self-Referential Generic Type Constraints (1.26)

Generic types may now refer to themselves in their type parameter list. This enables patterns like fluent interfaces and recursive data structures with generic constraints.

```go
type Adder[A Adder[A]] interface {
	Add(A) A
}

func algo[A Adder[A]](x, y A) A { return x.Add(y) }
```

This was previously a compiler error — the type parameter `A` could not appear in its own constraint.
