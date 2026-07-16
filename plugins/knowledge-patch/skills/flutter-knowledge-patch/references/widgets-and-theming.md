# Widgets and theming

## Contents

- [Material and Cupertino package transition](#material-and-cupertino-package-transition)
- [Theme type and property migrations](#theme-type-and-property-migrations)
- [Navigation components](#navigation-components)
- [Material visual defaults](#material-visual-defaults)
- [Forms and validation](#forms-and-validation)
- [Dropdowns and autocomplete](#dropdowns-and-autocomplete)
- [Radio, switch, and controlled state](#radio-switch-and-controlled-state)
- [Expand and collapse](#expand-and-collapse)
- [Menus](#menus)
- [Cupertino controls](#cupertino-controls)
- [Material interaction controls](#material-interaction-controls)
- [Tooltips](#tooltips)
- [Input decoration and shapes](#input-decoration-and-shapes)
- [Time picker](#time-picker)
- [Lists and callback migrations](#lists-and-callback-migrations)

## Material and Cupertino package transition

The in-framework Material and Cupertino libraries are frozen at their final feature
set (`3.44-guide`). Development is moving to independently versioned `material_ui`
and `cupertino_ui` packages, and the in-framework libraries were scheduled for
deprecation in the next stable release. Check a project's dependency strategy before
adding a component that exists only in the package line.

## Theme type and property migrations

Use data-oriented theme values consistently:

- Replace `ThemeData.dialogBackgroundColor` with
  `DialogThemeData.backgroundColor`.
- Replace `ThemeData.indicatorColor` with `TabBarThemeData.indicatorColor`.
- Supply `CardThemeData`, `DialogThemeData`, and `TabBarThemeData` to
  `ThemeData.cardTheme`, `ThemeData.dialogTheme`, and `ThemeData.tabBarTheme`, not the
  old component classes.
- Remaining component themes such as `AppBarTheme`, `BottomAppBarTheme`, and
  `InputDecorationTheme` likewise use `...ThemeData` values (`3.35-guide`).
- Replace `AppBarTheme.color` and `AppBarThemeData.color` with `backgroundColor`.
- Move `ButtonStyleButton.iconAlignment` to `ButtonStyle.iconAlignment` or the
  relevant `styleFrom` helper.
- Replace `Switch.activeColor` with `activeThumbColor`.

`FloatingActionButtonTheme` and `SnackBarTheme` widgets apply component theme
overrides to one subtree without modifying root `ThemeData` (`3.41.0`).

## Navigation components

`NavigationRail` can scroll. `NavigationDrawer` accepts a header and footer, allowing
navigation chrome to stay inside the component instead of being composed around it.

## Material visual defaults

### Progress indicators and sliders

The refreshed Material 3 `CircularProgressIndicator`, `LinearProgressIndicator`, and
`Slider` designs were initially opt-in through `year2023: false` on the component,
`ProgressIndicatorThemeData.year2023`, or `SliderThemeData.year2023` (`3.29.0`):

```dart
CircularProgressIndicator(year2023: false);
Slider(value: value, onChanged: onChanged, year2023: false);
```

Check the active SDK before retaining the transitional property. Slider value
indicators can be configured to remain visible. Both progress indicators can receive
an `AnimationController` when their motion must be driven externally.

### Dialog sizing

Material dialogs have a default maximum width of 560 dp. Override it with
`AlertDialog.constraints` or `SimpleDialog.constraints` only when the design needs a
different width (`3.35.0`).

## Forms and validation

`FormField` can build an arbitrary error widget, not only error text. `FormField.onReset`
runs field-specific clearing logic during `Form.reset`.

Use `AutovalidateMode.onUserInteractionIfError` when interaction-driven validation
should activate only while a field has an error:

```dart
Form(
  autovalidateMode: AutovalidateMode.onUserInteractionIfError,
  child: fields,
)
```

Form state exposes registered fields through `fields`. `clearError` clears a form or
individual `FormFieldState` validation error without resetting its value:

```dart
for (final field in formKey.currentState!.fields) {
  field.clearError();
}
```

A `Form` is not a sliver. Wrap it in `SliverToBoxAdapter` inside a
`CustomScrollView`.

## Dropdowns and autocomplete

`DropdownMenuFormField` integrates a Material 3 dropdown with form state. Replace
`DropdownButtonFormField.value` with `initialValue`.

`DropdownMenu<T>` requires a non-nullable `T`. It supports:

- `DropdownMenu.selectOnly` for selection-only behavior;
- `decorationBuilder` on the menu and form-field forms;
- `errorBuilder` on `DropdownMenuFormField`;
- `cursorHeight`;
- an external `menuController`;
- a focus-node hook for the trailing-icon button.

`MenuController` is not `final`, so specialized controllers may extend it.

`DropdownButton` has an explicit `enabled` property and no longer requires
`onChanged`. Express enabled state independently:

```dart
DropdownButton<String>(
  enabled: canSelect,
  onChanged: handleSelection,
  items: items,
)
```

Material `Autocomplete` supports keyboard traversal and accepts external `focusNode`
and `textEditingController` values. Set a `RawAutocomplete` options-view direction to
`OptionsViewOpenDirection.mostSpace` to open on the side with more room.

## Radio, switch, and controlled state

Move shared value and change handling for `Radio`, `CupertinoRadio`, and
`RadioListTile` into a surrounding `RadioGroup`; per-control `groupValue` and
`onChanged` are deprecated.

Control radio appearance with `RadioListTile.radioInnerRadius` per tile, or
`RadioThemeData.innerRadius` and `RadioThemeData.side` application-wide. A
`ChipThemeData.deleteIconColor` may be a `WidgetStateColor`.

`ExpansionTile`, `RadioListTile`, and `SwitchListTile` accept
`WidgetStatesController`, allowing application code to observe or drive interaction
state. `IconButton.statesController` programmatically controls its `WidgetState`-based
visual states.

## Expand and collapse

`Expansible` is the widget-layer primitive for themed expansion controls.
`RawMenuAnchor` is the unstyled menu primitive below Material's `MenuAnchor`
(`3.32-guide`). Replace deprecated `ExpansionTileController` with reusable
`ExpansibleController`.

Move `Expansible` duration and curve options from individual animation properties to
one `AnimationStyle`. `ExpansionTile.splashColor` controls its interaction splash.
`CupertinoExpansionTile` supplies the corresponding iOS-style control.

## Menus

### Material and raw menus

Material 3 `MenuAnchor` animations are disabled by default; set `animated: true` to
enable them. `SubmenuButton.hoverOpenDelay` controls hover-to-open delay. The ordering
of close callbacks on `RawMenuAnchor` changed, so custom menu state must not depend on
the old callback order.

### Cupertino menus

`CupertinoMenuAnchor` and `CupertinoMenuItem` provide Cupertino-styled anchored menus
on top of `RawMenuAnchor` without a Material dependency (`3.44.0`).

## Cupertino controls

### Buttons and segmented controls

Replace `CupertinoButton.minSize` with independent `minWidth` and `minHeight` values:

```dart
CupertinoButton(
  minWidth: 44,
  minHeight: 36,
  onPressed: submit,
  child: const Text('Submit'),
)
```

Set `CupertinoSlidingSegmentedControl.isMomentary` when a segment should trigger an
action without remaining selected (`3.38-guide`).

### Activity, date, and action controls

- `CupertinoLinearActivityIndicator` provides a linear activity control.
- `CupertinoDatePicker.selectableDayPredicate` rejects individual dates.
- `CupertinoCheckbox` has an adjusted default desktop size.
- `CupertinoActionSheetAction` can receive keyboard focus.
- `CupertinoDynamicColor`-specific methods such as `withAlpha` and `withOpacity` are
  deprecated; call the standard `Color` APIs.

Cupertino sheet navigation and scroll coordination are in the navigation reference.

## Material interaction controls

- `Badge.count(maxCount: ...)` caps the displayed count.
- `InkWell.onLongPressUp` reports release after a long press.
- `TableRowInkWell.onHover` reports row hover changes.
- `AppBar.automaticallyImplyActions` controls inference of action widgets.
- `CarouselView.itemClipBehavior` controls child clipping.
- `TabBar.onHover` and `onFocusChange` expose tab interaction, and
  `TabBarScrollController` provides external scroll control.
- `SearchAnchor` accepts `viewOnOpen`, while `SearchAnchor.bar` accepts `onOpen`.
- `CalendarDatePicker.calendarDelegate` supports non-Gregorian date systems.
- `animationStyle` customizes `showDialog`, `showAdaptiveDialog`, and `DialogRoute`
  transitions.

Material buttons use the basic arrow cursor by default on native platforms, not the
web-style click cursor.

## Tooltips

Replace `Tooltip.height` with `Tooltip.constraints`:

```dart
Tooltip(
  message: 'Refresh',
  constraints: const BoxConstraints(minHeight: 24),
  child: const Icon(Icons.refresh),
)
```

Tooltip placement is customizable, and `RawTooltip` exposes the tooltip widget for
low-level composition. `PlatformMenu` and `PlatformMenuItem` support tooltip text.

## Input decoration and shapes

`InputDecoration.hint` accepts an arbitrary widget. Replace
`maintainHintHeight` with `maintainHintSize`.

`ShapedInputBorder` adapts any `ShapeBorder` to a Material input border, including a
continuous-corner superellipse:

```dart
const InputDecoration(
  border: ShapedInputBorder(shape: RoundedSuperellipseBorder()),
)
```

## Time picker

`showTimePicker` can begin with no selected time when it opens directly in input mode
(`3.38.0`):

```dart
await showTimePicker(
  context: context,
  initialEntryMode: TimePickerEntryMode.input,
  initialTime: null,
);
```

## Lists and callback migrations

Flutter reports a debug error when `ListTile` is wrapped in a colored widget. Remove
or restructure that wrapper.

In separated `ListView` and `SliverList` constructors, replace
`findChildIndexCallback` with `findItemIndexCallback`:

```dart
ListView.separated(
  findItemIndexCallback: (key) => indexFor(key),
  itemBuilder: itemBuilder,
  separatorBuilder: separatorBuilder,
  itemCount: itemCount,
)
```

Replace `ReorderableListView.onReorder` with `onReorderItem`; its `newIndex` already
accounts for removing the item before reinsertion.
