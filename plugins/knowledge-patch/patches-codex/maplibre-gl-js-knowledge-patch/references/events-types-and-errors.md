# Events, types, and errors

## Listener subscriptions (since 5.0.0)

`Evented.on()` returns a `Subscription`, not the evented object. Fluent registration chains no longer work. Register listeners separately and retain a subscription when later removal is required.

```js
const moveSubscription = map.on('move', onMove);
map.on('zoom', onZoom);
moveSubscription.unsubscribe();
```

## Request failures (since 5.0.0)

Fetch failures—including CORS, DNS, and malformed-URL failures—reach the map's `error` event as `AJAXError` instances. Error handlers can inspect the request details exposed by that error.

```js
map.on('error', ({error}) => {
  if (error instanceof AJAXError) handleRequestFailure(error);
});
```

## Custom event declaration merging (since 5.8.0)

`MapEventType` is an interface, so TypeScript applications can add event names through declaration merging.

```ts
declare module 'maplibre-gl' {
  interface MapEventType {
    'app:ready': {type: 'app:ready'; payload: string};
  }
}
```

## Style loading after a diff (since 5.16.0)

`setStyle()` emits `style.load` when it applies supplied style JSON as a diff as well as when it fully reloads a style. Code waiting for the updated style can use one path for both cases.

```js
map.once('style.load', onStyleLoad);
map.setStyle(nextStyle);
```

## Event identification during migration (since migration-v5-v6)

V6 represents events as classes, but application code should discriminate them through the `type` field rather than `instanceof`.

```js
map.on('move', (event) => {
  if (event.type === 'move') handleMove(event);
});
```

## Event type model (since 6.0.0)

The event type system changes in several related ways:

- `Evented` is abstract and generic over an event map.
- Sources expose `SourceEventType`.
- The map event map includes roll lifecycle events and a typed `style.load` event.
- `MapDataEvent` is removed; use `MapSourceDataEvent | MapStyleDataEvent`.
- `MapLibreZoomEvent` is renamed to `MapBoxZoomEvent`.

```ts
abstract class TypedEvents extends Evented<AppEventType> {}
```

## Typed event names (since 6.1.0-6.4.1)

TypeScript checks map event names passed to `on`, `once`, `listens`, and `fire`. When an application event is not part of the declared map event type, make the escape explicit with a cast.

```ts
map.fire('app:ready' as any);
map.on('app:ready' as any, handleAppReady);
```
