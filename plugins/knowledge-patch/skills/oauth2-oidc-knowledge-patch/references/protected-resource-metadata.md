# Protected-Resource Metadata and Discovery

Source attribution: RFC 9728 (`rfc9728`).

Use this reference to implement protected-resource metadata producers and
consumers, challenge-based discovery, signed metadata, and trust controls for
dynamically learned authorization servers.

## Resource identifier and metadata URL

A protected resource identifier is an HTTPS URL without a fragment and normally
without a query. Derive its metadata URL by inserting
`/.well-known/oauth-protected-resource` after the authority. Do not append the
well-known path to the end of the resource identifier.

```text
https://resource.example.com/resource1
  -> https://resource.example.com/.well-known/oauth-protected-resource/resource1
```

The client sends `GET` to the derived URL. A successful response is a `200`
response whose body is a JSON object.

## Exact resource binding

Every metadata document has a required `resource` member. Its required value
depends on how the document was located:

| Discovery path | Required `resource` value |
| --- | --- |
| Client derived the metadata URL from an identifier | Exactly the identifier used for derivation |
| Client followed `resource_metadata` from a `WWW-Authenticate` challenge | Exactly the URL used for the protected-resource request |

Reject the document when the value differs. Compare strings by Unicode code
point after JSON unescaping, without normalization. Do not apply Unicode
normalization or URL normalization before this equality check.

When producing or consuming the JSON document:

- Ignore unknown members.
- Represent parameters with multiple values as arrays.
- Omit parameters that have no values.

## Capability members

Protected-resource metadata can advertise:

| Member or category | Meaning and constraint |
| --- | --- |
| `resource` | Required protected-resource identifier and exact binding value |
| `authorization_servers` | Authorization-server issuer identifiers associated with the resource |
| `jwks_uri` | HTTPS location of the resource's JSON Web Key Set |
| `scopes_supported` | Scopes understood by the resource |
| `bearer_methods_supported` | Bearer-token presentation methods: `header`, `body`, or `query` |
| `resource_signing_alg_values_supported` | Algorithms usable for signed resource responses; `none` is forbidden |
| `resource_name` | Human-readable resource name, optionally accompanied by localized variants |
| Documentation, policy, and terms URLs | Human-facing resource information |
| `tls_client_certificate_bound_access_tokens` | Whether certificate-bound access tokens are supported |
| `authorization_details_types_supported` | Supported Rich Authorization Request detail types |
| `dpop_signing_alg_values_supported` | Supported DPoP proof signing algorithms |
| `dpop_bound_access_tokens_required` | Whether DPoP-bound access tokens are required |

Example:

```json
{
  "resource": "https://resource.example.com",
  "authorization_servers": ["https://as1.example.com"],
  "scopes_supported": ["profile", "email"],
  "bearer_methods_supported": ["header"],
  "dpop_bound_access_tokens_required": true
}
```

## Defaults and absence semantics

Do not collapse omitted members, empty arrays, and explicit booleans into one
state.

### Bearer presentation methods

An empty `bearer_methods_supported` array explicitly means the resource supports
none of the listed presentation methods. If the member is omitted, there is no
default: omission says neither that a method is supported nor that it is
unsupported.

### Token-binding flags

Both token-binding booleans default to `false` when omitted:

- `tls_client_certificate_bound_access_tokens`
- `dpop_bound_access_tokens_required`

### Resource-response signing algorithms

An omitted `resource_signing_alg_values_supported` list has no default. If the
list is present, it must not contain `none`.

## Localized human-readable metadata

Human-readable members can carry a language suffix formed with `#` and a BCP 47
language tag, for example `resource_name#it`.

```json
{
  "resource_name": "My Resource",
  "resource_name#it": "La mia bella risorsa"
}
```

An untagged value has no implied language or script. Supply an untagged value as
the broadly displayable fallback in addition to localized variants.

## Signed metadata precedence

`signed_metadata` is a signed or MACed JWT containing an `iss` claim. Before
using its claims:

1. Validate the JWT signature or MAC.
2. Validate that `iss` is a trusted issuer.
3. Only then allow its claims to override matching members in the plain JSON
   document.

Reject a signed metadata JWT that includes its own `signed_metadata` claim. This
prevents recursive nesting of signed metadata.

## Reciprocal authorization-server association

The resource-to-server direction uses `authorization_servers` in
protected-resource metadata. Authorization-server metadata can publish the
inverse `protected_resources` array of protected resource identifiers.

Neither list is necessarily exhaustive:

- Either list may be absent.
- Either list may omit supported peers.
- Absence or omission can be necessary when the full set is not enumerable.

When a profile uses both directions, cross-check the associations. A matching
association is still not a complete trust decision: the client needs an
application-specific rule for deciding which authorization server is
appropriate.

## Challenge-based discovery and refresh

A protected resource can advertise its metadata URL through the
`resource_metadata` authentication parameter in a challenge. The parameter can
appear under either the `Bearer` or `DPoP` authentication scheme.

```http
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer resource_metadata="https://resource.example.com/.well-known/oauth-protected-resource"
```

Validate the fetched document using the challenge-specific exact binding rule:
its `resource` value must equal the URL used for the resource request.

If a later challenge includes `resource_metadata`, treat it as notice that the
metadata may have changed. Fetch and validate the document again rather than
continuing indefinitely with the cached copy.

## Security boundaries for dynamic discovery

### Audience-restricted access tokens

When a client accesses multiple resource servers, it should request
audience-restricted tokens using Resource Indicators. The authorization server
should support Resource Indicators for this use. Audience restriction prevents
a malicious resource server from replaying a broadly usable token at a
different resource server.

### SSRF-capable authorization-server locations

Authorization-server locations learned from resource metadata are untrusted
network destinations until policy accepts them. Treat follow-up metadata fetches
as SSRF-capable input. Apply controls such as blocking internal IP ranges, and
separately make the application-specific trust decision for the authorization
server.

## Validation checklist

- The resource identifier uses HTTPS, has no fragment, and normally has no
  query.
- URL derivation inserts the well-known segment after the authority.
- A successful endpoint response is a `200` JSON object.
- `resource` is checked against the correct discovery context with exact,
  non-normalizing comparison.
- Unknown members are ignored; multivalued parameters are arrays; valueless
  parameters are omitted.
- Empty and omitted bearer-method lists remain distinguishable.
- Both token-binding boolean defaults and the no-default signing-algorithm case
  are implemented independently.
- `jwks_uri` is HTTPS and the signing-algorithm list never contains `none`.
- Signed claims take precedence only after signature or MAC and issuer trust
  validation.
- Nested `signed_metadata` is rejected.
- Reciprocal associations are cross-checked without replacing application trust
  policy.
- A later `resource_metadata` challenge triggers re-fetch and revalidation.
- Tokens are audience restricted and metadata-directed fetches have SSRF
  controls.
