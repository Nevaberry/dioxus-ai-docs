---
name: model-context-protocol-knowledge-patch
description: Model Context Protocol (MCP)
version: 2025-11-25
license: MIT
metadata:
  author: Nevaberry
---


# Model Context Protocol Knowledge Patch

Use this skill when implementing, reviewing, or debugging MCP clients, servers,
transports, authorization, capability negotiation, or protocol schemas. First
identify the protocol revision negotiated during initialization; several rules
below are revision-specific and later revisions intentionally reverse earlier
behavior.

## Reference index

| Reference | Topics |
| --- | --- |
| [Authorization, registration, and security](references/authorization.md) | OAuth profile, discovery, resource binding, registration, scopes, bearer tokens, and Origin validation |
| [Streamable HTTP, sessions, and resumption](references/http-and-subscriptions.md) | POST/GET framing, version headers, sessions, SSE replay, polling, cancellation, and legacy HTTP+SSE fallback |
| [Interaction patterns](references/interaction-patterns.md) | Tools, completion, elicitation, sampling, tasks, progress, content, icons, and validation errors |
| [Protocol core](references/protocol-core.md) | Lifecycle, JSON-RPC batching, `_meta`, implementation metadata, schemas, and revision status |

## Apply revision-aware behavior

1. Read the negotiated protocol version from initialization and retain it for
   the connection or session.
2. Gate optional requests and fields on advertised capabilities.
3. Apply the exact transport, authorization, and schema rules for that
   revision; do not blend incompatible rules from different revisions.
4. Preserve wire-level error distinctions so callers can decide whether to
   retry, reauthorize, correct input, or reinitialize.
5. When interoperating with an older peer, follow the explicitly documented
   fallback rather than assuming that a newer feature will be ignored.

## Breaking changes and deprecations

### Do not batch JSON-RPC messages in current revisioned transports

Top-level JSON-RPC arrays were introduced and then removed. For the later
revision, send each request, notification, and response as a separate message.
Streamable HTTP POST bodies likewise carry one JSON-RPC message.

See [Protocol core](references/protocol-core.md#json-rpc-batching-by-revision)
for the revision boundary.

### Treat the lifecycle operation as mandatory

The lifecycle requirement is a **MUST** in the later lifecycle rules. Do not
implement it as an optional optimization.

### Preserve stricter legacy transport detection

Only an initial Streamable HTTP POST failure with status 400, 404, or 405
triggers legacy HTTP+SSE detection under the newer fallback rule. Other 4xx
responses are real errors, not a signal to switch transports.

### Prefer metadata-document registration

For clients without a pre-existing relationship with the authorization
server, prefer a Client ID Metadata Document when advertised. Dynamic Client
Registration remains an optional compatibility fallback, followed by
user-entered credentials.

### Avoid sampling context unless negotiated

`includeContext` values `thisServer` and `allServers` are soft-deprecated.
Omit the field for its `none` default unless the client explicitly advertises
the sampling context capability.

## Authorization quick reference

### Bind tokens to the MCP resource

For the protected-resource profile:

- Discover protected-resource metadata from the 401 challenge or well-known
  locations.
- Include the RFC 8707 `resource` parameter in authorization and token
  requests.
- Use the most specific canonical absolute MCP URI without a fragment.
- Reject tokens issued for another resource.
- Never forward the inbound MCP access token to an upstream API.

Send the bearer token on every HTTP request, including requests within an MCP
session. Never put it in the query string.

### Distinguish authentication and authorization failures

- Return 401 for missing, invalid, or expired credentials and advertise
  protected-resource metadata as required by the applicable profile.
- Return 403 with `insufficient_scope`, required scopes, and resource metadata
  when the token is valid but under-scoped.
- Reauthorize and retry a scope-challenged operation only with a small retry
  limit.

### Enforce HTTP security boundaries

Validate `Origin` on every incoming Streamable HTTP connection and return 403
when it is invalid. Local servers should bind to loopback, authenticate
connections, use HTTPS authorization endpoints, and accept only localhost or
HTTPS redirect URIs.

## Streamable HTTP quick reference

### Send and receive both response forms

Use one MCP endpoint for POST and optional GET traffic. A client POST sends:

```http
Accept: application/json, text/event-stream
Content-Type: application/json
```

For a request, accept either one JSON response or an SSE stream. Accepted
notification-only or response-only input receives an empty 202. A separate GET
with `Accept: text/event-stream` can carry server-initiated traffic; a server
without that stream returns 405.

### Maintain session and version headers

If initialization returns `Mcp-Session-Id`, repeat it on every later HTTP
request. A missing required ID is a 400. A terminated or expired ID is a 404;
reinitialize without the old ID. Use DELETE for cleanup, tolerating 405 when
the server does not support deletion.

After initialization, send `MCP-Protocol-Version` on every HTTP request.
Reject invalid or unsupported versions with HTTP 400.

### Resume without implying cancellation

Reconnect an SSE stream with `Last-Event-ID`. Replay only the disconnected
logical stream. A dropped stream does not cancel its request; send an explicit
`CancelledNotification` when cancellation is intended.

For pollable SSE, honor the server's `retry` delay and reconnect with GET even
when the logical stream began as a POST response.

## Interaction quick reference

### Return structured tool output compatibly

A tool may declare `outputSchema` and return a conforming object in
`structuredContent`. Validate the result and also serialize the same JSON into
a text content item for older clients. A result may contain a `resource_link`;
do not assume the linked resource also appears in `resources/list`.

Treat tool input validation failures as Tool Execution Errors so the caller
can inspect and correct the arguments, rather than as Protocol Errors.

### Negotiate elicitation mode

Advertise supported form and URL modes. An empty elicitation capability means
form-only, and an omitted request mode defaults to `form`. Keep form schemas
flat. Use URL mode for sensitive or third-party out-of-band interactions, not
for authorizing the client to the MCP server.

For URL mode, `accept` means only that the user agreed to open the URL. Wait
for the matching completion notification or handle the required-elicitation
error before retrying the original operation.

### Enforce sampling tool-call ordering

Send sampling tools only when the client advertises `sampling.tools`. Every
assistant `tool_use` must be followed immediately by exactly one matching user
`tool_result`, and that result message may contain only tool results. Invalid
ordering or matching uses `-32602`.

### Run experimental tasks by capability

Negotiate tasks separately for each request category and for list/cancel
operations. Enforce each tool's `execution.taskSupport`. Poll `tasks/get` at
the advertised interval; status notifications supplement but do not replace
polling. Use `tasks/result` to obtain the exact underlying result or error.

Terminal task states never transition. Treat `input_required` as a signal to
call `tasks/result`, and keep related-task metadata off task control requests
where the task ID parameter is authoritative.

## Schema and presentation quick reference

- Use JSON Schema 2020-12 by default unless another dialect is explicitly
  selected.
- Account for standalone request-parameter schemas rather than assuming every
  payload schema is embedded in an RPC method definition.
- Allow `_meta` on the expanded interface set defined by the revision.
- Use `name` as the programmatic identifier and `title` as the display label.
- Present optional icons on tools, resources, resource templates, and prompts.
- Preserve the optional implementation `description` exchanged during
  initialization.
- Check the `completions` capability before sending completion requests and
  pass previously resolved variables through completion `context` when used.
- Support audio alongside text and image content where that revision permits
  it.
