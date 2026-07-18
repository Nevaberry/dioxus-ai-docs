---
name: htmx-knowledge-patch
description: htmx
license: MIT
version: "4.0.0"
metadata:
  author: Nevaberry
---

# htmx Knowledge Patch

Use this skill when implementing, reviewing, debugging, or upgrading htmx applications.
Start with the migration notes when touching established code, then open the topic
reference that matches the task.

## Reference index

| Reference | Topics |
| --- | --- |
| [Migration and configuration](references/migration-and-configuration.md) | Extension packaging, distribution builds, removed APIs, Shadow DOM, maintenance policy |
| [Events and JavaScript](references/events-and-javascript.md) | Trigger sources and filters, polling, asynchronous confirmation, inheritance |
| [History and caching](references/history-and-caching.md) | History restoration, snapshot safety, cache variants, cache bypass |
| [Requests and validation](references/requests-and-validation.md) | Request defaults, URL validation, CORS, form validation, boosted CSRF tokens |
| [Swaps and responses](references/swaps-and-responses.md) | Scrolling, literal text, out-of-band content, status handling, redirects |
| [Extensions and security](references/extensions-and-security.md) | CSP nonces, attribute mutation, URL parameters, JSON forms |

## Breaking migrations first

### Upgrade separately distributed extensions

Extensions no longer share the core package's versioning. Audit each installed
extension independently. In particular, upgrade the SSE extension and replace
the removed `hx-sse` and `hx-ws` attributes with the attributes supplied by the
corresponding extensions.

See [Migration and configuration](references/migration-and-configuration.md#extension-packaging-and-removed-attributes).

### Load the build for the actual module system

| Consumer | Distribution |
| --- | --- |
| Browser script | `/dist/htmx.js` |
| ECMAScript module | `/dist/htmx.esm.js` |
| AMD | `/dist/htmx.amd.js` |
| CommonJS | `/dist/htmx.cjs.js` |

The ESM distribution has a default export:

```js
import htmx from "htmx.org/dist/htmx.esm.js";
```

### Account for changed defaults

Requests are same-origin-only by default, `DELETE` values use URL parameters,
and swap scrolling is instant. Restore the earlier behaviors only when the
application depends on them:

```js
htmx.config.methodsThatUseUrlParams = ["get"];
htmx.config.selfRequestsOnly = false;
htmx.config.scrollBehavior = "smooth";
```

If cross-origin requests are enabled, add an explicit `htmx:validateUrl`
allowlist and configure CORS for htmx headers. See
[Requests and validation](references/requests-and-validation.md#cross-origin-requests).

### Replace removed JavaScript and attribute APIs

Use one `hx-on:<event>` attribute per inline handler; the multi-event `hx-on`
form is removed.

```html
<button hx-post="/save" hx-on:click="this.disabled = true">Save</button>
```

Use the public `htmx.swap()` API instead of the removed internal
`selectAndSwap()` method:

```js
htmx.swap(document.querySelector("#result"), "<p>Updated</p>", {
  swapStyle: "innerHTML"
});
```

## High-value request controls

### Confirm requests asynchronously

`htmx:confirm` fires for every request trigger, even without `hx-confirm`.
Cancel the event and call `event.detail.issueRequest()` only after approval:

```js
document.body.addEventListener("htmx:confirm", (event) => {
  if (!event.target.matches("[data-confirm]")) return;
  event.preventDefault();
  Promise.resolve(window.confirm("Continue?")).then((ok) => {
    if (ok) event.detail.issueRequest();
  });
});
```

### Stop server-driven polling

For an `hx-trigger="every ..."` request, return HTTP status `286` when the
server wants htmx to stop polling.

### Report native validation when desired

Invalid forms are blocked, but native validation UI and first-invalid-control
focus are disabled by default. Enable them with:

```js
htmx.config.reportValidityOfForms = true;
```

Use `hx-validate="true"` when a non-form request trigger must run validation.

## High-value swap and response controls

### Swap literal text safely

Use the core `textContent` swap style when the response must be inserted as
text rather than parsed as HTML:

```html
<button hx-get="/source" hx-target="#result" hx-swap="textContent">
  Show source
</button>
<pre id="result"></pre>
```

### Return context-sensitive out-of-band elements

Wrap elements such as table rows in `<template>` so the response parser does
not discard them outside their required HTML context:

```html
<template>
  <tr id="status-row" hx-swap-oob="outerHTML">
    <td>Ready</td>
  </tr>
</template>
```

To process only top-level out-of-band fragments:

```js
htmx.config.allowNestedOobSwaps = false;
```

### Handle response statuses in order

`htmx.config.responseHandling` is ordered; the first matching regular
expression wins. Prepend specific cases before broad defaults:

```js
htmx.config.responseHandling.unshift({
  code: "422",
  swap: true,
  error: false
});
```

Do not attach `HX-Redirect`, `HX-Location`, or `HX-Trigger` to an HTTP redirect
and expect htmx to process it: the browser consumes `3xx` responses first.
Return a non-redirect response when using those headers.

## History and cache safety

Every pushed URL must be able to return a complete document after a history
cache miss. A miss carries `HX-History-Restore-Request: true`; prevent ordinary
`HX-Request` fragment negotiation from interfering with restoration:

```js
htmx.config.historyRestoreAsHxRequest = false;
```

Use `refreshOnHistoryMiss` when a hard refresh is the intended fallback.

When a URL must not be snapshotted, place `hx-history="false"` anywhere in the
current document or loaded fragment. Keep a custom `hx-history-elt` present on
every page, and use `htmx:beforeHistorySave` to undo temporary DOM mutations.

For URLs that serve both documents and fragments, send `Vary: HX-Request` and
distinct ETags. If the cache cannot vary on that header, enable:

```js
htmx.config.getCacheBusterParam = true;
```

## Trigger and inheritance rules

The selector in `from:<selector>` is resolved once. It does not automatically
track later DOM additions. In trigger filters, names resolve against the event
before the global scope, and `this` is the element carrying `hx-trigger`.

Clear a single inherited attribute with an `unset` value, such as
`hx-confirm="unset"`. Use `hx-disinherit` to block selected inheritance. To
make inheritance opt-in globally, set:

```js
htmx.config.disableInheritance = true;
```

Descendants can then opt in with `hx-inherit`.

## Extension selection guide

| Need | Extension |
| --- | --- |
| Toggle arbitrary attributes | `attribute-tools` |
| Fill URL path variables from request parameters | `path-params` |
| Resolve URL placeholders through a function or `window` | `dynamic-url` |
| Change or delete selected parameters | `replace-params` |
| Bypass browser and cooperating server caches | `no-cache` |
| Preserve scalar types and encode files in nested JSON | `form-json` |
| Encode complex objects, lists, and indexed form structures | `json-enc-custom` |

Read [Extensions and security](references/extensions-and-security.md) before
choosing between similarly shaped URL or JSON extensions.

## Security checklist

- Keep same-origin-only requests unless cross-origin access is necessary.
- Cancel `htmx:validateUrl` for destinations outside an explicit allowlist.
- Allow htmx request headers and expose required response headers in CORS.
- Apply `inlineStyleNonce` before htmx loads when CSP protects inline styles.
- Put rotating boosted-navigation CSRF tokens inside content that is replaced.
- Prefer framework-provided hidden CSRF inputs when available.

## Working approach

Preserve working behavior unless a fix or feature requires a change. The
project favors compatibility, configuration switches for behavioral
improvements, and extensions for experimentation. Upgrade selectively for the
bug fixes or features the application needs, and test extensions independently
from core.
