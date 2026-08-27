# OpenAPI, Minimal APIs, and JSON

## OpenAPI document and schema behavior

### Account for OpenAPI 3.1 defaults

Generated documents default to OpenAPI 3.1 (since 10.0). Nullable scalar
schemas represent the type as an array that includes `null`; nullable complex
types and collections use `oneOf`.

ASP.NET Core's default `JsonNumberHandling.AllowReadingFromString` changes the
schema for `int` and `long`: it uses a digit pattern without
`type: integer`. Configure number handling as `Strict` when consumers require
integer schemas.

### Migrate transformers to OpenAPI.NET 2

OpenAPI entities are interfaces with separate inline and reference
implementations (since 10.0). Update transformer code even when the generated
document is configured for OpenAPI 3.0:

- Replace `OpenApiSchema.Nullable` with a check for `JsonSchemaType.Null`.
- Replace `OpenApiAny` values with `JsonNode`.
- Handle inline and referenced implementations instead of assuming one concrete
  entity class.

### Generate and register schemas in transformers

Document, operation, and schema transformer contexts expose
`GetOrCreateSchemaAsync` to generate a schema from a C# type (since 10.0).
Operation and schema contexts also expose `Document`. Use that document with
`AddComponent` when the generated schema must be registered as a component.

## Documentation metadata

### Populate OpenAPI from XML comments

Enable the documentation file to let the OpenAPI source generator populate
summaries, remarks, parameter descriptions, return descriptions, and comments
from referenced projects (since 10.0):

```xml
<GenerateDocumentationFile>true</GenerateDocumentationFile>
```

Minimal API lambdas cannot carry this XML metadata. Use a documented method as
the endpoint handler when the generated operation needs the comments.

## Minimal API and JSON behavior

### Make converters compatible with `PipeReader`

MVC, Minimal APIs, and `ReadFromJsonAsync` deserialize through `PipeReader`
(since 10.0). Custom `JsonConverter` implementations must not assume that token
data always resides in `Utf8JsonReader.ValueSpan`; use `ValueSequence` when
`HasValueSequence` is true:

```csharp
var span = reader.HasValueSequence
    ? reader.ValueSequence.ToArray()
    : reader.ValueSpan;
```

As a temporary fallback, set the
`Microsoft.AspNetCore.UseStreamBasedJsonParsing` AppContext switch to `true`.
