# Migrations and breaking changes

## Removed build and generated artifacts

- Migrate Android Gradle application from the imperative script to declarative
  plug-ins and migrate Android v1 embedding code to v2 (3.29.0,
  `breaking-change-guides`).
- Stop selecting the removed web HTML renderer (3.29.0), importing synthetic
  `package:flutter_gen` output, or producing iOS SkSL warm-up bundles (3.32.0).
- `.flutter-plugins` is gone; read `.flutter-plugins-dependencies` instead. Direct
  dependency checks cannot be disabled (3.35.0).
- The SDK-root `version` file and default `AssetManifest.json` generation are gone;
  use `bin/cache/flutter.version.json` and avoid assuming a legacy manifest exists
  (`3.38-guide`).

## Theme and component type migrations

- Replace `ThemeData.dialogBackgroundColor` with
  `DialogThemeData.backgroundColor`, and move
  `ButtonStyleButton.iconAlignment` into `ButtonStyle.iconAlignment` or
  `styleFrom` (3.29.0).
- Replace `ThemeData.indicatorColor` with `TabBarThemeData.indicatorColor`.
  `cardTheme`, `dialogTheme`, and `tabBarTheme` values use `CardThemeData`,
  `DialogThemeData`, and `TabBarThemeData` (`3.32-guide`).
- Remaining component theme values, including app-bar, bottom-app-bar, and input
  decoration themes, use their data-oriented `...ThemeData` forms
  (`3.35-guide`).
- Replace `Switch.activeColor` with `activeThumbColor`; replace deprecated
  `AppBarTheme.color`/`AppBarThemeData.color` with `backgroundColor` (3.35.0).
- Cupertino dynamic-color convenience methods such as `withAlpha` and
  `withOpacity` are deprecated; use standard `Color` APIs (`3.38-guide`).

## Widget and form contracts

- `PipelineOwner` is `base`: external custom types must extend it with an allowed
  `base`, `final`, or `sealed` class modifier, not implement it (3.32.0).
- Replace `CupertinoButton.minSize` with independent `minWidth` and `minHeight`.
  Replace `Tooltip.height` with `Tooltip.constraints` (3.32.0).
- Put `Form` in `SliverToBoxAdapter` rather than using it directly in a
  `CustomScrollView`. Replace
  `DropdownButtonFormField.value` with `initialValue` (`3.35-guide`).
- Put radio group state and change handling in `RadioGroup`; per-radio
  `groupValue` and `onChanged` are deprecated (`3.35-guide`).
- Configure `Expansible` timing and curves through `AnimationStyle` (3.41.0).
- `DropdownMenu<T>` requires non-nullable `T` (3.41.0). Express a
  `DropdownButton`'s enabled state with `enabled`, independently of `onChanged`
  (`breaking-change-guides`).
- Remove colored wrappers around `ListTile` that trigger the Flutter 3.44 debug
  error. Variable fonts now use `FontWeight` as their weight-axis value starting
  in Flutter 3.41 (`breaking-change-guides`).

## Renamed members and callbacks

- Replace `ExpansionTileController` with `ExpansibleController`
  (`3.32-guide`).
- Replace separated-list `findChildIndexCallback` with `findItemIndexCallback`.
  Replace `InputDecoration.maintainHintHeight` with `maintainHintSize`
  (`breaking-change-guides`).
- Replace `ReorderableListView.onReorder` with `onReorderItem`; its `newIndex`
  already accounts for removal before reinsertion. Audit custom `RawMenuAnchor`
  logic because close-callback ordering changed (`3.44-guide`).
- Replace deprecated Cupertino sheet `builder`/`pageBuilder` with
  `scrollableBuilder`, which supplies the coordinated controller (`3.44-guide`).
- Replace `OverlayPortal.targetsRootOverlay` with `OverlayPortal` and
  `overlayLocation: OverlayChildLocation.rootOverlay` (`3.38-guide`).

## Final classes and removals

- `IconData` and `TextDecoration` are final; use instances or composition.
  `ExtendSelectionByPageIntent` is removed. Remove the `bounded` argument from
  `ImageFilterConfig.blur` (3.44.0).
- Remove `SemanticsConfiguration`/`SemanticsNode` elevation and thickness
  properties (`3.35-guide`).
- The `plugin_ffi` template is deprecated in favor of the standard plug-in
  template with FFI support; Objective-C plug-in generation is deprecated in favor
  of Swift (`3.44-guide`, 3.38.0).

## Behavior changes to retest

- Route removal now calls `didComplete`, so futures and custom lifecycle work run
  after `Navigator.removeRoute` (3.32.0).
- Corrected underdamped `SpringDescription` math changes motion when mass is not 1,
  especially near critical damping; retune parameters if old motion is required
  (`3.32-guide`).
- `SnackBar` with an action no longer auto-dismisses (`3.38-guide`).
- `ImageFilter.blur` chooses tile mode automatically when omitted; specify one if
  edge sampling must remain fixed (`breaking-change-guides`).
- Edge-to-edge system UI is the Android default, large screens increasingly ignore
  orientation/resizability restrictions, and integrations cannot restore separate
  mobile UI/platform threads.
