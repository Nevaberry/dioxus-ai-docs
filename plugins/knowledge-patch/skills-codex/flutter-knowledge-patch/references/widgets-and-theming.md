# Widgets and theming

## Material visual defaults and themes

- In 3.29.0, set `year2023: false` on progress indicators or `Slider`, or on
  `ProgressIndicatorThemeData.year2023`/`SliderThemeData.year2023`, to opt into the refreshed
  Material 3 appearance. `FadeForwardsPageTransitionsBuilder` supplies the newer
  navigation transition.
- Replace `ThemeData.dialogBackgroundColor` with
  `DialogThemeData.backgroundColor`, and move button icon alignment to
  `ButtonStyle.iconAlignment` or `styleFrom` (3.29.0).
- Replace `ThemeData.indicatorColor` with `TabBarThemeData.indicatorColor` and use
  `CardThemeData`, `DialogThemeData`, and `TabBarThemeData` values
  for `ThemeData.cardTheme`, `dialogTheme`, and `tabBarTheme` (`3.32-guide`).
  Remaining component themes, including `AppBarTheme`,
  `BottomAppBarTheme`, and `InputDecorationTheme`, likewise use `...ThemeData`
  forms (`3.35-guide`).
- Move deprecated `Switch.activeColor` to `activeThumbColor`, and app-bar theme
  `color` to `backgroundColor` (3.35.0).
- `FloatingActionButtonTheme` and `SnackBarTheme` widgets provide subtree-scoped
  overrides without changing root `ThemeData` (3.41.0).
- Material and Cupertino libraries reached their final in-framework feature set in
  `3.44-guide` and are moving to independently versioned `material_ui` and
  `cupertino_ui` packages; in-framework versions were scheduled for deprecation.

## Menus and anchored controls

- `RawMenuAnchor` is the unstyled primitive under Material `MenuAnchor`
  (`3.32-guide`). `MenuController` can be subclassed in 3.38.0.
- Material 3 `MenuAnchor` animations are off by default; set `animated: true`.
  `SubmenuButton.hoverOpenDelay` controls pointer-hover opening (`3.44-guide`).
- Audit custom `RawMenuAnchor` behavior because close callback ordering changed
  (`3.44-guide`).
- `CupertinoMenuAnchor` and `CupertinoMenuItem` provide Cupertino anchored menus
  without Material (3.44.0).

## Forms, fields, and validation

- `FormField` error output can be any widget, and `onTapUpOutside` customizes field
  behavior (`3.32-guide`). `InputDecoration.hint` accepts a widget when `hintText`
  is too restrictive (3.32.0).
- `FormField.onReset` handles field-specific clearing. `DropdownMenuFormField`
  integrates Material 3 dropdowns with forms (`3.35-guide`).
- Do not use `Form` directly as a sliver; wrap it in `SliverToBoxAdapter`. Replace
  `DropdownButtonFormField.value` with `initialValue` (`3.35-guide`).
- `AutovalidateMode.onUserInteractionIfError` enables interaction validation when
  a field has an error (3.41.0).
- `DropdownMenu` also adds `cursorHeight`, an external `menuController`, and a
  `focusNode` hook for its trailing-icon button; `MenuController` is subclassable
  (3.38.0).
- `DropdownMenu<T>` requires non-nullable `T`; `DropdownMenu.selectOnly` adds selection-only
  behavior. `DropdownMenu` and its form-field variant accept `decorationBuilder`,
  and the form field accepts `errorBuilder` (3.41.0).
- `DropdownButton.enabled` expresses enabled state separately from `onChanged`
  (`breaking-change-guides`).
- Form state exposes registered `fields`; `clearError` clears form or individual
  `FormFieldState` errors without resetting values (3.44.0).
- Replace `InputDecoration.maintainHintHeight` with `maintainHintSize`; use
  `ShapedInputBorder` to adapt a `ShapeBorder` (`breaking-change-guides`,
  `3.44-guide`).

## Selection and editing controls

- `SelectionListener` reports selection details and
  `SelectableRegionSelectionStatusScope` reports changing/final state (3.29.0).
- Material `Autocomplete` supports keyboard navigation (3.32.0). It accepts an
  external `focusNode` and `textEditingController` in 3.35.0.
- Text input accepts Android `hintLocales` and `selectAllOnFocus` controls automatic
  full selection (3.35.0). iOS inline prediction is an opt-in experimental
  `enableInlinePrediction` behavior (`3.44-guide`).
- Web `SelectableRegion` preserves constraints and multiline copy line breaks
  (`3.44-guide`).

## Expansion, radio, and external state

- `Expansible` is the widget-layer expand/collapse primitive; migrate
  `ExpansionTileController` to `ExpansibleController` (`3.32-guide`). Move its
  animation settings into `AnimationStyle` (3.41.0).
