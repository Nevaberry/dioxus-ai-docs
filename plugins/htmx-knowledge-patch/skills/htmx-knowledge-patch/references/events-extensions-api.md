# htmx 4.0: Events, Extensions & API

## Event Naming (Breaking)

All events renamed to `htmx:phase:action` pattern. All errors consolidated to `htmx:error`.

| htmx 2.x | htmx 4.0 |
|-----------|----------|
| `htmx:beforeRequest` | `htmx:before:request` |
| `htmx:afterSwap` | `htmx:after:swap` |
| `htmx:configRequest` | `htmx:config:request` |
| `htmx:afterProcessNode` / `htmx:load` | `htmx:after:init` |
| `htmx:responseError` / `htmx:sendError` / `htmx:timeout` | `htmx:error` |

Use `htmx-2-compat` extension to restore old event names.

## Request Header Changes (Breaking)

| htmx 2.x | htmx 4.0 |
|-----------|----------|
| `HX-Trigger` (request header) | `HX-Source` (format: `tagName#id`, e.g. `button#submit`) |
| `HX-Trigger-Name` | Removed |
| — | New: `HX-Request-Type` (`"full"` or `"partial"`) |
| — | New: explicit `Accept: text/html` |

## Response Header Changes

`HX-Trigger-After-Swap` and `HX-Trigger-After-Settle` removed. Use `HX-Trigger` instead.

## Extension API (Rewritten)

`htmx.defineExtension()` → `htmx.registerExtension()`. Event-hook based, no `hx-ext` attribute needed:

```js
htmx.registerExtension("my-ext", {
    init: (internalAPI) => { /* called once */ },
    htmx_before_request: (elt, detail) => {
        // return false to cancel
    },
    htmx_after_request: (elt, detail) => {},
    handle_swap: (swapStyle, target, fragment, swapSpec) => {
        // return true if handled
    },
});
```

Extensions load by including the script. Optionally restrict which extensions are active:
```html
<meta name="htmx-config" content='{"extensions": "sse,ws"}'>
```

## New JS Methods

| Method | Description |
|--------|-------------|
| `htmx.forEvent(eventName, timeout)` | Returns a promise that resolves when event fires |
| `htmx.takeClass(element, className, container)` | Removes class from siblings, adds to element |
| `htmx.timeout(time)` | Promise-based delay |

## Removed JS Methods

Use native DOM instead:

| Removed | Native replacement |
|---------|-------------------|
| `htmx.addClass()` | `element.classList.add()` |
| `htmx.removeClass()` | `element.classList.remove()` |
| `htmx.toggleClass()` | `element.classList.toggle()` |
| `htmx.closest()` | `element.closest()` |
| `htmx.remove()` | `element.remove()` |
| `htmx.defineExtension()` | `htmx.registerExtension()` |

## Config Changes

| htmx 2.x | htmx 4.0 | Notes |
|-----------|----------|-------|
| `defaultSwapStyle` | `defaultSwap` | |
| `globalViewTransitions` | `transitions` | |
| `historyEnabled` | `history` | |
| `timeout` | `defaultTimeout` | Default changed to 60s |
| `includeIndicatorStyles` | `includeIndicatorCSS` | |

## History

History no longer uses localStorage for caching. Back navigation re-fetches the page.

Configure with `htmx.config.history`:
- `"reload"` — full page reload on back navigation
- `false` — disable history support entirely

## Compatibility Extension

Load `htmx-2-compat` for gradual migration from htmx 2.x to 4.0:

```html
<script src="/path/to/htmx.js"></script>
<script src="/path/to/ext/htmx-2-compat.js"></script>
```

Restores implicit inheritance, old event names, and previous error-swapping defaults.
