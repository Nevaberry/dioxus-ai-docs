# Static Service-Worker Routing

## Why use static routes

`InstallEvent.addRoutes()` installs fetch rules that can select network or
cache sources before the service worker starts. This avoids an unnecessary
worker startup cycle for predictable requests (batch `static-routing-api`).

The API has limited browser availability and is not Baseline. Preserve a
fallback for browsers without it.

## Condition composition

Router condition behavior is defined in
`service-workers-crd-2026-06`.

The following leaf members are ANDed when they share a condition:

- `urlPattern`;
- `requestMethod`;
- `requestMode`;
- `requestDestination`;
- `runningStatus`.

`runningStatus` accepts only `"running"` or `"not-running"`.

Boolean nodes use `or` or `not`, and that boolean operator must be the
condition object's sole member. A condition object containing no recognized
member is invalid.

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

URL patterns are resolved against the service-worker script URL. They cannot
contain regular-expression groups. A request method must be a valid,
non-forbidden HTTP method.

## Route sources

A route can use:

- `"network"`;
- `"cache"`;
- `"fetch-event"`;
- `{ cacheName }` to select one named cache;
- `"race-network-and-fetch-handler"`.

When a route selects a named cache that does not exist, the browser falls back
to the network. The missing cache alone does not fail the request.

Both handler-backed sources require the service worker to have a `fetch`
listener. Otherwise, `addRoutes()` rejects with `TypeError`.

The race source applies only to `GET`. It races an OK network response against
the fetch-handler result. When the handler produces a valid response first,
the browser aborts the network request.

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

## Ordering and quotas

Each `addRoutes()` call appends rules to the worker's existing list. The first
matching rule supplies the source, so put narrower or higher-priority rules
first.

The accumulated rule list has:

- a 1024-condition count budget;
- a maximum nesting depth of 10.

An invalid or over-limit addition rejects atomically; it does not partially
append the submitted rules.

## Deciding whether route failure fails installation

Calling `addRoutes()` keeps the install event alive using an internal lifetime
promise that always fulfills. This means a rejected route-registration promise
does not, by itself, fail installation.

Pass the returned promise explicitly to `waitUntil()` when registration
failure must fail the install:

```js
self.addEventListener("install", event => {
  const added = event.addRoutes({
    condition: { urlPattern: "/offline/*" },
    source: { cacheName: "offline-v1" }
  });
  event.waitUntil(added);
});
```

Before deploying, verify:

- support is feature-tested;
- handler-backed sources have a `fetch` listener;
- conditions use valid leaf and boolean shapes;
- ordering implements the intended priority;
- totals remain within the count and nesting limits;
- the returned promise is passed to `waitUntil()` if rejection must stop
  installation.
