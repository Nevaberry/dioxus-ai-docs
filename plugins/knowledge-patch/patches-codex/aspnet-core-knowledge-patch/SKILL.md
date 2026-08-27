---
name: aspnet-core-knowledge-patch
description: ASP.NET Core
version: "10.0"
license: MIT
metadata:
  author: Nevaberry
---


# ASP.NET Core Knowledge Patch

Use this skill when upgrading, reviewing, or implementing ASP.NET Core applications where current Blazor, OpenAPI, Minimal API, hosting, or JSON behavior matters.

## How to Apply This Skill

1. Inspect the project file and installed SDK before changing code.
2. Identify whether the app uses Blazor WebAssembly, Blazor Web App, MVC, Minimal APIs, Kestrel, or HTTP.sys.
3. Read the matching topic reference before editing configuration or compatibility code.
4. Apply removals and changed defaults before opting into new capabilities.
5. Validate behavior with the project's existing build and tests.

Treat the project manifest, code, tests, and observed runtime behavior as authoritative when they disagree with general guidance.

## Reference Index

| Reference | Topics |
| --- | --- |
| [Blazor Components, Navigation, and Circuits](references/blazor-components-navigation.md) | Navigation, routing, reconnection, JavaScript object interop, circuit state |
| [Blazor WebAssembly, Static Assets, and Tooling](references/blazor-wasm-tooling.md) | Environment selection, boot assets, caching, streaming, fingerprinting, bundlers, culture |
| [Forms, Validation, Persistent State, and Identity](references/forms-validation-state-identity.md) | Recursive validation, form binding, persisted state, passkeys, Identity redirects |
| [Hosting, Security, Compression, and Observability](references/hosting-security-observability.md) | Diagnostics, metrics, Kestrel, HTTP.sys, memory pools, integration testing |
| [OpenAPI, HTTP APIs, and JSON](references/openapi-http-apis.md) | OpenAPI generation and transformers, XML comments, schemas, JSON converters |

## Breaking Changes First

### Remove obsolete Blazor boot assumptions

Do not read or patch `blazor.boot.json`; boot configuration is inlined into `dotnet.js`. There is no documented replacement for workflows that altered that file, including published-asset integrity scripts and DLL-extension customization.

Remove `BlazorCacheBootResources` from client project files. Fingerprinted browser assets now provide caching.

```diff
- <BlazorCacheBootResources>true</BlazorCacheBootResources>
```

### Set standalone WebAssembly environments at build time

Standalone Blazor WebAssembly no longer selects its environment from the `Blazor-Environment` header, `launchSettings.json`, or `ASPNETCORE_ENVIRONMENT`. Configure the project property instead:

```xml
<WasmApplicationEnvironmentName>Staging</WasmApplicationEnvironmentName>
```

Builds default to `Development`; published output defaults to `Production`.

### Account for streamed browser responses

Blazor WebAssembly enables response streaming by default. `ReadAsStreamAsync` returns a `BrowserHttpReadStream`, which cannot perform synchronous reads. Disable streaming only where compatibility requires it:

```csharp
requestMessage.SetBrowserResponseStreamingEnabled(false);
```

Use `<WasmEnableStreamingResponse>false</WasmEnableStreamingResponse>` or `DOTNET_WASM_ENABLE_STREAMING_RESPONSE=0` for a global opt-out.

### Update OpenAPI transformer code

OpenAPI.NET 2 represents OpenAPI entities as interfaces with separate inline and reference implementations. Replace `OpenApiSchema.Nullable` checks with `JsonSchemaType.Null` checks and replace `OpenApiAny` values with `JsonNode`. These API migrations apply even when emitting an OpenAPI 3.0 document.

### Make JSON converters sequence-safe

ASP.NET Core JSON input paths now deserialize through `PipeReader`. A custom converter must handle `Utf8JsonReader.HasValueSequence` instead of assuming `ValueSpan` always contains the complete token:

```csharp
var span = reader.HasValueSequence
    ? reader.ValueSequence.ToArray()
    : reader.ValueSpan;
```

The `Microsoft.AspNetCore.UseStreamBasedJsonParsing` AppContext switch is a temporary compatibility escape hatch.

## Blazor WebAssembly Quick Reference

### Ensure the Blazor script is included

The compressed, fingerprinted Blazor script is automatically included only when the project contains a `.razor` file. Force inclusion for component-free hosts that still need it:

```xml
<RequiresAspNetWebAssets>true</RequiresAspNetWebAssets>
```

### Fingerprint standalone assets

Enable HTML placeholder replacement, add an import map, and place the fingerprint marker in the framework script path:

```xml
<OverrideHtmlAssetPlaceholders>true</OverrideHtmlAssetPlaceholders>
```

```html
<script type="importmap"></script>
<script src="_framework/blazor.webassembly#[.{fingerprint}].js"></script>
```

Developer modules can use the same `#[.{fingerprint}]` marker through a `StaticWebAssetFingerprintPattern`.

### Prepare output for JavaScript bundlers

For published output consumed by Webpack, Rollup, or a similar bundler, enable:

```xml
<WasmBundlerFriendlyBootConfig>true</WasmBundlerFriendlyBootConfig>
```

Standalone apps also load globalization resources for `CultureInfo.DefaultThreadCurrentUICulture`, not only `DefaultThreadCurrentCulture`.

