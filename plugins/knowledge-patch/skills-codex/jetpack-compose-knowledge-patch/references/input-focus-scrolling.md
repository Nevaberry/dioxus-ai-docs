# Input, Focus, and Scrolling

Use this reference when migrating focus, indication, pointer, drag, nested-scroll, overscroll, visibility, or interaction-feedback code.

## Focus navigation and restoration (1.8.0)

Stable focus APIs use receiver-based `FocusProperties.onEnter` and `onExit` instead of `enter` and `exit`. `FocusRequester` and `FocusTargetModifierNode` expose `requestFocus(FocusDirection)`.

`Modifier.focusRestorer()` takes a non-null parameter named `fallback`, defaulting to `FocusRequester.Default`; it no longer takes a lambda.

## Indications and clickable modifiers

### Recompilation migration (1.9.0)

After recompilation, `clickable`, `combinedClickable`, `selectable`, `toggleable`, and `triStateToggleable` overloads without an explicit indication accept only an `IndicationNodeFactory` from `LocalIndication`. Supplying a deprecated `Indication` can crash at runtime.

Migrate the indication implementation or use an overload with an explicit indication as a compatibility bridge. `ComposeFoundationFlags.isNonComposedClickableEnabled = false` was a temporary fallback at this stage.

### Compatibility flag removal (1.10.0)

`ComposeFoundationFlags.isNonComposedClickableEnabled` is removed, so the indication migration can no longer be deferred through that flag.

## Overscroll (1.8.0)

Replace `OverscrollConfiguration` and `LocalOverscrollConfiguration` with `rememberPlatformOverscrollFactory` and `LocalOverscrollFactory`.

- Disable overscroll with `LocalOverscrollFactory provides null`.
- Customize platform overscroll with `rememberPlatformOverscrollFactory(color, padding)`.
- Pass a custom `OverscrollEffect` to scroll, lazy, grid, staggered-grid, or pager APIs.
- Use `withoutVisualEffect` and `withoutEventHandling` when event handling and drawing belong to different components.
- Draw a given effect exactly once.

## Anchored dragging (1.8.0)

`AnchoredDraggableState.confirmValueChange` is deprecated. Remove disallowed values from the active anchor set instead. An `OverscrollEffect` can communicate that a requested action is unavailable.

## Gesture dispatch and nested hand-off (1.8.0)

Tap gesture detectors dispatch coroutines immediately by default. The compatibility switch is `ComposeFoundationFlags.isDetectTapGesturesImmediateCoroutineDispatchEnabled`.

A parent draggable or scrollable may take over a gesture abandoned by a child. When a fling reaches a bound, remaining velocity passes to the next scrollable in the nested chain.

## Two-dimensional scrolling and drag detection (1.9.0)

Use `Modifier.scrollable2D`, `Scrollable2DState`, its state factories, and common scroll extensions for two-axis scrolling. The final `Scrollable2DState.canScroll` contract accepts an `Offset`, not an angle.

A `detectDragGestures` overload exposes touch-slop and orientation-lock controls. `ViewConfiguration.minimumFlingVelocity` exposes the minimum fling threshold.

## Scroll and visibility notifications (1.9.0)

Compose can dispatch `ViewTreeObserver.OnScrollChanged` when `isOnScrollChangedCallbackEnabled` is enabled. A modifier node can request dispatch through `DelegatableNode.dispatchOnScrollChanged`.

`Modifier.onFirstVisible` and `Modifier.onVisibilityChanged` provide callbacks suited to impression logging, autoplay, and other visibility-driven behavior. Later behavior and deprecations are described under visibility observation below.

## Scrollbars and scrollable areas (1.10.0)

`ScrollIndicatorState` represents scrollbar data through `ScrollableState.scrollIndicatorState`. Implementations exist for `ScrollState`, `LazyListState`, `LazyGridState`, `LazyStaggeredGridState`, and `PagerState`.

`Modifier.scrollableArea()` combines scrolling with bounds clipping and derives content direction from orientation, RTL, and `reverseScrolling`.

