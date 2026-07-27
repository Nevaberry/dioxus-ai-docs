---
name: openapi-knowledge-patch
description: OpenAPI
version: "3.2.0"
license: MIT
metadata:
  author: Nevaberry
---

# OpenAPI Knowledge Patch

Load this skill when authoring, reviewing, validating, or generating from an
OpenAPI document. Start with the behavior changes and deprecations below, then
open the topic reference that matches the part of the document being changed.

## Reference index

| Reference | Topics |
| --- | --- |
| [Document structure and operations](references/document-structure-and-operations.md) | Document identity, nested tags, QUERY and extension methods, responses, reusable media types |
| [Payloads and serialization](references/payloads-and-serialization.md) | Sequential and multipart media, whole-query-string parameters, parameter and header serialization, XML, examples, discriminators |
| [Security, servers, and validation](references/security-servers-and-validation.md) | OAuth device authorization, security-scheme metadata and references, named servers, template grammar, JSON Schema and HTTP references |

## Behavior changes and deprecations

### Prefer `xml.nodeType`

Use `nodeType` to say how a schema maps to XML. The available values are
`element`, `attribute`, `text`, `cdata`, and `none`.

```yaml
type: string
xml:
  nodeType: attribute
```

Do not introduce `attribute: true` or `wrapped: true`; both are deprecated.
Arrays default to `nodeType: none` for compatibility. The `xml` keyword is
valid on any Schema Object, namespace values may be IRIs, and a root XML
schema should use its component name.

### Apply serialization rules by location and style

`allowReserved` is valid on Header Objects and on parameters at any `in`
location. It matters only when the chosen location and style would otherwise
percent-encode a value. Header serialization itself does not use
percent-encoding.

Cookie parameters can select `style: cookie`. That style separates values
with semicolons and leaves data values unencoded.

```yaml
parameters:
  - name: preferences
    in: cookie
    style: cookie
    schema:
      type: object
```

### Respect the tightened Server Object rules

A Server Object may have `name`. Keep its `url` free of query and fragment
components, and do not repeat a server variable in the URL.

```yaml
servers:
  - name: production
    url: https://{region}.example.com
    variables:
      region:
        default: eu
```

Server substitution, path templating, and Link Object runtime expressions now
have formal ABNF grammars. Follow those grammars when implementing a parser,
validator, renderer, or generator.

### Update validators and HTTP handling

Use `draft-bhutton-json-schema-01` for JSON Schema core,
`draft-bhutton-json-schema-validation-01` for JSON Schema validation, and RFC
9110 for HTTP semantics. Do not validate these documents against older
referenced drafts merely because an earlier toolchain did so.

## Document identity and navigation

### Set an explicit base URI with `$self`

Top-level `$self` gives the document an identity and supplies the base URI for
relative reference resolution.

```yaml
openapi: 3.2.0
$self: https://api.example.com/openapi.yaml
```

Use this identity when resolving relative references rather than assuming the
retrieval location is always the intended base.

### Build nested, purpose-specific tag structures

Tag Objects accept `summary`, `parent`, and free-form `kind`. A `parent` value
names the containing tag. `kind` lets tooling recognize a conventional
purpose, such as `nav`, without restricting other values.

```yaml
tags:
  - name: products
    summary: Products
    kind: nav
  - name: books
    parent: products
    kind: nav
```

## Operations and responses

### Represent QUERY and extension methods correctly

Use the lowercase `query` Path Item field for a QUERY operation. Put other
extension HTTP methods in `additionalOperations`, keyed by their correctly
capitalized method names.

```yaml
paths:
  /items:
    query:
      operationId: queryItems
    additionalOperations:
      LINK:
        operationId: linkItems
```

First-class methods remain ordinary lowercase sibling fields. For example,
use `head`, not a `HEAD` entry in `additionalOperations`.

### Use concise responses when appropriate

A Response Object no longer requires `description`, and it can carry a short
`summary`.

```yaml
responses:
  "204":
    summary: Deleted
```

Keep a description when it adds useful detail; do not synthesize one solely
to satisfy an outdated validator.

## Media types and parameters

### Describe sequential representations with `itemSchema`

Media Type Objects use `itemSchema` for each repeated item in a sequential
representation, including `text/event-stream`, `application/jsonl`,
`application/json-seq`, and `multipart/mixed`.

```yaml
content:
  text/event-stream:
    itemSchema:
      $ref: "#/components/schemas/Event"
```

For multipart media types, use `prefixEncoding` and `itemEncoding` in place
of the older `encoding` field.

### Reuse complete Media Type Objects

Define reusable Media Type Objects under `components.mediaTypes`, then
reference them from content entries.

```yaml
components:
  mediaTypes:
    event:
      itemSchema:
        $ref: "#/components/schemas/Event"
```

### Model the whole query string as one value

Use `in: querystring` when one Parameter Object represents the entire query
string. Describe its representation with `content`, rather than splitting it
into separate query parameters.

```yaml
parameters:
  - name: filter
    in: querystring
    content:
      application/json:
        schema:
          type: object
```

## Examples and schema selection

### Separate structured and wire examples

Example Objects use `dataValue` for structured data and `serializedValue` for
the wire representation. An existing `externalValue` also denotes a
serialized value.

```yaml
examples:
  structured:
    dataValue:
      id: 42
  onTheWire:
    serializedValue: '{"id":42}'
```

Choose the field that matches whether consumers need data to process or bytes
to send.

### Provide a discriminator fallback

`Discriminator.propertyName` is optional. Use `defaultMapping` to select a
schema when the property is missing or its value is unrecognized.

```yaml
discriminator:
  defaultMapping: "#/components/schemas/Unknown"
```

## Security quick reference

OAuth 2.0 flows can use `deviceAuthorization` with
`deviceAuthorizationUrl`, `tokenUrl`, and `scopes`. Security Scheme Objects
also support `oauth2MetadataUrl` and `deprecated`.

```yaml
type: oauth2
oauth2MetadataUrl: https://auth.example.com/.well-known/oauth-authorization-server
flows:
  deviceAuthorization:
    deviceAuthorizationUrl: https://auth.example.com/device
    tokenUrl: https://auth.example.com/token
    scopes: {}
```

A security scheme may be referenced by URI instead of being declared under
components. Preserve that form in resolvers and generators.
