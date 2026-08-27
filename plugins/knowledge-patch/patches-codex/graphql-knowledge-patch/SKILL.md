---
name: graphql-knowledge-patch
description: GraphQL
version: "GraphQL-over-HTTP draft 2026-07"
license: MIT
metadata:
  author: Nevaberry
---



# GraphQL Knowledge Patch

Use this skill when implementing, reviewing, or debugging GraphQL schemas,
execution engines, clients, servers, gateways, or GraphQL-over-HTTP behavior.
Start with the compatibility checks below, then open the topic reference that
matches the work.

## Working Method

1. Identify whether the change concerns source syntax, schema validation,
   execution, or HTTP transport.
2. Inspect the implementation's declared GraphQL specification and
   GraphQL-over-HTTP support before changing behavior.
3. Apply the breaking and validation checks before adopting convenience
   behavior.
4. Keep transport errors distinct from GraphQL request and execution errors.
5. Test custom-scalar coercion, non-null propagation, and content negotiation
   explicitly when they are in scope.
6. Consult the repository's code, tests, and pinned dependencies for
   implementation-specific behavior.

## Reference Index

| Reference | Topics |
| --- | --- |
| [language-and-schema.md](references/language-and-schema.md) | Unicode source text, escapes, schema coordinates, deprecation validation, stable ordering |
| [execution.md](references/execution.md) | Request extensions, executable descriptions, default coercion, argument errors, response propagation |
| [http-transport.md](references/http-transport.md) | Media negotiation, GET and POST envelopes, response status mapping, granular failures |

## Breaking and Validation Checks

### Do not pass explicit null to non-null control arguments

The built-in `@deprecated` directive's `reason` argument and introspection's
`includeDeprecated` arguments are non-null but retain defaults. Omission is
valid; explicitly supplying `null` is invalid.

Audit schema generation and introspection clients for patterns such as:

```graphql
field: String @deprecated(reason: null)
```

and:

```graphql
query {
  __type(name: "Business") {
    fields(includeDeprecated: null) {
      name
    }
  }
}
```

Omit these arguments to select their defaults.

### Enforce interface deprecation consistency

An object field cannot be deprecated unless the corresponding interface field
is also deprecated. Reject a schema that deprecates only the implementing
object's version of an interface field.

When deprecating an implemented field:

1. Deprecate the interface field.
2. Deprecate the corresponding fields on implementing objects as needed.
3. Re-run schema validation before publishing the schema.

### Classify coercion failures by phase

Variable coercion failures are request errors and prevent execution. Input
coercion failures encountered while coercing a field's arguments are execution
errors. The latter participate in partial-result handling and non-null
propagation.

Do not collapse both paths into one pre-execution error category. Tests should
assert whether resolvers run, whether partial `data` is present, and where
errors are reported.

### Negotiate the preferred response media type

A conforming client includes `application/graphql-response+json` in `Accept`.
When server support is unknown, send:

```http
Accept: application/graphql-response+json, application/json;q=0.9
```

Servers support the preferred media type and select the highest-priority
supported type. If no response type is acceptable, returning `406` and
stopping is the recommended behavior in the cases detailed by the transport
reference.

### Do not assume every GraphQL response uses status 200

For `application/graphql-response+json`, response shape determines the status
class:

| Response shape | Status rule |
| --- | --- |
| `data` is non-null | Must be `2xx` |
| `data` exists and `errors` is absent | Should be `200` |
| `data` and `errors` both exist | Should be `294 Partial Success` |
| `data` is absent | Must be an appropriate `4xx` or `5xx` |

The custom `294` recommendation includes `data: null` with `errors`. A failure
that prevents formation of a well-formed GraphQL response uses an appropriate
`4xx` or `5xx` and must not claim the preferred GraphQL response media type.

## Language and Schema Quick Reference

### Encode supplementary characters with scalar escapes

GraphQL source characters are Unicode scalar values through U+10FFFF. In
quoted strings, prefer variable-width brace escapes for supplementary
characters:

