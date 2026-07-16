# Swaps and Responses

## Scroll behavior

Swap scrolling is instant by default. Applications that require smooth
scrolling can restore it globally:

```js
htmx.config.scrollBehavior = "smooth";
```

## Literal-text swaps

`textContent` is a core swap style. It assigns the response as literal text
instead of parsing the response as HTML:

```html
<button hx-get="/source" hx-target="#result" hx-swap="textContent">
  Show source
</button>
<pre id="result"></pre>
```

Use it for source, logs, or other content that must remain text even if the
response contains markup.

## Template-wrapped out-of-band swaps

Some elements need a specific parsing context and are invalid as free-standing
response nodes. Wrap them in `<template>` while retaining `hx-swap-oob` on the
element to swap:

```html
<template>
  <tr id="status-row" hx-swap-oob="outerHTML">
    <td>Ready</td>
  </tr>
</template>
```

This is especially useful for table rows and other context-sensitive HTML.

## Nested out-of-band fragments

By default, nested out-of-band fragments may be processed. To process only
top-level out-of-band fragments, configure:

```js
htmx.config.allowNestedOobSwaps = false;
```

## Ordered response-status handling

`htmx.config.responseHandling` is an ordered list. The first regular-expression
match determines whether a response swaps and whether it is treated as an
error. The defaults skip `204`, swap `2xx` and `3xx`, and treat `4xx` and `5xx`
as unswapped errors.

Entries may also override title handling, response selection, the target, or
the swap style. Insert a specific status rule before the broader defaults:

```js
htmx.config.responseHandling.unshift({
  code: "422",
  swap: true,
  error: false
});
```

## Redirects and htmx response headers

The browser handles HTTP `3xx` redirects before htmx receives the response, so
htmx-specific response headers on the redirect are not processed. Return a
non-redirect response, such as `200`, when using headers including
`HX-Redirect`, `HX-Location`, or `HX-Trigger`.
