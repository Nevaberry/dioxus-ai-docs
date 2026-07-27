---
name: oauth2-oidc-knowledge-patch
description: OAuth 2.0 / OIDC
version: null
license: MIT
metadata:
  author: Nevaberry
---

# OAuth 2.0 and OpenID Connect

Use this skill when implementing or reviewing OAuth authorization-code flows,
OpenID Connect clients, protected-resource discovery, or authorization-server
and resource-server metadata.

Start by identifying which role the code implements: client, authorization
server, or protected resource. Apply the security-critical rules before adding
discovery conveniences. Keep exact identifiers and transaction state available
until every binding check has completed.

## Reference index

| Reference | Topics |
| --- | --- |
| [references/authorization-security.md](references/authorization-security.md) | PKCE downgrade rejection, OIDC nonce constraints, client and user identity separation, endpoint CORS policy |
| [references/protected-resource-metadata.md](references/protected-resource-metadata.md) | Metadata URL derivation, resource binding, capability members and defaults, localization, signed metadata, reciprocal association, challenge refresh, audience restriction, SSRF defense |

## Security-critical behavior

### Reject PKCE downgrade attempts

Tie the token request to the stored authorization transaction. A token request
that contains `code_verifier` is acceptable only when the corresponding
authorization request contained `code_challenge`. Reject the request if the
verifier appears without that stored challenge; otherwise an attacker can strip
the challenge from the authorization request and downgrade the flow.

Make PKCE support discoverable, preferably through authorization-server
metadata:

```json
{
  "code_challenge_methods_supported": ["S256"]
}
```

Do not infer that the presence of a verifier repairs missing authorization-time
state. The server must correlate the verifier with the original challenge.

### Use an OIDC nonce alternative only in its narrow case

Only a confidential OpenID Connect client may use a transaction-specific
`nonce` instead of PKCE as an authorization-code injection defense. Public
clients still require PKCE.

For the confidential-client alternative:

1. Bind a fresh nonce to the authorization transaction.
2. Validate it in the ID Token returned by the token endpoint.
3. Perform that token-endpoint validation even if the authorization response
   also contained an ID Token.
4. Do not use any returned token until nonce validation succeeds.

### Keep client and resource-owner identities distinct

If client identifiers and user subject identifiers share a namespace, prevent
clients from influencing `client_id` or any other claim that could be mistaken
for a genuine resource-owner identity.

If that separation cannot be enforced, give the resource server another
unambiguous way to distinguish client-only grants from grants involving a
resource owner.

### Preserve the browser CORS boundary

Browser clients navigate to the authorization endpoint. They do not call it as
a cross-origin API, so the authorization endpoint must not support CORS.

These endpoints may support CORS for direct browser access:

| Endpoint | CORS policy |
| --- | --- |
| Token | May support CORS |
| Authorization-server or protected-resource metadata | May support CORS |
| `jwks_uri` | May support CORS |
| Dynamic client registration | May support CORS |
| Authorization | Must not support CORS |

## Protected-resource discovery

### Derive the metadata URL by insertion

A protected resource identifier is an HTTPS URL with no fragment and normally
no query. Insert `/.well-known/oauth-protected-resource` immediately after the
authority; do not append it to the complete resource path.

```text
https://resource.example.com/resource1
  -> https://resource.example.com/.well-known/oauth-protected-resource/resource1
```

Fetch that URL with `GET`. A successful response is a `200` response containing
a JSON object.

### Enforce exact resource binding

The response's required `resource` member must exactly match its context:

- For metadata-URL derivation, it equals the protected resource identifier from
  which the metadata URL was derived.
- For discovery through a `WWW-Authenticate` challenge, it equals the URL used
  for the protected-resource request.

Reject a mismatch. Compare the strings by Unicode code point after JSON
unescaping, without Unicode or URL normalization. Ignore unknown members,
encode multiple values as arrays, and omit parameters that have no values.

### Interpret capability metadata precisely

A resource can advertise authorization servers, scopes, token presentation
methods, signing capabilities, display and policy information, token binding,
Rich Authorization Request types, and DPoP requirements.

```json
{
  "resource": "https://resource.example.com",
  "authorization_servers": ["https://as1.example.com"],
  "scopes_supported": ["profile", "email"],
  "bearer_methods_supported": ["header"],
  "dpop_bound_access_tokens_required": true
}
```

