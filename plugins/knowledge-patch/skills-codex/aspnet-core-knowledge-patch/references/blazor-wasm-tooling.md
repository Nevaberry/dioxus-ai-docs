# Blazor WebAssembly, Static Assets, and Tooling

Batch attribution: `10.0-migration` and `10.0`.

## Select the Standalone App Environment

Standalone Blazor WebAssembly apps do not select the environment from the `Blazor-Environment` header, `Properties/launchSettings.json`, or `ASPNETCORE_ENVIRONMENT`. Set it in the project file:

```xml
<WasmApplicationEnvironmentName>Staging</WasmApplicationEnvironmentName>
```

A build defaults to `Development`, while a publish defaults to `Production`.

## Stop Depending on `blazor.boot.json`

The standalone `blazor.boot.json` asset no longer exists. Its content is inlined into `dotnet.js`.

Workflows that directly inspected or changed `blazor.boot.json` must not assume a replacement file. No documented replacement exists for the published-asset integrity script or DLL-extension customization based on editing that file.

## Remove the Custom Boot-Resource Cache Setting

Browser caching of fingerprinted client files replaces Blazor's custom caching mechanism. `BlazorCacheBootResources` is unavailable or ineffective and must be removed:

```diff
- <BlazorCacheBootResources>...</BlazorCacheBootResources>
```

## Include the Blazor Script Without Components

The Blazor script is a compressed, fingerprinted static web asset. It is included automatically only when the project contains a `.razor` file.

If an app contains no component but still needs the script, force static-web-asset inclusion:

```xml
<RequiresAspNetWebAssets>true</RequiresAspNetWebAssets>
```

## Handle Streaming HTTP Responses

Response streaming is enabled by default in Blazor WebAssembly. `ReadAsStreamAsync` returns `BrowserHttpReadStream`, not `MemoryStream`, and the browser stream does not support synchronous reads.

Opt out for one request when a dependency requires the older buffered behavior:

```csharp
requestMessage.SetBrowserResponseStreamingEnabled(false);
```

For a global opt-out, use either:

```xml
<WasmEnableStreamingResponse>false</WasmEnableStreamingResponse>
```

```text
DOTNET_WASM_ENABLE_STREAMING_RESPONSE=0
```

## Fingerprint Standalone Assets

Standalone apps can opt into build-time fingerprinting by enabling HTML placeholder replacement, adding an import map, and placing the fingerprint marker in the framework script name:

```xml
<OverrideHtmlAssetPlaceholders>true</OverrideHtmlAssetPlaceholders>
```

```html
<script type="importmap"></script>
<script src="_framework/blazor.webassembly#[.{fingerprint}].js"></script>
```

Developer modules can use the same `#[.{fingerprint}]` marker with a `StaticWebAssetFingerprintPattern`.

## Publish Bundler-Friendly Output

Enable bundler-friendly boot configuration when published output will be consumed by Webpack, Rollup, or a similar JavaScript bundler:

```xml
<WasmBundlerFriendlyBootConfig>true</WasmBundlerFriendlyBootConfig>
```

## Load UI Culture Resources

Standalone apps load globalization resources for `CultureInfo.DefaultThreadCurrentUICulture` as well as `DefaultThreadCurrentCulture`. Include the UI-culture setting when diagnosing missing localized resources.
