# Navigation, layout, and animation

## Route completion and observation

Removing a route invokes `didComplete` as of 3.32.0. Futures and custom `Route`
logic tied to completion therefore run after `Navigator.removeRoute` as well as a
normal pop. Audit code that treated removal as silent disposal.

Use the selective `ModalRoute.opaqueOf(context)`,
`ModalRoute.isActiveOf(context)`, `ModalRoute.isFirstOf(context)`, and
`ModalRoute.popDispositionOf(context)` lookups when a widget needs one route
property without rebuilding for every route change (3.35.0).

`Navigator.popUntilWithResult` pops multiple routes while delivering one result to
the destination route (3.41-guide).

## Material transitions and predictive back

`FadeForwardsPageTransitionsBuilder` combines right-to-left motion with cross-fades
for incoming and outgoing pages (3.29.0).

By 3.38-guide, `MaterialApp` enables Android predictive-back transitions by default
and replaces the old `ZoomPageTransitionsBuilder` default with
`FadeForwardsPageTransitionsBuilder`. Override explicitly if an app must retain the
old visual behavior.

Shared-element transitions participate in Android predictive back (3.35.0).
`FlutterFragment` and `FlutterFragmentActivity` later support predictive back in
fragment and add-to-app hosts (3.44.0).

`Hero` exposes customizable flight animation curves, so easing no longer requires
replacing the whole transition (3.44.0).

## Cupertino navigation bars and sheets

### Navigation-bar additions (3.29.0)

`CupertinoNavigationBar` and `CupertinoSliverNavigationBar` accept a `bottom`
widget. The sliver's `bottomMode` chooses whether that widget resizes away while
scrolling or stays visible. `CupertinoNavigationBar.large` provides a static
large-title bar.

### Sheet creation and dismissal

`CupertinoSheetRoute` provides an iOS-style drag-to-dismiss modal route, while
`showCupertinoSheet` creates the usual nested-navigation arrangement (3.29.0).
Set `enableDrag: false` to disable drag-down dismissal (3.32-guide).

`CupertinoSheet.showDragHandle` adds the native-styled handle (3.41-guide).
Full-height sheets stretch upward by 3.38.0.

### Scrolling and route identity

Use `CupertinoSheetRoute.scrollableBuilder` so sheet content receives the route's
managed `ScrollController` and coordinates scrolling with drag dismissal
(3.44-guide). The old `builder` and `pageBuilder` parameters on
`CupertinoSheetRoute` and `showCupertinoSheet` are deprecated.

```dart
showCupertinoSheet<void>(
  context: context,
  scrollableBuilder: (context, controller) =>
      ListView(controller: controller, children: const [Text('Content')]),
);
```

`showCupertinoSheet.routeSettings` carries names and arguments for navigator
observers (3.44.0).

## Dialogs and overlays

`fullscreenDialog` is available on `ModalRoute`, descendants, and `showDialog`
(3.35-guide).

`OverlayPortal.overlayChildLayoutBuilder` positions an overlay child from overlay
and anchor geometry and rebuilds when its portal rebuilds (3.32.0).

Replace `OverlayPortal.targetsRootOverlay(...)` with `OverlayPortal(...)` and
`overlayLocation: OverlayChildLocation.rootOverlay` (3.38-guide).

Experimental desktop windowing can create a separate child window for Material
`showDialog` (3.44-guide). Do not assume that production or unsupported targets
provide this behavior.

## Slivers, grids, and caching

Control sliver paint order explicitly when z-order or overlap, such as sticky
headers, must differ from child order (3.35-guide).

Two-dimensional viewports can select a cache-extent type, including
viewport-relative caching. `GridView` constructors accept `mainAxisExtent` for
fixed main-axis tile size (3.41.0).

`ScrollCacheExtent` supplies shared cache configuration across scroll views, and
`PageView.scrollCacheExtent` caches pages outside the viewport explicitly
(3.44.0).

Lower-level sliver code can use `RenderSliver.getMaxPaintRect` rather than infer a
maximum paint rectangle from current painted geometry (3.44.0).

For continuous accessibility ordering, builder constructors on `SliverList`,
`SliverGrid`, and `SliverFixedExtentList` accept `semanticIndexOffset` (3.38.0).

## Alignment, borders, and geometry

`AlignmentGeometry` has directional static members such as `.centerStart`
(3.41.0), avoiding the need to spell them through `AlignmentDirectional`:

```dart
Align(alignment: .centerStart, child: child)
```

Scrollbar padding accepts `EdgeInsetsGeometry` for direction-aware insets.
`TableBorder` supports non-uniform side styles (3.38.0).

Rounded-superellipse primitives include `RoundedSuperellipseBorder`,
`ClipRSuperellipse`, `Canvas.drawRSuperellipse`, `Canvas.clipRSuperellipse`, and
`Path.addRSuperellipse` (3.32-guide). They initially fell back to rounded
rectangles off mobile; `CupertinoAlertDialog` and `CupertinoActionSheet` use the
new shape. The web renderer gained native support in 3.35.0.

`ShapedInputBorder` adapts any `ShapeBorder`, including
`RoundedSuperellipseBorder`, for Material input decoration (3.44-guide).

## Animation controls

The corrected `SpringDescription` formula changes underdamped springs whose mass is
not 1, especially near critical damping (3.32-guide). Retune parameters if an
existing animation must preserve its old motion.

`RepeatingAnimationBuilder` runs a continuous animation without an owned
`AnimationController`. `RepeatMode.reverse` alternates direction (3.41-guide).

Progress indicators can instead receive an external `AnimationController` when
their motion must synchronize with application state (3.38.0).

`Expansible` animation configuration moved from individual properties to a single
`AnimationStyle` (3.41.0).

## Layout verification

- Exercise route removal completion, results across multiple pops, observer-visible
  sheet settings, and selective route dependencies.
- Test predictive back at partial gesture progress, cancellation, shared elements,
  fragments, and add-to-app boundaries.
- Exercise sheet content at top, middle, and end scroll positions before dragging.
- Inspect overlay placement at viewport edges and root-overlay behavior.
- Test sliver overlap, accessibility indexes, cache extent, fixed grid extent, and
  custom maximum paint bounds.
- Compare animation timing after spring migration and under reduced-motion
  preferences.
