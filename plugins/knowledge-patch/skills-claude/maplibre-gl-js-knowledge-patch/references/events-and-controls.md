# Events and Controls

## Listener registration and event typing

### Listener subscriptions

`Evented.on()` returns a `Subscription` rather than the evented object (since
5.0.0). Fluent listener chains no longer work. Register separately and retain
the subscription for later removal.

```js
const moveSubscription = map.on('move', onMove);
map.on('zoom', onZoom);
moveSubscription.unsubscribe();
```

### Extensible map event maps

`MapEventType` is an interface in 5.8.0, allowing TypeScript declaration
merging for application events.

```ts
declare module 'maplibre-gl' {
  interface MapEventType {
    'app:ready': {type: 'app:ready'; payload: string};
  }
}
```

### Event classes and identification

During migration-v5-v6, events become classes, but consumers should identify
them through the `type` field rather than `instanceof`.

```js
map.on('move', (event) => {
  if (event.type === 'move') handleMove(event);
});
```

### Event type overhaul

In 6.0.0:

- `Evented` is abstract and generic over an event map.
- Sources expose `SourceEventType`.
- The map event map includes roll lifecycle and typed `style.load` events.
- `MapDataEvent` is replaced by `MapSourceDataEvent | MapStyleDataEvent`.
- `MapLibreZoomEvent` is renamed to `MapBoxZoomEvent`.

```ts
abstract class TypedEvents extends Evented<AppEventType> {}
```

### Typed event names

Map event names passed to `on`, `once`, `listens`, and `fire` are checked by
TypeScript in 6.1.0-6.4.1. Declaration merging is appropriate for a stable
application event map; an explicit cast remains available for ad hoc names.

```ts
map.fire('app:ready' as any);
map.on('app:ready' as any, handleAppReady);
```

## Map and style lifecycle events

### Style loads after a diff

When `setStyle()` receives style JSON and applies it as a diff, `style.load`
is emitted (since 5.16.0). The same event can therefore gate work after a
diffed update or a full style reload.

```js
map.once('style.load', onStyleLoad);
map.setStyle(nextStyle);
```

### Request failures

Fetch failures, including CORS, DNS, and malformed URLs, surface as
`AJAXError` instances through the map's `error` event (since 5.0.0). The error
exposes request details to the handler.

## Geolocation and motion

### `outofmaxbounds` and tracking

`GeolocateControl` emits `outofmaxbounds` only when `trackUserLocation` is
enabled (since 5.8.0). Treat it as an active location-tracking event.

### Map-level reduced motion

`MapOptions.reduceMotion` configures reduced-motion behavior during map
construction (since 5.12.0).

```js
const map = new Map({container: 'map', reduceMotion: true});
```

## Popups and box zoom

### Popup edge padding

`Popup` accepts `padding` to keep automatic placement away from map-container
edges (since 5.16.0).

```js
const popup = new Popup({padding: 16});
```

### Custom box-zoom completion

Box-zoom configuration exposes `boxZoom.boxZoomEnd` in 5.20.0. Use it to
customize what happens after a Shift-drag box selection completes.

## Marker visibility and accessibility

### Numeric opacity and covered state

`Marker` and `MarkerOptions` accept numbers or strings for `opacity` and
`opacityWhenCovered` (since 5.20.0). A marker covered by 3D terrain or a globe
receives `maplibregl-marker-covered` for state-specific styling.

```js
new Marker({opacity: 1, opacityWhenCovered: 0.25});
```

### Default marker roles

Default markers use `role="img"` while non-interactive and `role="button"`
once interactive (6.1.0-6.4.1). Tests should expect the role to reflect the
marker's current behavior.

### Keyboard-operable dragging

Default draggable markers are focusable and move one pixel per arrow-key press,
or ten pixels with Shift (6.1.0-6.4.1). A custom marker element must provide
its own focus and keyboard movement behavior.

