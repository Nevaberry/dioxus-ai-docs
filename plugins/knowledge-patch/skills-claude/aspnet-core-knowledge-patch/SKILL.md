---
name: aspnet-core-knowledge-patch
description: ASP.NET Core
version: 10.0
license: MIT
metadata:
  author: Nevaberry
---


# ASP.NET Core Knowledge Patch

Use this patch when implementing, reviewing, testing, or upgrading ASP.NET Core applications.
Check breaking behavior first, then open only the topic references relevant to the task.

## Index

| Reference | Topics |
| --- | --- |
| [Components, Navigation, and Interop](references/components-navigation-and-interop.md) | Blazor navigation, reconnection, JavaScript interop, streaming, component state, circuits, and culture |
| [Forms, Validation, and Persistence](references/forms-validation-and-persistence.md) | Recursive validation, form binding, and persistent component state |
| [Hosting, HTTP, Caching, and Security](references/hosting-http-caching-and-security.md) | Kestrel, HTTP.sys, memory pools, and development domains |
| [Migrations, Assets, and Tooling](references/migrations-assets-and-tooling.md) | Blazor WebAssembly migration, boot assets, fingerprinting, bundlers, and testing |
| [Observability, Identity, and SignalR](references/observability-identity-and-signalr.md) | Exception diagnostics, authentication and Identity metrics, passkeys, and Identity redirects |
| [OpenAPI, Minimal APIs, and JSON](references/openapi-minimal-apis-and-json.md) | OpenAPI 3.1, OpenAPI.NET 2, transformers, XML comments, and JSON converters |

## Breaking-change checks

### Stop depending on `blazor.boot.json`

The boot configuration is inlined into `dotnet.js`; there is no separate
`blazor.boot.json`. Workflows that inspect or mutate the old file, including
published-integrity and DLL-extension customizations, have no documented direct
replacement. Remove assumptions about that artifact before upgrading.

Also remove `BlazorCacheBootResources`. Fingerprinted browser assets now provide
the cache behavior, so the property is unavailable or ineffective.

### Audit WebAssembly response-stream consumers

Blazor WebAssembly enables response streaming by default. `ReadAsStreamAsync`
returns `BrowserHttpReadStream`, which does not support synchronous reads. Code
that expects a buffered `MemoryStream` must become asynchronous or disable
streaming per request:

```csharp
requestMessage.SetBrowserResponseStreamingEnabled(false);
```

For a temporary global opt-out, set either:

```xml
<WasmEnableStreamingResponse>false</WasmEnableStreamingResponse>
```

or `DOTNET_WASM_ENABLE_STREAMING_RESPONSE=0`.

### Migrate OpenAPI transformers to OpenAPI.NET 2

OpenAPI entities are interfaces with distinct inline and reference
implementations. Replace `OpenApiSchema.Nullable` checks with
`JsonSchemaType.Null` checks, and replace `OpenApiAny` with `JsonNode`. These
changes apply even when emitting an OpenAPI 3.0 document.

Generated documents default to OpenAPI 3.1. Nullable scalar schemas use a type
array containing `null`; nullable complex types and collections use `oneOf`.

### Preserve diagnostics for handled exceptions when needed

An exception handled by `IExceptionHandler` no longer emits logs or other
diagnostics by default. Restore reporting globally, or choose cases precisely,
through `SuppressDiagnosticsCallback`:

```csharp
app.UseExceptionHandler(new ExceptionHandlerOptions
{
    SuppressDiagnosticsCallback = context => false
});
```

### Replace the old router Not Found fragment

The old `<NotFound>` router fragment is unsupported. Set `Router.NotFoundPage`,
call `NavigationManager.NotFound()` to signal a 404, and use
`NavigationManager.OnNotFound` for custom handling.

```razor
<Router AppAssembly="@typeof(Program).Assembly"
        NotFoundPage="typeof(Pages.NotFound)">
    <Found Context="routeData">
        <RouteView RouteData="@routeData" />
    </Found>
</Router>
```

## Migration essentials

### Select a standalone WebAssembly environment in the project

Do not use the `Blazor-Environment` response header,
`Properties/launchSettings.json`, or `ASPNETCORE_ENVIRONMENT` to select the
environment of a standalone Blazor WebAssembly app. Set the MSBuild property:

```xml
<WasmApplicationEnvironmentName>Staging</WasmApplicationEnvironmentName>
```

Builds default to `Development`; published output defaults to `Production`.

