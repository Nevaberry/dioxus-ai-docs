# Debug & Testing

## `echo` keyword (1.9)

New language keyword replacing `io.debug` for print debugging. Prints the value plus file path and line number to stderr. Works standalone or in pipelines. The build tool warns if `echo` is left in published packages.

```gleam
pub fn main() {
  echo [1, 2, 3]
  // Output:
  // src/main.gleam:2
  // [1, 2, 3]
}

// In a pipeline:
pub fn transform() {
  [1, 2, 3]
  |> list.map(fn(x) { x + 1 })
  |> echo
  |> list.map(fn(x) { x * 2 })
}
```

## `echo` with custom messages (1.12)

The `echo` keyword supports `as` to add a label to the debug output.

```gleam
pub fn main() {
  echo 11 as "lucky number"
}
// Output:
// /src/main.gleam:2 lucky number
// 11
```

## Custom messages for `let assert` (1.7)

The `as` keyword adds a custom error message to partial pattern assertions.

```gleam
let assert Ok(regex) = regex.compile("ab?c+") as "This regex is always valid"
```

## `assert` for testing (1.11)

New language keyword for test assertions. Panics if the expression evaluates to `False`, with rich error metadata (source location, code text, evaluated values) that test frameworks can display.

```gleam
pub fn hello_test() {
  assert telecom.ring() == "Hello, Joe!"
}

// Custom message with `as`:
pub fn system_test() {
  assert telecom.is_up(key, strict, 2025)
    as "My internet must always be up!"
}
```