```graphql
mutation {
  send(message: "\u{1F4A9}")
}
```

Fixed-width escapes and valid surrogate-pair escapes remain accepted. An
unpaired surrogate is invalid. Escape sequences are interpreted in quoted
strings, not block strings.

### Use the schema-coordinate grammar

Schema coordinates are whitespace-free identifiers for schema elements:

```text
Business
Business.name
Query.searchBusiness(criteria:)
@private
@private(scope:)
```

`Type.member` can identify a field, input field, or enum value. Parenthesized
forms identify field or directive arguments. There is no coordinate for union
membership, and meta-fields and introspection types are not schema elements.

### Preserve stable order without assigning semantics

Implementations should retain the order of semantically unordered collections
where practical. This reduces needless churn for tools and people, but
consumers must not treat the observed order as meaningful.

## Execution Quick Reference

### Reserve top-level request fields

An execution request may include an `extensions` map for
implementation-specific information. Do not invent other top-level request
properties. Give extension keys unique prefixes to reduce collisions.

### Keep executable descriptions non-semantic

Descriptions and comments on operations, fragments, and variable definitions
must not affect execution, validation, or response content. They may support
logging or developer tooling only when that use has no observable execution
effect.

### Coerce defaults before runtime use

When an omitted variable or field argument has a default, including `null`,
coerce the default according to its declared input type before storing it or
passing it to a resolver. For custom scalars, use the coerced runtime value,
not the source literal. Schema argument-default coercion may be cached.

### Report one error per response position

If an execution error already made a response position `null`, propagation
through non-null parents does not add duplicate errors. A failed item in
`[T!]` nulls the entire list position; unresolved siblings may be cancelled.
If non-null propagation reaches the root, `data` becomes `null`.

## HTTP Request Quick Reference

### Interpret optional parameters carefully

For GET requests, non-empty `variables` and `extensions` values are JSON
strings. An empty optional parameter means omission. The URL value
`operationName=null` selects an operation literally named `null`; omit the
parameter or use an empty value to select no operation name.

In a JSON POST envelope, an optional parameter whose JSON value is `null` is
treated as omitted.

### Separate envelope validity from document validity

Servers must support UTF-8 `application/json` POST bodies. Unknown JSON
properties are ignored. A missing `query` or a parameter of the wrong type
makes the transport request malformed.

A string-valued `query` is transport-well-formed even if the contained GraphQL
document later fails parsing or validation. A POST without `Content-Type`
should receive an appropriate `4xx`.

### Use phase-specific failure statuses

Common mappings include:

- `400` for invalid JSON or an unparseable GraphQL document.
- `405` for a mutation over GET, and preferably for an unsupported method.
- `406` when no response media type is acceptable.
- `408`, `413`, `414`, and `431` for request-production timeout, an oversized
  body, an oversized URI, and oversized headers.
- `415` for an unsupported request media type.
- `422` for malformed envelopes, validation failures, ambiguous operation
  selection, or variable coercion failures.
- An appropriate `401` or `403` for permission failures.
- An appropriate `5xx` for maintenance or load shedding, preferably `503`.

Open [http-transport.md](references/http-transport.md) before implementing
status handling; the media type determines whether a body is safely
recognizable as a GraphQL response independently of status.

## Review Checklist

- Validate non-null deprecation and introspection control arguments.
- Validate interface and implementing-object deprecations together.
- Test quoted-string scalar escapes separately from block strings.
- Parse schema coordinates with their standalone grammar.
- Coerce omitted defaults to runtime values before resolver invocation.
- Distinguish variable coercion from field-argument coercion failures.
- Deduplicate errors while propagating through non-null response positions.
- Namespace request-extension keys and reject invented top-level fields.
- Negotiate response media types before selecting response status behavior.
- Treat GET and POST optional-parameter omission rules consistently.
- Keep transport, GraphQL parsing, validation, and execution failures distinct.
- Preserve stable collection order only as a presentation property.
