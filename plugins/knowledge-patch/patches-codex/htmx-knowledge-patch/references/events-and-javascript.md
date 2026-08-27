# Events and JavaScript

Use this reference when configuring event sources, polling, confirmation, or
attribute inheritance.

## Trigger sources and filters

### Static `from:` selectors

The selector in `from:<selector>` is evaluated once. It is not reevaluated when
matching elements are added later, so do not expect a trigger source to follow
later DOM changes automatically.

```html
<button hx-get="/shortcut" hx-trigger="keydown[ctrlKey] from:body">Save</button>
```

### Filter-name lookup and `this`

Within a trigger filter, names resolve against the triggering event before the
global scope. In the example above, `ctrlKey` is read from the `keydown` event.

`this` refers to the element that bears the `hx-trigger` attribute, not
necessarily the element matched by the `from:` selector.

## Polling

### Stop polling from the server

An endpoint serving an `hx-trigger="every ..."` poll can stop further polling
by responding with HTTP status `286`.

This lets the server terminate polling when the polled condition is complete
without requiring a separate client-side event handler.

## Request confirmation

### Confirm asynchronously

The `htmx:confirm` event fires for every request trigger, not only for elements
with `hx-confirm`. Scope a listener to the intended elements, cancel the
request, and resume it with `event.detail.issueRequest()` after asynchronous
approval.

```js
document.body.addEventListener("htmx:confirm", (event) => {
  if (!event.target.matches("[data-confirm]")) return;
  event.preventDefault();
  Promise.resolve(window.confirm("Continue?")).then((ok) => {
    if (ok) event.detail.issueRequest();
  });
});
```

If approval is denied, leave the canceled request unissued.

## Attribute inheritance

### Clear one inherited attribute

Assign the special `unset` value on a descendant to clear an inherited
attribute at that point:

```html
<button hx-confirm="unset">Save without inherited confirmation</button>
```

### Disable selected inheritance

Use `hx-disinherit` when a branch should stop inheriting selected attributes.
This differs from clearing one attribute value on one descendant.

### Make inheritance opt-in

Reverse the default globally with:

```js
htmx.config.disableInheritance = true;
```

After inheritance is disabled by default, descendants can opt in with
`hx-inherit`.
