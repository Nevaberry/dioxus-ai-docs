# GraphQL execution and coercion

Use this reference for execution-request shape, executable-document metadata,
default values, coercion error classification, partial results, and non-null
error propagation.

## Execution request shape

### Reserved extensions map

*Batch: september-2025-execution*

An execution request may contain an `extensions` map for implementation-specific
information. Implementations should not add unrelated top-level request
properties. Extension producers should prefix keys uniquely so independently
developed extensions are unlikely to collide.

Keep the distinction between the execution request and any transport envelope in
mind: this rule reserves implementation-specific execution metadata for
`extensions`; it does not define arbitrary new top-level fields.

## Executable document metadata

### Descriptions and comments are non-semantic

*Batch: september-2025-execution*

Descriptions and comments attached to operation, fragment, and variable
definitions have no observable effect on execution, validation, or the response.

Tools may consume them for non-observable purposes such as logging, editor
features, or developer documentation. Do not make resolver selection, validation
results, response content, or any other observable behavior depend on them.

## Runtime coercion

### Coerce omitted defaults before use

*Batch: september-2025-execution*

When a variable or field argument is omitted and has a default, coerce that
default according to the declared input type before storing the value or passing
it to a resolver. The rule also applies when the declared default is `null`.

This matters for custom scalars. Execution must receive the scalar's coerced
runtime value rather than the source literal that appeared in the variable or
argument definition. An implementation may cache coercion of schema argument
defaults, provided the cached result has the same runtime semantics.

### Classify coercion errors by phase

*Batch: september-2025-execution*

A variable coercion failure is a request error. It occurs before execution and
prevents the operation from executing.

An input-coercion error encountered while coercing a field's arguments is an
execution error. It participates in normal partial-result behavior and non-null
propagation. Do not promote that field-local failure into a pre-execution request
error.

Tests should cover the same invalid input shape in both positions so the request
and execution phases cannot accidentally share the wrong error policy.

## Response-position error propagation

### Report one error per position

*Batch: september-2025-execution*

Add only one error for a response position. When an execution error has already
made that position `null`, propagating the same failure through non-null parents
must not create duplicate errors for the position.

### Lists, siblings, and root propagation

*Batch: september-2025-execution*

If an item of a `[T!]` result fails, the non-null item type causes the entire list
position to become null. Work for unresolved sibling response positions may be
cancelled while the error propagates.

When every response position from the failure through the root is non-null,
propagation makes top-level `data` null. Preserve the original execution error
without adding another error at each parent crossed along the way.
