---
name: htmx-knowledge-patch
description: htmx
version: 4.0.0
license: MIT
metadata:
  author: Nevaberry
---


# htmx Knowledge Patch

Use this skill when implementing, reviewing, debugging, or upgrading htmx
applications. For established applications, start with migration and changed
defaults, then open the reference for the feature being changed.

## Reference index

| Reference | Topics |
| --- | --- |
| [Migration and configuration](references/migration-and-configuration.md) | Extension packaging, distribution builds, request and scrolling defaults, Shadow DOM, maintenance policy |
| [Events and JavaScript](references/events-and-javascript.md) | Inline handlers, trigger sources and filters, polling, asynchronous confirmation, inheritance |
| [History and caching](references/history-and-caching.md) | History restoration, snapshot safety, full-page and fragment cache variants |
| [Requests and validation](references/requests-and-validation.md) | Request defaults, URL validation, CORS, native form validation, boosted CSRF tokens |
| [Swaps and responses](references/swaps-and-responses.md) | Public swapping, literal text, out-of-band content, status handling, redirects |
| [Extensions and security](references/extensions-and-security.md) | CSP nonces, attribute mutation, URL parameters, cache bypass, JSON forms |

## Breaking migrations first

### Upgrade separately distributed extensions

Extensions no longer share the core package's versioning. Audit and upgrade
them independently. Most earlier extensions remain compatible, but the SSE
extension has a breaking change and must be upgraded. Replace removed
`hx-sse` and `hx-ws` attributes with the attributes supplied by their
respective extensions.

See [Migration and configuration](references/migration-and-configuration.md#upgrade-separately-distributed-extensions).

### Load the build for the module system

| Consumer | Distribution |
| --- | --- |
| Browser script | `/dist/htmx.js` |
| ECMAScript module | `/dist/htmx.esm.js` |
| AMD | `/dist/htmx.amd.js` |
| CommonJS | `/dist/htmx.cjs.js` |

The ESM build provides a default export:

```js
import htmx from "htmx.org/dist/htmx.esm.js";
```

### Review changed defaults

Requests are same-origin-only by default, `DELETE` values use URL parameters,
and swap scrolling is instant. Restore the earlier behavior only when the
application relies on it:

```js
htmx.config.methodsThatUseUrlParams = ["get"];
htmx.config.selfRequestsOnly = false;
htmx.config.scrollBehavior = "smooth";
```

Enabling cross-origin requests also requires an explicit destination
allowlist and suitable CORS policy. See
[Requests and validation](references/requests-and-validation.md#allowlist-cross-origin-destinations).

### Replace removed APIs

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
`hx-confirm`. Cancel the event and call `event.detail.issueRequest()` only
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

For a request triggered by `hx-trigger="every ..."`, return HTTP status `286`
when the server wants htmx to stop polling.

### Report native validation when desired

Invalid forms are blocked, but native validation UI and first-invalid-control
focus are disabled by default. Enable both with:

```js
htmx.config.reportValidityOfForms = true;
```

Use `hx-validate="true"` when a non-form request trigger must run validation.

## High-value swap and response controls

### Insert a response as literal text

Use the core `textContent` swap style when a response must not be parsed as
HTML:

```html
<button hx-get="/source" hx-target="#result" hx-swap="textContent">
  Show source
</button>
<pre id="result"></pre>
```

### Preserve parsing context for out-of-band elements

Wrap context-sensitive elements such as table rows in `<template>` so the
response parser does not discard them:

```html
<template>
  <tr id="status-row" hx-swap-oob="outerHTML">
    <td>Ready</td>
  </tr>
</template>
```

Process only top-level out-of-band fragments when required:

```js
htmx.config.allowNestedOobSwaps = false;
```

### Handle response statuses in order

`htmx.config.responseHandling` is ordered, and its first matching regular
expression wins. Prepend specific cases before broad defaults:

```js
htmx.config.responseHandling.unshift({
  code: "422",
  swap: true,
  error: false
});
```

Do not put `HX-Redirect`, `HX-Location`, or `HX-Trigger` on an HTTP redirect
and expect htmx to process it. The browser handles `3xx` responses first, so
return a non-redirect response when using those headers.

## History and cache safety

Every pushed URL must return a complete document after a history-cache miss.
The restoration request carries `HX-History-Restore-Request: true`. When
ordinary `HX-Request` handling would select a fragment, set:

```js
htmx.config.historyRestoreAsHxRequest = false;
```

Use `refreshOnHistoryMiss` when a hard refresh is the intended fallback.

To keep a URL out of the local history snapshot cache, put
`hx-history="false"` anywhere in the current document or loaded fragment.
Keep a custom `hx-history-elt` on every page, and use
`htmx:beforeHistorySave` to undo temporary DOM changes before snapshots.

When one URL serves both full pages and fragments, send `Vary: HX-Request`
and distinct ETags. If the cache cannot vary on that header, enable:

```js
htmx.config.getCacheBusterParam = true;
```

## Trigger and inheritance rules

The selector in `from:<selector>` is resolved once; it does not track elements
added later. In trigger filters, names resolve against the event before the
global scope, and `this` is the element bearing `hx-trigger`.

Clear one inherited attribute with an `unset` value such as
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
| Fill path variables from request parameters | `path-params` |
| Resolve URL placeholders with a function or `window` | `dynamic-url` |
| Change or remove selected parameters | `replace-params` |
| Bypass browser and cooperating server caches | `no-cache` |
| Preserve scalar types and encode files in nested JSON | `form-json` |
| Encode complex objects, lists, and indexed form structures | `json-enc-custom` |

Read [Extensions and security](references/extensions-and-security.md) before
choosing between similarly shaped URL or JSON extensions.

## Security checklist

- Keep same-origin-only requests unless cross-origin access is required.
- Cancel `htmx:validateUrl` for destinations outside an explicit allowlist.
- Allow htmx request headers and expose needed response headers in CORS.
- Configure `inlineStyleNonce` before htmx loads when CSP protects styles.
- Put rotating boosted-navigation CSRF tokens in content that gets replaced.
- Prefer framework-provided hidden CSRF inputs when available.

## Working approach

Preserve working behavior unless a fix or feature requires change. Upgrades
are intended to be low-risk: improvements favor configuration switches over
changed defaults, and new functionality is generally explored in extensions.
Follow releases selectively when a needed bug fix or capability justifies it.
