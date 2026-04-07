# Accessibility

## SelectionListener (Flutter 3.29)

Get selection details from `SelectionArea`:

```dart
SelectionListener(
  onSelectionChanged: (details) => print(details?.plainText),
  child: SelectionArea(child: Text('Select me')),
)
```

## SemanticsRole API (Flutter 3.32)

Assign specific roles to widget subtrees for screen readers:

```dart
Semantics(role: SemanticsRole.tabBar, child: myTabBar)
```

Web-only for now; other platforms coming.

## CalendarDatePicker calendarDelegate (Flutter 3.32)

Support non-Gregorian calendar systems via `calendarDelegate` parameter on `CalendarDatePicker`.

## SensitiveContent — Android (Flutter 3.35)

Obscure content during screen sharing (API 35+):

```dart
SensitiveContent(child: Text('Secret data'))
```

## SliverEnsureSemantics (Flutter 3.35)

Ensures slivers remain in the semantics tree even when scrolled out of view. Wrap slivers that must always be discoverable by screen readers.

## SemanticsLabelBuilder (Flutter 3.35)

Combine multiple data points into a single accessibility announcement without string concatenation.

## SliverSemantics (Flutter 3.38)

Annotate slivers for screen readers inside `CustomScrollView`:

```dart
SliverSemantics(
  label: 'Search results',
  child: SliverList(...),
)
```
