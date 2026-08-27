# Authorization, Registration, and Security

## HTTP authorization profile (`2025-03-26-compat`)

Authorization is optional. HTTP transports that implement it should use OAuth
2.1, while stdio implementations should obtain credentials from the
environment. PKCE is required for every client. Authorization-required and
invalid-token responses use HTTP 401. Servers may use authorization-code
grants for users or client-credentials grants for applications.

## Initial authorization-server discovery (`2025-03-26-compat`)

Clients must try RFC 8414 authorization-server metadata and should send
`MCP-Protocol-Version`. In this compatibility profile, discard the MCP URL's
entire path when forming the authorization base. If discovery fails, use
`/authorize`, `/token`, and `/register` at that origin. Dynamic Client
Registration is recommended here; a server-specific client ID or user-entered
registration details are fallbacks.

```text
MCP URL:  https://api.example.com/v1/mcp
Metadata: https://api.example.com/.well-known/oauth-authorization-server
Fallback: https://api.example.com/authorize
          https://api.example.com/token
          https://api.example.com/register
```

## Bearer tokens and delegated authorization (`2025-03-26-compat`)

Send `Authorization: Bearer <access-token>` on every HTTP request, even within
an established MCP session. Never put the token in the query string. Invalid
or expired tokens receive 401; insufficient scope receives 403.

When an MCP server delegates authorization to a third-party authorization
server, it must issue its own token bound to the upstream session and keep the
two tokens' validity and lifecycle synchronized.

## Protected-resource discovery and resource binding (`2025-06-18-compat`)

Authorized MCP servers are OAuth protected resources. They must publish RFC
9728 metadata with at least one `authorization_servers` entry and point to it
from the 401 `WWW-Authenticate` header. A client parses that metadata, chooses
an authorization server when several are advertised, and then reads the
selected server's RFC 8414 metadata.

Every authorization and token request must include the RFC 8707 `resource`
parameter, even when the authorization server does not support it. Use the
most specific canonical absolute MCP URI, including a distinguishing path
when needed and no fragment.

```text
resource=https%3A%2F%2Fmcp.example.com%2Fserver%2Fmcp
```

The MCP server must reject tokens not issued for that resource and must not
pass the inbound token through to an upstream API.

## Client ID Metadata Documents (`2025-11-25-compat`)

For a client and authorization server without a prior relationship, use this
registration order:

1. Use pre-registered client information when available.
2. When `client_id_metadata_document_supported` is true, use a Client ID
   Metadata Document.
3. Fall back to Dynamic Client Registration.
4. Finally, accept user-entered credentials.

The metadata-document `client_id` is an HTTPS URL with a path. Its JSON must
contain an exactly matching `client_id`, plus `client_name` and
`redirect_uris`. A supporting authorization server should fetch the document
and must validate both the document and the requested redirect URI.

```json
{
  "client_id": "https://app.example.com/oauth/client.json",
  "client_name": "Example MCP Client",
  "redirect_uris": ["http://127.0.0.1:3000/callback"]
}
```

Dynamic Client Registration is optional in this profile and remains only as a
backwards-compatible fallback.

## Expanded authorization discovery (`2025-11-25-compat`)

Clients must support both the `resource_metadata` parameter in a 401
`WWW-Authenticate` challenge and protected-resource well-known discovery. If
the header omits `resource_metadata`, try the MCP-path form before the origin
root:

```text
https://mcp.example.com/.well-known/oauth-protected-resource/public/mcp
https://mcp.example.com/.well-known/oauth-protected-resource
```

For an authorization-server issuer containing a path, try these locations in
order: OAuth metadata by path insertion, OIDC discovery by path insertion,
then OIDC discovery by path appending.

```text
https://auth.example.com/.well-known/oauth-authorization-server/tenant1
https://auth.example.com/.well-known/openid-configuration/tenant1
https://auth.example.com/tenant1/.well-known/openid-configuration
```

## Scope selection and step-up authorization (`2025-11-25-compat`)

For initial authorization, use the 401 challenge's `scope` when present. If it
is absent, request every `scopes_supported` value from protected-resource
metadata; omit `scope` when the metadata also omits that field. A challenged
scope set is authoritative for that request, regardless of its relationship
to `scopes_supported`.

At runtime, insufficient permission returns HTTP 403 with
`WWW-Authenticate: Bearer error="insufficient_scope"`, the required `scope`,
and `resource_metadata`. A user-facing client should reauthorize with the
increased scope set and retry the original operation with a small retry limit.

## Origin and redirect security (`2025-03-26-compat`, `2025-11-25`)

Validate `Origin` on every incoming Streamable HTTP connection to prevent DNS
rebinding. Return HTTP 403 Forbidden for an invalid Origin. Local servers
should bind to `127.0.0.1`, not `0.0.0.0`, and authenticate connections.
Authorization endpoints should use HTTPS, and redirect URIs should be limited
to localhost or HTTPS.
