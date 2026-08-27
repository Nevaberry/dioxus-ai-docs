# Forms, Validation, Persistent State, and Identity

Batch attribution: `10.0-migration` and `10.0`.

## Use Recursive Source-Generated Validation

Register validation services, place the model in a C# file rather than a Razor file, and mark the root model with `[ValidatableType]`:

```csharp
builder.Services.AddValidation();

[ValidatableType]
public sealed class Order
{
    [Required]
    public string? Number { get; set; }
}
```

This validates nested objects and collections without reflection. Apply `[SkipValidation]` to a property or type that should be excluded.

When the model lives in a different assembly, that assembly and the application must both call `AddValidation()` so the required generated validation metadata exists.

## Bind Empty Nullable Form Values

For a complex `[FromForm]` parameter, an empty string posted to a nullable value-type property binds as `null`. It no longer produces a parse failure. Tests that asserted the old failure should be updated to assert successful null binding.

## Declare Prerendered State

Components and services can mark state with `[PersistentState]` rather than using the more involved `PersistentComponentState` service pattern for every value persisted during prerendering.

Register `PersistentComponentStateSerializer<T>` when a state type requires serialization other than the default JSON representation.

`[PersistentState]` supports the following controls:

- `AllowUpdates = true` updates state across enhanced-navigation refreshes.
- `RestoreBehavior.SkipInitialValue` suppresses restoration during prerendering.
- `RestoreBehavior.SkipLastSnapshot` suppresses restoration during reconnection.
- `RegisterOnRestoring` provides imperative restoration control.

## Add Passkeys to an Existing App

Existing Blazor Web Apps can adopt passkey authentication through the dedicated migration path. Treat this as an Identity migration rather than assuming that updating package references alone modifies an existing account UI and data flow.

## Update Identity Redirects

The current Blazor Web App template enables:

```xml
<BlazorDisableThrowNavigationException>true</BlazorDisableThrowNavigationException>
```

When an older Individual Accounts app opts into this behavior during upgrade, edit `Components/Account/IdentityRedirectManager.cs`:

1. Remove the `InvalidOperationException` thrown by `RedirectTo`.
2. Remove all five `[DoesNotReturn]` attributes.

Leaving those declarations in place misrepresents control flow now that static SSR navigation no longer uses the navigation exception.
