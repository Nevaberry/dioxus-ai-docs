---
name: jetpack-compose-knowledge-patch
description: Jetpack Compose
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Jetpack Compose

Use this skill when implementing, upgrading, reviewing, or testing AndroidX
Compose UI, Foundation, Runtime, Material 3, compiler-plugin, or BOM code.
Treat those artifacts as separately versioned products: inspect the module's
Gradle declarations, version catalog, and resolved dependency graph before
applying guidance.

## Working Method

1. Identify the affected surface: build setup, runtime/state, input and focus,
   layout/graphics, text, Material 3, Android hosting, or testing.
2. Check the resolved version of every relevant artifact. A BOM aligns the
   artifacts it manages but does not make every Compose-related product share
   one release number.
3. Search the topic reference below for renamed, removed, or behavior-changing
   APIs before editing call sites.
4. Prefer the replacement API over compatibility flags. Several migration
   flags existed briefly and were removed in later releases.
5. Compile the affected source set, run Compose lint, and exercise UI tests on
   the scheduler and host configuration used by the project.
6. For Android-only behavior, verify API-level guards, window ownership,
   insets, resources, and View/Compose interop rather than assuming common-code
   behavior applies unchanged.

## Topic Index

| Reference | Topics |
| --- | --- |
| [Setup, Runtime, and State](references/setup-runtime-state.md) | Toolchain floors, BOMs, compiler reports, pausable composition, retained and saveable state, diagnostics |
| [Input, Scrolling, and Focus](references/input-scroll-focus.md) | Focus, pointer and trackpad input, haptics, overscroll, scrolling, visibility callbacks, indicators |
| [Layout, Animation, and Graphics](references/layout-animation-graphics.md) | Lookahead, shared transitions, FlexBox/Grid, lazy infrastructure, modifier nodes, shadows, shaders, mesh gradients |
| [Text, Autofill, and Resources](references/text-autofill-resources.md) | Text fields, autosizing, annotations, autofill, selection, fonts, resources, clipboard |
| [Material 3 Components](references/material3-components.md) | Component migrations, state APIs, navigation, pickers, tooltips, sheets, sliders, color and inset changes |
| [Platform, Window, and Interop](references/platform-window-interop.md) | Insets, window geometry, ComposeView hosting, dialogs/popups, paint and color interop, frame rate |
| [Semantics, Accessibility, and Testing](references/semantics-accessibility-testing.md) | Semantics tree changes, accessibility, test artifacts, schedulers, hybrid UI scoping |

## Breaking Changes First

### Toolchain and platform floors

- Compose Animation, Foundation, Runtime, and UI require Android API 23 or
  newer from 1.10.0.
- Artifacts built with Kotlin 2.0 require Kotlin Gradle Plugin 2.0.0 or newer.
- Compose 1.12 Android builds require `compileSdk = 37` and Android Gradle
  Plugin 9; `targetSdk` remains an independent choice.
- Compose lint from 1.9.0 requires AGP 8.8.2 or standalone Lint 8.8.2 and an
  Android Studio Ladybug-era toolchain or newer.

See [Setup, Runtime, and State](references/setup-runtime-state.md) before an
upgrade changes the build.

### Indication migration

After recompiling against 1.9.0, interaction modifiers whose overload omits an
explicit `Indication` require `LocalIndication` to provide an
`IndicationNodeFactory`. A legacy `Indication` can fail at runtime. Migrate the
implementation or use an explicit-indication overload while bridging. The
temporary `isNonComposedClickableEnabled` escape hatch is absent from 1.10.0.

### State and lifecycle changes

- Remove custom keys from `rememberSaveable`; positional scoping is now the
  supported behavior.
- A cancelled `PausableComposition` must be disposed and cannot be reused.
- Install custom retained-value stores with
  `LocalRetainedValuesStoreProvider`; do not provide the local directly.
- `retain` keeps values across temporary hierarchy removal without
  serialization. Do not retain keys or values that can leak resources; mark
  unsuitable types with `@DoNotRetain`.

### Semantics and test structure

`background`, `border`, and `graphicsLayer` can add semantics nodes. Tests that
assert exact parent/child/sibling structure are brittle; tag the intended node
or use an ancestor matcher. Replace `invisibleToUser()` with
`hideFromAccessibility()`, and retrieve a semantics ID through
`fetchSemanticsNode().id`.

