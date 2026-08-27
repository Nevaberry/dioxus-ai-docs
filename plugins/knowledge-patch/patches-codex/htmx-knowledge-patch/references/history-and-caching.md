# History and Caching

Use this reference when pushing URLs, restoring history, controlling snapshots,
or serving both complete pages and fragments from one URL.

## History restoration

### Serve a complete document after a cache miss

Every pushed URL must be able to return a complete document. When the local
history cache misses, htmx sends `HX-History-Restore-Request: true` and expects
the response needed to restore the page.

Ordinary fragment negotiation based on `HX-Request` can interfere with that
restore. Disable that request identity during restoration with:

```js
htmx.config.historyRestoreAsHxRequest = false;
```

Use `refreshOnHistoryMiss` instead when the desired fallback is a hard browser
refresh.

## Snapshot safety

### Keep sensitive or unsuitable pages out of history storage

Place `hx-history="false"` anywhere in the current document or in a loaded
fragment to keep that URL out of the `localStorage` history cache. A later
restoration fetches the URL from the server rather than using a stored
snapshot.

### Keep a custom history element stable

When using a custom `hx-history-elt`, include it on every page involved in
history navigation. Restoration depends on that element remaining available
across pages.

### Undo temporary DOM mutations before saving

Third-party code can leave transient DOM changes that should not be preserved
in a snapshot. Handle `htmx:beforeHistorySave` to undo those mutations before
an allowed snapshot is stored.

## Full-page and fragment cache variants

### Vary on `HX-Request`

If a URL returns complete HTML when `HX-Request` is absent and a fragment when
it is present, responses represent distinct cache variants. Send:

```http
Vary: HX-Request
```

Generate distinct ETags for the complete-document and fragment variants as
well.

### Use a cache-buster when varying is unavailable

If an intermediary cache cannot vary on `HX-Request`, enable:

```js
htmx.config.getCacheBusterParam = true;
```

htmx GET requests then carry an `org.htmx.cache-buster` target parameter,
separating them from ordinary browser requests to the same URL.

## Related extension

The `no-cache` extension addresses a different cache-control need: forcing a
fresh request and signaling a cooperating server. See
[Extensions and security](extensions-and-security.md#client-and-server-cache-bypass).
