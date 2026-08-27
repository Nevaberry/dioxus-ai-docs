---
name: htmx-knowledge-patch
description: htmx
version: "4.0.0"
license: MIT
metadata:
  author: Nevaberry
---


# htmx Knowledge Patch

Use this skill when implementing, reviewing, debugging, or upgrading htmx
applications. For established applications, begin with the migration guidance,
then open the topic reference that matches the work.

## Reference index

| Reference | Topics |
| --- | --- |
| [Migration and configuration](references/migration-and-configuration.md) | Extension packaging, module builds, changed defaults, removed APIs, Shadow DOM, maintenance policy |
| [Events and JavaScript](references/events-and-javascript.md) | Trigger sources and filters, polling, asynchronous confirmation, inheritance |
| [History and caching](references/history-and-caching.md) | History restoration, snapshot safety, full-page and fragment cache variants |
| [Requests and validation](references/requests-and-validation.md) | Native validation, URL allowlisting, CORS, boosted-navigation CSRF tokens |
| [Swaps and responses](references/swaps-and-responses.md) | Literal text, out-of-band content, ordered status handling, redirect headers |
| [Extensions and security](references/extensions-and-security.md) | CSP nonces, attribute mutation, URL parameters, cache bypass, JSON forms |

## Breaking migrations first

### Upgrade separately distributed extensions

Extensions are versioned outside the core repository. Audit and upgrade each
installed extension independently. Most 1.x extensions still work, but the SSE
extension has a breaking change and must be upgraded. Replace the removed
`hx-sse` and `hx-ws` attributes with the corresponding extension attributes.

See [Migration and configuration](references/migration-and-configuration.md#separately-distributed-extensions).

### Load the build for the module system

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
and swap scrolling is instant. Restore earlier behavior only where the
application depends on it:

```js
htmx.config.methodsThatUseUrlParams = ["get"];
htmx.config.selfRequestsOnly = false;
htmx.config.scrollBehavior = "smooth";
```

If cross-origin requests are enabled, enforce an explicit
`htmx:validateUrl` allowlist and configure CORS for the htmx headers. See
[Requests and validation](references/requests-and-validation.md#cross-origin-request-allowlisting).

### Replace removed JavaScript and attribute APIs

Use one `hx-on:<event>` attribute per inline handler; the legacy multi-event
`hx-on` form is removed.

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

`htmx:confirm` fires for every request trigger, including triggers without
`hx-confirm`. Cancel the event, then call `event.detail.issueRequest()` only
after approval:

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
server should stop the poll.

### Report native validation when desired

Invalid form requests are blocked, but native validation UI and focus on the
first invalid control are disabled by default. Enable them with:

```js
htmx.config.reportValidityOfForms = true;
```

Use `hx-validate="true"` when a non-form request trigger must validate too.

## High-value swap and response controls

### Swap literal text

Use the core `textContent` swap style when the response must be assigned as
literal text instead of parsed as HTML:

```html
<button hx-get="/source" hx-target="#result" hx-swap="textContent">Show source</button>
<pre id="result"></pre>
```

### Return context-sensitive out-of-band elements

Wrap elements such as table rows in `<template>` so they retain the parsing
context that a free-standing response node lacks:

```html
<template>
  <tr id="status-row" hx-swap-oob="outerHTML">
    <td>Ready</td>
  </tr>
</template>
```

Process only top-level out-of-band fragments with:

```js
htmx.config.allowNestedOobSwaps = false;
```

### Handle response statuses in order

`htmx.config.responseHandling` uses the first matching regular expression.
Prepend specific rules ahead of broad defaults:

```js
htmx.config.responseHandling.unshift({
  code: "422", swap: true, error: false
});
```

The browser consumes HTTP `3xx` responses before htmx can process htmx-specific
headers. Return a non-redirect response when using `HX-Redirect`, `HX-Location`,
or `HX-Trigger`.

## History and cache safety

Every pushed URL must be able to return a complete document after a history
cache miss. A miss carries `HX-History-Restore-Request: true`; when ordinary
`HX-Request` handling selects fragments, use:

```js
htmx.config.historyRestoreAsHxRequest = false;
```

Use `refreshOnHistoryMiss` when a hard refresh is the intended fallback.

Place `hx-history="false"` anywhere in the current document or loaded fragment
when its URL must not be snapshotted. Keep a custom `hx-history-elt` present on
every page, and undo temporary DOM mutations in `htmx:beforeHistorySave`.

For URLs that serve both complete documents and fragments, send
`Vary: HX-Request` and distinct ETags. If the cache cannot vary on that header,
enable `htmx.config.getCacheBusterParam = true`.

## Trigger and inheritance rules

The selector in `from:<selector>` is resolved once, so it does not track later
DOM additions. Trigger-filter names resolve against the triggering event before
the global scope, and `this` is the element carrying `hx-trigger`.

Clear a single inherited attribute with an `unset` value such as
`hx-confirm="unset"`. Use `hx-disinherit` to block selected inheritance. To make
inheritance opt-in globally, set:

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
- Configure `inlineStyleNonce` before htmx loads when CSP protects inline styles.
- Put rotating boosted-navigation CSRF tokens inside content that is replaced.
- Prefer framework-provided hidden CSRF inputs when available.

## Working approach

Preserve working behavior unless a fix or feature requires change. Prefer
configuration switches for behavioral improvements and extensions for new
functionality. Upgrade selectively when a particular fix or feature is needed.
