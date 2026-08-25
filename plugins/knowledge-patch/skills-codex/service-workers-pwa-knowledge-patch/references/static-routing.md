# Service Worker Static Routing

Use this reference when registering routes with `InstallEvent.addRoutes()`,
choosing a route source, validating a condition tree, or deciding whether a
route-registration failure should fail service worker installation.

## Why static routes matter

The static routing API lets a browser select a network or cache source before
starting the service worker. Predictable requests can therefore bypass an
otherwise unnecessary worker startup cycle.

The API has limited browser availability and is not Baseline. Treat it as a
capability that needs a compatible deployment path rather than an assumption
that all clients support.

## Condition model

The condition rules in `service-workers-crd-2026-06` are strict.

### Leaf composition

Recognized leaf members are:

- `urlPattern`
- `requestMethod`
- `requestMode`
- `requestDestination`
- `runningStatus`

When multiple leaf members are present, they are ANDed. `runningStatus`
accepts `"running"` or `"not-running"`.

`urlPattern` is resolved against the service worker script URL. It cannot
contain regular-expression groups. `requestMethod` must be a valid,
non-forbidden HTTP method.

### Boolean composition

A boolean condition object uses `or` or `not` as its sole member. Do not mix a
boolean member with leaf members or another boolean member in the same
condition object. A condition object with no recognized member is invalid.

```js
{
  condition: {
    or: [
      { urlPattern: "/assets/*", requestMethod: "GET" },
      { runningStatus: "not-running" }
    ]
  },
  source: "network"
}
```

## Route sources

A route may use:

- `"network"`
- `"cache"`
- `"fetch-event"`
- a single named cache, expressed as `{ cacheName }`
- `"race-network-and-fetch-handler"`

The `"fetch-event"` and `"race-network-and-fetch-handler"` sources are backed
by the service worker's fetch handler. The worker must have a `fetch`
listener, or `addRoutes()` rejects with `TypeError`.

The race source applies to `GET` requests. It races an OK network response
against the fetch-handler result. When the handler produces a valid response,
the network request is aborted.

```js
self.addEventListener("fetch", event => {
  event.respondWith(
    caches.match(event.request).then(response => response ?? fetch(event.request))
  );
});

self.addEventListener("install", event => {
  event.addRoutes([
    {
      condition: { urlPattern: "/static/*" },
      source: { cacheName: "static-v3" }
    },
    {
      condition: { urlPattern: "/api/*", requestMethod: "GET" },
      source: "race-network-and-fetch-handler"
    }
  ]);
});
```

## Named-cache fallback

When `{ cacheName: "pictures" }` names a cache that does not exist, the
browser falls back to the network. A missing named cache does not, by itself,
cause the request to fail.

## Ordering and accumulated limits

Each call to `addRoutes()` appends to the worker's existing rule list. The
first matching rule supplies the source, so register specific rules before any
broader rule that could match the same request.

Limits apply to the accumulated list:

- the condition-count budget is 1024; and
- the condition nesting-depth limit is 10.

An invalid or over-limit addition rejects atomically. It does not partially
append the submitted rule set.

## Installation lifetime and failure

`addRoutes()` keeps the install event alive with an internal lifetime promise,
but that internal promise is always fulfilled. Consequently, route
registration rejection does not automatically make installation fail.

When routes are required for a valid installation, explicitly pass the
promise returned by `addRoutes()` to `waitUntil()`:

```js
self.addEventListener("install", event => {
  const added = event.addRoutes({
    condition: { urlPattern: "/offline/*" },
    source: { cacheName: "offline-v1" }
  });
  event.waitUntil(added);
});
```

This connects route-registration rejection to the install event's success or
failure instead of relying only on the always-fulfilled internal lifetime
promise.
