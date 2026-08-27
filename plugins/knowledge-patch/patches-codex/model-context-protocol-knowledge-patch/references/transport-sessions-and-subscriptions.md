# Transport, Sessions, and Subscriptions

## Streamable HTTP request and response flow

Streamable HTTP replaces HTTP+SSE with one MCP endpoint supporting POST and
GET. Every client message gets a fresh POST whose `Accept` lists
`application/json, text/event-stream`. (`2025-03-26-compat`)

```http
POST /mcp HTTP/1.1
Accept: application/json, text/event-stream
Content-Type: application/json

{"jsonrpc":"2.0","id":1,"method":"ping"}
```

Accepted notification- or response-only input returns an empty HTTP 202. A
request returns either one JSON response or an SSE stream; clients must support
both response forms.

A client may separately GET the endpoint with `Accept: text/event-stream` for
server-initiated traffic. A server that does not provide that stream returns
HTTP 405. The GET stream must not carry ordinary JSON-RPC responses except when
replaying a previous request's stream.

## Message framing and protocol version

For `2025-06-18-compat`, each Streamable HTTP POST body must contain one
JSON-RPC request, notification, or response. A top-level JSON-RPC batch is not
valid on this transport.

After initialization, clients must send the negotiated version on every
subsequent HTTP request:

```http
MCP-Protocol-Version: 2025-06-18
```

Absent other version information, a missing header means `2025-03-26`. An
invalid or unsupported value produces HTTP 400.

## Stateful HTTP sessions

A server may return `Mcp-Session-Id` with the initialization response. The
client must repeat it on every later HTTP request. A required but missing ID
should produce HTTP 400. A terminated or expired ID produces HTTP 404 and
requires new initialization without an ID. (`2025-03-26-compat`)

Clients should request cleanup with DELETE. A server may reject DELETE with
HTTP 405.

## SSE event identity, resumption, and cancellation

Servers may assign SSE event IDs that are unique across the session, or across
the client when sessions are absent. A reconnecting client sends
`Last-Event-ID` on GET. Replay is confined to the disconnected stream.
(`2025-03-26-compat`)

A dropped stream does not cancel its request. Cancellation requires an explicit
`CancelledNotification`.

## Pollable SSE streams

For `2025-11-25-compat`, a server should first send an event ID with empty data
for an SSE response. After assigning an ID, it may close the HTTP connection
without terminating the logical stream and should send an SSE `retry` delay
first.

The client must honor the delay and reconnect with GET plus `Last-Event-ID`,
whether the original stream came from POST or GET.

## Origin, binding, and redirect security

Servers must validate `Origin` on every incoming connection to prevent DNS
rebinding. Local servers should bind to `127.0.0.1` rather than `0.0.0.0`,
authenticate connections, serve authorization endpoints over HTTPS, and accept
only localhost or HTTPS redirect URIs. (`2025-03-26-compat`)

A Streamable HTTP server must return HTTP 403 Forbidden when it rejects an
invalid `Origin` header. (`2025-11-25`)

## HTTP+SSE backwards compatibility

Servers supporting old clients should keep the legacy SSE and POST endpoints
alongside the new MCP endpoint. (`2025-03-26-compat`)

A client given an unknown server URL first POSTs an `InitializeRequest` using
the Streamable HTTP `Accept` header. Under the `2025-03-26-compat` behavior,
success selects Streamable HTTP, while a 4xx response triggers GET. An initial
`endpoint` event identifies the 2024-11-05 HTTP+SSE transport for all later
communication.

For `2025-11-25-compat`, legacy detection is limited to an initial Streamable
HTTP POST failing with HTTP 400, 404, or 405 before the client falls back to GET
and expects an `endpoint` event. Other 4xx responses do not trigger that
fallback.