## Components, Navigation, and Circuits

### Use current not-found routing

Call `NavigationManager.NotFound()` to set a 404 during static SSR or notify the interactive router. Select the page with `Router.NotFoundPage`, and use `NavigationManager.OnNotFound` for customization. The old `<NotFound>` router fragment is unsupported.

```razor
<Router AppAssembly="@typeof(Program).Assembly"
        NotFoundPage="typeof(Pages.NotFound)">
    <Found Context="routeData">
        <RouteView RouteData="routeData" />
    </Found>
</Router>
```

### Review navigation expectations

`NavigateTo` preserves scroll position for same-page query-string or fragment changes. `NavLinkMatch.All` compares only the path, so query strings and fragments no longer deactivate a link. The AppContext switch `Microsoft.AspNetCore.Components.Routing.NavLink.EnableMatchAllForQueryStringAndFragment` restores the earlier link-matching behavior.

### Integrate with reconnection state

The template `ReconnectModal` collocates its CSS and JavaScript, supporting strict CSP `style-src` policies. Listen for `components-reconnect-state-changed`; handle the added `retrying` state.

Server-side circuits can preserve unsaved state across an extended disconnect or proactive pause/resume, but not across a full-page refresh.

### Use direct JavaScript object interop

`IJSRuntime` and `IJSObjectReference` expose `InvokeConstructorAsync`, `GetValueAsync`, and `SetValueAsync`; in-process references provide synchronous equivalents.

```csharp
var instance = await JSRuntime.InvokeConstructorAsync(
    "jsInterop.TestClass", "Blazor!");
var text = await instance.GetValueAsync<string>("text");
await instance.SetValueAsync("text", "updated");
```

## Forms, State, and Identity

### Enable recursive generated validation

Call `AddValidation()`, define the model in a C# file, and annotate its root with `[ValidatableType]`. Nested objects and collections are then validated without reflection. `[SkipValidation]` excludes a property or type. For models in another assembly, both that assembly and the app must call `AddValidation()`.

```csharp
builder.Services.AddValidation();

[ValidatableType]
public sealed class Order
{
    [Required]
    public string? Number { get; set; }
}
```

For complex `[FromForm]` models, an empty string posted to a nullable value-type property now binds as `null` instead of failing to parse.

### Persist component state declaratively

Annotate component or service state with `[PersistentState]` instead of wiring every value through `PersistentComponentState`. Register `PersistentComponentStateSerializer<T>` to replace JSON serialization for a type.

Set `AllowUpdates = true` for enhanced-navigation refreshes. Use `RestoreBehavior.SkipInitialValue` or `SkipLastSnapshot` to suppress restoration during prerendering or reconnection; use `RegisterOnRestoring` for imperative control.

### Upgrade Identity behavior deliberately

Existing Blazor Web Apps can use the dedicated passkey migration path. If an older Individual Accounts app enables `<BlazorDisableThrowNavigationException>true</BlazorDisableThrowNavigationException>`, remove the `InvalidOperationException` from `RedirectTo` and remove all five `[DoesNotReturn]` attributes in `Components/Account/IdentityRedirectManager.cs`.

## OpenAPI and Hosting Defaults

Generated documents default to OpenAPI 3.1. Nullable scalar schemas use a type array containing `null`; nullable complex types and collections use `oneOf`.

The default `JsonNumberHandling.AllowReadingFromString` produces `int` and `long` schemas with a digit pattern and without `type: integer`. Configure strict number handling when downstream consumers require integer schemas.

Set `<GenerateDocumentationFile>true</GenerateDocumentationFile>` to populate OpenAPI summaries, remarks, parameter descriptions, return descriptions, and referenced-project comments. Use a documented method instead of a Minimal API lambda when the handler needs that metadata.

Transformer contexts expose `GetOrCreateSchemaAsync`; operation and schema contexts expose `Document`, allowing generated schemas to be registered with `AddComponent`.

## Diagnostics and Hosting Checks

- Handled `IExceptionHandler` exceptions suppress logs and diagnostics by default. Set `SuppressDiagnosticsCallback` when handled exceptions must still be reported.
- Authentication reports duration plus challenge, forbid, sign-in, sign-out, and authorization counts. Identity metrics come from the `Microsoft.AspNetCore.Identity` meter.
- Kestrel treats configured `*.localhost` hosts as loopback bindings. The templates support `--localhost-tld`; retrust the development certificate after adopting `*.dev.localhost`.
- `IMemoryPoolFactory<byte>` creates pools with automatic idle-block eviction. Custom factories provide eviction only if they implement it.
- `HttpSysOptions.RequestQueueSecurityDescriptor` applies only when HTTP.sys creates a new request queue; it cannot modify an existing queue.
- Top-level-statement apps should remove a manually declared `public partial class Program`; the source generator emits it for integration-test access.

## Verification Checklist

- Search project files and scripts for `blazor.boot.json` and `BlazorCacheBootResources`.
- Exercise WebAssembly callers that synchronously consume streams.
- Test query-string and fragment navigation, active links, not-found pages, and reconnection UI.
- Validate nested form models and nullable form fields.
- Generate the OpenAPI document and inspect nullable, numeric, and transformed schemas.
- Run custom JSON converters with segmented input.
- Confirm handled-exception telemetry matches operational requirements.
- Run the repository's normal build and test commands.
