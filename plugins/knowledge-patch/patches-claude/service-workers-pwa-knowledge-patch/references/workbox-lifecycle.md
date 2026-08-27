# Workbox Lifecycle and Deployment

The behaviors in this reference come from
`workbox-lifecycle-and-deployment`.

## Registration timing

`Workbox#register()` waits for the window `load` event by default. Pass
`{immediate: true}` when registration should begin before that default point.

Attach lifecycle listeners before calling `register()` so early state changes
are observed:

```js
const wb = new Workbox("/sw.js");
wb.addEventListener("waiting", event => showUpdatePrompt(event));
await wb.register({immediate: true});
```

## Lifecycle event provenance

Use lifecycle event fields to distinguish why an event fired:

- `isUpdate` differentiates a first installation from an update.
- In Workbox v6 and later, `isExternal: true` means the worker was installed
  independently of the current `Workbox` instance, such as by another tab.
- A `waiting` event sets `wasWaitingBeforeRegister` when the worker was
  already waiting before `register()` ran.

An already-waiting worker commonly causes the `waiting` event to appear again
after a reload. Use the flags instead of assuming the event describes a newly
installed update:

```js
wb.addEventListener("waiting", event => {
  if (event.isExternal || event.wasWaitingBeforeRegister) {
    showUpdatePrompt(event);
  }
});
```

## Instance messaging

`messageSW()` obtains a matching worker through `getSW()`. At registration
time, `getSW()` prefers a matching waiting worker over an active worker. If
neither is available, it waits for a matching installing worker.

Messaging uses `MessageChannel`. The `messageSW()` promise never resolves
unless the service worker explicitly replies through `event.ports[0]`.

```js
// sw.js
addEventListener("message", event => {
  if (event.data.type === "GET_VERSION") {
    event.ports[0].postMessage("2.0.0");
  }
});

// window
const version = await wb.messageSW({type: "GET_VERSION"});
```

For every request type sent with `messageSW()`, make the selected worker either
post a response to the supplied port or ensure the caller does not wait on the
returned promise.

## `CACHE_URLS` and custom routers

The default `workbox-routing` router listens for `CACHE_URLS` messages. It
caches only URLs that match its registered routes.

A separately constructed `Router` does not opt in automatically. Enable the
same message behavior with `addCacheListener()`:

```js
const router = new Router();
router.addCacheListener();
```
