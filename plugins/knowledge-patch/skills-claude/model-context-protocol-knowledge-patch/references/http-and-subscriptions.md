# Streamable HTTP, Sessions, and Resumption

## Streamable HTTP endpoint (`2025-03-26-compat`)

Streamable HTTP replaces HTTP+SSE with one MCP endpoint supporting POST and
GET. Every client message gets a fresh POST with both accepted response media
types:

```http
POST /mcp HTTP/1.1
Accept: application/json, text/event-stream
Content-Type: application/json

{"jsonrpc":"2.0","id":1,"method":"ping"}
```

Accepted notification-only or response-only input returns an empty 202. A
request returns either one JSON response or an SSE stream, and clients must
support both forms.

A client may separately GET the endpoint with
`Accept: text/event-stream` for server-initiated traffic. A server without
that stream returns 405. The GET stream must not carry ordinary JSON-RPC
responses except while replaying a previous request's stream.

## SSE event identity, resumption, and cancellation (`2025-03-26-compat`)

Servers may assign SSE event IDs unique across the session, or across the
client when sessions are absent. A reconnecting client sends `Last-Event-ID`
on GET. Replay is confined to the disconnected stream.

A dropped stream does not cancel its request. Send an explicit
`CancelledNotification` to cancel it.

## Stateful HTTP sessions (`2025-03-26-compat`)

A server may return `Mcp-Session-Id` with the initialization response. The
client must repeat it on every later HTTP request. Use these status semantics:

- A required but missing session ID produces HTTP 400.
- A terminated or expired ID produces HTTP 404; start a new initialization
  without that ID.
- A client should request cleanup with DELETE. The server may reject deletion
  with 405.

## HTTP protocol version and message framing (`2025-06-18-compat`)

Each Streamable HTTP POST body contains exactly one JSON-RPC request,
notification, or response. A top-level JSON-RPC batch is invalid on this
transport.

After initialization, the client must send the negotiated version on every
later HTTP request:

```http
MCP-Protocol-Version: 2025-06-18
```

Absent other version information, a missing header means `2025-03-26`. An
invalid or unsupported value produces HTTP 400.

## Pollable SSE streams (`2025-11-25-compat`)

For an SSE response, a server should first send an event ID with empty data.
After assigning that ID, it may close the HTTP connection without terminating
the logical stream. Before closing, it should send an SSE `retry` delay.

The client must honor the delay and reconnect with GET plus `Last-Event-ID`,
whether the original logical stream came from POST or GET.

## Legacy HTTP+SSE compatibility

### Original fallback (`2025-03-26-compat`)

A server supporting old clients should retain the legacy SSE and POST
endpoints alongside the new MCP endpoint. A client given an unknown server URL
first POSTs an `InitializeRequest` with the Streamable HTTP `Accept` header.
Success selects Streamable HTTP. Under this original rule, a 4xx response
triggers GET; an initial `endpoint` event identifies the `2024-11-05`
HTTP+SSE transport for later communication.

### Tightened fallback (`2025-11-25-compat`)

The later compatibility rule narrows fallback to an initial Streamable HTTP
POST failing with 400, 404, or 405. Only then issue GET and expect an
`endpoint` event. Other 4xx responses do not trigger legacy transport
detection.
