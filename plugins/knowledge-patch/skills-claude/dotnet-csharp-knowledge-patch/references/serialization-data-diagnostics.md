# Serialization, Data, and Diagnostics

Compatibility notes are attributed to `10.0-guides`; new APIs and behaviors are from
`10.0`.

## Serialization Validation

`System.Text.Json` checks for property-name conflicts. Models whose CLR members map
to the same JSON name can now fail contract creation or serialization. Include naming
policies, attributes, inheritance, and generated metadata when auditing collisions.

`XmlSerializer` no longer ignores properties marked with `ObsoleteAttribute`. Such
properties can enter the serialized contract. Marking a property obsolete is not a
wire-contract exclusion mechanism; use the serializer's supported ignore controls
when exclusion is required.

## Source-Generated JSON Reference Handling

In `10.0`, `JsonSourceGenerationOptionsAttribute.ReferenceHandler` can select a
`JsonKnownReferenceHandler`. This allows generated contexts to preserve references
instead of throwing when the object graph contains cycles.

```csharp
[JsonSourceGenerationOptions(ReferenceHandler = JsonKnownReferenceHandler.Preserve)]
[JsonSerializable(typeof(Node))]
partial class AppJsonContext : JsonSerializerContext;
```

Choose the generated reference policy as part of the wire contract; preserved output
contains reference metadata that consumers must understand.

## Strict and Duplicate-Safe JSON

In `10.0`, setting `AllowDuplicateProperties = false` makes serializers,
`JsonObject`, dictionaries, and `JsonDocument` reject duplicate names with
`JsonException`.

```csharp
var options = new JsonSerializerOptions { AllowDuplicateProperties = false };
var value = JsonSerializer.Deserialize<Model>(json, options);
```

The `JsonSerializerOptions.Strict` preset additionally:

- disallows unmapped members;
- retains case-sensitive property binding;
- enforces nullable annotations; and
- enforces required constructor parameters.

Adopt strictness with contract tests because inputs previously accepted by permissive
settings can fail.

## Diagnostics Schema and Rate-Limited Sampling

In `10.0`, `ActivitySource` and `Meter` can carry a telemetry schema URL.
`ActivitySourceOptions` provides the constructor path when multiple options must be
set together. Keep the schema URL aligned with the emitted attribute/event contract.

Out-of-process `Activity` serialization includes events and links. Update collectors,
payload-size assumptions, and tests that previously expected only core activity data.

EventSource trace aggregators can cap root activities per second with a filter such
as:

```text
[AS]*/-ParentRateLimitingSampler(100)
```

Select a limit appropriate for expected root-activity volume and verify the effect on
trace completeness.

## Named EF Core Query Filters

EF Core 10 supports multiple named query filters per entity type and selective
disabling of individual filters. Use names when a request must bypass one concern,
such as soft deletion, while retaining another, such as tenant isolation. Do not use
the all-filters disable path when only one filter should be removed.
