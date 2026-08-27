# Events and JavaScript

## Use one inline handler per event

The legacy multi-event `hx-on` attribute is removed. Use a separate
`hx-on:<event>` attribute for each handler:

```html
<button hx-post="/save" hx-on:click="this.disabled = true">Save</button>
```

## Account for static trigger sources

The selector in `from:<selector>` is evaluated once. It is not re-evaluated
when matching elements are later added to the DOM.

In a trigger filter, names resolve against the triggering event before the
global scope. `this` refers to the element carrying the `hx-trigger`
attribute.

```html
<button hx-get="/shortcut" hx-trigger="keydown[ctrlKey] from:body">
  Save
</button>
```

## Stop polling from the server

For an endpoint polled with `hx-trigger="every ..."`, return HTTP status `286`
when htmx should stop issuing further polling requests.

## Implement asynchronous request confirmation

The `htmx:confirm` event fires for every request trigger, not just elements
with `hx-confirm`. Filter for the requests that need confirmation, cancel the
event, and call `event.detail.issueRequest()` after asynchronous approval:

```js
document.body.addEventListener("htmx:confirm", (event) => {
  if (!event.target.matches("[data-confirm]")) return;
  event.preventDefault();
  Promise.resolve(window.confirm("Continue?")).then((ok) => {
    if (ok) event.detail.issueRequest();
  });
});
```

## Control attribute inheritance

Use an `unset` value to clear one inherited attribute on a descendant:

```html
<button hx-confirm="unset">Skip inherited confirmation</button>
```

Use `hx-disinherit` to disable selected inheritance. To reverse the global
default and make inheritance opt-in, configure:

```js
htmx.config.disableInheritance = true;
```

Descendants can then opt in with `hx-inherit`.
