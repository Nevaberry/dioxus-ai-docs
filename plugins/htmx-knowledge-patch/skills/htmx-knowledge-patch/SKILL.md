---
name: htmx-knowledge-patch
description: htmx changes since training cutoff (latest: 4.0 pre-release) — explicit inheritance, hx-status, hx-partial, new swap styles, fetch-based rewrite, extension API v2. Load before working with htmx 2.0+ or 4.0.
version: "4.0.0"
license: MIT
metadata:
  author: Nevaberry
---

# htmx Knowledge Patch

Claude Opus 4.6 knows htmx through 1.9.x (hx-get/post/put/patch/delete, hx-trigger, hx-target, hx-swap, hx-boost, hx-push-url, hx-select, hx-vals, hx-headers, hx-confirm, hx-indicator, hx-swap-oob, hx-on:, hx-ext, SSE/WebSocket extensions). It is **unaware** of the features below.

## Index

| Topic | Reference | Key features |
|---|---|---|
| htmx 2.0 changes | [references/htmx2-changes.md](references/htmx2-changes.md) | DELETE query params, selfRequestsOnly, extensions repo, hx-on removal, htmx.swap() |
| Attributes & inheritance | [references/attributes-and-inheritance.md](references/attributes-and-inheritance.md) | `:inherited` suffix, `:append`, hx-action, hx-method, hx-config, hx-ignore, hx-validate, hx-status, attribute renames/removals |
| Responses & swapping | [references/responses-and-swapping.md](references/responses-and-swapping.md) | Error responses swap by default, `<hx-partial>`, innerMorph/outerMorph/textContent/delete swap styles, OOB order change |
| Events, extensions & API | [references/events-extensions-api.md](references/events-extensions-api.md) | `htmx:phase:action` event naming, htmx.registerExtension(), header changes, JS method changes, config renames, history changes, compat extension |

---

## Quick Reference: htmx 2.0 Breaking Changes

| Change | Details |
|---|---|
| DELETE body | Query params instead of form-encoded body. Revert: `htmx.methodsThatUseUrlParams = ['get']` |
| Self-requests only | `htmx.config.selfRequestsOnly` defaults `true` |
| Scroll behavior | `htmx.config.scrollBehavior` defaults `'instant'` (was `'smooth'`) |
| Extensions | Moved to `extensions.htmx.org`; `hx-sse`/`hx-ws` attributes removed (use extensions) |
| `hx-on` removed | Use `hx-on:` prefix syntax only |
| `htmx.swap()` | New public API replacing internal `selectAndSwap()` |

---

## Quick Reference: htmx 4.0 Migration

### Attribute Renames (do BEFORE upgrading)

| htmx 2.x | htmx 4.0 | Purpose |
|---|---|---|
| `hx-disable` | `hx-ignore` | Skip htmx processing on element |
| `hx-disabled-elt` | `hx-disable` | Disable form elements during requests |

### Removed Attributes

`hx-vars` → use `hx-vals` with `js:` prefix | `hx-params` → use `htmx:config:request` event | `hx-prompt` → use `hx-confirm` with `js:` prefix | `hx-ext` → include extension script directly | `hx-disinherit`/`hx-inherit` → not needed | `hx-request` → use `hx-config` | `hx-history`/`hx-history-elt` → removed

### Event Renames (htmx 4.0)

| htmx 2.x | htmx 4.0 |
|---|---|
| `htmx:beforeRequest` | `htmx:before:request` |
| `htmx:afterSwap` | `htmx:after:swap` |
| `htmx:configRequest` | `htmx:config:request` |
| `htmx:afterProcessNode` / `htmx:load` | `htmx:after:init` |
| `htmx:responseError` / `htmx:sendError` / `htmx:timeout` | `htmx:error` |

### Header Changes

| htmx 2.x | htmx 4.0 |
|---|---|
| `HX-Trigger` (request) | `HX-Source` (format: `tagName#id`) |
| `HX-Trigger-Name` | Removed |
| — | New: `HX-Request-Type` (`"full"` or `"partial"`) |
| — | New: explicit `Accept: text/html` |
| `HX-Trigger-After-Swap` (response) | Removed, use `HX-Trigger` |
| `HX-Trigger-After-Settle` (response) | Removed, use `HX-Trigger` |

### Config Renames

| htmx 2.x | htmx 4.0 |
|---|---|
| `defaultSwapStyle` | `defaultSwap` |
| `globalViewTransitions` | `transitions` |
| `historyEnabled` | `history` |
| `timeout` | `defaultTimeout` (default 60s) |
| `includeIndicatorStyles` | `includeIndicatorCSS` |

---

## Explicit Inheritance (htmx 4.0)

Attributes no longer inherit down the DOM implicitly. Use `:inherited` suffix:

```html
<div hx-confirm:inherited="Are you sure?">
  <button hx-delete="/item/1">Delete</button>
</div>
```

Use `:append` to add to an inherited value:

```html
<div hx-include:inherited="#global-fields">
    <form hx-include:inherited:append=".extra">...</form>
</div>
```

Revert: `htmx.config.implicitInheritance = true`

---

## `<hx-partial>` Multi-Target Updates (htmx 4.0)

New element for explicit multi-target responses (alternative to `hx-swap-oob`):

```html
<!-- Server response -->
<hx-partial hx-target="#messages" hx-swap="beforeend">
  <div>New message</div>
</hx-partial>
<hx-partial hx-target="#count">
  <span>5</span>
</hx-partial>
<form id="my-form"><!-- main content --></form>
```

Template-friendly alternative: `<template hx type="partial" hx-target="..." hx-swap="...">`

---

## `hx-status` Per-Status-Code Behavior (htmx 4.0)

```html
<form
  hx-post="/save"
  hx-status:422="swap:innerHTML target:#errors select:#validation-errors"
  hx-status:5xx="swap:none push:false"
></form>
```

Keys: `swap:`, `target:`, `select:`, `push:`, `replace:`, `transition:`. Supports wildcards (`5xx`, `50x`).

---

## New Swap Styles (htmx 4.0)

| Swap style | Description |
|---|---|
| `innerMorph` | Morph using idiomorph algorithm (preserves state) |
| `outerMorph` | Outer morph with idiomorph |
| `textContent` | Set text content (no HTML parsing) |
| `delete` | Remove the target element |
| `before` | Alias for `beforebegin` |
| `after` | Alias for `afterend` |
| `prepend` | Alias for `afterbegin` |
| `append` | Alias for `beforeend` |

---

## Extension API (htmx 4.0)

`htmx.defineExtension()` → `htmx.registerExtension()`. Event-hook based, no `hx-ext` needed:

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

Extensions load by including the script. Optionally restrict:
```html
<meta name="htmx-config" content='{"extensions": "sse,ws"}'>
```

---

## Compatibility Extension

Load `htmx-2-compat` for gradual migration from htmx 2.x to 4.0:
```html
<script src="/path/to/htmx.js"></script>
<script src="/path/to/ext/htmx-2-compat.js"></script>
```

Restores implicit inheritance, old event names, and previous error-swapping defaults.
