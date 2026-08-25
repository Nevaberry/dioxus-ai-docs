# Stores, Actions, and Submissions

## Action lifecycle

### Observe completion and processed results

Solid Router actions support `onComplete`, expose errors, and return fully
processed responses. During navigation, clear only actions that have
completed; do not discard an in-flight action merely because navigation
started.

### Preserve supplied names

Both `action` and `createAsync` honor user-provided `name` values. An action
applies a hashed form of the supplied name rather than assigning every action
the fixed name `"mutate"`.

## Submissions and parameters

### Import public types from the package surface

`Submission` is exported from the top level. `SearchParams` is also a public
type. Its values may be optional, as may `Params` values, and search-parameter
values can be arrays.

`useParams()` supports the `in` operator, so membership checks can be used
without working around its proxy behavior.

## Form bodies

### Expect URL encoding by default

Form actions use URL-encoded bodies by default. `URLSearchParams` is accepted
when the encoding is not `multipart/form-data`; do not pass it for multipart
form encoding.

## Revalidation

### Represent no revalidation explicitly

An empty string or an empty array means no revalidation. Preserve this
distinction instead of treating those empty values as a request to revalidate
everything.

## Responses and redirects

### Handle `Response` objects

Response helpers return `Response` objects. The legacy `cache` helper and
`action` filter those results, so code using their processed output should not
assume that a helper's raw return value passes through unchanged.

When using the renamed query API, `query().handleResponse()` preserves
headers.

### Forward absolute server-side redirects

Absolute redirects produced inside server-side `cache` calls are forwarded to
the client. When migrating the data helper to `query`, preserve this redirect
behavior rather than resolving the redirect only on the server.

### Retain every cookie on redirects

SolidStart's newer redirect handling preserves multiple `Set-Cookie` headers.
Do not collapse a redirect response to a single cookie value.
