# Language and diagnostics

## Records, types, and constants

### Generic record updates

Since 1.7.0, changing a record field may safely change the parameterised type
of a generic record.

```gleam
pub type Named(element) {
  Named(name: String, value: element)
}

pub fn replace_value(data: Named(a), replacement: b) -> Named(b) {
  Named(..data, value: replacement)
}
```

Since 1.14.0, record-update syntax is valid in constants. Since 1.16.0,
list-spread syntax can prepend values to another constant list.

```gleam
pub const base = HttpConfig(host: "0.0.0.0", port: 8080)
pub const dev = HttpConfig(..base, port: 4000)

pub const mammals = ["dog", "cat", "human"]
pub const all_mammals = ["platypus", "echidna", ..mammals]
```

Since 1.17.0, a constant may contain `todo`, allowing it to be type-checked and
analysed while incomplete. Constants are evaluated at compile time, so a
program containing such a constant cannot run.

### Variant deprecation

Since 1.7.0, `@deprecated` can annotate one custom-type variant instead of a
function or an entire type.

```gleam
pub type HashAlgorithm {
  @deprecated("Please upgrade to another algorithm")
  Md5
  Sha224
  Sha512
}
```

## Assertions, debugging, and placeholders

### Assertion messages

Since 1.7.0, append `as "message"` to a partial-pattern `let assert` to set its
panic message.

```gleam
let assert Ok(regex) = regex.compile("ab?c+") as "This regex is always valid"
```

Since 1.11.0, `assert expression` panics when the expression is `False` and
records the source expression and relevant operand or argument values for test
frameworks. It also accepts a custom message with `as`.

```gleam
assert telecom.is_up(key, strict, 2025) as "My internet must always be up!"
```

### `echo`

Since 1.9.0, prefix an expression with `echo` to print its value and source
location to standard error. It can occur in a pipeline without consuming the
value. Publishing warns about `echo` expressions left in a project.

Since 1.12.0, append `as "message"` to print contextual text with the location
and value.

```gleam
echo 11 as "lucky number"
```

### Incomplete blocks

Since 1.7.0, an empty block is accepted with an incomplete-block warning, so
the surrounding program can still be type-checked.

```gleam
let value = {
  // warning: incomplete block
}
```

## Guards, pipelines, and formatting

### Guard expressions

Since 1.15.0, string concatenation with `<>` is valid in case-clause guards.
Rename, go-to-definition, hover, and find-references work on expressions inside
guards.

```gleam
case message {
  action if version <> ":" <> action == "v1:delete" -> handle_delete()
  _ -> ignore_command()
}
```

### Pipeline fallback

For `value |> function(arguments)`, Gleam first tries
`function(value, arguments)`. If that does not type-check, it calls
`function(arguments)(value)`. Use a function capture when the piped value
belongs in another argument position.

### Formatter behavior

Since 1.9.0, the formatter removes function-capture syntax when no extra
arguments make it useful, such as rewriting `io.print(_)` to `io.print`.

Since 1.12.0, a trailing comma before a list's closing bracket preserves
multiline formatting. Removing the comma allows one-line formatting again, and
blank lines within lists are preserved.

Since 1.13.0, repeated Boolean and integer negations collapse, such as
`!!!False` to `!False` and `--11` to `11`. Explicit blocks in case-clause guards
are preserved.

## Pattern rules and reachability

### Alternative patterns

Every case alternative separated by `|` must bind the same variable names with
the same types. Alternatives cannot be nested within another pattern, so
`[1 | 2 | 3]` is invalid.

```gleam
case item {
  #(1, value) | #(2, value) -> value
  _ -> 0
}
```

### Record accessors

For a multi-variant custom type, `.field` works without refinement only if
every variant has the field in the same position with the same type. A
variant-specific field is available only when the exact variant is known, such
as after pattern matching.

### String and variant analysis

Since 1.10.0, exhaustiveness analysis detects a string pattern made unreachable
by an earlier prefix pattern. The compiler also warns if a `let assert` pattern
cannot match a value whose variant is already inferred.

```gleam
case greeting {
  "Hello, " <> name -> name
  "Hello, Jak" -> "Jak" // Unreachable
  _ -> "Stranger"
}
```

### Bit-array reachability

Since 1.11.0, analysis detects a bit-array clause wholly covered by an earlier
clause. Since 1.13.0, it warns about segments that can never match, including an
out-of-range literal in the default one-byte integer segment.

Since 1.14.0, numeric spellings are normalised and interference-based pruning
finds equivalent string, decimal, binary, octal, and hexadecimal integer
segments, such as `<<"a">>` and `<<97>>`.

### Other warnings and deprecations

- Since 1.11.0, discarding the result of a side-effect-free call warns; this
  catches immutable updates whose replacement value was accidentally ignored.
- Since 1.11.0, an integer literal too large for its bit-array segment warns and
  shows the truncated value; `<<258>>` produces `2` in the default byte segment.
- Since 1.12.0, an unqualified function or constant import shadowed by a local
  definition warns because the import is unreachable.
- Since 1.12.0, a provably always-successful or always-failing comparison warns.
- Since 1.13.0, an argument used only by forwarding it into recursive calls is
  reported as unused.
- Since 1.13.0, redundant `_ as value` patterns are deprecated and format as
  plain `value`.
- Since 1.13.0, more empty/non-empty tests that traverse a linked list through
  `list.length`, including `0 < list.length(items)`, warn and recommend `[]`.
- Since 1.14.0, a regular `//` comment between a `///` comment and its definition
  warns because it detached that documentation.

## Bit-array construction and matching

`size(n)` counts units, and `unit` defaults to one bit. Integer segments default
to 8 bits; float segments default to 64 bits. `bits` embeds a bit array of any
size, while `bytes` requires byte alignment.

Since 1.12.0, UTF codepoint segments can specify endianness in construction and
patterns, and bit-array pattern sizes may contain calculations.

```gleam
let assert <<size, data:bytes-size(size / 8 - 1)>> = payload
```

## Documentation syntax

Use `////` at the top of a module for module documentation. Use `///`
immediately before a type or function to document that definition.

```gleam
//// Utilities for displaying greetings.

/// Return a greeting for a name.
pub fn greeting(name: String) -> String {
  "Hello, " <> name
}
```

## Float target differences

Both targets use 64-bit floats. JavaScript overflow produces `Infinity` or
`-Infinity` and can lead to `NaN`; BEAM overflow raises an error and provides no
infinity or NaN values. Float division by zero produces zero rather than
overflow.

## External fallbacks

A function with both an `@external` annotation and a Gleam body uses the
external implementation when the current target provides one and otherwise
runs the Gleam body.

```gleam
import gleam/list

@external(erlang, "lists", "reverse")
pub fn reverse(items: List(a)) -> List(a) {
  list.reverse(items)
}
```
