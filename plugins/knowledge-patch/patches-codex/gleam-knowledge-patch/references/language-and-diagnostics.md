# Language and diagnostics

## Assertions, incomplete code, and debugging

### Boolean assertions

Gleam has a Boolean `assert` expression (since 1.11.0). It panics when its
condition is `False` and records the source expression plus relevant operand
or argument values for test frameworks. Add a custom failure message with
`as`:

```gleam
assert telecom.is_up(key, strict, 2025) as "internet must be available"
```

### Partial-pattern assertion messages

`let assert` accepts `as "message"` (since 1.7.0):

```gleam
let assert Ok(regex) = regex.compile("ab?c+") as "known-valid expression"
```

The compiler also warns when a `let assert` pattern can never match a value
whose variant is already inferred (since 1.10.0).

### `echo` expressions

Prefix any expression with `echo` to print its value and source location to
standard error without changing the value (since 1.9.0). It composes inside a
pipeline. Add context with `as "message"` (since 1.12.0):

```gleam
echo 11 as "lucky number"
```

The build tool warns about leftover `echo` expressions during publishing.

### Incomplete blocks

An empty block is accepted as an incomplete placeholder (since 1.7.0). It
produces an incomplete-block warning while allowing the surrounding program
to be type-checked:

```gleam
let value = {
  // incomplete
}
```

## Records, custom types, and constants

### Generic-changing record updates

A record update can change the parameterised type of a generic record (since
1.7.0):

```gleam
pub type Named(element) {
  Named(name: String, value: element)
}

pub fn replace_value(data: Named(a), replacement: b) -> Named(b) {
  Named(..data, value: replacement)
}
```

Keep the returned record. The compiler warns when the result of a pure call is
discarded (since 1.11.0), catching immutable updates that would otherwise have
no effect.

### Variant deprecation

`@deprecated` may annotate an individual custom-type variant (since 1.7.0),
not only a function or entire type:

```gleam
pub type HashAlgorithm {
  @deprecated("Use another algorithm")
  Md5
  Sha512
}
```

### Field access across variants

On a multi-variant custom type, `.field` is available before refinement only
when every variant has that field in the same position and with the same type.
A variant-specific field is available after matching narrows the value:

```gleam
pub type Person {
  Teacher(name: String, subject: String)
  Student(name: String)
}

fn name(person: Person) -> String {
  person.name
}
```

### Constant record updates and list spreads

Record-update syntax works in constants (since 1.14.0):

```gleam
pub const base = HttpConfig(host: "0.0.0.0", port: 8080)
pub const dev = HttpConfig(..base, port: 4000)
```

Constant lists can prepend elements to another constant list (since 1.16.0):

```gleam
pub const mammals = ["dog", "cat", "human"]
pub const all_mammals = ["platypus", "echidna", ..mammals]
```

### `todo` in constants

Constants may contain `todo` (since 1.17.0). They can be type-checked and
analysed, and fill-labels can insert `todo` for missing fields, but a program
containing such a constant cannot run because constants are evaluated at
compile time.

```gleam
pub const cleffa = Pokemon(number: 173, name: todo, hp: todo)
```

Gleam 1.18.0 fixes invalid generated code for constant strings used as
bit-array segments. When a referenced constant aliases another constant in a
bit-array segment, string concatenation, or guard, use 1.18.1 or newer because
1.18.0 can generate incorrect Erlang.

## Pipelines, guards, and patterns

### Type-directed pipeline fallback

For `value |> function(arguments)`, Gleam first tries
`function(value, arguments)`. If that does not type-check, it calls
`function(arguments)(value)`. Use a function capture when the piped value
belongs in another argument position.

```gleam
fn add_to(x: Int) -> fn(Int) -> Int {
  fn(y) { x + y }
}

let three = 2 |> add_to(1)
```

### String concatenation in guards

Case guards accept the string concatenation operator `<>` (since 1.15.0):

```gleam
case message {
  action if version <> ":" <> action == "v1:delete" -> handle_delete()
  _ -> ignore_command()
}
```

