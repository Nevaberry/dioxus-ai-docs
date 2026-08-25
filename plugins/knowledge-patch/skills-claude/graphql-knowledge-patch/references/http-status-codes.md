# GraphQL-over-HTTP status codes

Use this reference after negotiating `application/graphql-response+json` to map
response shape and failure phase to HTTP status.

## Media type and body processing

### GraphQL responses at every status

*Batch: graphql-over-http-2026-07*

When the response has `Content-Type: application/graphql-response+json`, a client
processes the body as a GraphQL response regardless of the HTTP status. This
property is specific to that response media type.

If a failure prevents the server from forming a well-formed GraphQL response,
return an appropriate `4xx` or `5xx` status and do not claim
`application/graphql-response+json` for the body.

## Status by GraphQL response shape

### Required and recommended mappings

*Batch: graphql-over-http-2026-07*

Apply the response-shape rules before choosing a more specific failure status:

| Response shape | Status rule |
| --- | --- |
| `data` is non-null | Must use a `2xx` status |
| `data` exists and `errors` is absent | Should use `200 OK` |
| `data` and `errors` both exist | Should use `294 Partial Success` |
| `data` is absent | Must use an appropriate `4xx` or `5xx` status |

The `294` recommendation includes a response with `data: null` and `errors`.
`294 Partial Success` is a custom, non-IETF status recommended together with
`application/graphql-response+json`. Clients, servers, proxies, and monitoring
must opt into its handling deliberately.

## Request and transport failure statuses

### Malformed bytes, envelope, and GraphQL requests

*Batch: graphql-over-http-2026-07*

When a GraphQL response contains no `data`, distinguish the failure phase:

- `400 Bad Request`: invalid JSON or an unparseable GraphQL document.
- `422 Unprocessable Content`: malformed GraphQL-over-HTTP envelope, GraphQL
  validation failure, ambiguous operation selection, or variable coercion
  failure.

An envelope with a string-valued `query` is transport-well-formed even when that
query later produces the `400` parse failure or `422` validation failure.

### Method and media-type failures

*Batch: graphql-over-http-2026-07*

- `405 Method Not Allowed` is required for a mutation submitted over GET and is
  recommended for any unsupported HTTP method.
- `406 Not Acceptable` indicates that no acceptable response media type can be
  selected.
- `415 Unsupported Media Type` indicates an unsupported request `Content-Type`.

### Time and size limits

*Batch: graphql-over-http-2026-07*

- `408 Request Timeout` indicates a timeout while producing the request.
- `413 Content Too Large` indicates an oversized POST body.
- `414 URI Too Long` indicates an oversized request URI.
- `431 Request Header Fields Too Large` indicates oversized request headers.

### Permission and server availability failures

*Batch: graphql-over-http-2026-07*

Use an appropriate permission status, such as `401 Unauthorized` or `403
Forbidden`, when authorization or authentication prevents the request.

Use an appropriate `5xx` status for maintenance or load shedding. `503 Service
Unavailable` is the recommended status for that class of temporary server
unavailability.
