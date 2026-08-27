---
name: jetpack-compose-knowledge-patch
description: Jetpack Compose
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Jetpack Compose Compatibility

Use this patch when implementing, upgrading, or testing Jetpack Compose code whose APIs or behavior may have changed. Compose Runtime, UI, Foundation, Material 3, compiler tooling, and BOMs are independently versioned, so inspect the project's Gradle declarations and version catalog before applying guidance.

Trust the project's resolved dependencies, source, and tests when they disagree with general guidance. Apply only advice relevant to the artifact and version actually in use.

## Reference Index

| Reference | Topics |
| --- | --- |
| [Android Hosts, Windows, and Insets](references/android-host-windows.md) | `ComposeView`, windows, insets, resources, window geometry, Android interop |
| [Build, Runtime, and State](references/build-runtime-state.md) | toolchain floors, BOMs, Runtime, snapshots, saveable and retained state, diagnostics |
| [Input, Focus, and Scrolling](references/input-focus-scrolling.md) | focus, pointer input, drag, scroll, overscroll, indications, interaction feedback |
| [Layout, Animation, and Graphics](references/layout-animation-graphics.md) | lookahead, shared transitions, lazy/custom layouts, modifiers, shadows, shaders, painters |
| [Material 3 Components](references/material3-components.md) | navigation, search, text fields, pickers, sheets, tooltips, carousels, sliders, colors |
| [Semantics, Accessibility, and Testing](references/semantics-accessibility-testing.md) | autofill, semantics trees, accessibility, visibility, test dispatchers, hybrid tests |
| [Text and Editing](references/text-editing.md) | autosizing, ellipsis, annotated text, fonts, text fields, undo, menus, secure input |

## Start With the Resolved Build

Before changing code:

1. Identify the resolved versions of Runtime, UI, Foundation, Material 3, and test artifacts; do not infer all component versions from one library.
2. Check whether the project imports a stable, beta, or alpha Compose BOM and whether individual dependencies override it.
3. Inspect `compileSdk`, Android Gradle Plugin, Kotlin Gradle Plugin, and standalone Lint settings.
4. Search for compatibility flags, deprecated overloads, and custom modifier nodes that can change behavior after recompilation.
5. Run focused UI, accessibility, state-restoration, and hybrid View/Compose tests after migration.

## High-Impact Build and Migration Checks

- Compose 1.12 Android builds require `compileSdk = 37` and Android Gradle Plugin 9. This does not force `targetSdk` 37.
- Animation, Foundation, Runtime, and UI moved their Android minimum from API 21 to API 23; artifacts built with Kotlin 2.0 require Kotlin Gradle Plugin 2.0.0 or newer.
- Compose lint requires AGP 8.8.2 or standalone Lint 8.8.2 or newer.
- Recompiled clickable/selectable APIs expect `LocalIndication` to provide an `IndicationNodeFactory`. The temporary compatibility flag was later removed.
- Material 3 no longer brings in `material-icons-core` transitively. Prefer Material Symbols Vector Drawable XML, or declare the old artifact explicitly while migrating.
- `TabRow` and `ScrollableTabRow` are deprecated in favor of primary or secondary variants.
- `TextAutoSize` replaces `AutoSize`; removed overloads require source migration.
- Replace `OverscrollConfiguration` and `LocalOverscrollConfiguration` with overscroll factories and `LocalOverscrollFactory`.
- Remove custom keys from `rememberSaveable`; positional scoping is now the supported model.
- Replace `currentCompositeKeyHash` with `currentCompositeKeyHashCode`.
- Remove assignments to deleted behavior flags instead of preserving old behavior through unavailable switches.

Read [Build, Runtime, and State](references/build-runtime-state.md) for exact toolchain, BOM, Runtime, and state implications. Read [Input, Focus, and Scrolling](references/input-focus-scrolling.md) before migrating indications or deleted interaction flags.

### Common symbol migrations

| Replace or remove | Use or verify |
| --- | --- |
| `FocusProperties.enter` / `exit` | receiver-based `onEnter` / `onExit` |
| `AutoSize` | `TextAutoSize` |
| `LocalOverscrollConfiguration` | `LocalOverscrollFactory` |
| `currentCompositeKeyHash` | `currentCompositeKeyHashCode` |
| `requestedFrameRate` | `preferredFrameRate` |
| `ScaleToBounds` | `scaleToBounds` |
| `UnplacedStateAwareModifierNode` | `UnplacedAwareModifierNode` |
| `invalidateLayoutForSubtree` | `invalidateMeasurementForSubtree` |
| `NativePaint` | `android.graphics.Paint` |
| `Paint.asFrameworkPaint()` | `Paint.nativePaint` |
| `UiModes` | `AndroidUiModes` |
| `getExitedValueOrDefault` | `consumeExitedValueOrDefault` |

## Runtime and State

Choose state lifetime deliberately:

- `rememberSaveable` remains appropriate for values that can be saved; Android snapshot state lists and sets are parcelable.
- `rememberSerializable` is the `KSerializer`-based API; the `Saver`-based API remains `rememberSaveable`.
- `retain` keeps values across temporary removal without serialization, but has a shorter lifetime than saveable state. Avoid retaining keys or values that can leak resources, and mark unsuitable types with `@DoNotRetain`.
- A cancelled `PausableComposition` must be disposed and cannot be reused.
- Use `Snapshot.snapshotId`; convert widened IDs only when arithmetic is unavoidable.
- Treat values annotated `@FrequentlyChangingValue` as unsuitable for direct composition reads when a derived or draw/layout-phase read is possible.

