---
name: graphql-knowledge-patch
description: GraphQL
version: GraphQL-over-HTTP draft 2026-07
license: MIT
metadata:
  author: Nevaberry
---



# GraphQL Knowledge Patch

Use this skill when implementing, reviewing, or troubleshooting GraphQL source
text, schemas, execution, clients, servers, or the HTTP transport. Determine the
specification and transport behavior implemented by the project, then open the
reference that matches the task.

Project schemas, implementation documentation, tests, and observed behavior are
authoritative when they differ from this guidance. Treat draft transport details
as a protocol contract shared by the client, server, gateway, and intermediaries.

## How to use this skill

1. Identify whether the task concerns the language, schema validation, execution,
   request encoding, response negotiation, or status handling.
2. Establish which GraphQL and GraphQL-over-HTTP rules the implementation claims
   to support.
3. Read the matching reference before changing parsers, validators, coercion,
   error propagation, media types, or status codes.
4. Test both success and failure paths at the boundary where behavior changes.
5. Prefer local implementation behavior when the project deliberately targets a
   different specification revision, and document that compatibility decision.

## Reference index

| Reference | Topics |
| --- | --- |
| [references/language-and-schema.md](references/language-and-schema.md) | Unicode source text, string escapes, schema coordinates, deprecation rules, stable ordering |
| [references/execution-and-coercion.md](references/execution-and-coercion.md) | Request extensions, executable descriptions, defaults, argument coercion, error propagation |
| [references/http-transport-and-negotiation.md](references/http-transport-and-negotiation.md) | `Accept`, response media types, GET parameters, JSON POST envelopes |
| [references/http-status-codes.md](references/http-status-codes.md) | Response-shape status rules and granular transport or request failure statuses |

## Breaking changes and deprecations

### Send an acceptable response type

- Conforming clients include `application/graphql-response+json` in `Accept`.
- When server support is uncertain, use the compatibility form:

  ```http
  Accept: application/graphql-response+json, application/json;q=0.9
  ```

- Servers support `application/graphql-response+json` and honor the highest-
  priority supported response type.
- When no offered type is acceptable, return `406` and stop or disregard
  `Accept`; prefer `406` when the request offers neither a supported type nor
  `application/json`.

### Do not pass null to non-null deprecation controls

- `@deprecated(reason:)` and introspection `includeDeprecated` arguments are
  non-null while retaining defaults.
- Callers may omit these arguments, but explicitly supplying `null` is invalid.

### Keep interface and object deprecations consistent

- An object field that implements an interface field cannot be deprecated unless
  the corresponding interface field is also deprecated.
- Reject schemas that deprecate only the implementing object's field.

### Distinguish variable and field-argument coercion failures

- Variable coercion failures are request errors and prevent execution.
- Input-coercion failures encountered while coercing a field's arguments are
  execution errors. Preserve partial-result handling and non-null propagation.

### Do not assume every GraphQL failure is HTTP 200

- For `application/graphql-response+json`, a non-null `data` requires `2xx`.
- If `data` is absent, use an appropriate `4xx` or `5xx`.
- The transport guidance distinguishes malformed transport, parse, validation,
  selection, coercion, authorization, timeout, and capacity failures.

## HTTP quick reference

### Encode requests precisely

- For GET, encode non-empty `variables` and `extensions` as JSON strings.
- Treat an empty optional GET parameter as omitted.
- `operationName=null` selects an operation literally named `null`; omit the
  parameter or send an empty value when no operation name is selected.
- In a JSON POST body, treat JSON `null` for an optional parameter as omission.
- Support UTF-8 `application/json` POST bodies. Reject a missing `Content-Type`
  with an appropriate `4xx` when enforcing the recommended behavior.
- Ignore unknown JSON properties. Treat a missing `query` or a parameter of the
  wrong type as a malformed transport request.
- A string `query` is transport-well-formed even if GraphQL parsing or validation
  subsequently fails.

### Interpret the negotiated media type

- With `application/graphql-response+json`, process the body as a GraphQL
  response regardless of HTTP status.
- Only that media type identifies a body as a GraphQL response independently of
  status.
- For a legacy client accepting only `application/json`, apply the same status
  rules, but send `Content-Type: application/json` only for `2xx` responses.
