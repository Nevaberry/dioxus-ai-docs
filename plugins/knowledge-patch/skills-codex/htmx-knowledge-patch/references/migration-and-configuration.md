# Migration and Configuration

Use this reference when upgrading an established htmx application, choosing a
distribution build, or deciding how closely to follow new releases.

## htmx 2.0.0 migration

### Separately distributed extensions

Extensions are versioned outside the core repository. Most 1.x extensions
continue to work, but each extension should be audited and upgraded separately
from core.

The SSE extension has a breaking change and must be upgraded. The core
`hx-sse` and `hx-ws` attributes were removed; migrate each use to the
attributes provided by its corresponding extension.

### Module-specific builds

Load the artifact that matches the consumer's module system:

| Consumer | Distribution |
| --- | --- |
| Direct browser script | `/dist/htmx.js` |
| ECMAScript module | `/dist/htmx.esm.js` |
| AMD | `/dist/htmx.amd.js` |
| CommonJS | `/dist/htmx.cjs.js` |

Do not substitute the directly browser-loadable build for a module-specific
artifact.

### ESM default export

The ESM build exposes htmx as its default export:

```js
import htmx from "htmx.org/dist/htmx.esm.js";
```

### Changed request and scrolling defaults

Three defaults differ from 1.x:

- `DELETE` values are sent as URL parameters.
- Requests are restricted to the same origin.
- Swap scrolling is instant rather than smooth.

Restore the corresponding earlier behaviors only if the application requires
them:

```js
htmx.config.methodsThatUseUrlParams = ["get"];
htmx.config.selfRequestsOnly = false;
htmx.config.scrollBehavior = "smooth";
```

Turning off `selfRequestsOnly` requires an explicit URL allowlist and suitable
CORS rules. See
[Requests and validation](requests-and-validation.md#cross-origin-request-allowlisting).

### Per-event inline handlers

The legacy multi-event `hx-on` attribute is removed. Declare each inline
handler with a separate `hx-on:<event>` attribute:

```html
<button hx-post="/save" hx-on:click="this.disabled = true">Save</button>
```

### Public swap API

The internal `selectAndSwap()` method is removed. Extensions and direct callers
must use the public `htmx.swap()` replacement:

```js
htmx.swap(document.querySelector("#result"), "<p>Updated</p>", {
  swapStyle: "innerHTML"
});
```

### Shadow DOM support

htmx behavior now works inside Shadow DOM. Web Components can place htmx
attributes on elements within their shadow roots.

## Maintenance policy

### Stability-first maintenance

Treat working behavior as intentional compatibility surface. Existing APIs,
implementation quirks, and defaults are intended to remain stable so upgrades
stay low-risk. When behavior needs improvement, a new configuration option is
preferred over changing a default.

A working 1.x installation does not need to migrate to 2.x solely to remain
current. Upgrade when the application needs a specific fix or feature.

### Extensions before core features

Expect new functionality to be explored through extensions rather than added
directly to core. Core additions are mainly expected when browser capabilities
open a new opportunity. The extensions API may expand to enable external
features.

This policy makes extension compatibility and versioning independent concerns.

### Quarterly release cadence

Releases are planned roughly quarterly and are not expected to impose recurring
major-feature migrations. Projects can follow the cadence selectively rather
than upgrading for every release.
