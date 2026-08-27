# Layout, Animation, and Graphics

## Lookahead and Bounds Animation

### `animateBounds` and lazy lookahead (`1.8.0`)

`Modifier.animateBounds` animates size and position changes inside a lookahead
scope. `LazyGrid` and Pager support lookahead and keep lookahead and approach
passes distinct for scrolling, retained or composed items, disposal, and item
animation targets.

### Visual debugging (`1.11.0`)

Use `LookaheadAnimationVisualDebugging`,
`CustomizedLookaheadAnimationVisualDebugging`, and
`LookaheadAnimationVisualDebugConfig` to inspect target bounds, animation
trajectories, shared-element matches, and active-transition state for shared
elements and `Modifier.animatedBounds`.

## Animation APIs

### Finalized animation surfaces (`1.8.0`)

Keyframes with Arcs and Splines and the `AnimatedImageVector` API suite are
stable. The `sharedElement` argument previously named `state` is now
`sharedContentState`.

### Shared transitions (`1.10.0`)

Shared-transition APIs are stable and support:

- dynamic enablement;
- fallback target bounds when targets have been disposed;
- initial gesture velocity;
- lookahead-scope coordinates; and
- `Modifier.skipToLookaheadPosition`.

The skip-to-size and skip-to-position modifiers are active by default only
during a shared transition. Replace `ScaleToBounds` with `scaleToBounds`.
Remove uses of the lambda-taking `SharedContentConfig` factory and the removed
`clipInOverlayDuringTransition` parameter. `BoundsTransform` now follows
`SizeTransform`.

### Veil transitions (`1.10.0`)

`unveilIn` and `veilOut` are `EnterTransition` and `ExitTransition` options
that animate an overlay in front of entering or exiting `AnimatedVisibility`
and `AnimatedContent`.

### Animation state correctness (`1.11.0`)

`SeekableTransitionState` handles off-UI-thread changes made inside
`Snapshot.withMutableSnapshot()` without attempting to process the transition
on that thread. `InfiniteRepeatableSpec` prevents zero-duration cycles. Custom
`AnimationSpec` implementations have their `visibilityThreshold` honored by
`animateFloatAsState`.

## Flow, Flex, and Grid Layouts

### Flow migration (`1.8.0`)

`ContextualFlowRow` and `ContextualFlowColumn` are deprecated, as are
experimental `FlowRow` and `FlowColumn` overloads with an `overflow` parameter.
Prefer overloads without `overflow`; they retain `Clip` behavior. Many
contextual-row cases fit `FlowRow`, while uncommon cases require a custom
layout.

### `FlexBox` (`1.11.0`)

`FlexBox` is a configurable superset of `Row`, `Column`, `FlowRow`, and
`FlowColumn`. Use `FlexBoxConfig` and `Modifier.flex` for grow, shrink,
wrapping, direction, and alignment. Its DSL uses calls such as `grow(1f)`, not
property assignments.

Children that cannot shrink far enough overflow the main axis. Add
`Modifier.clipToBounds()` when clipping is desired.

### Explicit non-lazy `Grid` (`1.11.0`)

The experimental `Grid` composable provides CSS-like two-dimensional layout
with fixed, percentage, flexible, and content-sized tracks. Place content with
`Modifier.gridItem()` and opt in to `ExperimentalGridApi`.

`GridConfigurationScope.constraints` exposes available size.
`GridTrackSize.Auto` ranges from min-content to max-content. When a flexible
track contains a `SubcomposeLayout` such as `LazyColumn`, use
`MinMax(0.dp, 1.fr)` to avoid intrinsic queries.

## Lazy Layout Infrastructure

### Stable custom lazy layouts (`1.9.0`)

`LazyLayout`, `LazyLayoutItemProvider`, and `LazyLayoutMeasureScope` are stable
and work with `LazyLayoutMeasurePolicy`. The empty `LazyLayoutPrefetchState`
constructor and its precomposition and premeasure scheduling methods are also
stable.

Custom `PrefetchScheduler` implementations are deprecated; use automatic
internal scheduling.

### Node and key-index APIs (`1.10.0`)

`BeyondBoundsLayoutModifierNode` supports layout beyond visible bounds during
focus search. `LazyLayoutKeyIndexMap` has a default implementation factory.
The former automatic-nested-prefetch behavior flag was removed, so delete
assignments rather than trying to preserve the old path.

## Modifier-Node Lifecycle

### Environment-change hooks (`1.8.0`)

`DelegatableNode` provides `onDensityChange` and `onLayoutDirectionChange` for
nodes whose cached calculations depend on those values.

### Placement and measurement (`1.10.0`, `1.11.0`)

`UnplacedStateAwareModifierNode` was finalized as
`UnplacedAwareModifierNode`; it is notified when a previously placed layout
becomes unplaced. Replace
`DelegatableNode.invalidateLayoutForSubtree` with
`invalidateMeasurementForSubtree`.

A custom node that only needs `onRemeasured()` should implement
`MeasuredSizeAwareModifierNode`, not the broader `LayoutAwareModifierNode`.

## Shadows, Shaders, and Layers

### Custom shadows (`1.9.0`)

Shadow modifiers plus `DropShadowPainter` and `InnerShadowPainter` provide
custom drop and inner shadows. Share generated shadow infrastructure across
call sites instead of regenerating it for each use.

### Shader composition (`1.9.0`)

`CompositeShader` and `CompositeShaderBrush` combine two shaders.
`ShaderBrush.transform` applies a transformation matrix. `graphicsLayer`
accepts both `blendMode` and `colorFilter`.

### Wide-gamut color (`1.12.0`)

On Android API 29 and newer, `Paint` and `Shader` preserve colors in spaces
such as Adobe RGB and Display P3. Older Android versions fall back to sRGB.

### Mesh gradients (`1.12.0`)

`MeshGradientPainter` replaces `Modifier.meshGradient`. It renders with the
hardware-accelerated `Canvas.drawMesh`; install it through `Modifier.paint`.

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
