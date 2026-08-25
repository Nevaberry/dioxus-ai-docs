# Migrations, Assets, and Tooling

## Standalone Blazor WebAssembly migration

### Select the environment at build or publish time

Standalone apps no longer use the `Blazor-Environment` header,
`Properties/launchSettings.json`, or `ASPNETCORE_ENVIRONMENT` to select their
environment (`10.0-migration`). Configure it in the project file:

```xml
<WasmApplicationEnvironmentName>Staging</WasmApplicationEnvironmentName>
```

A build defaults to `Development`; a publish defaults to `Production`.

### Remove `blazor.boot.json` workflows

The boot configuration is inlined into `dotnet.js`, and the separate
`blazor.boot.json` artifact no longer exists (`10.0-migration`). Direct
inspection or mutation workflows must be redesigned. This includes the
published-asset integrity script and DLL-extension customization; neither has a
documented replacement.

### Remove the custom boot-resource cache setting

Browser caching of fingerprinted client files replaces Blazor's custom cache
(`10.0-migration`). Remove `BlazorCacheBootResources` from client projects; it
is no longer available or effective.

```diff
- <BlazorCacheBootResources>...</BlazorCacheBootResources>
```

## Static web assets

### Force Blazor script inclusion without components

The Blazor script is a compressed, fingerprinted static web asset and is
included automatically only if the project contains a `.razor` file (since
10.0). A project that needs the script but has no component must opt in:

```xml
<RequiresAspNetWebAssets>true</RequiresAspNetWebAssets>
```

### Fingerprint standalone WebAssembly assets

Enable HTML asset-placeholder replacement, add an import map, and place the
fingerprint marker in the framework script filename (since 10.0):

```xml
<OverrideHtmlAssetPlaceholders>true</OverrideHtmlAssetPlaceholders>
```

```html
<script type="importmap"></script>
<script src="_framework/blazor.webassembly#[.{fingerprint}].js"></script>
```

Developer modules can use the same `#[.{fingerprint}]` marker by defining a
`StaticWebAssetFingerprintPattern`.

### Produce bundler-friendly published output

Set the following project property when published WebAssembly output must be
consumed by a JavaScript bundler such as Webpack or Rollup (since 10.0):

```xml
<WasmBundlerFriendlyBootConfig>true</WasmBundlerFriendlyBootConfig>
```

## Testing

### Let the source generator expose `Program`

For top-level-statement applications, the ASP.NET Core source generator emits
the `public partial class Program` needed by test projects (since 10.0). Remove
the manual declaration previously used for test visibility to avoid a duplicate.
