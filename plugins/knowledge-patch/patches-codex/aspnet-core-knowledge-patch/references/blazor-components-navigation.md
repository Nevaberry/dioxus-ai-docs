# Blazor Components, Navigation, and Circuits

Batch attribution: `10.0`.

## Navigate Within the Same Page

`NavigationManager.NavigateTo` preserves the current scroll position when navigation remains on the same page and only the query string or fragment changes. Do not add scroll-restoration workarounds based on the earlier automatic scroll-to-top behavior.

## Match Navigation Links

`NavLinkMatch.All` compares only the URI path. A link remains active when the query string or fragment changes.

Set the following AppContext switch to `true` only when compatibility requires matching the query string and fragment too:

```text
Microsoft.AspNetCore.Components.Routing.NavLink.EnableMatchAllForQueryStringAndFragment
```

## Handle Reconnection State

The template `ReconnectModal` keeps its CSS and JavaScript collocated rather than injecting styles, so it works with strict CSP `style-src` policies.

Reconnection transitions dispatch the `components-reconnect-state-changed` event. Consumers must recognize the added `retrying` state as well as the other connection states.

## Route Not-Found Results

`NavigationManager.NotFound()` sets the HTTP 404 status during static SSR and signals the router during interactive rendering. Use `Router.NotFoundPage` to choose the routed component and subscribe to `NavigationManager.OnNotFound` when custom handling is needed.

```razor
<Router AppAssembly="@typeof(Program).Assembly"
        NotFoundPage="typeof(Pages.NotFound)">
    <Found Context="routeData">
        <RouteView RouteData="routeData" />
    </Found>
</Router>
```

The old `<NotFound>` router fragment is unsupported. Replace it instead of maintaining both patterns.

## Construct and Access JavaScript Objects

`IJSRuntime` and `IJSObjectReference` can construct a JavaScript object and read or write its properties with `InvokeConstructorAsync`, `GetValueAsync`, and `SetValueAsync`.

```csharp
var instance = await JSRuntime.InvokeConstructorAsync(
    "jsInterop.TestClass", "Blazor!");
var text = await instance.GetValueAsync<string>("text");
await instance.SetValueAsync("text", "updated");
```

In-process object references expose synchronous equivalents for code that is already constrained to in-process execution.

## Resume Server Circuits

Server-side Blazor circuit state can survive an extended lost connection or a proactive pause and resume without discarding unsaved state. A full-page refresh still prevents resumption, so do not present circuit resumption as durable persistence across reloads.