Apply these absence and default rules exactly:

- `bearer_methods_supported` accepts `header`, `body`, and `query`. An empty
  array explicitly means none. Omission has no default and asserts neither
  support nor lack of support.
- `tls_client_certificate_bound_access_tokens` defaults to `false`.
- `dpop_bound_access_tokens_required` defaults to `false`.
- An omitted `resource_signing_alg_values_supported` has no default; `none` is
  forbidden when the list is present.
- `jwks_uri` is an HTTPS URL.

See the protected-resource metadata reference for the complete member set.

### Handle localized and signed metadata

Human-readable members may use BCP 47 suffixes such as `resource_name#it`.
An untagged value implies no language or script and should also be present as a
broadly displayable fallback.

```json
{
  "resource_name": "My Resource",
  "resource_name#it": "La mia bella risorsa"
}
```

`signed_metadata` is a signed or MACed JWT containing `iss`. Validate its
signature and trusted issuer before using it. Validated signed claims override
matching plain JSON members. Reject a signed metadata JWT that itself contains
`signed_metadata`.

### Refresh and cross-check associations

Protected-resource metadata may list issuer identifiers in
`authorization_servers`; authorization-server metadata may provide the inverse
`protected_resources` list. Either side may be absent or may omit supported
peers when the set is not enumerable. When a profile uses both, cross-check the
lists, but still make an application-specific trust decision about the chosen
authorization server.

A `Bearer` or `DPoP` challenge may advertise a metadata URL with
`resource_metadata`:

```http
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer resource_metadata="https://resource.example.com/.well-known/oauth-protected-resource"
```

If a later challenge contains `resource_metadata`, treat it as a signal that
the metadata may have changed. Fetch and validate it again.

### Constrain dynamically discovered trust

For clients that access multiple resource servers, request
audience-restricted tokens using Resource Indicators; the authorization server
should support them. This prevents a malicious resource from replaying a
broadly usable token at another resource.

Treat authorization-server locations learned from resource metadata as
SSRF-capable input. Apply outbound-fetch controls such as blocking internal IP
ranges, then make the application-specific issuer trust decision.

## Implementation checklist

### Client

- Classify the client as public or confidential before choosing PKCE or the
  narrow OIDC nonce alternative.
- Keep transaction-specific challenge or nonce state through the token
  response.
- Withhold every returned token until the required binding validation passes.
- Derive protected-resource metadata URLs by insertion after the authority.
- Validate the exact `resource` value before trusting any capability member.
- Distinguish omitted values from empty arrays and explicit `false` values.
- Re-fetch metadata when a later challenge advertises `resource_metadata`.
- Restrict token audiences and harden metadata-directed network fetches.

### Authorization server

- Reject `code_verifier` when the authorization transaction had no
  `code_challenge`.
- Publish supported PKCE methods so clients can detect support.
- Keep client-only and resource-owner identities distinguishable to resource
  servers.
- Do not enable CORS on the authorization endpoint.
- Cross-check reciprocal resource associations when the active profile uses
  both directions.

### Protected resource

- Return a `200` JSON object from the derived metadata endpoint.
- Set `resource` to the exact identifier required by the discovery context.
- Serialize multiple values as arrays and omit parameters with no values.
- Use the specified defaults without inventing defaults for omitted lists.
- Emit `resource_metadata` in `Bearer` or `DPoP` challenges when advertising
  discovery or signaling a metadata refresh.
- Give downstream authorization logic an unambiguous client-only versus
  resource-owner signal when identifiers could otherwise collide.

## Review and test cases

- A verifier without a stored challenge is rejected.
- A public client cannot replace PKCE with an OIDC nonce.
- A confidential nonce flow blocks token use until the token-endpoint ID Token
  validates, even when an ID Token arrived earlier.
- The authorization endpoint has no CORS behavior while eligible API endpoints
  may have it.
- Metadata URL construction preserves the resource path after the inserted
  well-known segment.
- Exact resource binding rejects strings that become equal only after
  normalization.
- Empty and omitted bearer-method lists produce different states.
- Signed claims override plain members only after signature and issuer checks.
- Nested `signed_metadata` is rejected.
- A repeated metadata challenge causes a fresh fetch and validation pass.
