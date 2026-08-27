# Serialization, Hosting, Configuration, and Data

Compatibility guidance is attributed to `10.0-guides`; new APIs are attributed
to `10.0`.

## Hosting, Configuration, and Logging Compatibility

- All of `BackgroundService.ExecuteAsync` now executes as a `Task`; synchronous
  work before the first await no longer receives special startup treatment.
- Configuration preserves null values.
- `ProviderAliasAttribute` moved to
  `Microsoft.Extensions.Logging.Abstractions`.
- Trim-related `DynamicallyAccessedMembers` annotations were removed from
  trim-unsafe `Microsoft.Extensions.Configuration` code. Treat those paths as
  trim unsafe and validate published output.
- The ICU override variable is `DOTNET_ICU_VERSION_OVERRIDE`.

## Serialization Compatibility

`System.Text.Json` checks for property-name conflicts. `XmlSerializer` no longer
ignores properties marked with `ObsoleteAttribute`, so those properties can enter
the serialized contract. Re-test payload shape and compatibility rather than
assuming an obsolete member remains excluded.

## Source-Generated JSON Reference Handling

`JsonSourceGenerationOptionsAttribute.ReferenceHandler` can select a
`JsonKnownReferenceHandler`. Generated contexts can therefore preserve references
instead of throwing when they encounter cycles.

```csharp
[JsonSourceGenerationOptions(ReferenceHandler = JsonKnownReferenceHandler.Preserve)]
[JsonSerializable(typeof(Node))]
partial class AppJsonContext : JsonSerializerContext;
```

## Strict and Duplicate-Safe JSON

Set `AllowDuplicateProperties = false` to make serializers, `JsonObject`,
dictionaries, and `JsonDocument` reject duplicate names with `JsonException`.
The `JsonSerializerOptions.Strict` preset also disallows unmapped members, keeps
case-sensitive binding, and enforces nullable annotations and required
constructor parameters.

```csharp
var options = new JsonSerializerOptions { AllowDuplicateProperties = false };
var value = JsonSerializer.Deserialize<Model>(json, options);
```

## Named EF Core Query Filters

EF Core 10 supports multiple named query filters per entity type. Disable a
specific filter selectively when a query must bypass one policy while retaining
the others, rather than disabling every filter on the entity.
