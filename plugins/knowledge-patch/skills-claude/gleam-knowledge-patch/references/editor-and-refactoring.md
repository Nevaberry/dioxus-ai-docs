# Editor and refactoring

## Navigation, references, and display

### Find references and rename

Since 1.8.0, rename handles local variables and function arguments and updates
all their uses. Other Gleam symbols were outside that first iteration's scope.

Since 1.10.0, find-references locates every use of a type or value throughout a
project, and renaming types and values updates cross-module references.

Since 1.15.0, module rename can start on any qualifier use, not just its import;
it adds an import alias and updates qualifiers throughout the file. Find
references and rename also work for variables bound in string-prefix patterns.

Since 1.18.0, constructor renames update references inside constants correctly.

### Navigation and hover

- Since 1.9.0, go-to-type-definition on an expression presents definitions for
  the types of values used in that expression.
- Since 1.9.0, hovering an imported type or value's module qualifier shows that
  module's documentation.
- Since 1.11.0, hover, completion, and go-to-definition work in constants.
- Since 1.15.0, rename, go-to-definition, hover, and find-references work in
  guards.
- Since 1.17.0, `textDocument/documentHighlight` lets an editor highlight all
  references to the variable under the cursor.
- Since 1.17.0, hovering the spread value in a record update lists unchanged
  fields.

Since 1.17.0, warnings print types with the qualifier or import alias visible in
the source file, not always the canonical module name.

## Generating functions, types, and modules

### Missing functions

Since 1.8.0, invoking generate-function on an undefined call inserts a function
with inferred argument and return types and a `todo` body.

```gleam
fn to_string(pokemon: Pokemon) -> String {
  todo
}
```

Since 1.11.0, generated parameter names come from argument labels and local
variable names rather than generic placeholders.

Since 1.13.0, the action works on a missing qualified call and edits the imported
module with a public function outline and inferred annotations.

### Types and variants

Since 1.11.0, an action can add a missing custom-type variant inferred from its
use, including field types and labels.

Since 1.15.0, a quick fix adds an undeclared type variable used by a custom-type
variant to the type header.

```gleam
pub type Store(inner_type) {
  Store(name: String, data: inner_type)
}
```

### Missing modules

Since 1.17.0, an import of a nonexistent module in the package can create the
corresponding source file. For example, `import wobble/woo` in
`src/wiggle.gleam` can create `src/wobble/woo.gleam`.

## Pattern-match actions

### Exhaustive matches

Since 1.8.0, the language server can add a `case` for a local variable or
function argument with every pattern required to exhaustively match its type.

```gleam
case result {
  Ok(value) -> todo
  Error(value) -> todo
}
```

Since 1.7.0, an inexhaustive `let` binding can be replaced by a `case` with
missing patterns inserted as `todo` branches.

Since 1.11.0, inexhaustive-case diagnostics show record labels in missing
patterns, and the insert-missing-clauses action includes those labels.

Since 1.13.0, pattern-match generation handles lists and variables introduced
by other patterns. When invoked on a variable bound by an enclosing case clause,
it expands that clause into specialised exhaustive patterns.

Since 1.15.0, add-missing-patterns uses a catch-all for an internal type rather
than exposing its variants. Field completions are omitted, and inexhaustive
diagnostics do not reveal the internal structure.

Since 1.17.0, the action can expand a discard nested in a case pattern into
exhaustive alternatives.

```gleam
Ok(_) -> todo
// Becomes:
Ok([]) -> todo
Ok([first, ..rest]) -> todo
```

### Expanding and simplifying patterns

Since 1.10.0, an action replaces `..` in a custom-type pattern with every field
that it ignored.

```gleam
let Pokemon(..) = pokemon
// Becomes:
let Pokemon(id:, name:, moves:) = pokemon
```

Since 1.13.0, a quick fix removes case clauses already diagnosed as unreachable.

Since 1.14.0, selected case clauses with identical bodies can merge into one
alternative pattern.

```gleam
case user {
  Admin(name:, ..) | Guest(name:, ..) -> todo
  _ -> todo
}
```

Since 1.13.0, nested case expressions can collapse into equivalent flat clauses
whose patterns combine the outer and inner cases.

## Labels and completions

### Fill and add labels

Since 1.8.0, fill-labels handles partially supplied calls, inserting missing
labelled arguments as `todo`.

```gleam
string.replace("wibble", each: todo, with: todo)
```

Since 1.11.0, fill-labels adds omitted fields to record patterns while retaining
already supplied fields.

Since 1.13.0, an action labels positional arguments when the function parameter
or constructor field has a label.

```gleam
User(first_name, "Cavalieri", ["gleam"])
// Becomes:
User(first_name:, last_name: "Cavalieri", likes: ["gleam"])
```