### Align older Identity apps with navigation behavior

When an upgraded Individual Accounts app enables
`BlazorDisableThrowNavigationException`, remove the `InvalidOperationException`
from `RedirectTo` and all five `[DoesNotReturn]` attributes in
`Components/Account/IdentityRedirectManager.cs`.

### Remove manual test-visible `Program` declarations

The ASP.NET Core source generator emits the `public partial class Program`
needed by test projects for top-level-statement apps. Delete a manual duplicate.

## High-use implementation patterns

### Include and fingerprint Blazor static assets deliberately

The compressed, fingerprinted Blazor script is automatically included only
when the project contains a `.razor` file. Force inclusion in component-free
projects with:

```xml
<RequiresAspNetWebAssets>true</RequiresAspNetWebAssets>
```

Standalone WebAssembly apps can enable build-time fingerprinting with HTML
placeholder replacement, an import map, and a fingerprint marker:

```xml
<OverrideHtmlAssetPlaceholders>true</OverrideHtmlAssetPlaceholders>
```

```html
<script type="importmap"></script>
<script src="_framework/blazor.webassembly#[.{fingerprint}].js"></script>
```

Developer modules can use the same marker through a
`StaticWebAssetFingerprintPattern`.

### Generate recursive form validation

Register validation, place the root type in a C# file, and mark it with
`[ValidatableType]` to validate nested objects and collections without
reflection:

```csharp
builder.Services.AddValidation();

[ValidatableType]
public sealed class Order
{
    [Required]
    public string? Number { get; set; }
}
```

Use `[SkipValidation]` on excluded properties or types. When the validatable
types live in another assembly, both that assembly and the app must call
`AddValidation`.

### Prefer declarative persistent component state

Use `[PersistentState]` on component or service state instead of wiring the
full `PersistentComponentState` service pattern. Set `AllowUpdates = true` for
enhanced-navigation refreshes. Use `RestoreBehavior.SkipInitialValue` or
`SkipLastSnapshot` to suppress restoration during prerendering or reconnection,
and `RegisterOnRestoring` when imperative control is necessary.

Register `PersistentComponentStateSerializer<T>` when a type needs something
other than JSON serialization.

### Generate and register schemas inside transformers

Document, operation, and schema transformer contexts expose
`GetOrCreateSchemaAsync` for generating a schema from a C# type. Operation and
schema contexts also expose `Document`; use it with `AddComponent` to register
the generated schema.

Enable XML documentation for OpenAPI summaries, remarks, parameters, return
descriptions, and referenced-project comments:

```xml
<GenerateDocumentationFile>true</GenerateDocumentationFile>
```

Minimal API lambdas cannot carry that XML metadata, so route a documented
method as the endpoint handler.

### Make custom JSON converters sequence-aware

MVC, Minimal APIs, and `ReadFromJsonAsync` deserialize with `PipeReader`.
Converters must handle segmented values when `Utf8JsonReader.HasValueSequence`
is true:

```csharp
var span = reader.HasValueSequence
    ? reader.ValueSequence.ToArray()
    : reader.ValueSpan;
```

The `Microsoft.AspNetCore.UseStreamBasedJsonParsing` AppContext switch is a
temporary compatibility escape hatch.

### Use direct JavaScript object interop

`IJSRuntime` and `IJSObjectReference` support `InvokeConstructorAsync`,
`GetValueAsync`, and `SetValueAsync`; in-process references offer synchronous
equivalents.

```csharp
var instance = await JSRuntime.InvokeConstructorAsync(
    "jsInterop.TestClass", "Blazor!");
var text = await instance.GetValueAsync<string>("text");
await instance.SetValueAsync("text", "updated");
```

## Review reminders

- Same-page `NavigateTo` calls preserve scroll position.
- `NavLinkMatch.All` matches the path only unless its compatibility AppContext
  switch is enabled.
- A strict CSP can use the collocated `ReconnectModal` assets; listen for
  `components-reconnect-state-changed`, including the `retrying` state.
- Circuit resumption preserves server-side state across long disconnects or a
  proactive pause, but not a full-page refresh.
- For a complex `[FromForm]` value, an empty string binds to a nullable
  value-type property as `null`.
- Re-trust the development certificate before relying on `*.dev.localhost`.
- A custom `IMemoryPoolFactory<byte>` must implement idle-block eviction itself.
- An HTTP.sys request-queue security descriptor affects only a newly created
  queue.
