# Navigation, layout, and animation

## Routes and transitions

- `FadeForwardsPageTransitionsBuilder` combines forward horizontal motion with
  incoming/outgoing cross-fades (3.29.0). It becomes `MaterialApp`'s default in
  `3.38-guide`, alongside predictive-back-aware route transitions; override it
  explicitly only when retaining `ZoomPageTransitionsBuilder` is required.
- Removing a route invokes `didComplete`, so route futures and custom completion
  logic run even for `Navigator.removeRoute` (3.32.0).
- `ModalRoute.opaqueOf(context)`, `ModalRoute.isActiveOf(context)`,
  `ModalRoute.isFirstOf(context)`, and `ModalRoute.popDispositionOf(context)`
  subscribe to one route property rather than all route changes (3.35.0).
- `fullscreenDialog` is available through `ModalRoute`, descendants, and
  `showDialog` (`3.35-guide`).
- Shared-element transitions participate in Android predictive back (3.35.0), and
  `Hero` exposes animation-curve customization in 3.44.0.
- `Navigator.popUntilWithResult` pops several routes while delivering one result to
  the destination route (`3.41-guide`).

## Cupertino sheets and bars

- `CupertinoNavigationBar` and `CupertinoSliverNavigationBar` accept `bottom`;
  `bottomMode` controls whether a sliver bar's bottom resizes away. Use
  `CupertinoNavigationBar.large` for a static large-title bar (3.29.0).
- `CupertinoSheetRoute` and `showCupertinoSheet` create drag-dismissable iOS-style
  sheets with nested navigation. `enableDrag: false` disables drag dismissal
  (`3.29.0`, `3.32-guide`).
- Full-height sheets stretch upward and `CupertinoSheet.showDragHandle` adds the
  native handle (3.38.0, `3.41-guide`).
- Replace deprecated `builder` and `pageBuilder` with
  `CupertinoSheetRoute.scrollableBuilder`; use its managed controller so scrolling
  and drag dismissal cooperate (`3.44-guide`).
- `showCupertinoSheet.routeSettings` gives observers a route name and arguments
  (3.44.0).

```dart
showCupertinoSheet<void>(
  context: context,
  routeSettings: const RouteSettings(name: '/filters'),
  scrollableBuilder: (context, controller) =>
      ListView(controller: controller, children: const [Text('Content')]),
);
```

## Overlays, menus, and anchored placement

- `OverlayPortal.overlayChildLayoutBuilder` positions an overlay child from overlay
  and anchor geometry and rebuilds with its portal (3.32.0).
- Replace `OverlayPortal.targetsRootOverlay(...)` with `OverlayPortal(...)` and
  `overlayLocation: OverlayChildLocation.rootOverlay` (`3.38-guide`).
- `RawAutocomplete` can use `OptionsViewOpenDirection.mostSpace` to choose the side
  with most room (`3.41-guide`); Material `Autocomplete` supports keyboard option
  navigation (3.32.0).
- `CupertinoMenuAnchor` and `CupertinoMenuItem` provide anchored menus without a
  Material dependency (3.44.0).

## Slivers, viewports, and grids

- Explicit sliver paint order controls z-order for overlaps such as sticky headers
  (`3.35-guide`).
- `SliverList.builder`, `SliverGrid.builder`, and `SliverFixedExtentList.builder`
  accept `semanticIndexOffset` to continue accessibility indexing across slivers
  (3.38.0).
- Two-dimensional viewports choose a cache-extent type, including viewport-relative
  caching. `GridView` constructors accept `mainAxisExtent` for fixed main-axis tile
  size (3.41.0).
- `ScrollCacheExtent` shares cache configuration across scroll views, and
  `PageView.scrollCacheExtent` caches pages beyond the viewport (3.44.0).
- Rendering code can use `RenderSliver.getMaxPaintRect` rather than infer maximum
  paint bounds from current geometry (3.44.0).

## Layout and shapes

- Rounded-superellipse APIs include `RoundedSuperellipseBorder`,
  `ClipRSuperellipse`, `Canvas.drawRSuperellipse`, `Canvas.clipRSuperellipse`, and
  `Path.addRSuperellipse`
  (`3.32-guide`). Initial desktop/web fallback to rounded rectangles ended for web
  in 3.35.0.
- Scrollbar padding accepts `EdgeInsetsGeometry`; `TableBorder` paints non-uniform
  side styles (3.38.0).
- Material dialogs default to a 560 dp maximum width. Override through
  `AlertDialog.constraints` or `SimpleDialog.constraints` (3.35.0).
- `ShapedInputBorder` adapts any `ShapeBorder`, including a rounded superellipse,
  for Material input decoration (`3.44-guide`).

## Animation

- Dialog entry points and `DialogRoute` accept `animationStyle`
  (`3.32-guide`).
- Corrected `SpringDescription` math changes underdamped motion for masses other
  than 1 near critical damping; retune parameters when preserving old motion
  (`3.32-guide`).
- `RepeatingAnimationBuilder` owns a continuous animation without a manual
  controller; `RepeatMode.reverse` alternates direction (`3.41-guide`).
- `Expansible` consolidates timing and curve configuration in `AnimationStyle`
  (3.41.0).
- `CarouselView` supports infinite looping, `onIndexChanged`, and
  `CarouselController.leadingItem` (`3.44-guide`).

## Window-linked layout

Experimental desktop windowing can size views from content. `Overlay.alwaysSizeToContent`
keeps the window following overlay content (3.44.0). Gate this behavior because
unsupported window archetypes may throw and main-channel APIs can change.
