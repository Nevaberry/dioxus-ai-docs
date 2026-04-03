# Navigation & Animation

## FadeForwardsPageTransitionsBuilder (Flutter 3.29)

New M3 page transition (slide + fade). Replaces `ZoomPageTransitionsBuilder` as default in Flutter 3.38:

```dart
MaterialApp(
  theme: ThemeData(
    pageTransitionsTheme: PageTransitionsTheme(builders: {
      TargetPlatform.android: FadeForwardsPageTransitionsBuilder(),
    }),
  ),
)
```

## Predictive Back Transition (Flutter 3.38)

`PredictiveBackPageTransitionBuilder` is the default Android page transition. Users see a home screen preview during back gesture. Applied automatically in `MaterialApp`.

## Navigator.popUntilWithResult (Flutter 3.41)

Pop multiple screens and return a value:

```dart
Navigator.of(context).popUntilWithResult<String>(
  (route) => route.isFirst,
  'result_value',
);
```

## RepeatingAnimationBuilder (Flutter 3.41)

Declarative continuous animations:

```dart
RepeatingAnimationBuilder<double>(
  animatable: Tween(begin: 0.0, end: 1.0),
  duration: Duration(seconds: 1),
  repeatMode: RepeatMode.reverse,
  curve: Curves.easeInOut,
  builder: (context, value, child) => Opacity(opacity: value, child: child),
  child: Icon(Icons.star),
)
```

## OverlayPortal.overlayChildLayoutBuilder (Flutter 3.38)

Render overlay children in any `Overlay` up the widget tree:

```dart
OverlayPortal(
  overlayChildLayoutBuilder: (context, constraints) => Positioned(...),
  overlayChildBuilder: (context) => MyOverlay(),
)
```

## Fragment Shader Improvements (Flutter 3.41)

- `decodeImageFromPixelsSync` for synchronous texture creation (no frame lag)
- High bitrate textures up to 128-bit float via `TargetPixelFormat.rFloat32`