For custom retained stores, lifecycle hooks, composition completion, host-default locals, stack traces, and multiplatform Runtime artifacts, read [Build, Runtime, and State](references/build-runtime-state.md).

## Input, Focus, and Scrolling

- Focus entry and exit callbacks are receiver-based `onEnter` and `onExit`; `focusRestorer` takes a non-null `fallback` requester.
- Exclude forbidden values from `AnchoredDraggableState` anchors rather than using deprecated `confirmValueChange`.
- Two-dimensional scrolling uses an `Offset`-based `canScroll` contract.
- Use one overscroll effect drawing path. `withoutVisualEffect` and `withoutEventHandling` split responsibilities but do not make duplicate drawing safe.
- Parent drag/scroll containers can take over abandoned child gestures, and remaining fling velocity can continue through nested scroll chains.
- Indirect pointer APIs replace indirect-touch names; pointer presses outside focus clear focus by default unless the hosting view opts out.
- Scroll indicator APIs now cover standard scroll, lazy, grid, staggered-grid, and pager state.

Read [Input, Focus, and Scrolling](references/input-focus-scrolling.md) for gesture dispatch, trackpad tests, delayed presses, visibility callbacks, interaction sounds, and removed flags.

## Layout, Animation, and Graphics

- `Modifier.animateBounds` animates lookahead size and position changes; lazy grids and pagers participate in distinct lookahead and approach passes.
- Shared-transition APIs are stable, but several interim names and factories were removed. Verify `scaleToBounds`, `BoundsTransform`, and skip-to-lookahead usage.
- `FlexBox` supports grow, shrink, wrapping, direction, and alignment. Its DSL uses calls such as `grow(1f)`.
- Experimental `Grid` provides explicit two-dimensional tracks and placement; use `MinMax(0.dp, 1.fr)` to avoid intrinsic queries around subcomposition when appropriate.
- `BasicText` no longer creates an implicit graphics layer.
- Packed Compose colors require conversion before comparison with Android `ColorLong` values.
- `MeshGradientPainter` replaces the mesh-gradient modifier and is installed with `Modifier.paint`.

Read [Layout, Animation, and Graphics](references/layout-animation-graphics.md) for flow-layout deprecations, custom nodes, lazy prefetch, shadows, shaders, wide gamut, frame-rate requests, and visual debugging.

## Text and Editing

- Keep `maxLines = 1` with start or middle ellipsis.
- State-backed text-field edits create undo entries; explicitly clear history when a programmatic replacement should reset undo.
- Style transformed output with `OutputTransformation` and `TextFieldBuffer.addStyle`; the interim annotated transformation API is gone.
- Secure text fields follow the Android show-password setting for last-character reveal.
- Use `LocalResources.current` for configuration-sensitive Android resource lookup.
- Resource-font load failures fall back to the default font instead of throwing during measurement.

Read [Text and Editing](references/text-editing.md) for annotated paragraphs, custom menus, smart selection, transliteration state, downloadable variable fonts, clipboard, and secure Material fields.

## Semantics, Accessibility, and Tests

- Prefer typed autofill through `fillableData` and `onFillData`; legacy text-only semantics are deprecated.
- Replace `invisibleToUser()` with `hideFromAccessibility()` and obtain semantics IDs from fetched nodes.
- Background, border, and graphics-layer nodes can alter semantics-tree shape. Tag the intended node or use resilient ancestor matchers.
- Accessibility checks live in dedicated accessibility test artifacts.
- Standard-dispatcher test APIs queue work until the scheduler advances; call the exposed scheduler or `MainTestClock.runCurrent()` as appropriate.
- Hybrid UI tests can scope Compose lookup to a selected Espresso `ViewInteraction`.

Read [Semantics, Accessibility, and Testing](references/semantics-accessibility-testing.md) for shapes, bounds, Android extras, visibility observation, host themes, restoration, and testing v2.

## Material 3

- Verify navigation selected-label colors after upgrading; defaults now use the secondary color.
- Drive state-backed text fields, search bars, carousels, and sliders from their dedicated state objects.
- Search collapsed and expanded surfaces are separate composables, with expanded variants hosted in a new window.
- Migrate pull-to-refresh default names and implement `isAnimating` in custom state.
- Use `rememberTooltipPositionProvider`; dismissal, focusability, action semantics, caret access, and width defaults changed.
- Wide navigation rails require explicit expansion state and use standard vertical arrangement.
- Custom `ColorScheme` instances should provide fixed roles and surface-container roles.

Read [Material 3 Components](references/material3-components.md) before changing Material components or preserving older visuals.

## Verification

After applying guidance:

- Confirm every changed symbol is imported from the intended artifact and source set.
- Re-resolve dependencies and inspect the actual BOM constraints rather than assuming uniform versions.
- Compile Android targets against the required SDK and plugin levels.
- Exercise focus restoration, nested scrolling, pointer hand-off, text undo, state restoration, and accessibility behavior where affected.
- Advance queued coroutine work explicitly in tests using standard dispatchers.
- Check semantics selectors for structural assumptions and hybrid tests for the intended host View.
- Inspect graphics and window-inset behavior on the Android API levels relevant to the change.