## Fling, wheel, and selection behavior (1.10.0)

`SnapFlingBehavior` accepts an overshooting `snapAnimationSpec`, enabling bouncy snap springs; overshoot is still ignored during the approach phase.

Mouse-wheel scrolling handles two-dimensional deltas, with matching `MouseInjectionScope` test support. Double-tap word selection works in `SelectionContainer` and the value/on-value-change `BasicTextField`.

## Frequently changing scroll values (1.10.0)

`PagerState.currentPageOffsetFraction` and `ScrollState.value` are annotated `@FrequentlyChangingValue`. The related lint rule warns about reading them directly in composition because they can invalidate frequently.

## Removed Foundation behavior flags (1.10.0)

Delete assignments to removed flags for:

- on-scroll callbacks;
- fling continuation;
- drag pickup;
- automatic nested prefetch;
- pointer-velocity adjustment;
- pointer/nested-scroll interop fixes.

Their former compatibility branches are no longer selectable.

## Indirect pointers and focus behavior (1.10.0)

Indirect-touch APIs are renamed to indirect-pointer equivalents. Mouse or touchpad presses outside the focused node clear focus by default; set `AbstractComposeView.isClearFocusOnPointerDownEnabled = false` to opt out.

A non-focusable `FocusTargetModifierNode.requestFocus()` routes focus to a child. `DelegatableNode.requestFocusForChildInRootBounds()` targets an overlapping child. Enable non-touch initial focus with `ComposeUiFlags.isInitialFocusOnFocusableAvailable`.

## Trackpad input and tests (1.11.0)

Cursor-driving trackpad gestures generally arrive as mouse input. Platform pan and scale gestures use these pointer event types:

- `PanStart`, `PanMove`, and `PanEnd`;
- `ScaleStart`, `ScaleChange`, and `ScaleEnd`.

Tests can inject them with `SemanticsNodeInteraction.performTrackpadInput` or `MultiModalInjectionScope.trackpad`. Multimodal key and rotary injection APIs are stable, and pan/scale end injection accepts `delayMillis`.

## Delayed presses in draggable containers (1.11.0)

`ComposeFoundationFlags.isDelayPressesUsingGestureConsumptionEnabled` opts drag containers into delaying press handling according to gesture consumption. It also changes `Modifier.draggable`, which did not previously delay presses.

## Custom scroll indicators and draw visibility (1.11.0)

`Modifier.scrollIndicator` and `ScrollIndicatorFactory` support custom indicators. `Modifier.visible` suppresses drawing while preserving the composable's layout space.

## Visibility callback correction (1.11.0)

`Modifier.onFirstVisible()` is deprecated because it fires each time an item becomes visible, not only the first time. Use `onVisibilityChanged()` and track prior state according to the use case.

## Removed interaction flags (1.11.0)

Delete assignments to removed Foundation flags:

- `isDetectTapGesturesImmediateCoroutineDispatchEnabled`;
- `isNonSuspendingPointerInputInClickableEnabled`;
- `isTextFieldDpadNavigationEnabled`;
- `isKeepInViewFocusObservationChangeEnabled`.

Also remove the deleted UI flag `isSemanticAutofillEnabled`. Semantic autofill, text-field D-pad navigation, and keep-in-view focus observation are always enabled.

## Haptic feedback (1.8.0)

`LocalHapticFeedback` supplies a default Android implementation when the vibrator reports support. Available `HapticFeedbackType` additions are `Confirm`, `ContextClick`, `GestureEnd`, `GestureThresholdActivate`, `Reject`, `SegmentFrequentTick`, `SegmentTick`, `ToggleOn`, `ToggleOff`, and `VirtualKey`.

## Interaction sounds (1.12.0)

Compose automatically plays Android-configured click and navigation sounds. Suppress them for a subtree with:

```kotlin
SoundEffectOnInteraction(enabled = false) {
    Button(onClick = {}) { Text("Silent Button") }
}
```
