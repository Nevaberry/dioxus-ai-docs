# Authorization-Flow Security

Source attribution: RFC 9700 (`rfc9700`).

Use this reference when implementing or auditing authorization-code processing,
OpenID Connect transaction binding, identity claims, or browser endpoint
exposure.

## PKCE downgrade rejection and discovery

The authorization server must correlate the token request with the original
authorization request. It may accept a token request containing `code_verifier`
only if the corresponding authorization request contained `code_challenge`.

If the server accepts a verifier when the saved transaction has no challenge,
an attacker can strip the authorization request's challenge and downgrade the
flow. The verifier's presence at the token endpoint is not evidence that a
challenge was present earlier.

Persist enough transaction state to distinguish at least these cases:

| Authorization request | Token request | Required handling |
| --- | --- | --- |
| Has `code_challenge` | Has matching `code_verifier` | Continue normal PKCE processing |
| Has `code_challenge` | Missing or invalid verifier | Apply PKCE failure handling |
| Has no `code_challenge` | Has `code_verifier` | Reject as a downgrade condition |

The authorization server must also provide a way to detect PKCE support. The
preferred mechanism is authorization-server metadata listing its supported
methods:

```json
{
  "code_challenge_methods_supported": ["S256"]
}
```

## OIDC nonce as an authorization-code injection defense

The transaction-specific `nonce` alternative is narrower than PKCE:

- Only a confidential OpenID Connect client may use it for this injection
  defense.
- A public client still requires PKCE.
- The nonce must be bound to the transaction and validated in the ID Token
  returned by the token endpoint.
- The client must validate that token-endpoint ID Token even if an ID Token was
  also returned in the authorization response.
- The client must not use any returned token until nonce validation succeeds.

Do not treat front-channel ID Token validation as a substitute for validating
the ID Token delivered with the token response. The token-endpoint result is the
required validation point for this defense.

## Separate client and resource-owner identities

A shared namespace for client IDs and user subject identifiers creates an
ambiguity at the resource server. A client-controlled value could be interpreted
as a genuine resource-owner identity.

The authorization server should prevent clients from influencing `client_id` or
any other claim that could be confused with a resource owner. If it cannot
prevent that ambiguity, it must provide the resource server with another way to
distinguish:

- grants made only to a client; and
- grants that involve a resource owner.

Review claim construction and downstream authorization together. The resource
server needs a reliable distinction, not merely a naming convention that a
client can affect.

## CORS boundary for browser clients

Direct browser access is appropriate only for endpoints that behave as APIs.
The authorization endpoint is a user-agent navigation target and must not
support CORS.

| Endpoint | Direct cross-origin API access |
| --- | --- |
| Token endpoint | May support CORS |
| Metadata endpoint | May support CORS |
| `jwks_uri` endpoint | May support CORS |
| Dynamic registration endpoint | May support CORS |
| Authorization endpoint | Must not support CORS |

This distinction remains important for browser-based clients: configure CORS
per endpoint instead of applying one blanket policy to the authorization
server.

## Audit checklist

- The authorization transaction records whether `code_challenge` was present.
- A stray `code_verifier` cannot turn a non-PKCE transaction into a PKCE one.
- Supported challenge methods are discoverable in server metadata.
- Public clients always use PKCE for this defense.
- Confidential nonce flows validate the token-endpoint ID Token before any
  returned token is consumed.
- Client-only grants cannot masquerade as resource-owner grants.
- CORS configuration excludes the authorization endpoint.
