# Editor and refactoring

## Contents

- [Navigation, hover, and completion](#navigation-hover-and-completion)
- [References and rename](#references-and-rename)
- [Generating definitions and codecs](#generating-definitions-and-codecs)
- [Patterns and labels](#patterns-and-labels)
- [Extraction and structural refactoring](#extraction-and-structural-refactoring)
- [Cleanup and migration actions](#cleanup-and-migration-actions)
- [Running the language server](#running-the-language-server)

## Navigation, hover, and completion

### Richer hover and navigation

Since 1.7.0, hover includes types and documentation for patterns and function labels. Since 1.9.0, go-to-type-definition on an expression presents the definitions of the types of values used by that expression.

Since 1.11.0, hover, completion, and go-to-definition work in module constant expressions. Generate-function and qualify/unqualify actions also work in constants as of 1.14.0.

Since 1.13.0, go-to-definition, rename, and related actions work from every alternative of a `case` pattern, including names after `|`. Hovering a record-access field shows that field's documentation.

### Public aliases and opaque internals

Since 1.13.0, hovers and annotation actions prefer an accessible public type alias instead of exposing the aliased internal type name. Generated Hex documentation follows the same rule.

Since 1.15.0, inexhaustive-pattern errors do not expose the structure of an internal type, field completions are suppressed, and add-missing-patterns inserts a catch-all rather than revealing variants.

### Context-aware completion and hover

Since 1.16.0, record updates complete labelled fields, while completion after a qualified type excludes values.

Since 1.17.0, hovering the spread value in a record update lists the fields left unchanged, making the remaining available labels visible without navigating to the record definition.

The server also implements `textDocument/documentHighlight`, so editors can highlight every reference to the selected variable in the current document.

## References and rename

### Local and project-wide symbols

Since 1.8.0, rename updates a local variable or function argument and all of its uses. Since 1.10.0, find-references and rename operate project-wide for types and values, including uses across module boundaries.

### Module aliases from usages

Since 1.15.0, invoke module rename on any module usage. The action adds an alias to the import and updates qualified type and value references to use it.

## Generating definitions and codecs

### Missing functions and modules

Since 1.8.0, a generate-function action on an unresolved call creates a definition with inferred argument and return annotations and a `todo` body.

Since 1.11.0, generated parameter names come from call labels and argument variables. A call such as `remove(each: number, in: list)` generates labelled parameters named `number` and `list`.

Since 1.13.0, generating from a missing qualified call such as `maths.subtract(2, 1)` adds a public typed skeleton to the imported module. Since 1.17.0, an import of a nonexistent module can create its source file; `import wobble/woo` in a `src` module creates `src/wobble/woo.gleam`.

### Custom type variants and parameters

Since 1.11.0, when an unknown variant's owning custom type can be inferred, generate the variant in that type with inferred field types and labels.

Since 1.15.0, when a variant uses an undeclared type variable, add it to the custom type header; for example, change `pub type Store` to `pub type Store(inner_type)`.

### Dynamic decoders

Since 1.7.0, invoke decoder generation on a custom type header to create a `gleam/dynamic/decode` function with decoders for the type's fields.

Since 1.9.0, the action supports multi-variant types. It decodes a string `"type"` field, branches on lowercased variant names, and decodes each variant's fields.

Since 1.15.0, generation handles `Nil` and produces best-effort zero values for `decode.failure`.

### JSON encoders

Since 1.9.0, generate an encoder using `gleam/json` from a custom type. Record-like variants become `json.object` values whose fields use the matching encoders.

Since 1.10.0, generated encoders destructure every custom-type field without `..`. Adding a field therefore creates a compile error until the encoder is updated instead of silently omitting the new data.

### Type-variable names and annotations

Since 1.13.0, add-annotations and generate-function choose type-variable names relative to the function being edited, without reserving names used elsewhere in the module.

Since 1.14.0, add inferred annotations to every top-level constant and function in a module with one action.

Since 1.16.0, replace `_` in a type annotation with its inferred type, such as changing `Result(_, Error)` to `Result(User, Error)`.

## Patterns and labels

### Generate exhaustive matches

Since 1.8.0, the pattern-match action on a local variable or argument inserts a `case` with all patterns required for exhaustiveness and `todo` branches.

Since 1.13.0, the action generates empty and non-empty branches for lists and works on variables introduced by `let` and `case` patterns. For a binding in an existing clause, it specialises that clause into the variable's variants instead of nesting another `case`.

Since 1.17.0, invoke the action on a discard nested in a `case` pattern. For example, an `Ok(_)` holding a list can expand to `Ok([])` and `Ok([first, ..rest])`.

### Convert an inexhaustive binding

Since 1.7.0, an inexhaustive `let` diagnostic offers a replacement `case` with the missing patterns and `todo` placeholders.

### Add and expand fields and labels

Since 1.8.0, fill-labels works on partial calls, adding missing labelled arguments with `todo` values.

Since 1.10.0, fill-unused-fields expands `..` in a pattern into every ignored field, such as changing `Pokemon(..)` to `Pokemon(id:, name:, moves:)`.

Since 1.11.0, fill-labels works on record patterns, changing forms such as `Person(age:)` to `Person(age:, name:, job:)`.

Since 1.13.0, add-omitted-labels can label arguments already present rather than inserting missing arguments.

```gleam
User(first_name, "Cavalieri", ["gleam"])
// becomes
User(first_name:, last_name: "Cavalieri", likes: ["gleam"])
```

Since 1.17.0, fill-labels works on constant record constructors and uses constant `todo` expressions for missing fields.

### Reshape case expressions

Since 1.13.0, remove a clause diagnosed as unreachable with a quick fix. Another action collapses a nested `case` into its enclosing `case`, flattening clauses while preserving behavior.

Since 1.14.0, merge selected clauses with identical bodies into one alternative pattern such as `Admin(..) | Guest(..) -> todo`.

## Extraction and structural refactoring

### `use`, captures, and pipelines

Since 1.7.0, convert a `use` expression to its callback-based function call and back again. The server can also expand a capture such as `int.add(_, 11)` into `fn(value) { int.add(value, 11) }`.

Since 1.9.0, convert a normal call to pipeline syntax or a pipeline back to a call. Select a non-first argument before conversion to pipe that position.

Since 1.16.0, replace a single-call anonymous function with its direct function reference and restore the anonymous form later.

```gleam
[-1, -2, -3] |> list.map(fn(value) { int.absolute_value(value) })
// becomes: [-1, -2, -3] |> list.map(int.absolute_value)
```

### Extract variables and constants

Since 1.7.0, extract the expression at the cursor into a `let` binding and replace the expression with that variable.

Since 1.10.0, lift a non-dynamic expression into a module constant and replace its original occurrence.

### Extract functions

Since 1.13.0, replace selected code with a call and move the expression into a new private function with inferred parameter and return types. The initial name is `function`; rename it afterward.

Since 1.15.0, extracting an anonymous function moves its body into the new named function and passes captured values as parameters rather than extracting the anonymous expression itself.

Since 1.16.0, extraction can move selected steps from the middle of a pipeline into a function. When invoked on an assignment, it extracts the assigned expression and replaces the value with a call.

### String interpolation and blocks

Since 1.9.0, invoke interpolation inside a string to split it and insert `<> todo <>`; selecting a valid name inserts that variable instead.

```gleam
"wibble wobble"
// selecting `wobble` becomes:
"wibble " <> wobble
```

Since 1.10.0, wrap an assignment value or case-clause value in a block, ready for more expressions. Since 1.12.0, remove a block containing only one expression, replacing `{ "Hello" }` with the expression.

## Cleanup and migration actions

### Remove debug and unused code

Since 1.10.0, remove every `echo` expression from the current module in one action.

Since 1.11.0, remove-unused-imports deletes unused unqualified types and values from grouped imports while retaining used members.

### Simplify records and cases

Since 1.17.0, remove a record spread when every field is already supplied, rewriting `User(..old, name: new_name, likes: new_likes)` as a direct constructor.

Flatten a tuple-valued `case` subject and tuple patterns into Gleam's equivalent multiple-subject form:

```gleam
case a, b {
  1, 2 -> todo
  _, _ -> todo
}
```

### Fix warnings and deprecated code

Bind an intentionally ignored failure result to `_` to silence an unused-result warning, though handling the failure is preferable:

```gleam
let _ = function_which_can_fail()
```

Remove `opaque` from a private custom type because opacity has no effect outside a public API.

Use `gleam fix` to rewrite deprecated code when an automatic supported migration is available:

```sh
gleam fix
```

## Running the language server

The language server ships in the main executable. Run it from a project root for a generic editor:

```sh
gleam lsp
```

With `nvim-lspconfig`, use the API matching the editor version:

```lua
vim.lsp.enable("gleam") -- Neovim 0.11+, nvim-lspconfig 2.1+
require("lspconfig").gleam.setup({}) -- Neovim 0.10 and earlier
```

One editor session can contain multiple Gleam projects. The server associates each file with its project, uses unsaved buffer contents, and follows the configured target. It performs no code generation or Erlang/Elixir compilation, so opening a project cannot execute its code. Outside a Gleam project, only formatting is available.
