# Navigation, layout, and animation

## Contents

- [Routes and completion](#routes-and-completion)
- [Page transitions and predictive back](#page-transitions-and-predictive-back)
- [Cupertino navigation bars and sheets](#cupertino-navigation-bars-and-sheets)
- [Overlays and anchored layout](#overlays-and-anchored-layout)
- [Slivers and paint geometry](#slivers-and-paint-geometry)
- [Scrolling and cache extent](#scrolling-and-cache-extent)
- [Grids and carousels](#grids-and-carousels)
- [Declarative repeating animation](#declarative-repeating-animation)
- [Alignment and directionality](#alignment-and-directionality)

## Routes and completion

Removing a route now invokes `didComplete` (`3.32.0`). A future returned when the
route was pushed, and custom completion logic, can therefore finish after
`Navigator.removeRoute` as well as after a normal pop.

Use `Navigator.popUntilWithResult` to pop several routes and pass one value to the
destination route in the same operation (`3.41-guide`).

`fullscreenDialog` is available on `ModalRoute`, its descendants, and `showDialog`,
allowing a dialog route to use fullscreen navigation behavior.

For selective rebuilds, use `ModalRoute.opaqueOf(context)`, `isActiveOf(context)`,
`isFirstOf(context)`, and `popDispositionOf(context)` rather than subscribing to every
property on the enclosing route.

## Page transitions and predictive back

`FadeForwardsPageTransitionsBuilder` provides the Material transition that combines
right-to-left movement with cross-fading for both incoming and outgoing pages
(`3.29.0`). It replaces `ZoomPageTransitionsBuilder` as the `MaterialApp` default.

Material navigation enables Android predictive-back route transitions by default.
Shared-element transitions participate in predictive-back gestures, and `Hero`
exposes configurable flight curves (`3.44.0`). Override these defaults explicitly only
when the application must retain a prior motion design.

The corrected `SpringDescription` formula affects underdamped springs with a mass
other than `1`, especially near critical damping. Retune spring parameters when
existing motion must remain visually identical.

## Cupertino navigation bars and sheets

`CupertinoNavigationBar` and `CupertinoSliverNavigationBar` accept a `bottom` widget.
On the sliver form, `bottomMode` selects whether the bottom resizes away during scroll
or remains visible. `CupertinoNavigationBar.large` is a static large-title bar.

`CupertinoSheetRoute` and `showCupertinoSheet` create an iOS-style drag-to-dismiss
route with the normal nested-navigation setup. The sheet surface can display its
native-styled drag handle through `CupertinoSheet.showDragHandle`.

Set `enableDrag: false` when drag dismissal is inappropriate:

```dart
showCupertinoSheet<void>(
  context: context,
  enableDrag: false,
  scrollableBuilder: (context, controller) =>
      ListView(controller: controller),
);
```

Use `scrollableBuilder` to receive the managed `ScrollController`. This coordinates
content scrolling with drag-to-dismiss motion and replaces the deprecated `builder`
and `pageBuilder` parameters (`3.44-guide`).

Pass `routeSettings` when navigator observers need a sheet name or arguments:

```dart
showCupertinoSheet<void>(
  context: context,
  routeSettings: const RouteSettings(name: '/filters'),
  scrollableBuilder: (context, controller) =>
      ListView(controller: controller),
);
```

Full-height Cupertino sheets stretch upward. On iOS, their backdrop blur uses bounded
behavior so translucent colors do not bleed at the filter edges.

## Overlays and anchored layout

`OverlayPortal.overlayChildLayoutBuilder` receives overlay and anchor geometry for
positioning an overlay child. Expect the layout builder to rebuild whenever its
`OverlayPortal` rebuilds.

Replace `OverlayPortal.targetsRootOverlay(...)` with the normal constructor plus:

```dart
OverlayPortal(
  overlayLocation: OverlayChildLocation.rootOverlay,
  controller: controller,
  overlayChildBuilder: overlayBuilder,
  child: child,
)
```

For an experimental content-sized desktop window, `Overlay.alwaysSizeToContent` keeps
the overlay sizing its window from its contents beyond the usual sizing path.

## Slivers and paint geometry

- Control sliver paint order explicitly when z-order matters, for example for an
  overlapping sticky header (`3.35-guide`).
- `RenderSliver.getMaxPaintRect` returns a custom sliver's maximum paint rectangle;
  do not infer it from current painted geometry.
- A `Form` cannot itself be a sliver. Place it inside `SliverToBoxAdapter` in a
  `CustomScrollView`.
- Continue a semantics index across multiple builder slivers with
  `semanticIndexOffset`; see the accessibility reference.

## Scrolling and cache extent

`ScrollCacheExtent` supplies shared cache-extent configuration to more scrolling
widgets. `PageView.scrollCacheExtent` explicitly caches pages outside the viewport.
Two-dimensional viewports can select a cache-extent type, including a
viewport-relative extent (`3.41.0`).

`Scrollbar` padding APIs accept `EdgeInsetsGeometry`, enabling direction-aware
insets. `TableBorder` can paint non-uniform sides.

## Grids and carousels

`GridView` constructors accept `mainAxisExtent`, so fixed-height or fixed-width tiles
do not need a custom delegate:

```dart
GridView.count(
  crossAxisCount: 2,
  mainAxisExtent: 120,
  children: children,
)
```

`CarouselView` supports infinite scrolling and reports movement through
`onIndexChanged`. `CarouselController.leadingItem` exposes the current leading item.
Use `CarouselView.itemClipBehavior` to select child clipping.

## Declarative repeating animation

`RepeatingAnimationBuilder` drives a continuous animation without an owned
`AnimationController`. `RepeatMode.reverse` alternates direction.

```dart
RepeatingAnimationBuilder<Offset>(
  animatable: Tween(
    begin: const Offset(-1, 0),
    end: const Offset(1, 0),
  ),
  duration: const Duration(seconds: 1),
  repeatMode: RepeatMode.reverse,
  builder: (context, offset, child) => FractionalTranslation(
    translation: offset,
    child: child,
  ),
  child: const SizedBox.square(dimension: 100),
)
```

Progress indicators may instead receive an `AnimationController` when application
state must drive or synchronize their animation.

## Alignment and directionality

`AlignmentGeometry` provides directional static members. In a context expecting
`AlignmentGeometry`, dot shorthand can select `.centerStart` without spelling
`AlignmentDirectional.centerStart`:

```dart
Align(alignment: .centerStart, child: child)
```

Always test directional members in both text directions.