Rename, go-to-definition, hover, find-references, and operator correction work
inside guards.

### Alternative patterns

Every alternative separated by `|` in a case clause must bind the same names
with the same types. Alternatives cannot nest inside another pattern, so
`[1 | 2 | 3]` is invalid.

```gleam
case item {
  #(1, value) | #(2, value) -> value
  _ -> 0
}
```

### String-pattern reachability

Exhaustiveness analysis detects a string pattern made unreachable by an
earlier prefix pattern (since 1.10.0):

```gleam
case greeting {
  "Hello, " <> name -> name
  "Hello, Jak" -> "Jak" // unreachable
  _ -> "Stranger"
}
```

### Redundant discard aliases

The redundant pattern `_ as value` is deprecated (since 1.13.0). The formatter
rewrites it to the equivalent `value` pattern.

## Bit arrays

### Segment defaults

`size(n)` counts units and `unit` defaults to one bit. Integer segments default
to 8 bits and float segments to 64 bits. Use `bits` to embed any bit-array
alignment and `bytes` to require byte alignment:

```gleam
let joined = <<first:bits, second:bits>>
```

UTF codepoint segments accept endianness in construction and matching, and
pattern sizes may contain calculations (since 1.12.0):

```gleam
let assert <<size, data:bytes-size(size / 8 - 1)>> = payload
```

### Truncation and impossible-pattern warnings

The compiler warns when an integer literal does not fit its segment and shows
the truncated value (since 1.11.0); for example, `<<258>>` becomes `2` in the
default one-byte segment.

It also detects:

- A bit-array clause fully covered by an earlier clause (since 1.11.0).
- An impossible out-of-range segment such as `<<404, _:bits>>` (since 1.13.0).
- Equivalent integer spellings in string, decimal, binary, octal, or
  hexadecimal patterns (since 1.14.0), such as `<<"a">>` followed by `<<97>>`.

## Compiler warnings and build diagnostics

### Inefficient list emptiness checks

The compiler detects empty and non-empty checks that traverse a linked list
with `list.length`, including comparisons such as `0 < list.length(items)`
(expanded in 1.13.0). Prefer patterns, `items == []`, or `items != []`.

### Unused recursively forwarded arguments

Unused-argument analysis warns when an argument is merely forwarded into
recursive calls and is never otherwise used (since 1.13.0).

### Shadowed unqualified imports

An unqualified function or constant import warns when the importing module
defines the same name, making the import unreachable (since 1.12.0).

### Redundant comparisons

The compiler warns when it can prove a comparison always succeeds or always
fails (since 1.12.0), such as comparing a value with itself.

### Opaque internal types

Diagnostics and editor actions preserve internal abstraction (since 1.15.0):
missing-pattern actions insert a catch-all rather than revealing variants,
field completion is omitted, and inexhaustive-pattern errors do not expose
the structure.

### Local names in displayed warning types

Warning types use the module qualifier or import alias visible in the current
file (since 1.17.0), rather than always printing a canonical module name.
Likewise, generated documentation, hovers, and annotation actions prefer an
accessible public type alias over an internal aliased type (since 1.13.0).

## Documentation and formatting

### Documentation comments

Use four slashes for module documentation and three for a following type or
function:

```gleam
//// Utilities for displaying greetings.

/// Return a greeting.
pub fn greeting() { "Hello" }
```

A regular `//` comment between `///` and a definition detaches the earlier
documentation and warns (since 1.14.0).

### Multiline lists

A trailing comma before a list's closing bracket preserves multiline layout
(since 1.12.0). Remove it to permit collapsing. Blank lines within lists are
also preserved.

### Captures, negation, and guards

The formatter replaces a redundant capture such as `io.print(_)` with
`io.print` (since 1.9.0). It collapses repeated Boolean and integer negation,
such as `!!!False` to `!False` and `--11` to `11`, while preserving explicit
blocks in case-clause guards (since 1.13.0).
