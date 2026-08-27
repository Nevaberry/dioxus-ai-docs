# Widgets and theming

## Theme and style migrations

### Material 3 visual opt-in (3.29.0)

The refreshed progress-indicator and Slider visuals were not yet the default.
Set the component `year2023` property, or
`ProgressIndicatorThemeData.year2023` / `SliderThemeData.year2023`, to false to
opt in:

```dart
CircularProgressIndicator(year2023: false);
Slider(value: value, onChanged: onChanged, year2023: false);
```

### ThemeData value types

Replace `ThemeData.dialogBackgroundColor` with
`DialogThemeData.backgroundColor`, and move
`ButtonStyleButton.iconAlignment` into `ButtonStyle.iconAlignment` or a
`styleFrom` method (3.29.0).

Replace `ThemeData.indicatorColor` with `TabBarThemeData.indicatorColor`.
`ThemeData.cardTheme`, `dialogTheme`, and `tabBarTheme` take
`CardThemeData`, `DialogThemeData`, and `TabBarThemeData`
(3.32-guide).

Remaining component themes such as `AppBarTheme`, `BottomAppBarTheme`, and
`InputDecorationTheme` use their corresponding `...ThemeData` value types
(3.35-guide).

Move `AppBarTheme.color` / `AppBarThemeData.color` to `backgroundColor`
(3.35.0). Move `Switch.activeColor` to `activeThumbColor`.

`FloatingActionButtonTheme` and `SnackBarTheme` widgets apply local subtree theme
overrides without changing root `ThemeData` (3.41.0).

### Framework package transition (3.44-guide)

The in-framework Material and Cupertino libraries are frozen at their final feature
set and are moving to independently versioned `material_ui` and `cupertino_ui`
packages. The framework versions were scheduled for deprecation in the following
stable release. Check the project's dependency direction before adding new
component APIs.

## Expansion, radio, and externally controlled state

`Expansible` is the widget-layer expand/collapse primitive; `RawMenuAnchor` is the
unstyled menu primitive below Material `MenuAnchor`. Replace
`ExpansionTileController` with `ExpansibleController` (3.32-guide).

`Expansible` animation timing and curves later moved into `AnimationStyle`
(3.41.0).

Move `Radio`, `CupertinoRadio`, and `RadioListTile` shared value and change handling
to a surrounding `RadioGroup`; per-control `groupValue` and `onChanged` are
deprecated (3.35-guide).

Use `RadioListTile.radioInnerRadius` for one tile, or
`RadioThemeData.innerRadius` and `RadioThemeData.side` across a theme. A
`WidgetStateColor` can drive `ChipThemeData.deleteIconColor` (3.38.0).

`ExpansionTile`, `RadioListTile`, and `SwitchListTile` accept
`WidgetStatesController` for observed or driven interaction state. `TabBar` accepts
`TabBarScrollController` (3.44.0).

## Menus and selection controls

### Material menus

`RawMenuAnchor` underpins custom unstyled menus (3.32-guide). Its close-related
callback order changed; custom logic must not depend on the former ordering
(3.44-guide).

Material 3 `MenuAnchor` animations are disabled by default; set `animated: true` to
enable them. `SubmenuButton.hoverOpenDelay` controls hover-open delay
(3.44-guide).

`DropdownMenu` adds `cursorHeight`, an external `menuController`, and a focus-node
hook for its trailing-icon button. `MenuController` is no longer final and can be
subclassed (3.38.0).

`DropdownMenu<T>` requires a non-nullable generic type.
`DropdownMenu.selectOnly` provides selection-only behavior. `DropdownMenu` and
`DropdownMenuFormField` accept `decorationBuilder`, and the form variant accepts
`errorBuilder` (3.41.0).

`DropdownMenuFormField` integrates the Material 3 menu with forms
(3.35-guide). Replace `DropdownButtonFormField.value` with `initialValue`.

`DropdownButton.enabled` controls enabled state independently of `onChanged`, which
is no longer required (breaking-change-guides).

### Cupertino menus and segments

Set `CupertinoSlidingSegmentedControl.isMomentary` when a tap should trigger an
action without retaining selection (3.38-guide).

`CupertinoMenuAnchor` and `CupertinoMenuItem` provide anchored Cupertino menus on
`RawMenuAnchor` without a Material dependency (3.44.0).

## Forms and input decoration

`InputDecoration.hint` accepts an arbitrary widget when `hintText` is too
restrictive (3.32.0).

Replace `Tooltip.height` with `Tooltip.constraints`, which can express minimum and
maximum dimensions (3.32.0).

`FormField` error output can be an arbitrary widget, and `FormField.onReset` runs
field-level clearing logic when a form resets (3.32-guide, 3.35-guide).

A `Form` cannot be used directly as a sliver in a `CustomScrollView`; wrap it in
`SliverToBoxAdapter` (3.35-guide).

