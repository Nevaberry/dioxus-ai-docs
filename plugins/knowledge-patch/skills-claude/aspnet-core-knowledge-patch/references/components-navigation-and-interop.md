# Components, Navigation, and Interop

## Navigation and routing

### Same-page navigation preserves scroll position

`NavigationManager.NavigateTo` no longer scrolls to the top when navigation
stays on the current page and changes only a query string or fragment (since
10.0). Do not add scroll-restoration workarounds unless the application actually
requires a reset.

### `NavLinkMatch.All` matches only the path

`NavLinkMatch.All` ignores the query string and fragment, so the link remains
active while either changes (since 10.0). Restore the earlier whole-URI match
with this AppContext switch:

```text
Microsoft.AspNetCore.Components.Routing.NavLink.EnableMatchAllForQueryStringAndFragment
```

Set the switch to `true` before the affected navigation logic runs.

### Not Found routing

`NavigationManager.NotFound()` sets the 404 status during static SSR and signals
the router during interactive rendering (since 10.0). Set `Router.NotFoundPage`
to choose the routed component and subscribe to `NavigationManager.OnNotFound`
when custom behavior is required. The old `<NotFound>` router fragment is not
supported.

```razor
<Router AppAssembly="@typeof(Program).Assembly"
        NotFoundPage="typeof(Pages.NotFound)">
    <Found Context="routeData">
        <RouteView RouteData="@routeData" />
    </Found>
</Router>
```

## Reconnection and circuit state

### Reconnection notifications

The template `ReconnectModal` collocates CSS and JavaScript instead of injecting
styles, allowing strict CSP `style-src` policies (since 10.0). Reconnection
transitions dispatch the `components-reconnect-state-changed` browser event.
Handle the `retrying` state as well as the other reconnection states.

### Server circuit resumption

A server-side Blazor circuit can retain unsaved state across an extended lost
connection or a proactive pause and resume (since 10.0). A full-page refresh
still discards the circuit, so do not treat resumption as durable persistence.

## Browser HTTP and JavaScript interop

### Streaming WebAssembly responses

Response streaming is enabled by default in Blazor WebAssembly (since 10.0).
`ReadAsStreamAsync` returns `BrowserHttpReadStream`, not `MemoryStream`, and the
browser stream rejects synchronous reads. Prefer asynchronous consumers.

Disable streaming for one request when a dependency requires buffering:

```csharp
requestMessage.SetBrowserResponseStreamingEnabled(false);
```

Disable it globally with either project configuration or an environment flag:

```xml
<WasmEnableStreamingResponse>false</WasmEnableStreamingResponse>
```

```text
DOTNET_WASM_ENABLE_STREAMING_RESPONSE=0
```

### Direct JavaScript object access

`IJSRuntime` and `IJSObjectReference` can construct objects and access
properties with `InvokeConstructorAsync`, `GetValueAsync`, and `SetValueAsync`
(since 10.0). In-process references provide synchronous equivalents.

```csharp
var instance = await JSRuntime.InvokeConstructorAsync(
    "jsInterop.TestClass", "Blazor!");
var text = await instance.GetValueAsync<string>("text");
await instance.SetValueAsync("text", "updated");
```

## Globalization

### UI-culture resources in standalone WebAssembly

Standalone Blazor WebAssembly apps load globalization resources for
`CultureInfo.DefaultThreadCurrentUICulture` as well as
`DefaultThreadCurrentCulture` (since 10.0). Account for both values when
choosing which satellite resources must ship.
