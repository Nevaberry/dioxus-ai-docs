# New & Changed Widgets

## CupertinoSheetRoute (Flutter 3.29)

iOS-styled draggable modal sheet:

```dart
Navigator.of(context).push(
  CupertinoSheetRoute<void>(builder: (context) => MySheet()),
);

// Convenience function with nested navigation:
showCupertinoSheet<void>(
  context: context,
  pageBuilder: (context) => MySheet(),
);
```

### enableDrag (Flutter 3.32)

Disable drag-to-dismiss:

```dart
showCupertinoSheet(enableDrag: false, ...)
```

## Squircles — Rounded Superellipse (Flutter 3.32)

iOS-style continuous corner shapes:

```dart
// As a shape border
Container(
  decoration: ShapeDecoration(shape: RoundedSuperellipseBorder(
    borderRadius: BorderRadius.circular(20),
  )),
)

// As a clip widget
ClipRSuperellipse(
  borderRadius: BorderRadius.circular(20),
  child: Image.asset('photo.jpg'),
)

// Low-level canvas API
canvas.drawRSuperellipse(rSuperellipse, paint);
```

Currently iOS and Android only; falls back to rounded rectangle elsewhere.

## Expansible (Flutter 3.32)

Unstyled expand/collapse widget (building block for `ExpansionTile`):

```dart
Expansible(
  isExpanded: _expanded,
  header: Text('Tap to expand'),
  body: Text('Expanded content'),
)
```

## RawMenuAnchor (Flutter 3.32)

Unstyled menu widget (building block for `MenuAnchor`). Full control over appearance while keeping menu positioning and keyboard navigation.

## DropdownMenuFormField (Flutter 3.35)

M3 dropdown integrated into forms:

```dart
DropdownMenuFormField<String>(
  dropdownMenuEntries: [
    DropdownMenuEntry(value: 'a', label: 'Option A'),
    DropdownMenuEntry(value: 'b', label: 'Option B'),
  ],
)
```

## CupertinoExpansionTile (Flutter 3.35)

iOS-style expandable list tile:

```dart
CupertinoExpansionTile(
  title: Text('Section'),
  children: [Text('Content')],
)
```

## RadioGroup (Flutter 3.35 — Breaking Change)

`Radio.groupValue` and `Radio.onChanged` are deprecated. Use `RadioGroup`:

```dart
RadioGroup<String>(
  groupValue: selected,
  onChanged: (value) => setState(() => selected = value),
  children: [
    Radio<String>(value: 'a'),
    Radio<String>(value: 'b'),
  ],
)
```

## Badge.count maxCount (Flutter 3.38)

Cap displayed count:

```dart
Badge.count(count: 150, maxCount: 99) // shows "99+"
```

## CarouselView.builder (Flutter 3.41)

Dynamic carousel content:

```dart
CarouselView.builder(
  itemCount: items.length,
  itemBuilder: (context, index) => ItemCard(items[index]),
)
```

## Flutter Property Editor (Flutter 3.32)

IDE sidebar for editing widget properties. Available in VS Code and Android Studio.

## Widget Previews — Experimental (Flutter 3.35)

Preview widgets in isolation, similar to Storybook/SwiftUI Previews. Supports multiple configurations side-by-side for testing themes, sizes, etc.
