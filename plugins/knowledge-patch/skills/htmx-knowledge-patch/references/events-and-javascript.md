# Events and JavaScript

## Static trigger sources

The selector in `from:<selector>` is evaluated once when the trigger is
initialized. Elements added later do not cause the selector to be re-evaluated.

```html
<button hx-get="/shortcut" hx-trigger="keydown[ctrlKey] from:body">
  Save
</button>
```

For dynamic content, design the trigger source around an element that already
exists instead of assuming `from:` will track future selector matches.

## Trigger-filter lookup

Inside a trigger filter, a name is resolved on the triggering event first and
then against the global scope. In the example above, `ctrlKey` comes from the
keyboard event. `this` refers to the element bearing the `hx-trigger`
attribute, not necessarily the event source selected by `from:`.

## Server-controlled polling

An endpoint serving a request triggered by `hx-trigger="every ..."` can stop
future polling by returning HTTP status `286`.

## Asynchronous request confirmation

The `htmx:confirm` event fires for every request trigger, not only elements
with `hx-confirm`. This makes it the interception point for asynchronous
approval. Cancel the pending request, then invoke `event.detail.issueRequest()`
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

Filtering the event before calling `preventDefault()` is important because the
event occurs even for requests that do not need custom confirmation.

## Attribute inheritance controls

Use an `unset` value to clear a specific inherited attribute on a descendant:

```html
<main hx-confirm="Are you sure?">
  <button hx-delete="/draft">Delete</button>
  <button hx-get="/preview" hx-confirm="unset">Preview</button>
</main>
```

Use `hx-disinherit` when an element should stop inheriting selected attributes.
To reverse the global default, configure:

```js
htmx.config.disableInheritance = true;
```

With inheritance disabled globally, descendants explicitly opt in through
`hx-inherit`.
