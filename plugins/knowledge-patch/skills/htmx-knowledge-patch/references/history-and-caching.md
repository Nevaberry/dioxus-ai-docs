# History and Caching

## Restoring after a history-cache miss

When a history snapshot is missing, htmx sends
`HX-History-Restore-Request: true` and expects the response to be a complete
page. Every URL placed in history must therefore be able to serve a full
document, not only a fragment.

If the server normally uses `HX-Request` to choose a fragment response, set:

```js
htmx.config.historyRestoreAsHxRequest = false;
```

This keeps history restoration from being treated as an ordinary fragment
request. Alternatively, `refreshOnHistoryMiss` forces a hard browser refresh
when the snapshot is unavailable.

## Excluding sensitive pages from snapshots

If `hx-history="false"` appears anywhere in the current document or in a
loaded fragment, htmx does not store that URL's snapshot in `localStorage`.
Returning to the URL fetches it from the server instead.

This is a document-wide safety control; it does not need to be placed on the
history element itself.

## Stable snapshot elements

A custom `hx-history-elt` must exist on every page that can participate in the
history flow. Missing it on one page makes snapshot and restoration behavior
inconsistent.

Third-party code may mutate the live DOM into a state that should not be
cached. Handle `htmx:beforeHistorySave` to undo those mutations before an
allowed snapshot is written.

## Full-page and fragment cache variants

When the same URL serves a full document without `HX-Request` and a fragment
with it, caches must treat those responses as distinct variants:

```http
Vary: HX-Request
```

Generate distinct ETags for the full-page and fragment representations as
well. Reusing an ETag across them can validate the wrong representation.

If an intermediary cannot vary on `HX-Request`, enable:

```js
htmx.config.getCacheBusterParam = true;
```

htmx then separates its GET requests with an `org.htmx.cache-buster` target
parameter.

## Explicit client and server cache bypass

The `no-cache` extension forces a fresh request that bypasses browser caches.
It also adds an `hx-no-cache` request header so a cooperating server can bypass
its own cache for the request.
