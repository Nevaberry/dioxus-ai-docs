# GraphQL Execution

This reference covers execution-request extensibility, non-semantic executable
text, input coercion, and response-position error propagation.

## Reserved Request Extensions

An execution request may carry an `extensions` map for
implementation-specific information. The map is the designated extension
point.

- Do not invent additional top-level request properties.
- Put implementation-specific values under `extensions`.
- Prefix extension keys uniquely to reduce collisions between implementations
  and integrations.

For example, prefer a namespaced entry such as:

```json
{
  "query": "query { business { name } }",
  "extensions": {
    "example.trace": {
      "requestId": "abc123"
    }
  }
}
```

The exact prefix is implementation-defined; its purpose is collision
avoidance, not GraphQL semantics.

Attribution: `september-2025-execution` (2025-09-03).

## Executable Descriptions and Comments

Descriptions and comments may appear on operation, fragment, and variable
definitions. They are non-semantic and must have no observable effect on:

- Execution.
- Validation.
- The response.

Implementations may consume them for non-observable uses such as logging and
developer tooling. They must not change field selection, variable behavior,
resolver invocation, error generation, or returned data.

A conformance test can execute equivalent documents with and without such
descriptions or comments and assert identical validation and response
behavior.

Attribution: `september-2025-execution` (2025-09-03).

## Runtime Coercion of Default Values

When a variable or field argument is omitted and has a default, coerce that
default according to the declared input type before storing or using it. This
also applies when the default literal is `null`.

The required sequence is:

1. Determine that the variable or argument was omitted.
2. Select its declared default.
3. Coerce the default through the declared input type.
4. Store the coerced value or pass it to the resolver.

This matters especially for custom scalars. Execution must use the scalar's
coerced runtime representation, not its source literal representation.

For schema argument defaults, an implementation may cache the result of
coercion. A cache must preserve the same runtime value and error behavior as
coercing the declared default normally.

Test omitted defaults separately from explicitly supplied values, and include
custom scalars whose literal representation differs from their runtime value.

Attribution: `september-2025-execution` (2025-09-03).

## Coercion Failure Classification

The phase where coercion fails determines the error category.

| Failure | Classification | Execution consequence |
| --- | --- | --- |
| Variable coercion | Request error | Prevents execution |
| Field-argument input coercion | Execution error | Participates in partial results and non-null propagation |

A variable coercion failure occurs while preparing the operation and remains a
request error. No field execution begins.

An input-coercion error encountered while coercing a field's arguments occurs
during field execution. Report it as an execution error at that response
position. Other positions may still produce partial data unless non-null
propagation removes it.

Do not convert a field-argument coercion failure into a request-wide
pre-execution failure merely because both paths use input coercion logic.

Attribution: `september-2025-execution` (2025-09-03).

## Response-Position Error Propagation

Add only one error per response position. If a position is already `null`
because of a reported execution error, propagating the failure through
`Non-Null` parents must not add duplicate errors for that position.

For a list of type `[T!]`, failure of one item has these effects:

1. The failed non-null item cannot remain `null` within the list.
2. The entire list response position becomes `null`.
3. Unresolved sibling positions may be cancelled.
4. Propagation continues if the list position itself is non-null.

When every position from the failure up to the operation root is non-null,
propagation reaches the root and the response's `data` value becomes `null`.

Tests should assert:

- One reported error for the original response position.
- No additional errors solely from propagation through non-null parents.
- Nullification of the full `[T!]` list position after an item failure.
- Optional cancellation of unresolved siblings without fabricated errors.
- `data: null` when propagation reaches the root.

Attribution: `september-2025-execution` (2025-09-03).