`AutovalidateMode.onUserInteractionIfError` uses interaction-driven validation when
a field has an error (3.41.0).

Form state exposes registered `fields`, and `clearError` clears form-level or
individual `FormFieldState` errors without resetting values (3.44.0):

```dart
for (final field in formKey.currentState!.fields) {
  field.clearError();
}
```

Replace `InputDecoration.maintainHintHeight` with `maintainHintSize`
(breaking-change-guides).

`ShapedInputBorder` adapts a `ShapeBorder`, including
`RoundedSuperellipseBorder`, to Material input decoration (3.44-guide).

## Buttons, bars, dialogs, and tooltips

### Buttons and app bars

`CupertinoButton.minSize` is replaced by independent `minWidth` and `minHeight`
parameters, permitting non-square minimums (3.32.0).

`TabBar` adds `onHover` and `onFocusChange`. `SearchAnchor.viewOnOpen` and
`SearchAnchor.bar.onOpen` expose search-view opening. A
`CalendarDatePicker.calendarDelegate` supports non-Gregorian calendars
(3.32-guide).

`IconButton.statesController` controls `WidgetState` visuals programmatically
(3.38-guide).

`AppBar.automaticallyImplyActions` controls inferred actions. Material buttons use
the basic arrow cursor by default on non-web targets (3.38.0, 3.41.0).

### Dialogs and tooltips

`animationStyle` customizes transitions for `showDialog`,
`showAdaptiveDialog`, and `DialogRoute` (3.32-guide).

Material dialogs default to a maximum width of 560 dp.
`AlertDialog.constraints` and `SimpleDialog.constraints` override it
(3.35.0).

Tooltip positioning is customizable, and `RawTooltip` exposes the tooltip widget
for lower-level composition. `PlatformMenu` and `PlatformMenuItem` support tooltip
text (3.41.0).

### SnackBars

A `SnackBar` with an action no longer auto-dismisses. Application code must dismiss
it when a finite lifetime is required (3.38-guide).

## Lists, carousels, navigation, and pickers

`NavigationRail` can scroll, `NavigationDrawer` accepts header and footer widgets,
and `CupertinoExpansionTile` provides an iOS-style expandable item
(3.35-guide).

`CarouselView.itemClipBehavior` controls child clipping (3.38.0). It later gains
infinite scrolling and `onIndexChanged`, while
`CarouselController.leadingItem` exposes the current leading item (3.44-guide).

Replace `ReorderableListView.onReorder` with `onReorderItem`. The new callback's
`newIndex` already accounts for removing the item before reinsertion
(3.44-guide).

In separated `ListView` and `SliverList` constructors, replace
`findChildIndexCallback` with `findItemIndexCallback`
(breaking-change-guides).

`showTimePicker` may use `initialTime: null` only when starting directly in
`TimePickerEntryMode.input` (3.38.0).

`CupertinoDatePicker.selectableDayPredicate` rejects individual days.
`CupertinoCheckbox` uses an adjusted desktop default size, and
`CupertinoLinearActivityIndicator` supplies a linear Cupertino progress control
(3.38.0).

## Interaction and rendering controls

`Badge.count(maxCount: ...)` caps displayed counts.
`InkWell.onLongPressUp` reports release after a long press, and
`TableRowInkWell.onHover` reports hover. `ExpansionTile.splashColor` controls
interaction color (3.38.0).

A Slider value indicator can stay visible (3.35-guide).
`CircularProgressIndicator` and `LinearProgressIndicator` can accept an external
`AnimationController` for synchronized motion (3.38.0).

`Visibility.maintainFocusability` controls hidden maintained-subtree focus, while
hidden `IndexedStack` children are no longer focusable (3.35.0).

`Autocomplete` can accept external focus and text controllers and already supports
keyboard option traversal (3.35.0, 3.32.0).

## Source-level constraints

`PipelineOwner` is a `base` class. External custom pipeline types must extend rather
than implement it and declare an allowed modifier such as `base`, `final`, or
`sealed` (3.32.0).

`IconData` and `TextDecoration` are final; replace external subclasses with
instances or composition (3.44.0).

Flutter 3.44 reports a debug error when `ListTile` is wrapped in a colored widget.
Remove or restructure colored wrappers (breaking-change-guides).

Starting in Flutter 3.41, `FontWeight` also controls a variable font's weight axis,
which can change rendering when `fontWeight` is set
(breaking-change-guides).

## Widget verification

- Run `dart fix` where migrations are supported, then review every edit.
- Exercise form reset, validation, error clearing, dropdown enabled state, menu
  close order, and list reordering.
- Test focus, hover, keyboard traversal, controller-driven states, and screen-reader
  behavior.
- Compare component layout under dialog constraints, shaped borders, variable
  fonts, persistent SnackBars, and carousel looping.
- Search for old theme types, final-class subclasses, removed callbacks, and colored
  `ListTile` wrappers.
