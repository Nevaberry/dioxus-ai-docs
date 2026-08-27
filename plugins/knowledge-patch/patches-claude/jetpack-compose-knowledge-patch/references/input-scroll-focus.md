# Input, Scrolling, and Focus

## Focus Navigation and Restoration

### Focus callbacks and directional requests (`1.8.0`)

The stable focus APIs replace `FocusProperties.enter` and `exit` with the
receiver-based `onEnter` and `onExit` callbacks. `FocusRequester` and
`FocusTargetModifierNode` support `requestFocus(FocusDirection)`.

`Modifier.focusRestorer()` now takes a non-null `FocusRequester` parameter
named `fallback`, defaulting to `FocusRequester.Default`; it no longer takes a
lambda.

### Pointer-driven focus behavior (`1.10.0`)

Mouse and touchpad presses outside the focused node clear focus by default. Set
`AbstractComposeView.isClearFocusOnPointerDownEnabled = false` to opt out.

A non-focusable `FocusTargetModifierNode.requestFocus()` routes focus to a
child. `DelegatableNode.requestFocusForChildInRootBounds()` finds an
overlapping child, and `ComposeUiFlags.isInitialFocusOnFocusableAvailable`
enables non-touch initial focus.

### Focus-related flag removal (`1.11.0`)

Delete assignments to removed
`ComposeFoundationFlags.isTextFieldDpadNavigationEnabled` and
`isKeepInViewFocusObservationChangeEnabled`. Text-field D-pad navigation and
the keep-in-view focus-observation behavior are always active.

## Interaction Indications and Feedback

### `IndicationNodeFactory` (`1.9.0`, `1.10.0`)

After recompilation against 1.9.0, the no-explicit-indication overloads of
`clickable`, `combinedClickable`, `selectable`, `toggleable`, and
`triStateToggleable` accept only an `IndicationNodeFactory` from
`LocalIndication`. Supplying a deprecated `Indication` can crash at runtime.

Migrate the indication or temporarily use an overload with an explicit
indication. The former
`ComposeFoundationFlags.isNonComposedClickableEnabled` escape hatch was
removed in 1.10.0; `ComposeFoundationFlags.isNonComposedClickableEnabled = false`
is therefore only a temporary 1.9.0 bridge.

### Haptic feedback (`1.8.0`)

`LocalHapticFeedback` supplies a default Android implementation when the
vibrator reports support. Available `HapticFeedbackType` values include `Confirm`,
`ContextClick`, `GestureEnd`, `GestureThresholdActivate`, `Reject`,
`SegmentFrequentTick`, `SegmentTick`, `ToggleOn`, `ToggleOff`, and
`VirtualKey`.

### Platform interaction sounds (`1.12.0`)

Compose automatically plays Android-configured click and navigation sounds.
Disable them for a subtree when needed:

```kotlin
SoundEffectOnInteraction(enabled = false) {
    Button(onClick = {}) { Text("Silent Button") }
}
```

## Pointer and Gesture Input

### Tap dispatch and nested hand-off (`1.8.0`, `1.10.0`, `1.11.0`)

Tap gesture detectors dispatch their coroutines immediately by default. The
compatibility switch moved to
`ComposeFoundationFlags.isDetectTapGesturesImmediateCoroutineDispatchEnabled`
and was later removed; delete assignments when moving to 1.11.0.

When a child abandons a gesture, a parent draggable or scrollable can pick it
up. When a fling reaches a bound, remaining velocity passes to the next
scrollable in the chain. The migration flags for drag pickup, fling
continuation, pointer-velocity adjustment, and pointer/nested-scroll interop
fixes were removed in 1.10.0.

Also delete the removed 1.11.0
`isNonSuspendingPointerInputInClickableEnabled` assignment.

### Drag detection and thresholds (`1.9.0`)

A `detectDragGestures` overload controls touch slop and orientation locking.
`ViewConfiguration.minimumFlingVelocity` exposes the minimum fling threshold.

### Delayed presses (`1.11.0`)

`ComposeFoundationFlags.isDelayPressesUsingGestureConsumptionEnabled` makes
drag containers delay presses based on gesture consumption. This changes
`Modifier.draggable`, which previously did not delay presses.

### Trackpad events and injection (`1.11.0`)

Trackpad gestures that move a cursor generally arrive as mouse input. Platform
pan and scale gestures use these pointer event types:

