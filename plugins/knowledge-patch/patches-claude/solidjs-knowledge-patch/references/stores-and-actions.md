# Stores, Actions, and Submissions

## Action lifecycle and results

Actions support `onComplete`, expose errors, and return their fully processed
responses. Use `onComplete` for completion handling, and do not assume the raw
handler return value is the action's final result.

Navigation clears only completed actions. Pending actions remain observable, so
application cleanup must not depend on every action disappearing when a route
changes.

## Action and async-data names

User-provided names are honored by both `action` and `createAsync`. An action
hashes its supplied name instead of forcing every action to the fixed name
`"mutate"`. Code that keys diagnostics, submissions, or UI state by name must
accept the hashed action identity.

## Submission and parameter exports

`Submission` is exported from the package top level. Import it there rather
than from an internal path.

`SearchParams` is also a public exported type. Search-parameter values may be
optional or arrays, and `Params` values may be optional. Reflect those unions
when an action derives input from route state.

## Form bodies

Form actions use URL-encoded bodies by default. `URLSearchParams` is accepted
when the encoding is not `multipart/form-data`:

```ts
const body = new URLSearchParams({ title: "Example" });
```

Do not pass `URLSearchParams` for a multipart form; construct the body that
matches the selected encoding.

## Revalidation sentinels

An empty string or an empty array means no revalidation. Preserve these values
as intentional sentinels rather than expanding them into a default route or
global invalidation.

## Response processing and redirects

Response helpers return `Response` objects, while router data and action
helpers filter or process those objects under their own contracts. Account for
that processing before reading a returned value as a raw `Response`.

Absolute redirects produced inside server-side calls using the former `cache`
helper are forwarded to the client. When migrating those calls to `query`,
retain redirect forwarding and use `query().handleResponse()` when response
headers must survive processing.

Redirect responses can carry multiple `Set-Cookie` headers. Preserve every
header rather than joining them incorrectly or retaining only one.

## Single-flight mutation navigation

Solid Router can combine mutation, redirect, and destination loading through
the server-function transport (solidstart-1.0.0). After the mutation, the
router starts loading the destination and streams that data in the mutation
response while the browser performs the redirect.

Use this flow when the next route depends on the mutation. It avoids a
sequential mutation-response, redirect, and next-page-fetch waterfall while
keeping destination data loading in the router lifecycle.
