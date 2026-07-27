# Document Structure and Operations

These document, navigation, operation, response, and reuse rules apply to
OpenAPI 3.2.0.

## Explicit document identity

The top-level `$self` field gives an OpenAPI document its own base URI.
Resolve relative references against that identity.

```yaml
openapi: 3.2.0
$self: https://api.example.com/openapi.yaml
```

Do not treat `$self` as descriptive metadata. It participates directly in
reference resolution. A consumer that always uses the retrieval URL as the
base can therefore resolve a relative reference incorrectly.

## Nested, purpose-specific tags

Tag Objects have three additional fields:

- `summary` provides a short display label or explanation.
- `parent` names the tag that contains this tag.
- `kind` is a free-form purpose marker. Tools can agree on conventional
  values such as `nav`, but the field is not limited to those values.

```yaml
tags:
  - name: products
    summary: Products
    kind: nav
  - name: books
    summary: Books
    parent: products
    kind: nav
```

Match `parent` to a tag's `name`; it is a name-based relationship rather than
an inline nested Tag Object.

## QUERY operations

Path Items have a first-class lowercase `query` field for the QUERY HTTP
method.

```yaml
paths:
  /items:
    query:
      operationId: queryItems
      responses:
        "200":
          summary: Results
```

Treat `query` like the other first-class operation fields when walking a Path
Item. A hard-coded operation list that ends at `trace` will miss it.

## Extension HTTP methods

Methods without first-class Path Item fields belong in
`additionalOperations`. Each map key is the correctly capitalized method
name, such as `LINK`.

```yaml
paths:
  /items:
    additionalOperations:
      LINK:
        operationId: linkItems
        responses:
          "204":
            summary: Linked
```

Do not move first-class methods into this map. They retain their ordinary
lowercase sibling fields: use `head`, for example, rather than `HEAD` under
`additionalOperations`.

Tools that enumerate operations must combine the first-class fields with the
entries in `additionalOperations`, while preserving the distinct spelling
rules of the two locations.

## Response summaries and optional descriptions

The Response Object has a short `summary` field. Its `description` field is
optional.

```yaml
responses:
  "204":
    summary: Deleted
```

A response may contain both fields when a short label and a longer
explanation are useful. Validators, generators, and type definitions must not
reject a response merely because `description` is absent.

## Reusable Media Type Objects

The Components Object has a `mediaTypes` map. Each entry is a complete Media
Type Object that can be defined once and referenced from content entries.

```yaml
components:
  mediaTypes:
    event:
      itemSchema:
        $ref: "#/components/schemas/Event"

paths:
  /events:
    get:
      responses:
        "200":
          content:
            text/event-stream:
              $ref: "#/components/mediaTypes/event"
```

Account for `components.mediaTypes` in component indexing, reference
resolution, bundling, and code generation. Its values are Media Type Objects,
not schemas.
