# htmx 4.0: Responses & Swapping

## Error Responses Swap by Default (Breaking)

All HTTP responses are now swapped into the DOM. Only 204 (No Content) and 304 (Not Modified) are excluded. Previously 4xx/5xx responses did not swap.

Revert to old behavior: `htmx.config.noSwap = [204, 304, '4xx', '5xx']`

## `<hx-partial>` for Multi-Target Updates

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

## New Swap Styles

| Swap style | Description |
|-----------|-------------|
| `innerMorph` | Morph inner content using idiomorph algorithm (preserves DOM state) |
| `outerMorph` | Morph entire element using idiomorph algorithm |
| `textContent` | Set text content only (no HTML parsing, safe for user input) |
| `delete` | Remove the target element from the DOM |

### Short Aliases

| Alias | Equivalent |
|-------|-----------|
| `before` | `beforebegin` |
| `after` | `afterend` |
| `prepend` | `afterbegin` |
| `append` | `beforeend` |

## OOB Swap Order Changed

In htmx 4.0, main content swaps first, then OOB/partial elements. This is the opposite of htmx 2.x behavior.
