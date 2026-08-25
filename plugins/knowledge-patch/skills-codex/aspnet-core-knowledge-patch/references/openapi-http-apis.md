# OpenAPI, HTTP APIs, and JSON

Batch attribution: `10.0`.

## Generate OpenAPI 3.1 Schemas

Generated documents default to OpenAPI 3.1.

- Nullable scalar types use a type array that contains `null`.
- Nullable complex types and collections use `oneOf`.
- With the default `JsonNumberHandling.AllowReadingFromString`, `int` and `long` schemas use a digit pattern without `type: integer`.

Configure JSON number handling as `Strict` when consumers require integer schemas instead of the default string-readable numeric representation.

## Migrate OpenAPI.NET Transformer Code

OpenAPI.NET 2 changes the APIs consumed by document, operation, and schema transformers:

- OpenAPI entities are interfaces with separate inline and reference implementations.
- `OpenApiSchema.Nullable` is replaced by checking for `JsonSchemaType.Null`.
- `OpenApiAny` is replaced by `JsonNode`.

Make these code changes even if `OpenApiVersion` is configured to emit OpenAPI 3.0. The transformer object model and the emitted specification version are separate concerns.

## Populate Documentation from XML Comments

Enable the documentation file in the project:

```xml
<GenerateDocumentationFile>true</GenerateDocumentationFile>
```

The OpenAPI source generator can then populate summaries, remarks, parameter descriptions, return descriptions, and comments from referenced projects.

Minimal API lambdas cannot carry this XML documentation metadata. Use a documented method as the endpoint handler when the generated operation needs it.

## Generate and Register Schemas in Transformers

Document, operation, and schema transformer contexts expose `GetOrCreateSchemaAsync` for generating a schema from a C# type.

Operation and schema transformer contexts also expose `Document`. Use the returned document with `AddComponent` when the generated schema must be registered as a reusable component.

## Read JSON from Segmented Input

MVC, Minimal APIs, and `ReadFromJsonAsync` deserialize through `PipeReader`. A custom `JsonConverter` must handle tokens split across multiple segments:

```csharp
var span = reader.HasValueSequence
    ? reader.ValueSequence.ToArray()
    : reader.ValueSpan;
```

Code that always consumes `Utf8JsonReader.ValueSpan` can silently lose token data when `HasValueSequence` is `true`.

For temporary compatibility while converters are being corrected, set the following AppContext switch to `true`:

```text
Microsoft.AspNetCore.UseStreamBasedJsonParsing
```
