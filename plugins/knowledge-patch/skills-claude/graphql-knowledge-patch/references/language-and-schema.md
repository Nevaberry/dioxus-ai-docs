# GraphQL language and schema

Use this reference for source parsing, schema tooling, schema coordinates,
deprecation validation, introspection arguments, and deterministic presentation.

## Source text and string escapes

### Unicode scalar source text

*Batch: september-2025-language*

GraphQL source characters are Unicode scalar values through U+10FFFF. When the
source representation is UTF-16, a valid surrogate pair represents one source
character. An unpaired surrogate does not encode a scalar value and is invalid.

Do not count the two UTF-16 code units of a valid surrogate pair as two GraphQL
source characters. Parser validation should reject lone high and low surrogates.

### Variable-width Unicode escapes

*Batch: september-2025-language*

Quoted strings accept brace-form, variable-width Unicode escapes. The enclosed
value must encode a Unicode scalar value:

```graphql
mutation {
  send(message: "\u{1F4A9}")
}
```

Fixed-width escapes and valid surrogate-pair escapes remain valid. Prefer the
brace form for supplementary characters because it expresses the scalar value
directly.

Escape processing applies only to quoted strings. A sequence resembling an
escape inside a block string remains literal block-string content.

## Schema coordinates

### Coordinate grammar and supported elements

*Batch: september-2025-language*

A schema coordinate is a standalone, whitespace-free identifier for one schema
element. Supported forms include:

```text
Business
Business.name
Query.searchBusiness(criteria:)
@private
@private(scope:)
```

Interpret the forms as follows:

- `Type` identifies a type.
- `Type.member` identifies a field, input field, or enum value.
- `Type.field(argument:)` identifies a field argument.
- `@directive` identifies a directive.
- `@directive(argument:)` identifies a directive argument.

Coordinates may identify built-in schema elements. There is no coordinate for a
union membership relation. Meta-fields and introspection types are not schema
elements, so they do not have schema coordinates.

Use the coordinate grammar as its own grammar rather than parsing it as ordinary
GraphQL source. In particular, do not admit whitespace between its components.

## Deprecation validation

### Non-null control arguments with defaults

*Batch: september-2025*

The built-in `@deprecated` directive's `reason` argument is non-null and retains
its default. The introspection `includeDeprecated` arguments are likewise
non-null and retain their defaults.

Because a default still exists, callers may omit these arguments. Explicitly
supplying `null` is invalid. Tests and generated queries should distinguish
omission from an explicit null value.

### Interface field consistency

*Batch: september-2025*

An object type may deprecate a field inherited from an interface only when the
corresponding interface field is also deprecated. Reject a schema that deprecates
the implementing object's field while leaving the interface field active.

This check applies to schema validation rather than merely to presentation in
introspection or documentation.

## Stable presentation order

### Preserve order where possible

*Batch: september-2025*

Implementations are encouraged to preserve the existing order of semantically
unordered collections when practical. Stable order reduces needless reordering
in generated output, diffs, developer tools, and human review.

The order remains non-semantic. Consumers must not infer meaning, priority, or
execution behavior from it, even when a producer reliably preserves it.
