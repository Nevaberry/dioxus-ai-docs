# Controls, markers, and UI

## Globe marker dragging (since 5.4.0)

Marker drag coordinates on globe maps no longer carry an erroneous ±360-degree longitude offset. Use the reported longitude directly instead of compensating for a full-world wrap.

## Geolocation bounds events (since 5.8.0)

`GeolocateControl` emits `outofmaxbounds` only while `trackUserLocation` is enabled. Treat the event as part of active user-location tracking rather than a general location validation event.

## Popup edge padding (since 5.16.0)

`Popup` accepts `padding` to keep automatic placement away from map-container edges.

```js
const popup = new Popup({padding: 16});
```

## Marker opacity and covered state (since 5.20.0)

`Marker` and `MarkerOptions` accept either numbers or strings for `opacity` and `opacityWhenCovered`.

```js
new Marker({opacity: 1, opacityWhenCovered: 0.25});
```

A marker occluded by 3D terrain or the globe receives the `maplibregl-marker-covered` CSS class. Use that class for covered-state styling when the opacity options alone are insufficient.

## Default marker roles (since 6.1.0-6.4.1)

A default marker has `role="img"` while non-interactive and changes to `role="button"` when it becomes interactive. Accessibility logic and tests can use the role as a reflection of marker behavior.

## Keyboard dragging (since 6.1.0-6.4.1)

Default draggable markers are focusable and respond to arrow keys. Each keypress moves one pixel, or ten pixels while Shift is held. A custom marker element remains responsible for implementing its own focus and keyboard interaction.
