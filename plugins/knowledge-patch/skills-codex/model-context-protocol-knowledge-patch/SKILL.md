---
name: model-context-protocol-knowledge-patch
description: Model Context Protocol (MCP)
version: 2025-11-25
license: MIT
metadata:
  author: Nevaberry
---


# Model Context Protocol Compatibility Guidance

Use this skill when implementing or reviewing MCP authorization, transports,
schemas, tools, elicitation, sampling, or tasks. Match behavior to the negotiated
protocol revision; requirements that changed between revisions are called out
explicitly.

## Reference index

| Reference | Topics |
| --- | --- |
| [Authorization](references/authorization.md) | OAuth profile, discovery, registration, token binding, scopes, and step-up authorization |
| [Interactive operations](references/interactive-operations.md) | Tools, content, progress, completion, elicitation, sampling, tasks, and presentation metadata |
| [Protocol revisions and schemas](references/protocol-revisions-and-schemas.md) | Batching, lifecycle requirements, metadata, schema dialect, parameter schemas, and revision status |
| [Transport, sessions, and subscriptions](references/transport-sessions-and-subscriptions.md) | Streamable HTTP, SSE, framing, sessions, cancellation, security, and legacy fallback |

## Breaking changes and required behavior

### JSON-RPC batching is revision-sensitive

The 2025-03-26 revision added top-level JSON-RPC batches, but the 2025-06-18
revision removed them. For 2025-06-18, send each request, notification, or
response as a separate JSON-RPC message rather than a top-level array.

Streamable HTTP framing for 2025-06-18 likewise requires each POST body to
contain one JSON-RPC request, notification, or response.

### The lifecycle operation is mandatory

For 2025-06-18, the lifecycle operation requirement is **MUST**, strengthened
from **SHOULD**. Treat the operation as required for implementations targeting
that revision.

### Separate tool execution errors from protocol errors

For 2025-11-25, return tool-call input validation failures as Tool Execution
Errors rather than Protocol Errors so the failure can be inspected and the tool
input corrected.

### Use the current schema organization

JSON Schema 2020-12 is the default dialect for 2025-11-25 MCP schemas unless
another dialect is selected explicitly. Request payload schemas are standalone
parameter schemas rather than being coupled to RPC method definitions.

### Stable revision status

The 2026-07-28 protocol revision is stable. Behavior previously published in
its release candidate is no longer prerelease guidance.

## Authorization quick reference

### Choose credentials by transport

Authorization is optional. HTTP transports that implement it should use OAuth
2.1, while stdio implementations should obtain credentials from the
environment. PKCE is required for every client.

Servers may use authorization-code grants for users or client-credentials
grants for applications. Authorization-required or invalid-token responses use
HTTP 401.

### Authenticate every HTTP request

Send `Authorization: Bearer <access-token>` on every HTTP request, including
requests made within an established MCP session. Never place the token in the
query string.

Invalid or expired tokens receive HTTP 401; insufficient scope receives HTTP
403. A server delegating authorization must issue its own token bound to the
upstream session and synchronize both tokens' validity and lifecycle.

### Bind tokens to the MCP resource

For the 2025-06-18 authorization profile, every authorization and token request
must include the RFC 8707 `resource` parameter, even when the authorization
server does not support it. Use the most specific canonical absolute MCP URI,
including a distinguishing path when needed and no fragment.

The MCP server must reject tokens not issued for that resource and must not pass
the inbound token through to an upstream API.

### Discover authorization metadata

For 2025-06-18, an authorized MCP server must publish RFC 9728 metadata with at
least one `authorization_servers` entry and advertise that metadata in a 401
`WWW-Authenticate` header. The client chooses an advertised authorization
server and uses its RFC 8414 metadata.

For 2025-11-25, support both the challenge's `resource_metadata` value and
protected-resource well-known discovery. Follow the MCP-path and origin-root
fallback order, then the documented OAuth and OIDC issuer-path order in the
[authorization reference](references/authorization.md).

### Register clients and handle scope escalation

For 2025-11-25 clients and authorization servers without a prior relationship,
Client ID Metadata Documents are the preferred registration path when
`client_id_metadata_document_supported` is true. Dynamic registration and
user-entered credentials are fallbacks.

For initial authorization, use the scope from the 401 challenge; otherwise
request all `scopes_supported` values or omit `scope` when that metadata field
is absent. On an insufficient-scope challenge, user-facing clients should
reauthorize with the increased scope set and retry with a small retry limit.

## Streamable HTTP quick reference

### POST and GET roles

Streamable HTTP replaces HTTP+SSE with one MCP endpoint supporting POST and
GET. Each client message uses a fresh POST with `Accept` listing
`application/json, text/event-stream`.

Accepted notification- or response-only input returns an empty HTTP 202. A
request returns either one JSON response or an SSE stream; clients must support
both forms.

A client may separately GET with `Accept: text/event-stream` for
server-initiated traffic. A server without that stream returns HTTP 405. The GET
stream must not carry ordinary JSON-RPC responses except while replaying a
previous request's stream.

### Carry session and revision headers

When initialization returns `Mcp-Session-Id`, repeat it on every later HTTP
request. A required missing ID should produce HTTP 400; a terminated or expired
ID produces HTTP 404 and requires new initialization without an ID.

After initialization, send `MCP-Protocol-Version` on every subsequent HTTP
request. Without other version information, a missing header means
`2025-03-26`; an invalid or unsupported value produces HTTP 400.

### Resume and cancel explicitly

Reconnect SSE with GET plus `Last-Event-ID`. Replay is confined to the
disconnected stream. Dropping the stream does not cancel its request; send an
explicit `CancelledNotification` to cancel.

For pollable SSE, honor the server's `retry` delay before reconnecting, whether
the original stream came from POST or GET.

### Enforce HTTP security

Validate `Origin` on every incoming connection. Return HTTP 403 when rejecting
an invalid `Origin`. Local servers should bind to `127.0.0.1`, authenticate
connections, serve authorization endpoints over HTTPS, and accept only
localhost or HTTPS redirect URIs.

## Interactive operations quick reference

### Advertise capabilities before use

Use `completions` to advertise argument-completion support, and check it before
relying on completion requests. Later completion requests can use `context` for
previously resolved variables.

A client advertises `capabilities.elicitation` before a server sends nested
`elicitation/create`. For 2025-11-25, negotiate form and URL modes explicitly;
the legacy empty capability object is form-only and an omitted request `mode`
defaults to `"form"`.

Clients advertise `sampling: {tools: {}}` before servers include sampling tools
or `toolChoice`. Tasks are experimental in 2025-11-25 and require capability
negotiation by request category.

### Return structured and linked tool results

A tool may declare `outputSchema` and return a matching JSON object in
`structuredContent`. Servers must conform to the schema, clients should
validate it, and servers should also serialize the JSON into a text content
item for older clients.

A tool result may contain a `resource_link` with a fetchable or subscribable
URI and resource annotations. The linked resource is not guaranteed to appear
in `resources/list`.

### Preserve sampling tool-message order

A sampling tool use must be followed, before any other message, by exactly one
matching tool result. A tool-result message must contain only tool results;
violations use `-32602`.

### Poll task results

An accepted augmented request returns `result.task` immediately. Poll
`tasks/get` while respecting `pollInterval`; optional status notifications do
not replace polling. `tasks/result` blocks until a terminal state and then
returns exactly the underlying result or JSON-RPC error.

Read [interactive operations](references/interactive-operations.md) for task
capability shapes, status transitions, related-task metadata, URL elicitation,
form schemas, sampling content, and the remaining presentation fields.
