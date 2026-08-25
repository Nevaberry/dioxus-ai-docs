# GraphQL over HTTP

This reference covers request and response media negotiation, envelope
handling, and status selection.

## Response Content Negotiation

A conforming client must include `application/graphql-response+json` in its
`Accept` header. When server support is unknown, use a compatibility fallback:

```http
Accept: application/graphql-response+json, application/json;q=0.9
```

A conforming server must support `application/graphql-response+json` and honor
the highest-priority response type it supports.

If none of the client's acceptable types is supported, a server has two
permitted choices:

1. Return `406 Not Acceptable` and stop.
2. Disregard the `Accept` header.

Returning `406` is recommended when the client offered neither a supported
type nor `application/json`.

Attribution: `graphql-over-http-2026-07` (2026-07-17).

## Legacy JSON Responses

When a legacy client accepts `application/json` but does not accept a preferred
response type, apply the same status rules used for
`application/graphql-response+json`.

Change the response `Content-Type` to `application/json` only for `2xx`
results. This distinction matters because only
`application/graphql-response+json` tells the client that the body is a
GraphQL response independently of HTTP status.

A client receiving legacy JSON on a non-`2xx` result cannot infer from that
media type alone that the body has GraphQL response shape.

Attribution: `graphql-over-http-2026-07` (2026-07-17).

## Optional GET Parameters

For a GraphQL GET URL:

- A non-empty `variables` value is a JSON string.
- A non-empty `extensions` value is a JSON string.
- An empty optional parameter is equivalent to omitting it.
- `operationName=null` names an operation literally called `null`.

To select no operation name, omit `operationName` or provide it with an empty
value. Do not use the URL text `null` as an omission sentinel.

Examples:

```text
?query=query%20Q%7Bviewer%7Bid%7D%7D&operationName=Q
?query=%7Bviewer%7Bid%7D%7D&variables=%7B%22limit%22%3A10%7D
```

Decode the URL value first, then parse non-empty `variables` and `extensions`
as JSON strings.

Attribution: `graphql-over-http-2026-07` (2026-07-17).

## Optional POST Parameters

In a JSON POST body, an optional parameter whose JSON value is `null` is
treated as omitted. This applies to optional members such as `operationName`,
`variables`, and `extensions`.

This POST rule differs from the GET URL text `operationName=null`, where
`null` is the literal operation name rather than a JSON null value.

Attribution: `graphql-over-http-2026-07` (2026-07-17).

## POST Envelope Handling

A server must support UTF-8 `application/json` POST bodies. It should reject a
POST request that lacks `Content-Type` with an appropriate `4xx`.

Envelope parsing follows these rules:

- Ignore unknown JSON properties.
- Treat a missing `query` as a malformed transport request.
- Treat a parameter of the wrong JSON type as a malformed transport request.
- Treat a string-valued `query` as transport-well-formed.

The last rule holds even when the string does not contain a parseable or valid
GraphQL document. Transport-envelope validation precedes GraphQL parsing and
validation; failures in those phases receive their own classifications.

Attribution: `graphql-over-http-2026-07` (2026-07-17).

## Response Shape and Status

With `application/graphql-response+json`, a client processes the body as a
GraphQL response regardless of HTTP status.

Select status according to response shape:

| Response shape | Requirement |
| --- | --- |
| `data` is non-null | Must use `2xx` |
| `data` exists and `errors` is absent | Should use `200` |
| `data` and `errors` both exist | Should use `294 Partial Success` |
| `data` is absent | Must use an appropriate `4xx` or `5xx` |

The `294 Partial Success` recommendation includes responses with `data: null`
plus `errors`. It is a custom, non-IETF status code recommended for use with
`application/graphql-response+json`.

A failure that prevents formation of a well-formed GraphQL response must:

1. Use an appropriate `4xx` or `5xx`.
2. Not claim `application/graphql-response+json` as its media type.

This keeps malformed transport error bodies distinct from GraphQL responses
that legitimately contain errors.

Attribution: `graphql-over-http-2026-07` (2026-07-17).

## Request-Failure Statuses

When a GraphQL response has no `data`, distinguish the phase and failure
condition:

| Status | Condition |
| --- | --- |
| `400` | Invalid JSON or an unparseable GraphQL document |
| `405` | Mutation over GET; also recommended for an unsupported method |
| `406` | No acceptable response media type |
| `408` | Request production timeout |
| `413` | POST body too large |
| `414` | URI too large |
| `415` | Unsupported request `Content-Type` |
| `422` | Malformed GraphQL-over-HTTP envelope |
| `422` | GraphQL validation failure |
| `422` | Ambiguous operation selection |
| `422` | Variable coercion failure |
| `431` | Request headers too large |

A mutation over GET requires `405`. For a different unsupported method, `405`
is recommended.

Use an appropriate permission status such as `401` or `403` for authorization
or authentication failures. Use an appropriate `5xx` for server maintenance or
load shedding, with `503` recommended.

Attribution: `graphql-over-http-2026-07` (2026-07-17).

## Server Implementation Checklist

- Parse and prioritize the client's accepted response media types.
- Support `application/graphql-response+json`.
- Keep the legacy JSON path restricted to `2xx` content typing.
- Apply omission rules after distinguishing URL strings from JSON values.
- Ignore unknown POST properties but reject missing or mistyped required
  envelope members.
- Keep JSON parsing, GraphQL parsing, validation, operation selection,
  variable coercion, and execution as distinct phases.
- Select the status from response shape and failure phase.
- Never label a non-GraphQL error body as
  `application/graphql-response+json`.

## Client Implementation Checklist

- Offer the preferred GraphQL response media type in every conforming request.
- Add the lower-priority JSON fallback when server support is uncertain.
- Process the preferred media type as a GraphQL response at any status.
- Do not assume legacy JSON at non-`2xx` has GraphQL response shape.
- Serialize non-empty GET `variables` and `extensions` as JSON strings.
- Omit an absent operation name instead of serializing URL text `null`.
- Preserve response `data` and `errors` according to shape rather than
  assuming status `200`.