Since 1.15.0, fill-labels inserts an in-scope variable when its name and type
match a label and leaves `todo` only if there is no suitable variable.

Since 1.17.0, fill-labels works in constants and uses `todo` for missing fields.

### Context-aware completion

Since 1.16.0, completion suggests labelled fields while writing a record update
and suppresses value completions while editing a qualified type.

Since 1.17.0, an unknown unqualified value prompts the compiler to search
already imported modules and suggest matching qualified values, such as
`io.println` when `gleam/io` is imported.

## Generating encoders and decoders

### Dynamic decoders

Since 1.7.0, a code action on a custom-type header generates a decoder using
`gleam/dynamic/decode`.

```gleam
import gleam/dynamic/decode

pub type Person {
  Person(name: String, age: Int)
}

fn person_decoder() -> decode.Decoder(Person) {
  use name <- decode.field("name", decode.string)
  use age <- decode.field("age", decode.int)
  decode.success(Person(name:, age:))
}
```

Since 1.9.0, decoder generation supports multi-variant types. It reads a string
field named `"type"`, matches lower-case variant names such as `"adult"` and
`"child"`, decodes that variant's fields, and leaves an unknown discriminator
as a `decode.failure` placeholder to complete.

Since 1.15.0, decoder generation supports `Nil` and supplies best-effort zero
values for `decode.failure`.

### JSON encoders

Since 1.9.0, an action on a custom type generates an encoder with `gleam_json`.

```gleam
import gleam/json

fn encode_person(person: Person) -> json.Json {
  json.object([
    #("name", json.string(person.name)),
    #("age", json.int(person.age)),
  ])
}
```

Since 1.10.0, the generated encoder first performs a full-field pattern match.
Adding a field to the type then prevents compilation until the encoder is
updated, instead of silently omitting the field.

## Call and `use` refactors

Since 1.7.0, actions convert a `use` expression to an equivalent callback call
and back.

Since 1.9.0, actions convert ordinary calls to pipeline syntax and back.
Selecting an argument before conversion allows an argument other than the first
to become the piped value.

```gleam
list.map([1, 2, 3], double)
[1, 2, 3] |> list.map(double)
```

Since 1.16.0, actions switch between a single-call anonymous function and its
equivalent direct function reference.

```gleam
fn(value) { int.absolute_value(value) }
int.absolute_value
```

## Extraction actions

Since 1.10.0, extract-constant lifts a selected non-dynamic expression into a
module constant and replaces the selection with its name.

Since 1.13.0, extract-function turns a selected expression into a typed private
function and replaces it with a call. The generated name is `function`; rename
it to a meaningful name.

Since 1.15.0, extracting an anonymous function extracts its body and passes
captured values as parameters. The action can also extract the initial
expression of a pipeline into a variable.

```gleam
list.map(numbers, function(_, multiplier))

fn function(number: Int, multiplier: Int) -> Int {
  number * multiplier
}
```

Since 1.16.0, extract-function can lift consecutive selected pipeline steps into
a function and leave a call in the pipeline. On an assignment, it can extract
the assigned expression instead of the enclosing assignment.

## String interpolation

Since 1.9.0, an action splits a string at the cursor and inserts `todo`, or
replaces a selected valid Gleam name with an interpolation.

```gleam
"wibble " <> todo <> " wobble"
"wibble " <> wobble <> " woo"
```

Since 1.15.0, interpolate-string can cut out any selected substring; it no
longer needs to be a valid Gleam identifier.

## Annotations, operators, and cleanup

### Type annotations

Since 1.14.0, one action adds inferred type annotations to every top-level
constant and function in a module.

Since 1.16.0, an action replaces `_` in a type annotation with the inferred
type at that position.

```gleam
fn identity(value: Int) -> _ { value }
// Becomes:
fn identity(value: Int) -> Int { value }
```

### Operator corrections

Since 1.10.0, when an operator has the wrong operand types, the compiler points
at it and recommends the appropriate operator; the language server can apply
the correction. Since 1.17.0, this works in case guards too, such as replacing
string `+` with `<>`.

### Import and qualifier cleanup

Since 1.11.0, remove-unused-imports removes unused unqualified types and values
from grouped imports while retaining used names.

The language server can add or remove qualifiers while updating imports and all
uses in a module. Qualifying supports all types and values; unqualifying is
limited to types and custom-type variant constructors.

### Record cleanup

Since 1.17.0, an action removes a record spread when every field is explicitly
provided and rewrites the expression as a constructor call.

```gleam
User(..lucy, name: "Jak", likes: ["Gleam", "Dogs"])
// Becomes:
User(name: "Jak", likes: ["Gleam", "Dogs"])
```

## Editor protocol features

Since 1.15.0, the language server implements `textDocument/foldingRange` for
contiguous import blocks and multiline top-level functions, custom types,
constants, and type aliases.
