# Authorization

## Transport-specific authorization profile

For `2025-03-26-compat`, authorization is optional. HTTP transports that
implement authorization should use OAuth 2.1, while stdio implementations
should obtain credentials from the environment.

PKCE is required for every client. Authorization-required or invalid-token
responses use HTTP 401. Servers may choose authorization-code grants for users
or client-credentials grants for applications.

## Request authentication and delegated authorization

Send `Authorization: Bearer <access-token>` on every HTTP request, including
requests made within an established MCP session. Never put the token in the
query string. Invalid or expired tokens receive HTTP 401, while insufficient
scope receives HTTP 403. (`2025-03-26-compat`)

An MCP server delegating to a third-party authorization server must issue its
own token bound to the upstream session and keep the two tokens' validity and
lifecycle synchronized. (`2025-03-26-compat`)

An authorized MCP server must not pass an inbound token through to an upstream
API. (`2025-06-18-compat`)

## Protected-resource metadata and token binding

Authorized MCP servers are OAuth protected resources in
`2025-06-18-compat`. They must publish RFC 9728 metadata containing at least one
`authorization_servers` entry and point clients to that metadata in a 401
`WWW-Authenticate` header. Clients parse the metadata, choose an authorization
server when several are advertised, and use that server's RFC 8414 metadata.

Every authorization and token request must include the RFC 8707 `resource`
parameter even when the authorization server does not support it. Use the most
specific canonical absolute MCP URI, including a distinguishing path when
needed and no fragment.

```text
resource=https%3A%2F%2Fmcp.example.com%2Fserver%2Fmcp
```

The MCP server must reject tokens not issued for that resource.

## Authorization-server discovery

For `2025-03-26-compat`, clients must try RFC 8414 authorization-server
metadata and should send `MCP-Protocol-Version`. The authorization base
discards the MCP URL's entire path.

If discovery fails, use `/authorize`, `/token`, and `/register` at the MCP
origin:

```text
MCP URL:  https://api.example.com/v1/mcp
Metadata: https://api.example.com/.well-known/oauth-authorization-server
Fallback: https://api.example.com/authorize
          https://api.example.com/token
          https://api.example.com/register
```

For `2025-11-25-compat`, clients must support both `resource_metadata` in a
401 `WWW-Authenticate` challenge and protected-resource well-known discovery.
When the header is absent, try the MCP-path form first and then the origin root:

```text
https://mcp.example.com/.well-known/oauth-protected-resource/public/mcp
https://mcp.example.com/.well-known/oauth-protected-resource
```

For an authorization-server issuer with a path, try OAuth metadata by path
insertion, OIDC discovery by path insertion, and then OIDC discovery by path
appending:

```text
https://auth.example.com/.well-known/oauth-authorization-server/tenant1
https://auth.example.com/.well-known/openid-configuration/tenant1
https://auth.example.com/tenant1/.well-known/openid-configuration
```

## Client registration

In `2025-03-26-compat`, dynamic client registration is recommended. A
server-specific client ID or user-entered registration details are fallbacks.

For clients and authorization servers with no prior relationship in
`2025-11-25-compat`, Client ID Metadata Documents are the preferred
registration path after pre-registration. Use them when
`client_id_metadata_document_supported` is true, then fall back to dynamic
registration or user-entered credentials.

The `client_id` is an HTTPS URL with a path. Its JSON document has an exactly
matching `client_id`, plus `client_name` and `redirect_uris`:

```json
{
  "client_id": "https://app.example.com/oauth/client.json",
  "client_name": "Example MCP Client",
  "redirect_uris": ["http://127.0.0.1:3000/callback"]
}
```

Supporting authorization servers should fetch the document and must validate
the document and requested redirect URI. Dynamic Client Registration is
optional and retained as a backwards-compatible fallback.

## Initial and step-up scope selection

For initial authorization in `2025-11-25-compat`, use the 401 challenge's
`scope` when present. Otherwise, request every `scopes_supported` value from
protected-resource metadata, or omit `scope` when that field is absent. A
challenged scope set is authoritative for that request regardless of its
relationship to `scopes_supported`.

At runtime, insufficient permission should return HTTP 403 with
`WWW-Authenticate: Bearer error="insufficient_scope"`, the required `scope`,
and `resource_metadata`. User-facing clients should reauthorize with the
increased scope set and retry the original operation with a small retry limit.
