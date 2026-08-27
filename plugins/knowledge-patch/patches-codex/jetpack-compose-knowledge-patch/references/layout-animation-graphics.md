# Layout, Animation, and Graphics

Use this reference for lookahead and shared transitions, custom layouts and modifier nodes, lazy infrastructure, shadows, shaders, color interop, and painters.

## Lookahead bounds animation (1.8.0)

`Modifier.animateBounds` animates size and position changes within a lookahead scope. `LazyGrid` and Pager support lookahead, separating lookahead from approach passes for scrolling, retained or composed items, disposal, and item-animation targets.

Code that observes placement or lifetime must account for both passes instead of treating lookahead as ordinary final layout.

## Animation API finalization (1.8.0)

Keyframes with Arcs and Splines are stable, as is the `AnimatedImageVector` API suite. The `sharedElement` parameter formerly named `state` is now `sharedContentState`; use the new named argument at call sites.

## Flow-layout deprecations (1.8.0)

`ContextualFlowRow` and `ContextualFlowColumn` are deprecated. Experimental `FlowRow` and `FlowColumn` overloads with an `overflow` parameter are also deprecated.

Prefer overloads without `overflow`; their behavior remains `Clip`. Many contextual-row cases can use `FlowRow`, while less common virtualization or placement needs may require a custom layout.

## Custom modifier-node hooks (1.8.0)

`DelegatableNode` receives `onDensityChange` and `onLayoutDirectionChange`. `PointerInputModifierNode.touchBoundsExpansion` enlarges the hit bounds of one pointer-input node.

`BringIntoViewResponderModifierNode` exposes bring-into-view behavior at modifier-node level and allows platform implementations.

## BasicText layer behavior (1.8.0)

`BasicText` no longer adds an implicit `graphicsLayer`. Add `Modifier.graphicsLayer()` explicitly when clipping, isolation, transforms, or another layer-dependent effect relies on it.

## Custom lazy layouts and prefetching (1.9.0)

`LazyLayout`, `LazyLayoutItemProvider`, and `LazyLayoutMeasureScope` are stable, along with `LazyLayoutMeasurePolicy`.

The empty `LazyLayoutPrefetchState` constructor and its precomposition and premeasure scheduling methods are stable. Custom `PrefetchScheduler` use is deprecated; rely on automatic internal scheduling.

## Drop and inner shadows (1.9.0)

Shadow modifier APIs plus `DropShadowPainter` and `InnerShadowPainter` support custom drop and inner shadows. Share generated shadow infrastructure across call sites when possible instead of regenerating it for every use.

## Shaders, layers, and packed colors (1.9.0)

`CompositeShader` and `CompositeShaderBrush` combine two shaders. `ShaderBrush.transform` applies a shader transformation matrix. `graphicsLayer` accepts `blendMode` and `colorFilter`.

Compose packed colors are not directly comparable with Android `ColorLong` values. Convert with `toColorLong()` and `fromColorLong()` before comparison or platform interop.

## Frame-rate requests (1.9.0)

Use `Modifier.preferredFrameRate` to request a numeric frame rate or `FrameRateCategory` from `androidx.compose.ui`. It replaces `requestedFrameRate`; `FrameRateCategory.NoPreference` is removed.

## Shared transitions (1.10.0)

Shared-transition APIs are stable and support:

- dynamic enablement;
- fallback target bounds when a target is disposed;
- initial gesture velocity;
- lookahead-scope coordinates;
- `Modifier.skipToLookaheadPosition`.

Skip-to-size and skip-to-position modifiers default to active only during a shared transition.

Apply these migrations:

- replace `ScaleToBounds` with `scaleToBounds`;
- remove the lambda-taking `SharedContentConfig` factory;
- remove `clipInOverlayDuringTransition`;
- treat `BoundsTransform` as following `SizeTransform`.

## Veil transitions (1.10.0)

`unveilIn` and `veilOut` are `EnterTransition` and `ExitTransition` options. They animate an overlay in front of content entering or exiting `AnimatedVisibility` or `AnimatedContent`.

## Modifier-node and lazy infrastructure (1.10.0)

`UnplacedStateAwareModifierNode` is finalized as `UnplacedAwareModifierNode`, notified when a previously placed layout becomes unplaced.

Rename `DelegatableNode.invalidateLayoutForSubtree` to `invalidateMeasurementForSubtree`. Foundation also adds `BeyondBoundsLayoutModifierNode` for focus-search layout and `LazyLayoutKeyIndexMap` with a default implementation factory.

## Lookahead visual debugging (1.11.0)

`LookaheadAnimationVisualDebugging`, `CustomizedLookaheadAnimationVisualDebugging`, and `LookaheadAnimationVisualDebugConfig` visualize target bounds, trajectories, shared-element matches, and active-transition state for shared elements and `Modifier.animatedBounds`.

## Animation state behavior (1.11.0)

`SeekableTransitionState` handles off-UI-thread changes made inside `Snapshot.withMutableSnapshot()` without processing the transition on that thread.

`InfiniteRepeatableSpec` prevents zero-duration cycles. Custom `AnimationSpec` implementations have their `visibilityThreshold` honored by `animateFloatAsState`.

## FlexBox (1.11.0)

`FlexBox` is a configurable superset of `Row`, `Column`, `FlowRow`, and `FlowColumn`. `FlexBoxConfig` and `Modifier.flex` control grow, shrink, wrapping, direction, and alignment.

The DSL uses calls such as `grow(1f)`, not property assignment. Content that cannot shrink enough overflows the main axis; add `Modifier.clipToBounds()` when overflow must be clipped.

## Explicit non-lazy Grid (1.11.0)

The experimental `Grid` composable provides CSS-like two-dimensional layout with fixed, percentage, flexible, and content-sized tracks plus `Modifier.gridItem()` placement. Opt in with `ExperimentalGridApi`.

`GridConfigurationScope.constraints` exposes available size. `GridTrackSize.Auto` ranges from min-content to max-content. When a flexible track contains a `SubcomposeLayout` such as `LazyColumn`, use `MinMax(0.dp, 1.fr)` to avoid intrinsic queries.

## Draw visibility and measurement nodes (1.11.0)

`Modifier.visible` suppresses drawing while retaining occupied layout space.

A custom modifier node that only needs `onRemeasured()` should implement `MeasuredSizeAwareModifierNode` rather than the broader `LayoutAwareModifierNode`.

## Wide-color-gamut graphics (1.12.0)

On API 29 and newer, `Paint` and `Shader` preserve non-sRGB colors such as Adobe RGB and Display P3. Older Android releases fall back to sRGB.

## Mesh-gradient painter (1.12.0)

`MeshGradientPainter` replaces `Modifier.meshGradient` and renders with the hardware-accelerated `Canvas.drawMesh`. Install the painter through `Modifier.paint`.

```kotlin
val meshPainter = remember {
    MeshGradientPainter(rows = 1, columns = 1, hasBicubicColor = true) {
        setVertex(0, 0, Offset(0f, 0f), Color.Red)
        setVertex(0, 1, Offset(1f, 0f), Color.Blue)
        setVertex(1, 0, Offset(0f, 1f), Color.Green)
        setVertex(1, 1, Offset(1f, 1f), Color.Yellow)
    }
}
Box(Modifier.paint(meshPainter))
```