- `PanStart`, `PanMove`, and `PanEnd`
- `ScaleStart`, `ScaleChange`, and `ScaleEnd`

Tests can inject them with
`SemanticsNodeInteraction.performTrackpadInput` or
`MultiModalInjectionScope.trackpad`. Multimodal key and rotary injection are
stable, and pan/scale end injection accepts `delayMillis`.

### Expanded pointer hit bounds (`1.8.0`)

`PointerInputModifierNode.touchBoundsExpansion` enlarges the hit bounds of one
pointer-input node without changing its layout bounds.

## Overscroll

### Factories and custom effects (`1.8.0`)

Replace `OverscrollConfiguration` and `LocalOverscrollConfiguration` with
`rememberPlatformOverscrollFactory` and `LocalOverscrollFactory`.

```kotlin
CompositionLocalProvider(LocalOverscrollFactory provides null) {
    contentWithoutOverscroll()
}
```

Provide `rememberPlatformOverscrollFactory(color, padding)` to customize the
platform effect. Scroll, lazy, grid, staggered-grid, and pager APIs accept a
custom `OverscrollEffect`. `withoutVisualEffect` and `withoutEventHandling`
allow one component to handle events and another to draw. Never draw the same
effect twice.

### Anchored draggables (`1.8.0`)

`AnchoredDraggableState.confirmValueChange` is deprecated. Remove disallowed
values from the active anchor set. Use an `OverscrollEffect` to communicate
that a requested action is unavailable.

## Scrolling

### Two-dimensional scrolling (`1.9.0`, `1.10.0`)

Use `Modifier.scrollable2D`, `Scrollable2DState`, its state factories, and
common scroll extensions for two-axis scrolling. The final
`Scrollable2DState.canScroll` contract takes an `Offset`, not an angle.

Mouse-wheel scrolling handles two-dimensional deltas; tests can provide the
same deltas through `MouseInjectionScope`.

### Scrollable areas and indicators (`1.10.0`, `1.11.0`)

`Modifier.scrollableArea()` combines scrolling with bounds clipping and
derives content direction from orientation, layout direction, and
`reverseScrolling`.

`ScrollIndicatorState` is available through `ScrollableState.scrollIndicatorState`
and has implementations for `ScrollState`, `LazyListState`, `LazyGridState`,
`LazyStaggeredGridState`, and `PagerState`. For custom rendering, use
`Modifier.scrollIndicator` and `ScrollIndicatorFactory`.

### Snapping and selection (`1.10.0`)

`SnapFlingBehavior` permits an overshooting `snapAnimationSpec`, which enables
bouncy snap springs; overshoot is still ignored during the approach phase.
Double-tap word selection works in `SelectionContainer` and the
value/on-value-change `BasicTextField`.

### Bring-into-view nodes (`1.8.0`)

`BringIntoViewResponderModifierNode` supplies a node-level mechanism that
platform implementations can use for bring-into-view requests.

## Scroll and Visibility Notifications

### View scroll callbacks (`1.9.0`, `1.10.0`)

Compose can dispatch `ViewTreeObserver.OnScrollChanged` while the transitional
`isOnScrollChangedCallbackEnabled` flag exists. Nodes can explicitly call
`DelegatableNode.dispatchOnScrollChanged`. The flag was removed in 1.10.0, so
delete assignments on upgrade.

### Visibility callbacks (`1.9.0`, `1.10.0`, `1.11.0`)

`Modifier.onVisibilityChanged` supports impression logging, autoplay, and
similar list behavior. It does not callback for an initially invisible node
and correctly emits `false` after a nonzero `minDurationMs`.
`onVisibilityChangedNode()` exposes the mechanism to a custom `Modifier.Node`.

`Modifier.onFirstVisible()` was deprecated because it fires whenever an item
becomes visible again. Use `onVisibilityChanged()` and track prior visibility
according to the intended one-shot or repeat behavior.

### Draw visibility (`1.11.0`)

`Modifier.visible` can suppress drawing while preserving the composable's
occupied layout space.

## Removed Foundation Flags (`1.10.0`)

Delete assignments for flags that formerly controlled automatic nested
prefetch, on-scroll callbacks, fling continuation, drag pickup,
pointer-velocity adjustment, and pointer/nested-scroll interop fixes. The
corresponding corrected behaviors are no longer optional.
