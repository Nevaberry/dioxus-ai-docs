# Editor and refactoring

## Navigation, symbols, and analysis

### Project-wide references and rename

Find-references locates every use of a type or value across the project, and
rename updates cross-module references (since 1.10.0). Rename also handles
local variables and function arguments (since 1.8.0).

Variables bound in string-prefix patterns support find-references and rename
(since 1.15.0):

```gleam
case value {
  "1" as digit <> rest -> digit <> rest
}
```

### Module rename from a qualifier

Module rename may be invoked on any qualifier use, not only the import (since
1.15.0). It introduces an import alias and updates qualifiers throughout the
file.

### Type definition and documentation

Go-to-type-definition on an expression presents the definitions of the value
types involved (since 1.9.0). Hovering the qualifier of an imported type or
value displays the imported module's documentation (since 1.9.0).

Hover, completion, and go-to-definition work within constant expressions
(since 1.11.0). Hovering the spread value in a record update lists fields that
remain unchanged (since 1.17.0).

### Highlights and folding

Editors can highlight every reference to the variable under the cursor through
`textDocument/documentHighlight` (since 1.17.0). Folding ranges cover
contiguous import blocks and multiline top-level functions, custom types,
constants, and type aliases (since 1.15.0).

### Non-executing project analysis

The language server type-checks unsaved buffers for the configured target
without code generation or Erlang/Elixir compilation. Analysis therefore does
not execute foreign code. A Gleam file outside a project only receives
formatting support.

## Function and module generation

### Generate a missing function

Invoke “Generate function” on a call to an undefined function to insert an
outline with inferred argument and return types and a `todo` body (since
1.8.0):

```gleam
fn to_string(pokemon: Pokemon) -> String {
  todo
}
```

Parameter names derive from argument labels and local names (since 1.11.0).
For a missing qualified call, the action edits the imported module and inserts
a public function with inferred annotations (since 1.13.0).

### Generate a custom-type variant

The language server can infer and add a missing custom-type variant from its
use, including field types and labels (since 1.11.0).

If an existing variant uses an undeclared type variable, a quick fix adds that
parameter to the custom type's header (since 1.15.0):

```gleam
pub type Store(inner_type) {
  Store(name: String, data: inner_type)
}
```

### Create a missing imported module

When an import names a nonexistent module in the package, an action creates
the source file (since 1.17.0). For example, `import wobble/woo` from
`src/wiggle.gleam` can create `src/wobble/woo.gleam`.

### Generate exhaustive matches

The pattern-match action creates a `case` for a local variable or function
argument with all variants needed to exhaustively match its type (since
1.8.0):

```gleam
case result {
  Ok(value) -> todo
  Error(value) -> todo
}
```

It also handles lists and variables introduced by enclosing patterns (since
1.13.0). For a variable bound by an outer case clause, it specialises that
clause into exhaustive alternatives. A discard nested in a case pattern can be
expanded similarly (since 1.17.0), for example `Ok(_)` into the empty and
non-empty list cases.

### Convert an inexhaustive `let` to `case`

For an inexhaustive `let` pattern, replace the binding with a `case` and insert
missing patterns as `todo` branches (since 1.7.0).

## Encoder and decoder generation

### Generate dynamic decoders

Invoke the decoder action on a custom-type header to generate a
`gleam/dynamic/decode` decoder (since 1.7.0). Multi-variant generation reads a
string field named `"type"`, matches lower-case variant names, decodes the
selected fields, and leaves an unknown discriminator as a `decode.failure`
placeholder (since 1.9.0).

Generated decoders support `Nil` and provide best-effort zero values to
`decode.failure` (since 1.15.0).

### Generate JSON encoders

The encoder action on a custom type generates a `gleam_json` encoder (since
1.9.0):

```gleam
fn encode_person(person: Person) -> json.Json {
  let Person(name:, age:) = person
  json.object([
    #("name", json.string(name)),
    #("age", json.int(age)),
  ])
}
```

The full-field pattern match was added in 1.10.0 so adding a custom-type field
causes a compile error until the encoder is updated, instead of silently
omitting the new field.

