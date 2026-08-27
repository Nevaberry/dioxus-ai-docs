# Accessibility, input, and testing

## Semantics structure and announcements

- Wrap `SelectionArea` or `SelectableRegion` with `SelectionListener`; its
  `SelectionListenerNotifier` reports `SelectionDetails`, including subtree-relative
  endpoints and whether a selection exists or is collapsed.
  `SelectableRegionSelectionStatusScope.maybeOf(context)` reports changing versus
  finalized state (3.29.0).
- Assign a fine-grained `SemanticsRole` to a subtree. Role support was web-only in
  `3.32-guide`. Use `ThemeData(useSystemColors: true)` for Windows forced colors.
- Prefer polite implicit announcements from `Semantics(liveRegion: true)` on
  Android API 36; explicit announcement events are deprecated there, and keeping
  announced text non-focusable had a known limitation (`3.32-guide`).
- `Text.semanticsIdentifier` gives accessibility and automation clients a stable
  identity without changing the spoken label (3.32.0).
- `SemanticsLabelBuilder` combines values into one announcement,
  `SliverEnsureSemantics` retains offscreen sliver semantics, and web semantics
  carry locales (`3.35-guide`).
- Remove reads and writes of `SemanticsConfiguration.elevation`,
  `SemanticsConfiguration.thickness`, and the matching `SemanticsNode` members;
  they are gone (`3.35-guide`).
- `WidgetsFlutterBinding.instance.ensureSemantics` can force iOS semantics on
  (`3.38-guide`). `semanticIndexOffset` on builder slivers keeps one continuous
  accessibility index across multiple slivers (3.38.0).
- Application-level locale propagation in `dart:ui` and section locales in the
  Android/iOS bridges support accessibility integrations (3.38.0).
- Progress indicators expose native progress updates, web respects user text
  spacing overrides, and `flutter_test` provides `isSemantics` and
  `accessibilityAnnouncement` matchers (`3.41-guide`).
- `Semantics.hitTestBehavior` explicitly selects pointer hit-testing behavior for
  the semantics subtree (3.41.0).

## Accessibility preferences

- Flutter web honors `prefers-reduced-motion` by disabling animations and exposes
  validation errors immediately through `aria-description` (`3.44-guide`).
- On iOS, `AccessibilityFeatures` exposes preferences for autoplaying animated
  images, autoplaying video previews, and blinking cursors. Use percentage strings
  such as `50%` for natural progress-indicator announcements (`3.44-guide`).

## Text input, selection, and focus

- `onTapUpOutside` permits custom outside-tap handling. `FormField` errors may be
  widgets. Basic iOS fields no longer show cross-app paste confirmation by default,
  although custom context-menu actions were not covered initially (`3.32-guide`).
- Android 14 handwriting works in Material and Cupertino text fields. Disable it
  with `stylusHandwritingEnabled: false`; rename
  `SelectionChangedCause.scribble` to
  `SelectionChangedCause.stylusHandwriting` (`3.32-guide`).
- iOS editable text uses `SystemContextMenu` by default (3.32.0). Custom iOS edit
  menu actions participate in secure-paste handling (3.38.0).
- `Visibility.maintainFocusability` controls focus in maintained hidden subtrees;
  hidden `IndexedStack` children are excluded from focus. Android-only
  `hintLocales` informs input methods, while `selectAllOnFocus` controls automatic
  selection in `TextField`, `TextFormField`, and `EditableText` (3.35.0).
- Single-line iOS fields are not user-scrollable; Android recognizes Home and End
  (`3.35-guide`). Desktop editing recognizes Shift-Delete, Ctrl-Insert, and
  Shift-Insert, and `CupertinoActionSheetAction` can take keyboard focus (3.41.0).
- `TextField.enableInlinePrediction` opts into experimental native iOS inline
  prediction and is off by default (`3.44-guide`).
- Web `SelectableRegion` preserves incoming layout constraints, and copying a
  multiline selection preserves line breaks across web and native targets
  (`3.44-guide`).

## Pointer and gesture input

- `ScaleStartDetails` exposes `PointerDeviceKind`, allowing touch, trackpad, mouse,
  and other sources to be distinguished (3.32.0).
- Pointer gesture detail objects share `PositionedGestureDetails` for generic
  position-aware handling (`3.35-guide`).
- Windows embedder stylus events include pressure and rotation (`3.44-guide`).

## Testing and diagnostics

- `flutter test --ignore-timeouts` delegates time limits to an external harness or
  interactive debugging session (3.32.0).
- Use semantics matchers for roles, announcements, progress, indexes, and hit-test
  behavior, and test forced colors, reduced motion, text spacing, screen readers,
  keyboards, pointer kinds, stylus, focus, selection, and platform context menus.
- `flutter test --no-uninstall integration_test` retains an integration-test app on
  its target after the run (3.44.0).