### Text and autofill migrations

- Replace `AutoSize` with `TextAutoSize`.
- Replace deprecated autofill APIs with semantic `fillableData` and
  `onFillData`; text autofill needs matching UI and Foundation support.
- `TextFieldState.edit {}` creates an undo entry. Explicitly call
  `undoState.clearHistory()` when programmatic edits should reset history.
- Use `OutputTransformation` plus `TextFieldBuffer.addStyle`; the interim
  `AnnotatedOutputTransformation` API is gone.

### Layout and animation removals

- Replace deprecated contextual flow layouts and overflow overloads with
  ordinary `FlowRow`/`FlowColumn` or a custom layout.
- Replace `ScaleToBounds` with `scaleToBounds`; removed shared-transition
  factories and parameters have no direct compatibility flag.
- Replace `Modifier.meshGradient` with a `MeshGradientPainter` installed via
  `Modifier.paint`.

### Material 3 dependency and component changes

- Material 3 no longer brings in `material-icons-core`. Declare it explicitly
  only when maintaining existing icons; prefer Material Symbols vector XML.
- Stable Material 3 excludes expressive and component-override APIs that still
  carried their experimental annotations. Use a compatible artifact line when
  those APIs are required.
- `TabRow` and `ScrollableTabRow` are deprecated; select the appropriate
  primary or secondary variant.
- Custom `ColorScheme` construction must supply fixed roles and surface
  container roles.

## High-Value APIs

### Observe placement and visibility precisely

Use `Modifier.onLayoutRectChanged` for debounced or throttled root-, window-,
or screen-relative bounds. Use `onVisibilityChanged` for visibility state;
`onFirstVisible` was deprecated because it could fire after every re-entry.
Custom nodes can use `onVisibilityChangedNode()`.

### Build advanced layouts

`Modifier.animateBounds` animates lookahead size and position. `FlexBox`
provides grow, shrink, wrapping, direction, and alignment. Experimental `Grid`
provides explicit two-dimensional tracks and placement. Stable lazy-layout
primitives support custom measure policies and internally scheduled prefetch.

### Handle modern scrolling

Use `scrollable2D` for two-axis motion, `scrollableArea()` for scrolling plus
bounds clipping, and `ScrollIndicatorState` or `Modifier.scrollIndicator` for
indicator integrations. An `OverscrollEffect` can separate event handling from
drawing, but the same effect must never be drawn twice.

### Choose the right persistence lifetime

- `remember`: composition lifetime.
- `retain`: survives temporary hierarchy removal without serialization.
- `rememberSaveable` or `rememberSerializable`: state restoration with
  supported saved-state encoding.

Check key lifetime, registry ownership, Android parcelability, and disposal
requirements in [Setup, Runtime, and State](references/setup-runtime-state.md).

### Host Compose beyond a standard activity

`ComposeViewContext` can compose an unattached `ComposeView`. Dialogs and
popups can receive custom window tokens, and window types enable service-owned
overlay hosts. Treat these as Android platform integration and verify token,
lifecycle, and permission ownership.

### Test deterministically

The v2 Compose UI test APIs use `StandardTestDispatcher` by default. Advance
their shared scheduler explicitly, such as with `runCurrent()`. Older test APIs
retain unconfined behavior unless an `effectContext` variant is configured.
Use `onRootWithViewInteraction` to scope node lookup inside one View hierarchy
in hybrid interfaces.

## Upgrade Checklist

- Resolve actual artifact versions and BOM constraints.
- Verify `minSdk`, `compileSdk`, AGP, Kotlin, and lint compatibility.
- Search for removed behavior-flag assignments and deprecated overloads.
- Check `LocalIndication`, saveable-state keys, retained-store installation,
  and pausable-composition disposal.
- Review focus clearing, insets consumption, window rulers, and host tokens.
- Re-run semantics tests without relying on an exact incidental tree shape.
- Advance queued test coroutines when using standard-dispatcher test APIs.
- Test API-level fallbacks for fonts, wide-gamut graphics, credential requests,
  date types, and Android-only properties.
- Confirm overscroll and modifier-node drawing occurs exactly once.
- Prefer direct node tags, state-backed text/component APIs, and explicit
  lifecycle ownership in new code.