## Labels, imports, annotations, and completion

### Fill labels

“Fill labels” works on partial calls, adding only missing labelled arguments as
`todo` (since 1.8.0). It fills omitted fields in record patterns (since
1.11.0), and in constants it inserts `todo` for missing fields (since 1.17.0).

Since 1.15.0, the action uses an in-scope variable when its name and type match
the label and leaves `todo` only when no suitable variable exists.

### Add omitted labels

A separate action adds labels to positional arguments when the function
parameter or constructor field is labelled (since 1.13.0):

```gleam
User(first_name:, last_name: "Cavalieri", likes: ["gleam"])
```

### Expand ignored pattern fields

Replace `..` in a record pattern with every ignored field (since 1.10.0):

```gleam
let Pokemon(id:, name:, moves:) = pokemon
```

Missing-pattern diagnostics and inserted clauses include record labels (since
1.11.0).

### Remove unused imports

Remove-unused-imports deletes unused unqualified types and values from a
grouped import while retaining names that are used (since 1.11.0).

### Qualify and unqualify symbols

Module-wide actions update both imports and every use. Qualifying supports all
types and values; unqualifying is limited to types and custom-type variant
constructors.

### Add annotations and fill type holes

One action annotates every top-level constant and function in a module with
its inferred type (since 1.14.0). Another replaces `_` in a type annotation
with the inferred type at that position (since 1.16.0):

```gleam
fn identity(value: Int) -> Int { value }
```

Generated displays prefer an accessible public type alias instead of exposing
the aliased internal type (since 1.13.0).

### Context-aware completion and suggestions

Completion offers labelled fields while writing a record update and suppresses
value suggestions while editing a qualified type (since 1.16.0). When an
unqualified value is unknown, the compiler searches already imported modules
and suggests matching qualified names such as `io.println` (since 1.17.0).

## Refactoring expressions and functions

### Convert calls and pipelines

Convert an ordinary call to pipe syntax or back (since 1.9.0). Before
conversion, select an argument to pipe a value into a position other than the
first.

The initial expression of a pipeline can be extracted into a variable (since
1.15.0).

### Sugar and desugar `use`

Convert a `use` expression to its equivalent callback-based call and back
(since 1.7.0). This is useful when learning or restructuring callback-heavy
code.

### Add or remove anonymous wrappers

Switch between a single-call anonymous function and a direct function
reference (since 1.16.0):

```gleam
fn(value) { int.absolute_value(value) }
int.absolute_value
```

### Extract functions

Extract a selected expression into a typed private function and replace the
selection with a call (since 1.13.0). The initial generated name is `function`;
rename it to a domain name.

When the selection is an anonymous function, the action extracts its body and
passes captured values as parameters (since 1.15.0). It can also extract
selected consecutive pipeline stages or the value of an assignment (since
1.16.0).

### Extract constants

Lift a selected non-dynamic expression into a module constant and replace the
original expression with its name (since 1.10.0).

### String interpolation

Split a string at the cursor and insert `todo`, or replace a selected Gleam
name with concatenation using that variable (since 1.9.0). Any arbitrary
substring can be selected and cut out for interpolation (since 1.15.0); it no
longer needs to be an identifier.

## Cases, operators, and record cleanup

### Operator corrections

When an operator has the wrong operand types, the compiler points at it and
suggests the appropriate operator; a code action applies the replacement
(since 1.10.0). The action also works inside guards (since 1.17.0), such as
changing string `+` to `<>`.

### Remove unreachable clauses

A quick fix deletes case clauses diagnosed as unreachable (since 1.13.0).

### Collapse and merge case clauses

Collapse an inner case into its enclosing case by combining their patterns
into flat clauses (since 1.13.0). Merge selected clauses with identical bodies
into one alternative pattern (since 1.14.0).

### Remove redundant record updates

When every record field is supplied explicitly, remove the spread and rewrite
the update as a constructor call (since 1.17.0):

```gleam
User(name: "Jak", likes: ["Gleam", "Dogs"])
```

### Constructor rename in constants

Constructor rename refactors update references inside constants correctly in
1.18.0; earlier behavior could produce incorrect code.
