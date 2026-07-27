# Payloads and Serialization

These media-type, parameter, XML, example, and discriminator rules apply to
OpenAPI 3.2.0.

## Sequential media representations

A Media Type Object can use `itemSchema` to describe each repeated item in a
sequential representation. Relevant media types include:

- `text/event-stream`
- `application/jsonl`
- `application/json-seq`
- `multipart/mixed`

```yaml
content:
  text/event-stream:
    itemSchema:
      $ref: "#/components/schemas/Event"
```

`itemSchema` describes one item, not an array containing the whole stream.
Parsers and generators should keep the representation's sequential nature
instead of coercing it to a single JSON array.

## Multipart encoding

Multipart media types can use `prefixEncoding` and `itemEncoding` instead of
`encoding`.

Recognize both new fields when validating or transforming multipart Media
Type Objects. Do not require the older `encoding` field for this form.

## Whole-query-string parameters

The Parameter Object location `in: querystring` represents the entire query
string as one field. Use `content` to describe that field's media type and
schema.

```yaml
parameters:
  - name: filter
    in: querystring
    content:
      application/json:
        schema:
          type: object
          properties:
            status:
              type: string
```

This is distinct from an ordinary `in: query` parameter. Do not expand it
into separate query parameters unless an application-specific transform
explicitly requires that loss of representation.

## `allowReserved` across parameter locations

`allowReserved` is allowed on Header Objects and on Parameter Objects at any
`in` location. It takes effect where the location and style combination
would otherwise percent-encode the value.

Do not interpret the field as a universal instruction to alter every
serialization path. First determine whether the selected location and style
would perform percent-encoding.

## Header serialization

Header serialization does not use percent-encoding. This applies even though
Header Objects may carry `allowReserved`; the field does not create
percent-encoding where the header rules omit it.

Keep URI encoding helpers out of the header path unless another protocol
layer specifically calls for them.

## Cookie style

Cookie parameters support `style: cookie`. This style uses semicolon
separators and leaves data values unencoded.

```yaml
parameters:
  - name: preferences
    in: cookie
    style: cookie
    schema:
      type: object
```

A serializer that routes cookies through ordinary query-string encoding will
produce the wrong delimiters and may incorrectly encode the values.

## XML node types

XML mappings use `nodeType` with one of these values:

| Value | XML mapping |
| --- | --- |
| `element` | Element node |
| `attribute` | Attribute node |
| `text` | Text node |
| `cdata` | CDATA node |
| `none` | No node mapping |

```yaml
type: string
xml:
  nodeType: attribute
```

Use `nodeType` instead of the deprecated `attribute: true` and `wrapped:
true` fields. Arrays default to `none` for compatibility.

The `xml` keyword may occur in any Schema Object. Namespace values may be
IRIs, not only URLs in a narrower URI-shaped form. A root XML schema should
use its component name.

Schema walkers must therefore accept `xml` wherever a Schema Object is
valid, rather than only on a subset of schema types.

## Structured and serialized examples

Example Objects distinguish a structured value from its wire form:

- `dataValue` contains a structured example.
- `serializedValue` contains its serialized representation.
- `externalValue` explicitly points to a serialized value.

```yaml
examples:
  structured:
    dataValue:
      id: 42
  onTheWire:
    serializedValue: '{"id":42}'
```

Do not parse or normalize `serializedValue` merely because it resembles JSON.
It represents what goes on the wire. Conversely, preserve the data model of
`dataValue` for tooling that validates or transforms structured examples.

## Discriminator fallbacks

`Discriminator.propertyName` is optional. `defaultMapping` chooses a schema
when the discriminator property is absent or when its value has no recognized
mapping.

```yaml
discriminator:
  mapping:
    book: "#/components/schemas/Book"
  defaultMapping: "#/components/schemas/Unknown"
```

Consumers must be able to apply `defaultMapping` without first reading a
`propertyName`. It handles both the missing-property case and the
unrecognized-value case.
