# Material 3 Components

Use this reference when upgrading stable Material 3 components or preserving behavior and visuals across the migration.

## Tab-row migration (1.9.0)

`TabRow` and `ScrollableTabRow` are deprecated. Migrate to the primary or secondary tab-row variant that matches the component's hierarchy and emphasis.

## Icons dependency (material3-1.4.0)

Material 3 no longer adds `material-icons-core` transitively. A project that still imports it must declare it directly.

The `androidx.compose.material.icons` library is no longer updated or recommended. Prefer a Material Symbols Vector Drawable XML downloaded from the Android tab of the Material icons site.

## Navigation-item selected labels (material3-1.4.0)

Selected `NavigationBarItem` and `NavigationRailItem` labels use `MaterialTheme.colorScheme.secondary` instead of `onSurface`.

To preserve the previous appearance, copy the default colors and set `selectedTextColor = MaterialTheme.colorScheme.onSurface`.

## Motion schemes (material3-1.4.0)

Material 3 components obtain motion from a `MotionScheme` supplied through `MaterialTheme`. Modifier nodes can read it with `currentValueOf(MotionTheme.LocalMotionScheme)`. Create the standard scheme with `MotionScheme.standard()`.

## Expressive and override APIs (material3-1.4.0)

Public APIs still annotated `ExperimentalMaterial3ExpressiveApi` or `ExperimentalMaterial3ComponentOverrideApi` were removed from the stable 1.4 line. Code that requires those APIs must use a compatible 1.5 alpha artifact rather than expecting them in stable 1.4.

## State-backed and secure text fields (material3-1.4.0)

`TextField` and `OutlinedTextField` have `TextFieldState` overloads. Their `TextFieldDecorator`-compatible decoration APIs are stable. Use `labelPosition` to keep a label minimized when a placeholder must remain visible while the field is unfocused.

`SecureTextField` and `OutlinedSecureTextField` provide Material password-entry components.

## Search bars and expanded views (material3-1.4.0)

Collapsed and expanded search surfaces are separate:

- `SearchBar` renders the collapsed surface.
- `ExpandedFullScreenSearchBar` and `ExpandedDockedSearchBar` render expanded views in a new window.
- `SearchBarState` coordinates the surfaces.
- `TopSearchBar` includes inset and scroll handling.
- `InputField` has a state-backed overload.

## Time pickers (material3-1.4.0)

`TimePickerDialog` can host `TimePicker`, `TimeInput`, or a UI that switches between them. Replace `TimePickerState.isAfternoon` with the `isPm` extension property.

## Hero carousel and state (material3-1.4.0)

`HorizontalCenteredHeroCarousel` provides a center-aligned hero layout. Carousel composables accept `userScrollEnabled`. `CarouselState` exposes `currentItem` and programmatic scrolling.

## Pull to refresh (material3-1.4.0)

In `PullToRefreshDefaults`:

- `shape` is renamed to `indicatorShape`;
- `containerColor` is renamed to `indicatorContainerColor`;
- `indicatorMaxDistance` is added.

Custom `PullToRefreshState` implementations must implement `isAnimating`; they no longer inherit a default implementation.

## Date pickers (material3-1.4.0)

`DatePicker`, `DateRangePicker`, and their supporting APIs are stable. Their state factories and extensions support `LocalDate` and `YearMonth` on API 26 and newer, or on older APIs with desugaring. `getDisplayedMonth()` is non-null.

The input-mode focus option accepts an optional `FocusRequester`, not a Boolean. Setting a state locale directly does not localize default title or headline text.

## Tooltip positioning and dismissal (material3-1.4.0)

Use `rememberTooltipPositionProvider` instead of deprecated plain and rich position-provider functions. `TooltipScope.layoutCoordinates` exposes the anchor and supersedes `drawCaret`; tooltips support custom caret shapes and positions.

The dismissal overload accepts `onDismissRequest`, and `onDismiss` is no longer suspend. `TooltipBox` defaults `focusable` to `false` and adds `hasAction`. Plain and rich tooltips default to maximum widths of 200 dp and 320 dp respectively.

## Bottom sheets (material3-1.4.0)

`ModalBottomSheet` adds `sheetGestureEnabled`. `ModalBottomSheetProperties` can prevent scrim clicks from requesting dismissal; its light status-bar and navigation-bar options are Android-only.

`SheetState.isAnimationRunning` is public. Its density constructor is deprecated in favor of positional and velocity thresholds. `BottomSheetDefaults.windowInsets` includes `WindowInsets.safeDrawing.Top`.

## Wide navigation rails (material3-1.4.0)

`WideNavigationRail`, `ShortNavigationBar`, and `NavigationItem` are stable. `WideNavigationRailItem` requires `railExpanded`, and `WideNavigationRailState` exposes Boolean current and target values.

Use `Arrangement.Vertical` instead of `WideNavigationRailArrangement`. Use renamed shape defaults in `WideNavigationRailDefaults`; `ModalWideNavigationRailDefaults` is removed.

## Navigation-suite layouts (material3-1.4.0)

`NavigationSuite`, `NavigationSuiteItem`, `NavigationSuiteColors`, and `NavigationSuiteTypes` support extra navigation layouts selected through `navigationSuiteType`. Matching scaffold and layout APIs accept optional primary-action content.

## Slider state and layouts (material3-1.4.0)

Hoist state with `rememberSliderState` and `rememberRangeSliderState`. `SliderState.shouldAutoSnap` can disable automatic snapping for a custom animation, and `onValueChange` is public.

Material 3 also provides `VerticalSlider`, center-origin `CenteredTrack`, customizable external track corners and icons, and `trackCornerSize` for range-slider tracks.

## Color schemes and annotated links (material3-1.4.0)

The `ColorScheme` constructor without fixed color roles is deprecated. The constructor without surface-container roles is hidden. Custom schemes should supply both role families.

`ColorScheme.contentColorFor(surfaceDim)` resolves to `onSurface`. Links in `Text(AnnotatedString)` receive Material styling by default.

## Display-cutout insets (material3-1.4.0)

Inset-aware Material 2 and Material 3 components include `displayCutout` in their default `WindowInsets`. Override the component's inset parameter when the layout intentionally draws into the cutout area.
