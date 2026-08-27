# Material 3 Components

## Dependencies, Themes, and Motion

### Material Icons dependency (`material3-1.4.0`)

Material 3 no longer declares `material-icons-core` transitively. Existing
projects that still use it must declare it directly. The
`androidx.compose.material.icons` library is no longer updated or recommended;
prefer Material Symbols Vector Drawable XML downloaded from the Android tab of
the Material icons site.

### Motion schemes (`material3-1.4.0`)

Material 3 components obtain motion from a `MotionScheme` supplied through
`MaterialTheme`. Modifier nodes can read it with
`currentValueOf(MotionTheme.LocalMotionScheme)`. Construct the standard scheme
with `MotionScheme.standard()`.

### Expressive and override APIs (`material3-1.4.0`)

The stable line removes public APIs still annotated with
`ExperimentalMaterial3ExpressiveApi` or
`ExperimentalMaterial3ComponentOverrideApi`. Code that needs those APIs must
use the 1.5.0 alpha line rather than expecting them in the stable library.

### Color schemes and linked text (`material3-1.4.0`)

The `ColorScheme` constructor without fixed color roles is deprecated, and the
constructor without surface-container roles is hidden. Custom color schemes
should supply both families.

`ColorScheme.contentColorFor(surfaceDim)` resolves to `onSurface`. Links in
`Text(AnnotatedString)` receive Material styling by default.

## Navigation

### Navigation item label color (`material3-1.4.0`)

Selected `NavigationBarItem` and `NavigationRailItem` labels use
`MaterialTheme.colorScheme.secondary` instead of `onSurface`. To preserve the
earlier appearance, copy the default colors and set `selectedTextColor` to
`MaterialTheme.colorScheme.onSurface`.

### Wide rails and short bars (`material3-1.4.0`)

`WideNavigationRail`, `ShortNavigationBar`, and `NavigationItem` are stable.
`WideNavigationRailItem` requires `railExpanded`, and
`WideNavigationRailState` exposes Boolean current and target values.

Replace `WideNavigationRailArrangement` with `Arrangement.Vertical`. Use the
renamed shapes under `WideNavigationRailDefaults`; the
`ModalWideNavigationRailDefaults` container was removed.

### Navigation suites (`material3-1.4.0`)

`NavigationSuite`, `NavigationSuiteItem`, `NavigationSuiteColors`, and
`NavigationSuiteTypes` support extra navigation layouts selected with
`navigationSuiteType`. The matching scaffold and layout APIs accept optional
primary-action content.

### Tab rows (`1.9.0`)

`TabRow` and `ScrollableTabRow` are deprecated. Choose the appropriate primary
or secondary tab-row variant.

## Text Fields and Search

### State-backed and secure fields (`material3-1.4.0`)

`TextField` and `OutlinedTextField` have `TextFieldState` overloads. Their
`TextFieldDecorator`-compatible decoration APIs are stable. Use
`labelPosition` to keep a label minimized when a placeholder must remain
visible while unfocused.

`SecureTextField` and `OutlinedSecureTextField` provide Material password
entry.

### Search bar roles (`material3-1.4.0`)

The search surface is split by presentation:

- `SearchBar` is the collapsed control.
- `ExpandedFullScreenSearchBar` and `ExpandedDockedSearchBar` are expanded
  views opened in a new window.

Drive the surfaces with `SearchBarState`. `TopSearchBar` adds inset and scroll
handling, and `InputField` has a state-backed overload.

## Pickers

### Time pickers (`material3-1.4.0`)

`TimePickerDialog` can contain `TimePicker`, `TimeInput`, or a switchable
combination. Replace `TimePickerState.isAfternoon` with the `isPm` extension
property.

### Date pickers (`material3-1.4.0`)

`DatePicker`, `DateRangePicker`, and their supporting APIs are stable. Their
state factories and extensions support `LocalDate` and `YearMonth` on API 26+
or with desugaring. `getDisplayedMonth()` is non-null.

The input-mode focus option takes an optional `FocusRequester`, not a Boolean.
Changing a state locale directly does not localize the default title or
headline text; provide localized content where required.

## Carousels and Pull to Refresh

### Hero carousels (`material3-1.4.0`)

`HorizontalCenteredHeroCarousel` provides a center-aligned hero layout.
Carousel composables accept `userScrollEnabled`. `CarouselState` exposes
`currentItem` and programmatic scrolling.

### Pull-to-refresh migration (`material3-1.4.0`)

In `PullToRefreshDefaults`:

- `shape` became `indicatorShape`;
- `containerColor` became `indicatorContainerColor`; and
- `indicatorMaxDistance` was added.

Custom `PullToRefreshState` implementations must implement `isAnimating`; it
no longer has an inherited default.

## Tooltips

### Positioning and dismissal (`material3-1.4.0`)

Use `rememberTooltipPositionProvider` instead of the deprecated plain and rich
position-provider functions. `TooltipScope.layoutCoordinates` exposes the
anchor and supersedes `drawCaret`; tooltips support custom caret shape and
position.

The new dismissal overload accepts `onDismissRequest`, while `onDismiss` is no
longer suspend. `TooltipBox` defaults `focusable` to `false` and adds
`hasAction`. Plain and rich tooltips default to maximum widths of 200 dp and
320 dp, respectively.

## Bottom Sheets

### Gesture and dismissal controls (`material3-1.4.0`)

`ModalBottomSheet` accepts `sheetGestureEnabled`.
`ModalBottomSheetProperties` can prevent scrim clicks from requesting
dismissal. Its light status-bar and navigation-bar options are Android-only.

`SheetState.isAnimationRunning` is public. Its density constructor is
deprecated; use positional and velocity thresholds. The default
`BottomSheetDefaults.windowInsets` includes `WindowInsets.safeDrawing.Top`.

## Sliders

### Hoisted state and layouts (`material3-1.4.0`)

Use `rememberSliderState` and `rememberRangeSliderState` for hoisted slider
state. `SliderState.shouldAutoSnap` can disable automatic snapping for a custom
animation, and `onValueChange` is public.

Additional layouts and customization include:

- `VerticalSlider`;
- center-origin `CenteredTrack`;
- external track corners and icons; and
- `trackCornerSize` for range-slider tracks.

## Insets

### Display cutouts (`material3-1.4.0`)

Inset-aware Material 2 and Material 3 components include `displayCutout` in
their default `WindowInsets`. Override the component's inset parameter when
content should intentionally occupy that region.