- If a failure prevents creation of a well-formed GraphQL response, use a suitable
  `4xx` or `5xx` and do not label the body
  `application/graphql-response+json`.

### Map response shapes before specific failures

| Response shape | Status guidance |
| --- | --- |
| `data` is non-null | Must use `2xx` |
| `data` exists and `errors` is absent | Should use `200` |
| `data` and `errors` both exist | Should use `294 Partial Success` |
| `data` is absent | Must use an appropriate `4xx` or `5xx` |

`294` is a custom, non-IETF recommendation. It also covers `data: null` with
`errors`; use it only with `application/graphql-response+json` under this
transport contract.

### Choose granular failure statuses

- `400`: invalid JSON or an unparseable GraphQL document.
- `405`: mutation over GET; also recommended for an unsupported method.
- `406`: no acceptable response media type.
- `408`: request production timeout.
- `413`: POST body too large.
- `414`: URI too large.
- `415`: unsupported request `Content-Type`.
- `422`: malformed GraphQL-over-HTTP envelope, validation failure, ambiguous
  operation selection, or variable coercion failure.
- `431`: request headers too large.
- Use an appropriate `401` or `403` for permission failures.
- Use an appropriate `5xx` for maintenance or load shedding; prefer `503`.

## Execution quick reference

### Coerce defaults into runtime values

- When an omitted variable or field argument has a default, coerce the default
  according to its declared input type before storing it or passing it to a
  resolver. This includes a default of `null`.
- For a custom scalar, pass the scalar's coerced runtime value, not its source
  literal.
- Implementations may cache coercion of schema argument defaults.

### Propagate errors once per response position

- Add only one error for a response position. If an execution error has already
  made the position `null`, propagating it through non-null parents does not add
  duplicate errors.
- If one item of `[T!]` fails, null the entire list position.
- Unresolved sibling positions may be cancelled during propagation.
- Set `data` to `null` when propagation crosses non-null positions all the way to
  the root.

### Keep executable descriptions non-semantic

- Descriptions and comments on operation, fragment, and variable definitions do
  not affect execution, validation, or the response.
- Consume them only for non-observable work such as logs and developer tooling.

### Reserve request metadata for extensions

- An execution request may carry an `extensions` map for implementation-specific
  information.
- Do not invent additional top-level request properties.
- Give extension keys unique prefixes to reduce collisions.

## Language and schema quick reference

### Parse Unicode scalar source text

- Treat source characters as Unicode scalar values through U+10FFFF.
- A valid UTF-16 surrogate pair represents one source character; an unpaired
  surrogate is invalid.
- Quoted strings accept variable-width scalar escapes such as `\u{1F4A9}`.
- Keep fixed-width escapes and valid surrogate-pair escapes accepted, while
  preferring brace-form escapes for supplementary characters.
- Interpret escapes only in quoted strings, never in block strings.

### Use schema coordinates for exact elements

- Coordinates are standalone and contain no whitespace.
- Use `Type`, `Type.member`, `Type.field(argument:)`, `@directive`, and
  `@directive(argument:)` forms.
- `Type.member` can identify a field, input field, or enum value.
- Coordinates can name built-ins, but cannot identify union membership.
- Meta-fields and introspection types are not schema elements and have no schema
  coordinates.

### Preserve stable order without assigning semantics

- Preserve the order of semantically unordered collections where practical to
  avoid needless churn in tools and human-readable output.
- Consumers must still not treat that order as semantically meaningful.

## Verification checklist

1. Exercise quoted and block strings separately, including supplementary scalar
   escapes and invalid unpaired surrogates.
2. Validate schema-coordinate parsing without accepting whitespace or unsupported
   element categories.
3. Test omitted and explicit-null deprecation arguments independently.
4. Test variable coercion before execution and field-argument coercion during
   execution as distinct error phases.
5. Verify one error per response position through lists and nested non-null fields.
6. Negotiate both preferred and legacy response media types, including an
   unacceptable `Accept` value.
7. Test empty, omitted, JSON-null, and wrong-type optional request parameters.
8. Assert response media type, response shape, and status code together.
9. Keep the custom `294` path explicit in client, proxy, monitoring, and server
   tests wherever that recommendation is adopted.
