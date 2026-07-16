# Stores, Actions, and Submissions

## Action lifecycle and names

Actions support `onComplete`, expose errors, and return fully processed
responses. Use these contracts rather than adding a separate completion or
response-normalization layer around every action.

Navigation clears only completed actions. Do not assume an unfinished action
disappears merely because the location changed.

User-supplied `name` values are honored by both `action` and `createAsync`.
For an action, the supplied name is hashed instead of being discarded in favor
of the fixed name `mutate`.

## Submission and route-parameter types

Import `Submission` from the package top level.

`SearchParams` is an exported type. Its values can be optional and can contain
arrays; `Params` values can likewise be optional. The object returned by
`useParams()` supports the `in` operator for presence checks.

These widened shapes matter when an action or submission reconstructs route
state. Do not narrow them to required scalar strings without application-level
validation.

## Form bodies

Form actions default to URL-encoded bodies. `URLSearchParams` is accepted when
the encoding is not `multipart/form-data`.

Choose the body representation to match the encoding:

- Use URL-encoded form behavior by default.
- Pass `URLSearchParams` for a compatible non-multipart request.
- Use the appropriate multipart body when the encoding is
  `multipart/form-data`; do not pass `URLSearchParams` in that case.

## Revalidation

An empty string or an empty array means no revalidation. Preserve that
sentinel behavior instead of interpreting either value as a request to
revalidate every query.

## Response filtering and redirects

Response helpers now return `Response` objects. Both the former `cache` helper
and `action` filter those results; after migrating the data helper, apply the
same behavior to `query`-based code.

Handle the associated response details explicitly:

- Forward an absolute redirect produced inside a server-side `cache` call (or
  its `query` replacement) to the client.
- Preserve headers through `query()`'s `handleResponse()`.
- Consume the fully processed response returned by an action.
- Preserve multiple `Set-Cookie` headers on SolidStart 2 alpha redirect
  responses.

## Single-flight mutations

Solid Router can pair the `solidstart-1.0.0` server-function transport with a
mutation to begin loading the destination page immediately after the update.
It can stream that destination data in the mutation response while the client
performs the redirect.

Use this single-flight path to combine:

1. The server update.
2. The redirect decision.
3. The next page's data loading.

This avoids imposing a sequential post-mutation fetch waterfall. Coordinate
the action's processed response, redirect, and revalidation rules rather than
starting an unconditional second client fetch after navigation.
