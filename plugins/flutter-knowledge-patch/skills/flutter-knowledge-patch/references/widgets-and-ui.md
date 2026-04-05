# Widgets & UI Features (Flutter 3.32–3.41)

## Rounded superellipse / squircle (Flutter 3.32)

New shape APIs for iOS-style "squircle" corners (smoother than rounded rectangles). Currently iOS and Android only; falls back to rounded rect on other platforms.

```dart
// As a shape border (e.g., in Container, Card)
Container(
  decoration: ShapeDecoration(
    shape: RoundedSuperellipseBorder(
      borderRadius: BorderRadius.circular(16),
    ),
  ),
)

// As a clip widget
ClipRSuperellipse(
  borderRadius: BorderRadius.circular(16),
  child: Image.asset('photo.jpg'),
)
```

`CupertinoAlertDialog` and `CupertinoActionSheet` now use this shape automatically.

## RawMenuAnchor (Flutter 3.32)

Unstyled menu widget in the widgets layer — use for fully custom menus without Material styling. Underlies `MenuAnchor`.

## RadioGroup widget (Flutter 3.35) — breaking

`Radio.groupValue` and `Radio.onChanged` are deprecated. Use the new `RadioGroup` widget to manage state for a set of radio buttons:

```dart
RadioGroup<String>(
  // manages groupValue and onChanged for child Radio widgets
  child: Column(
    children: [
      Radio<String>(value: 'a', child: Text('Option A')),
      Radio<String>(value: 'b', child: Text('Option B')),
    ],
  ),
)
```

Same applies to `CupertinoRadio` and `RadioListTile`.

## DropdownMenuFormField (Flutter 3.35)

New widget to integrate M3 `DropdownMenu` directly into `Form` widgets, like `TextFormField` but for dropdowns.

## CupertinoExpansionTile (Flutter 3.35)

New iOS-style expandable/collapsible list tile widget.

## SensitiveContent widget (Flutter 3.35, Android)

Wraps content to obscure the entire screen during media projection (screen share) on API 35+:

```dart
SensitiveContent(
  child: Text('Secret data'),
)
```

## Navigator.popUntilWithResult (Flutter 3.41)

Pop multiple screens and pass a value back to the destination route in one call:

```dart
Navigator.of(context).popUntilWithResult<String>(
  ModalRoute.withName('/home'),
  'result_value',
);
```

## RepeatingAnimationBuilder (Flutter 3.41)

Declarative widget for continuous/looping animations:

```dart
RepeatingAnimationBuilder<double>(
  animatable: Tween<double>(begin: 0.0, end: 1.0),
  duration: const Duration(seconds: 2),
  repeatMode: RepeatMode.reverse,
  curve: Curves.easeInOut,
  builder: (context, value, child) => Opacity(opacity: value, child: child),
  child: const Icon(Icons.favorite),
)
```

## Synchronous image decoding for shaders (Flutter 3.41)

`decodeImageFromPixelsSync` and high-bitrate textures (up to 128-bit float via `TargetPixelFormat.rFloat32`) for fragment shaders — generate textures and use as samplers in the same frame.

## Content-sized Flutter views — Add-to-App (Flutter 3.41)

Embedded Flutter views can auto-resize based on content. On iOS set `FlutterViewController.isAutoResizable = true`. On Android use `content_wrap` for FlutterView width/height. Root widget must support unbounded constraints (no `ListView` or `LayoutBuilder` at top level).

## CupertinoSheet drag handle (Flutter 3.41)

`CupertinoSheet` gains `showDragHandle` property for native-styled drag handles.