- `CupertinoExpansionTile` provides the Cupertino counterpart (`3.35-guide`).
- Move `Radio`, `CupertinoRadio`, and `RadioListTile` group value/change state into
  `RadioGroup` (`3.35-guide`).
- Style radios through `RadioListTile.radioInnerRadius`,
  `RadioThemeData.innerRadius`, and `RadioThemeData.side`. A chip delete icon can
  use `WidgetStateColor` through `ChipThemeData.deleteIconColor` (3.38.0).
- `ExpansionTile`, `RadioListTile`, and `SwitchListTile` accept
  `WidgetStatesController`; `TabBar` accepts `TabBarScrollController` (3.44.0).

## Material interaction controls

- `TabBar` reports `onHover` and `onFocusChange`. `SearchAnchor` adds `viewOnOpen`
  and `SearchAnchor.bar` adds `onOpen`. `CalendarDatePicker.calendarDelegate`
  supports non-Gregorian logic (`3.32-guide`).
- `NavigationRail` can scroll, `NavigationDrawer` accepts header/footer, and slider
  value indicators can remain visible (`3.35-guide`).
- `IconButton.statesController` drives programmatic widget states
  (`3.38-guide`).
- `Badge.count(maxCount: ...)` caps counts; `InkWell.onLongPressUp` and
  `TableRowInkWell.onHover` report interactions. `ExpansionTile.splashColor`,
  `AppBar.automaticallyImplyActions`, and `CarouselView.itemClipBehavior` control
  splash, inferred actions, and clipping (3.38.0).
- `CircularProgressIndicator` and `LinearProgressIndicator` accept an
  `AnimationController` for externally synchronized animation (3.38.0).
- Non-web Material buttons default to the basic arrow cursor, not the click cursor
  (3.41.0).
- `CarouselView` adds infinite looping and `onIndexChanged`;
  `CarouselController.leadingItem` reports the leading item (`3.44-guide`).

## Cupertino controls

- `CupertinoButton.minSize` is deprecated; use independent `minWidth` and
  `minHeight` (3.32.0).
- `CupertinoAlertDialog` and `CupertinoActionSheet` use the rounded-superellipse
  shape introduced in `3.32-guide`.
- `CupertinoSlidingSegmentedControl.isMomentary` triggers without retaining
  selection (`3.38-guide`).
- `CupertinoLinearActivityIndicator` is a linear activity control.
  `CupertinoDatePicker.selectableDayPredicate` rejects dates, full-height sheets
  stretch upward, and `CupertinoCheckbox` has an adjusted desktop default size
  (3.38.0).
- Standard `Color` methods replace deprecated `CupertinoDynamicColor`-specific
  `withAlpha` and `withOpacity` (`3.38-guide`).
- `CupertinoActionSheetAction` can receive keyboard focus (3.41.0), and
  `CupertinoSheet.showDragHandle` supplies a native-styled handle
  (`3.41-guide`).

## Dialogs, tooltips, and temporary UI

- `showDialog`, `showAdaptiveDialog`, and `DialogRoute` accept `animationStyle`
  (`3.32-guide`). Material dialogs default to
  maximum width 560 dp; override through `AlertDialog.constraints` or
  `SimpleDialog.constraints` (3.35.0).
- Replace `Tooltip.height` with `Tooltip.constraints` (3.32.0). Tooltip placement
  is customizable; `RawTooltip` exposes its widget, and `PlatformMenu`/
  `PlatformMenuItem` support tooltip text (3.41.0).
- A `SnackBar` with an action no longer auto-dismisses (`3.38-guide`).
- `showTimePicker` accepts `initialTime: null` when opened directly in text-input
  mode (3.38.0).

## Shapes, alignment, and paint

- Use `RoundedSuperellipseBorder`, `ClipRSuperellipse`, and matching canvas/path
  APIs for continuous corners (`3.32-guide`). Web gained native support in 3.35.0.
- `AlignmentGeometry` exposes directional members such as `.centerStart`
  instead of requiring `AlignmentDirectional` (3.41.0).
- `ColorFilter.saturation` provides direct saturation adjustment (3.41.0).
- Variable-font weight axes now follow the `fontWeight`/`FontWeight` setting
  starting in Flutter 3.41
  (`breaking-change-guides`).

## Callback and type migrations

- Replace separated-list `findChildIndexCallback` with `findItemIndexCallback` and
  `ReorderableListView.onReorder` with `onReorderItem`; the new reorder index is
  already adjusted (`breaking-change-guides`, `3.44-guide`).
- `IconData` and `TextDecoration` are final; do not subclass them.
  `ExtendSelectionByPageIntent` is removed (3.44.0).
- Colored wrappers around `ListTile` trigger a Flutter 3.44 debug error; restructure
  that coloring (`breaking-change-guides`).
