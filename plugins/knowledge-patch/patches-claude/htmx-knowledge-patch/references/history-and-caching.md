# History and Caching

## Restore a full document after a history-cache miss

A history-cache miss sends `HX-History-Restore-Request: true` and expects a
complete page. Every URL pushed into history must therefore be able to serve a
full document.

If ordinary `HX-Request` negotiation would return only a fragment during
restoration, set:

```js
htmx.config.historyRestoreAsHxRequest = false;
```

Use `refreshOnHistoryMiss` instead when restoration should fall back to a hard
refresh.

## Keep unsafe pages out of history snapshots

Put `hx-history="false"` anywhere in the current document or a loaded fragment
to keep that URL out of the `localStorage` history cache. Restoration will
fetch the URL from the server.

When using a custom `hx-history-elt`, keep the element present on every page.
Before an allowed snapshot, use `htmx:beforeHistorySave` to undo temporary DOM
mutations made by third-party code.

## Separate full-page and fragment cache variants

When the same URL returns a full document without `HX-Request` and a fragment
with it, send:

```http
Vary: HX-Request
```

Generate distinct ETags for the two representations. If the cache cannot vary
on that header, enable:

```js
htmx.config.getCacheBusterParam = true;
```

htmx GET requests will then include an `org.htmx.cache-buster` target
parameter to separate them from ordinary full-page requests.
