# Swaps and Responses

## Use the public swap API

The internal `selectAndSwap()` method is removed. Extensions and direct
callers must use the public `htmx.swap()` replacement:

```js
htmx.swap(document.querySelector("#result"), "<p>Updated</p>", {
  swapStyle: "innerHTML"
});
```

## Wrap context-sensitive out-of-band elements

Return out-of-band elements that require a parsing context inside
`<template>`. This prevents nodes such as table rows from being discarded as
invalid free-standing response content:

```html
<template>
  <tr id="status-row" hx-swap-oob="outerHTML">
    <td>Ready</td>
  </tr>
</template>
```

## Swap a response as literal text

`textContent` is a core swap style. It assigns the response as literal text
instead of parsing it as HTML:

```html
<button hx-get="/source" hx-target="#result" hx-swap="textContent">
  Show source
</button>
<pre id="result"></pre>
```

## Limit out-of-band processing to top-level fragments

Nested out-of-band fragments are processed by default. To process only
top-level out-of-band content, set:

```js
htmx.config.allowNestedOobSwaps = false;
```

## Order response-status rules from specific to broad

`htmx.config.responseHandling` is an ordered list. The first matching regular
expression determines swap and error treatment. Its defaults skip `204`, swap
`2xx` and `3xx`, and treat `4xx` and `5xx` as unswapped errors.

Prepend a specific status override before the broad defaults:

```js
htmx.config.responseHandling.unshift({
  code: "422",
  swap: true,
  error: false
});
```

An entry can also override title handling, selection, target, or swap style.

## Return a non-redirect response for htmx headers

The browser consumes HTTP `3xx` redirects before htmx can inspect their
headers. Consequently, `HX-Redirect`, `HX-Location`, and `HX-Trigger` on a
redirect response are not processed. Return a non-redirect response such as
`200` when using those headers.
