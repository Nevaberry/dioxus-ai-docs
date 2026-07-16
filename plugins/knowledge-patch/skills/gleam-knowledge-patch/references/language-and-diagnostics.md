# Language and diagnostics

## Contents

- [Assertions, debugging, and incomplete code](#assertions-debugging-and-incomplete-code)
- [Records, custom types, and constants](#records-custom-types-and-constants)
- [Pipelines, operators, and guards](#pipelines-operators-and-guards)
- [Patterns and exhaustiveness](#patterns-and-exhaustiveness)
- [Bit arrays and numeric edge cases](#bit-arrays-and-numeric-edge-cases)
- [Warnings and name resolution](#warnings-and-name-resolution)
- [Documentation and formatting](#documentation-and-formatting)

## Assertions, debugging, and incomplete code

### Built-in Boolean assertions

Since 1.11.0, `assert` panics when its Boolean expression is `False` and attaches source-expression, operand, and argument details for test frameworks to report. Like `panic` and `todo`, it accepts a custom message with `as`.

```gleam
assert telecom.is_up(key, strict, 2025) as "My internet must always be up!"
```

### Custom `let assert` failures

Since 1.7.0, add `as "message"` after the asserted expression to control the message used when the partial pattern does not match.

```gleam
let assert Ok(regex) = regex.compile("ab?c+") as "This regex is always valid"
```

### Value-preserving debug expressions

Since 1.9.0, prefix an expression with `echo` to print its value and source file and line to standard error while preserving the value. `echo` works inside pipelines, and publishing warns about any left behind.

```gleam
[1, 2, 3]
|> list.map(fn(x) { x + 1 })
|> echo
```

Since 1.12.0, add `as "message"` to print identifying context before the value:

```gleam
echo 11 as "lucky number"
```

### Incomplete blocks and constants

Since 1.7.0, an empty block is accepted with an `incomplete block` warning, like an unfinished function body, so surrounding code can still be type checked.

```gleam
let value = {
  // warning: incomplete block
}
```

Since 1.17.0, `todo` can appear in a constant. Incomplete constant code can be type checked and analysed, and label-filling can insert `todo` fields, but a program containing one cannot run.

```gleam
pub const cleffa = Pokemon(number: 173, name: todo, hp: todo)
```

## Records, custom types, and constants

### Generic record updates

Since 1.7.0, updating a generic record may change its type parameter when the replacement field makes the change safe.

```gleam
pub type Named(value) {
  Named(name: String, value: value)
}

pub fn replace(data: Named(a), replacement: b) -> Named(b) {
  Named(..data, value: replacement)
}
```

Since 1.17.0, invalid record-update and list-prepend expressions remain analysable, preserving later diagnostics and language-server help around the error.

### Variant deprecation

Since 1.7.0, place `@deprecated` directly on a custom-type variant. Using that variant emits the normal deprecated-value warning.

```gleam
pub type HashAlgorithm {
  @deprecated("Please use another algorithm")
  Md5
  Sha512
}
```

### Record access across variants

On a multi-variant value, a field accessor is available only when that field has the same label, position, and type in every variant. A variant-specific field becomes accessible after pattern matching identifies the variant. Likewise, `let` can destructure a record only for a single-variant type or a value whose variant is already known; otherwise use `case`.

```gleam
pub type SchoolPerson {
  Teacher(name: String, subject: String)
  Student(name: String)
}

fn name(person: SchoolPerson) -> String {
  person.name
}
```

### Richer constant expressions

Since 1.14.0, use record updates in constant definitions:

```gleam
pub const dev_config = HttpConfig(..base_http_config, port: 4000)
```

Since 1.16.0, prepend elements to another constant list with spread syntax:

```gleam
pub const viviparous = ["dog", "cat"]
pub const mammals = ["platypus", ..viviparous]
```

## Pipelines, operators, and guards

### Typed pipeline fallback

For `value |> function(1, 2)`, the compiler first tries `function(value, 1, 2)`. If the value cannot be the first argument, it calls the returned function as `function(1, 2)(value)` instead.

### String concatenation in guards

Since 1.15.0, `<>` can concatenate strings in `case` guards. Rename, go-to-definition, hover, and find-references also operate from guard expressions.

```gleam
case message {
  action if version <> ":" <> action == "v1:delete" -> handle_delete()
  _ -> ignore_command()
}
```

### Operator diagnostics

Since 1.10.0, a wrong binary operator produces a diagnostic on the operator with a suggested replacement. For example, string concatenation with `+` is corrected to `<>`; the correction action also works inside guards as of 1.17.0.

## Patterns and exhaustiveness

### Alternative-pattern restrictions

Every alternative in a clause must bind the same variable names with the same types. Alternatives such as `2 | 4 | 6` can be top-level patterns, but cannot currently be nested inside another pattern.

### String-aware and variant-aware analysis

Since 1.10.0, exhaustiveness analysis recognises unreachable string patterns, including a later literal already covered by an earlier prefix pattern. The compiler also warns when a `let assert` pattern cannot match the value's already inferred variant.

Since 1.11.0, inexhaustive `case` errors display record labels in missing patterns, such as `Student(name:, age:)`; generated missing patterns include the labels too.

### Discard alias deprecation

Since 1.13.0, the redundant pattern `_ as value` is deprecated, and the formatter rewrites it to the equivalent direct pattern `value`.

### Bit-pattern reachability

Pattern analysis catches several distinct kinds of impossible bit-array clause:

- Since 1.11.0, a clause is unreachable when an earlier clause already covers it.
- Since 1.13.0, an intrinsically impossible segment warns even without an earlier clause; `<<404, _:bits>>` cannot match because a default one-byte unsigned integer cannot contain `404`.
- Since 1.14.0, analysis normalises numeric representations and applies interference-based pruning, detecting equivalent string/integer encodings and covered integer bit patterns.

## Bit arrays and numeric edge cases

### Segment defaults and embedding

A segment is an 8-bit integer by default, and `size(n)` counts bits because the default unit is one. Use `:bits` to splice a bit array of any alignment or `:bytes` when the nested value must be byte-aligned. Segment options compose with dashes, and target support varies.

```gleam
let remainder = <<4, 2>>
<<3, 6147:size(16), "ok":utf8, remainder:bits>>
```

Since 1.12.0, UTF codepoint segments can specify endianness, and bit-array patterns can calculate segment sizes.

```gleam
let assert <<size, data:bytes-size(size / 8 - 1)>> = packet
```

Since 1.11.0, the compiler warns when a literal integer will be truncated to fit its segment and reports the resulting value. JavaScript-specific support and its 52-bit pattern limit are detailed in [targets-and-ffi.md](targets-and-ffi.md).

### Float target differences

Float division by zero is defined to return zero rather than overflow.

```gleam
echo 3.14 /. 0.0
```

JavaScript-targeted floats can produce infinities and `NaN`. An overflow on the Erlang target raises an error, and Erlang has neither special value.

## Warnings and name resolution

### Discarded and unused values

Since 1.11.0, discarding a side-effect-free function call as a non-final expression warns. This catches immutable-update bugs where the returned value was neither assigned nor piped onward.

Since 1.13.0, an argument used only by passing it unchanged into self-recursive calls is considered unused if the implementation never otherwise reads it.

### Inefficient list emptiness tests

Since 1.13.0, the compiler catches more `<` and `>` comparisons that traverse an entire list merely to decide whether it is empty. Prefer pattern matching, `items == []`, or `items != []` to comparisons involving `list.length(items)`.

### Inaccessible imports and discarded names

Since 1.12.0, importing a function or constant unqualified under the same name as a local function or constant warns because the local definition makes the import inaccessible.

If an unknown name such as `x` resembles a discarded binding such as `_x`, the diagnostic highlights that binding and suggests removing the underscore or choosing another variable. Language-server clients receive the secondary context.

Since 1.17.0, when an unqualified value is unknown, the compiler searches imported modules and suggests qualified forms such as `io.println`.

### Comparisons, arity, and displayed types

Since 1.12.0, comparisons provably guaranteed to succeed or fail warn, including comparing a value with itself. An incorrect-arity error also lists the labels of additional labelled arguments the function accepts.

Since 1.17.0, warning messages render types using the qualification or module alias visible in the current file instead of always using the canonical module name.

## Documentation and formatting

### Module and definition documentation

Use a `////` comment at the top of a file to document the module rather than one definition.

```gleam
//// Utilities for processing application messages.
```

Since 1.14.0, the compiler warns when a `///` definition comment is separated from its definition by a regular `//` comment and would be omitted from generated documentation.

### Capture, list, negation, and guard formatting

Since 1.9.0, formatting replaces a capture with no extra arguments by the direct function reference, such as `io.print(_)` becoming `io.print`.

Since 1.12.0, a trailing comma before `]` keeps even a short list multiline; removing it allows collapse. The formatter preserves deliberate one-per-line or packed grouping and one blank line within lists.

```gleam
let names = [
  "natu",
  "milotic",
]
```

Since 1.13.0, redundant repeated negations collapse (`--11` to `11`, `!!!False` to `!False`), while explicit blocks in `case` clause guards are preserved.
