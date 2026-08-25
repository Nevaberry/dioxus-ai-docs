# Swaps and Responses

Use this reference when inserting literal text, returning out-of-band elements,
or customizing handling by HTTP status.

## Literal-text swaps

`textContent` is a core swap style. It assigns the response as literal text
instead of parsing it as HTML:

```html
<button hx-get="/source" hx-target="#result" hx-swap="textContent">
  Show source
</button>
<pre id="result"></pre>
```

Choose this style when response markup must be displayed rather than applied to
the document.

## Out-of-band content

### Preserve parsing context with `<template>`

Some elements are invalid as free-standing response nodes and need their normal
HTML parsing context. Wrap such out-of-band elements in `<template>`; table rows
are a common example:

```html
<template>
  <tr id="status-row" hx-swap-oob="outerHTML">
    <td>Ready</td>
  </tr>
</template>
```

The wrapper allows the response parser to retain the row until htmx applies the
out-of-band swap.

### Process only top-level out-of-band fragments

Nested out-of-band fragments are processed by default. Restrict processing to
top-level fragments with:

```js
htmx.config.allowNestedOobSwaps = false;
```

## Response-status handling

### First matching rule wins

`htmx.config.responseHandling` is ordered. The first regular-expression match
controls whether the response swaps and whether it is treated as an error.

The defaults:

- Skip `204` responses.
- Swap `2xx` and `3xx` responses.
- Treat `4xx` and `5xx` responses as unswapped errors.

Prepend a specific case before the broad defaults. For example, swap a `422`
response without treating it as an error:

```js
htmx.config.responseHandling.unshift({
  code: "422",
  swap: true,
  error: false
});
```

An entry can also override title handling, response selection, the target, or
the swap style.

## Redirects and htmx response headers

The browser handles HTTP `3xx` redirects before htmx, so htmx-specific headers
on the redirect response are hidden from htmx and are not processed.

Return a non-redirect response such as `200` when relying on headers including:

- `HX-Redirect`
- `HX-Location`
- `HX-Trigger`

The header itself can then instruct htmx what to do.

## Related public API

Direct swap callers and extensions should use the public `htmx.swap()` API.
See [Migration and configuration](migration-and-configuration.md#public-swap-api).
