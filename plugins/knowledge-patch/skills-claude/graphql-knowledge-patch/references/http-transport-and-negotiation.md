# GraphQL-over-HTTP transport and negotiation

Use this reference for response media-type negotiation, legacy JSON handling,
GET query parameters, and JSON POST envelope validation.

## Response content negotiation

### Client `Accept` requirements

*Batch: graphql-over-http-2026-07*

A conforming client includes `application/graphql-response+json` in `Accept`.
When support on the server is unknown, use a weighted legacy fallback:

```http
Accept: application/graphql-response+json, application/json;q=0.9
```

The quality value makes the GraphQL response media type the preferred choice
while permitting a legacy JSON response.

### Server selection and unacceptable offers

*Batch: graphql-over-http-2026-07*

A conforming server supports `application/graphql-response+json` and honors the
highest-priority response type that it supports.

If no offered media type is acceptable, the server either returns `406 Not
Acceptable` without executing the request or disregards `Accept`. Returning `406`
is recommended when the client offered neither a supported response type nor
`application/json`.

### Legacy `application/json` clients

*Batch: graphql-over-http-2026-07*

When a legacy client accepts `application/json` but no preferred response type,
apply the same status rules used for `application/graphql-response+json`.
However, set the response `Content-Type` to `application/json` only when the
result uses a `2xx` status.

Only `application/graphql-response+json` tells the client that a body is a
GraphQL response independently of HTTP status. A non-`2xx` JSON response does not
carry that media-type guarantee for a legacy client.

## GET request parameters

### JSON-encoded optional maps

*Batch: graphql-over-http-2026-07*

In a GET URL, non-empty `variables` and `extensions` values are JSON strings.
An empty optional parameter is equivalent to omitting that parameter.

Validate the decoded JSON value according to the parameter's expected type; the
fact that the URL representation is a string does not change the parameter's
GraphQL-over-HTTP type.

### Operation-name edge cases

*Batch: graphql-over-http-2026-07*

The GET value `operationName=null` selects an operation whose name is literally
`null`. It is not a null sentinel. To select no operation name, omit the
parameter or send it with an empty value.

## JSON POST requests

### Required support and content type

*Batch: graphql-over-http-2026-07*

A server must support UTF-8 POST request bodies with
`Content-Type: application/json`. A server should reject a POST request that
omits `Content-Type` with an appropriate `4xx` response.

### Optional nulls and unknown properties

*Batch: graphql-over-http-2026-07*

In a JSON POST body, an optional parameter whose JSON value is `null` is treated
as omitted. Unknown JSON object properties must be ignored, allowing compatible
envelope extensions without changing the defined parameters.

### Malformed envelope versus GraphQL document failure

*Batch: graphql-over-http-2026-07*

A missing `query` property makes the transport request malformed. A defined
parameter with a value of the wrong type also makes the transport request
malformed.

A string-valued `query` is transport-well-formed. If that string later fails
GraphQL parsing or validation, classify the failure at the GraphQL request phase,
not as a malformed JSON envelope.
