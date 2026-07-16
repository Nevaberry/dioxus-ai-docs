# Migration and Configuration

## Extension packaging and removed attributes

Since 2.0.0, extensions are distributed and versioned separately from the core
repository. Most extensions written for the earlier major line continue to
work, but extension compatibility must be checked independently of the core
package.

The SSE extension has a breaking change and must be upgraded. The core
`hx-sse` and `hx-ws` attributes were removed; migrate them to the attributes
provided by the separately installed SSE and WebSocket extensions.

## Distribution builds

Choose the distribution that matches the loader:

| Loader | File |
| --- | --- |
| Direct browser script | `/dist/htmx.js` |
| ECMAScript module | `/dist/htmx.esm.js` |
| AMD | `/dist/htmx.amd.js` |
| CommonJS | `/dist/htmx.cjs.js` |

The ESM build exposes htmx as its default export:

```js
import htmx from "htmx.org/dist/htmx.esm.js";
```

Do not load the directly browser-oriented file through a module loader when a
module-specific distribution is available.

## Removed inline-event form

The legacy multi-event `hx-on` attribute is removed. Put each handler in its
own `hx-on:<event>` attribute:

```html
<button hx-post="/save" hx-on:click="this.disabled = true">Save</button>
```

## Public swap API

The internal `selectAndSwap()` method is removed. Extensions and application
code that called it directly must use the public `htmx.swap()` API:

```js
htmx.swap(document.querySelector("#result"), "<p>Updated</p>", {
  swapStyle: "innerHTML"
});
```

## Shadow DOM

htmx behavior is supported inside Shadow DOM. Web Components can place htmx
attributes on elements within their shadow roots rather than moving those
controls into the light DOM solely for htmx processing.

## Maintenance and upgrade policy

The project prioritizes stability: existing APIs, implementation quirks, and
defaults are intended to remain compatible so upgrades stay low-risk. When a
behavior can be improved without forcing a migration, a new configuration
option is preferred over changing the default. A working installation on the
earlier major line does not need to move solely to remain current.

New functionality is generally explored in extensions before it is considered
for core. Core additions are expected mainly when new browser capabilities
create an opportunity; the extension API may grow to enable external features.

Releases are planned roughly quarterly without an expectation of recurring
large feature migrations. Projects can upgrade selectively when they need a
particular bug fix rather than following every release automatically.
