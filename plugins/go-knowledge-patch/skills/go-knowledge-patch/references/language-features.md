# Go Language Features (1.26)

## `new()` with Initial Value

`new` can now take an expression operand, returning a pointer to a variable initialized with that value. Especially useful for optional pointer fields:

```go
type Person struct {
	Name string `json:"name"`
	Age  *int   `json:"age,omitempty"`
}

p := Person{Name: "Alice", Age: new(30)} // *int pointing to 30
```

## Self-Referential Generic Type Constraints

Generic types may now refer to themselves in their own type parameter list:

```go
type Adder[A Adder[A]] interface {
	Add(A) A
}

func Sum[A Adder[A]](x, y A) A { return x.Add(y) }
```
