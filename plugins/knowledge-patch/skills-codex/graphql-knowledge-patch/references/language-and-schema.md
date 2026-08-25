# GraphQL Language and Schema

This reference is organized around source parsing, schema-element addressing,
and schema validation.

## Unicode Source Text and Escapes

GraphQL source text is defined in Unicode scalar values through U+10FFFF.

- A valid UTF-16 surrogate pair represents one source character.
- An unpaired surrogate is invalid source text.
- Quoted strings accept variable-width brace-form Unicode escapes.
- A brace-form escape must encode a Unicode scalar value.

For example:

```graphql
mutation {
  send(message: "\u{1F4A9}")
}
```

Fixed-width escapes and valid surrogate-pair escapes remain accepted.
Brace-form escapes are preferred for supplementary characters because they
express the scalar directly.

Escape processing differs by string form:

- Interpret escapes in quoted strings.
- Do not interpret escape sequences in block strings.

Parsers and printers should test the boundary cases explicitly:

1. A literal scalar at U+10FFFF.
2. A supplementary character represented by a valid surrogate pair.
3. The same character represented by a brace-form escape.
4. Isolated high and low surrogates, which must fail.
5. Escape-looking text in a block string, which remains literal text.

Attribution: `september-2025-language` (2025-09-03).

## Schema Coordinates

Schema coordinates use a standalone, whitespace-free grammar to identify
schema elements uniquely. Supported forms include:

```text
Business
Business.name
Query.searchBusiness(criteria:)
@private
@private(scope:)
```

Interpret the forms as follows:

| Form | Identified element |
| --- | --- |
| `Type` | A type |
| `Type.member` | A field, input field, or enum value |
| `Type.field(argument:)` | A field argument |
| `@directive` | A directive |
| `@directive(argument:)` | A directive argument |

Coordinates may name built-in schema elements. The grammar intentionally does
not provide coordinates for every GraphQL concept:

- There is no coordinate for union membership.
- Meta-fields are not schema elements.
- Introspection types are not schema elements.

Do not parse coordinates as GraphQL executable documents or schema-definition
language snippets. Their standalone grammar rejects whitespace and identifies
the element by the coordinate's complete shape.

Useful parser tests include fields and input fields with the same member form,
enum values, field arguments, directive arguments, built-ins, whitespace
rejection, and attempts to express union membership.

Attribution: `september-2025-language` (2025-09-03).

## Deprecation Control Arguments

The built-in `@deprecated` directive's `reason` argument is non-null and keeps
its default. Introspection's `includeDeprecated` arguments follow the same
pattern: they are non-null and retain defaults.

This creates an important distinction:

- Omitting the argument is valid and selects its default.
- Explicitly supplying `null` is invalid.

Schema generators should omit an unspecified deprecation reason rather than
serialize it as `reason: null`. Introspection clients should likewise omit
`includeDeprecated` rather than bind it to `null`.

Attribution: `september-2025` (2025-09-03).

## Interface Field Deprecation Consistency

An implementing object may not deprecate a field unless the corresponding
interface field is also deprecated. A schema with object-only deprecation of
an interface field must be rejected.

For schema validation:

1. Find each object field that implements an interface field.
2. If the object field is deprecated, require the interface field to be
   deprecated.
3. Report object-only deprecation as a schema validation failure.

This rule permits the interface field and object field to be deprecated
together; it forbids presenting the interface contract as active while an
implementation declares the corresponding field deprecated.

Attribution: `september-2025` (2025-09-03).

## Stable Ordering

Implementations are encouraged to preserve the order of semantically unordered
collections when practical. Stable output reduces irrelevant reordering in
schema tools, generated artifacts, diffs, and human-facing displays.

Ordering remains non-semantic:

- Producers should preserve it where possible.
- Consumers must not assign meaning to it.
- Validation and execution must not depend on the observed order.

Treat ordering as a stability and presentation property, never as an implicit
priority or tie-break rule.

Attribution: `september-2025` (2025-09-03).
