# Workbox Lifecycle and Deployment

Use this reference when registering a Workbox-managed service worker,
interpreting lifecycle events, messaging the selected worker, or enabling
`CACHE_URLS` handling on a custom router.

## Registration timing

`Workbox#register()` waits for the window `load` event before registering by
default. Pass `{immediate: true}` when registration must begin without that
delay.

Attach lifecycle listeners before calling `register()` so an event is not
missed:

```js
const wb = new Workbox("/sw.js");
wb.addEventListener("waiting", event => showUpdatePrompt(event));
await wb.register({immediate: true});
```

## Lifecycle event provenance

Lifecycle events carry flags that distinguish why a worker is being observed.

### `isUpdate`

Use `isUpdate` to distinguish a first installation from an update.

### `isExternal`

In Workbox v6 and later, `isExternal: true` means the worker was installed
independently of the current `Workbox` instance. Another browser tab can
produce this state.

### `wasWaitingBeforeRegister`

On a `waiting` event, `wasWaitingBeforeRegister` means the worker was already
waiting before `register()` ran. This commonly explains an update prompt that
appears again after a page reload.

```js
wb.addEventListener("waiting", event => {
  if (event.isExternal || event.wasWaitingBeforeRegister) {
    showUpdatePrompt(event);
  }
});
```

Treat these flags independently: update status, installation provenance, and
pre-existing waiting state answer different lifecycle questions.

## Messaging the selected worker

`messageSW()` uses `getSW()` to choose a matching worker.

At registration time, `getSW()` prefers a matching waiting worker over a
matching active worker. If neither is available, it waits for a matching
installing worker.

The message is sent through `MessageChannel`. The promise returned by
`messageSW()` never resolves unless the service worker responds through
`event.ports[0]`.

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

A normal broadcast or unrelated `postMessage()` is not the required reply;
the response must use the transferred reply port.

## `CACHE_URLS` on custom routers

The default router from `workbox-routing` handles `CACHE_URLS` messages. It
caches only URLs that match routes registered on that router.

A separately constructed `Router` does not enable the message behavior
implicitly. Opt in with `addCacheListener()`:

```js
const router = new Router();
router.addCacheListener();
```

Register the routes that should accept cache requests on the same router,
because the cache listener still limits caching to URLs matching its
registered routes.
