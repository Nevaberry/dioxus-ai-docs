# Forms, Validation, and Persistence

## Source-generated validation

### Validate nested objects and collections

Register the validation services, define the model in a C# file rather than a
Razor file, and annotate its root with `[ValidatableType]` (since 10.0). This
enables recursive validation of nested objects and collections without
reflection.

```csharp
builder.Services.AddValidation();

[ValidatableType]
public sealed class Order
{
    [Required]
    public string? Number { get; set; }
}
```

Apply `[SkipValidation]` to a property or type that must be excluded. If a
validatable model belongs to another assembly, call `AddValidation` in that
assembly and in the application.

### Bind empty form fields to nullable values

For a complex `[FromForm]` parameter, an empty string posted to a nullable
value-type property binds as `null` instead of causing a parse failure (since
10.0). Keep explicit validation when `null` is not acceptable; do not rely on a
binding error to reject the empty value.

## Persistent component state

### Declare prerendered state

Components and services can mark state with `[PersistentState]`
(`10.0-migration`). Prefer this declarative approach when it can replace manual
coordination through `PersistentComponentState`.

### Control updates, restoration, and serialization

`[PersistentState]` has controls for later lifecycle transitions (since 10.0):

- Set `AllowUpdates = true` to accept state updates during enhanced-navigation
  refreshes.
- Use `RestoreBehavior.SkipInitialValue` to suppress restoration during
  prerendering.
- Use `RestoreBehavior.SkipLastSnapshot` to suppress restoration during
  reconnection.
- Use `RegisterOnRestoring` for imperative restoration control.

Register `PersistentComponentStateSerializer<T>` to replace JSON serialization
for a particular state type.
