# Accessibility, input, and testing

## Semantics and accessibility

### Roles, live regions, and forced colors (3.32-guide)

`SemanticsRole` assigns a fine-grained role to a `Semantics` subtree. Role support
was web-only when introduced. Flutter web can honor Windows forced-color themes
with `ThemeData(useSystemColors: true)`.

Android API 36 deprecates semantic announcement events. Prefer polite implicit
announcements through a live region, while accounting for the known limitation
around text that must remain non-focusable.

```dart
Semantics(liveRegion: true, child: Text(status))
```

### Stable identifiers and sliver semantics (3.32.0, 3.35-guide, 3.38.0)

Text widgets accept `semanticsIdentifier` so accessibility and automation clients
can distinguish similar nodes without changing their spoken labels.

Web semantics supports locales. `SemanticsLabelBuilder` joins values into one
announcement, and `SliverEnsureSemantics` keeps an offscreen sliver in the
semantics tree.

For a logical accessibility sequence spanning separately built slivers, set
`semanticIndexOffset` on `SliverList.builder`, `SliverGrid.builder`, and
`SliverFixedExtentList.builder`.

The obsolete `SemanticsConfiguration.elevation` and
`SemanticsConfiguration.thickness` members and their `SemanticsNode` counterparts
are removed; custom semantics code must stop accessing them (3.35-guide).

### Hit testing and platform enablement (3.38-guide, 3.41.0)

On iOS, `WidgetsFlutterBinding.instance.ensureSemantics` can keep semantics enabled
by default. `Semantics.hitTestBehavior` explicitly selects how a semantics node
participates in pointer hit testing.

```dart
Semantics(
  hitTestBehavior: HitTestBehavior.opaque,
  child: child,
)
```

### User preferences and feedback (3.41-guide, 3.44-guide)

Progress indicators expose native accessibility progress updates. Use natural
percentage text such as `50%` as `semanticsValue` when appropriate. Flutter web
honors user text-spacing overrides and `prefers-reduced-motion`; form validation
errors receive immediate screen-reader feedback through `aria-description`.

On iOS, `AccessibilityFeatures` exposes preferences for auto-playing animated
images, auto-playing video previews, and blinking cursors. Respect these preferences
when scheduling media or cursor effects.

```dart
CircularProgressIndicator(value: 0.5, semanticsValue: '50%')
```

## Selection and text input

### Observing selection (3.29.0)

Wrap a `SelectionArea` or `SelectableRegion` subtree in `SelectionListener` and use
its `SelectionListenerNotifier` to receive `SelectionDetails`: subtree-relative
start and end offsets plus absent/collapsed selection state.
`SelectableRegionSelectionStatusScope.maybeOf(context)` reports whether the
enclosing region is still changing or has finalized.

### Selectable-region layout and copy behavior (3.44-guide)

On web, `SelectableRegion` forwards constraints unchanged instead of shrinking its
child. Multiline copy preserves line breaks across native and web targets.

`ExtendSelectionByPageIntent` is removed (3.44.0); eliminate callers rather than
trying to retain page-extension behavior through that intent.

### Text-field hooks and context menus (3.32-guide, 3.32.0)

Text fields accept `onTapUpOutside`. A `FormField` can render an arbitrary error
widget rather than text only. On iOS, ordinary paste no longer prompts for cross-app
permission by default, but fields with custom context menus were not covered by
that change.

Editable text uses `SystemContextMenu` by default on iOS. Supply custom context-menu
behavior only when the application intentionally replaces the native baseline.
Custom iOS edit-menu actions later gained secure-paste participation (3.38.0).

### Platform keyboard and focus behavior

- Android 14 and newer supports stylus handwriting in Material and Cupertino text
  fields. Disable it with `stylusHandwritingEnabled: false` and rename
  `SelectionChangedCause.scribble` to `.stylusHandwriting` (3.32-guide).
- Single-line fields are no longer user-scrollable on iOS; Android text editing
  recognizes Home and End (3.35-guide).
- `hintLocales` supplies Android input-method language hints. `selectAllOnFocus` on
  `TextField`, `TextFormField`, and `EditableText` controls automatic full
  selection (3.35.0).
- Desktop text editing recognizes Shift-Delete, Ctrl-Insert, and Shift-Insert.
  Material buttons use the basic arrow cursor by default off web, and
  `CupertinoActionSheetAction` can receive keyboard focus (3.41.0).
- `TextField.enableInlinePrediction` opts into experimental native iOS inline
  prediction; it is off by default and its styling is experimental (3.44-guide).

## Focus, pointers, and gestures

`ScaleStartDetails` exposes the originating `PointerDeviceKind`, allowing touch,
trackpad, mouse, and other input to diverge when necessary (3.32.0).

Pointer-based detail objects share `PositionedGestureDetails`, enabling generic
handlers to consume common position information (3.35-guide).

`Visibility.maintainFocusability` decides whether a maintained but hidden subtree
can remain focusable. Hidden `IndexedStack` children are excluded from focusability
by default (3.35.0).

`Autocomplete` supports keyboard option traversal and can accept an external
`focusNode` and `textEditingController`. `RawAutocomplete` can open toward
`OptionsViewOpenDirection.mostSpace` when available space should drive placement
(3.32.0, 3.35.0, 3.41-guide).

On Windows, the embedder reports stylus pressure and rotation for native drawing and
handwriting input (3.44-guide). Test pointer-kind and stylus-specific code on real
target hardware.

`dart:ui` can set the application-level locale, and Android and iOS bridges carry
section locales for accessibility integrations (3.38.0).

## Diagnostics and test controls

### Semantics matchers (3.41-guide)

`flutter_test` provides `isSemantics` and `accessibilityAnnouncement` matchers.
Use them for semantics-tree and announcement behavior, not only visual widget
goldens.

### Timeouts and installed applications

`flutter test --ignore-timeouts` disables framework test timeouts when an external
harness or interactive debugger owns the limit (3.32.0).

For integration tests, `flutter test --no-uninstall integration_test` preserves the
installed app after the run for inspection or follow-up testing (3.44.0).

### Text, microtask, and runtime diagnostics

Set `debugPaintTextLayoutBoxes = true` in debug builds to render line and glyph
layout boxes (3.38.0). Use `flutter run --profile-microtasks` to profile excessive
or long `dart:async` microtask queues (3.35.0), and
`flutter run --profile-startup` for startup profiling (3.38.0).

The redesigned inspector stays in on-device selection mode until explicitly exited.
The Logging tool filters by severity and shows severity, category, zone, and isolate
metadata (3.29.0).

## Accessibility test matrix

- Screen readers: native progress updates, live regions, semantic identifiers,
  roles, continuous sliver indexes, and form errors.
- Preferences: reduced motion, forced colors, web text spacing, animated-image and
  video autoplay, and blinking cursors.
- Input: keyboard-only traversal, focus hiding, Android stylus, Windows stylus,
  pointer kinds, Home/End and desktop editing shortcuts.
- Selection: collapsed and changing selections, multiline copy, context menus, and
  secure paste.
- Layout: text boxes, offscreen sliver semantics, and web `SelectableRegion`
  constraints.
