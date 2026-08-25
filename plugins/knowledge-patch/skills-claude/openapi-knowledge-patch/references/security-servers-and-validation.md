# Security, Servers, and Validation

These security, server, grammar, and validation rules apply to OpenAPI 3.2.0.

## OAuth 2.0 device authorization

OAuth 2.0 flows support `deviceAuthorization`. The flow contains
`deviceAuthorizationUrl`, `tokenUrl`, and `scopes`.

```yaml
type: oauth2
flows:
  deviceAuthorization:
    deviceAuthorizationUrl: https://auth.example.com/device
    tokenUrl: https://auth.example.com/token
    scopes: {}
```

Include this flow in Security Scheme Object schemas, validators, renderers,
and client-generation logic. Do not assume the established authorization
code, implicit, password, and client credentials fields exhaust the possible
OAuth flow names.

## OAuth metadata and deprecation

Security Scheme Objects have:

- `oauth2MetadataUrl`, which points to OAuth 2.0 authorization-server
  metadata.
- `deprecated`, which marks the security scheme as deprecated.

```yaml
type: oauth2
oauth2MetadataUrl: https://auth.example.com/.well-known/oauth-authorization-server
deprecated: false
flows:
  deviceAuthorization:
    deviceAuthorizationUrl: https://auth.example.com/device
    tokenUrl: https://auth.example.com/token
    scopes: {}
```

Expose the deprecation signal to documentation and migration tooling rather
than discarding it as an unknown extension.

## URI-referenced security schemes

A security scheme can be referenced by URI instead of being declared under
`components`.

Resolvers, bundlers, validators, and generators must accept this form and
resolve the URI. Do not require every usable security scheme to have a local
`components.securitySchemes` entry.

## Named servers

Server Objects have a `name` field.

```yaml
servers:
  - name: production
    url: https://{region}.example.com
    variables:
      region:
        default: eu
```

Keep the name available to documentation, selection interfaces, and other
tools instead of treating it as an unrecognized property.

## Server URL constraints

A Server Object URL must contain neither a query component nor a fragment.
Each server variable may occur only once in that URL.

For example, the following shape obeys both constraints:

```yaml
servers:
  - name: regional
    url: https://{region}.example.com
    variables:
      region:
        default: eu
```

Validate the URL template before substitution as well as the substituted
result where appropriate. Do not accept repeated appearances of `{region}`
in one server URL.

## Formal template and expression grammars

The specification defines formal ABNF grammars for:

- Server Object variable substitution
- Path templating
- Link Object runtime expressions

Parser and validator implementations should follow those grammars rather
than relying on one permissive, shared brace-matching expression for all
three syntaxes. Each context has its own grammar and must be diagnosed in
that context.

## JSON Schema references

The referenced JSON Schema documents are:

- `draft-bhutton-json-schema-01` for core
- `draft-bhutton-json-schema-validation-01` for validation

Update validator registries, metaschema resolution, and documentation links
that still assume an older referenced draft. Schema behavior should be
checked against these references when the OpenAPI dialect delegates to JSON
Schema.

## HTTP semantics

The HTTP reference is RFC 9110.

Use RFC 9110 terminology and semantics in HTTP-aware validation and
generation. A tool that pins its OpenAPI handling to an older HTTP reference
can misclassify methods, fields, or semantics even when the document syntax
itself parses successfully.
