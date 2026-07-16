# Accessibility, input, and testing

## Contents

- [Semantics construction](#semantics-construction)
- [Announcements, progress, and user preferences](#announcements-progress-and-user-preferences)
- [Selection](#selection)
- [Text fields and editing](#text-fields-and-editing)
- [Pointer, keyboard, focus, and stylus input](#pointer-keyboard-focus-and-stylus-input)
- [Sensitive content](#sensitive-content)
- [Tests and diagnostics](#tests-and-diagnostics)

## Semantics construction

- Assign a fine-grained `SemanticsRole` to a `Semantics` subtree when the role is
  meaningful. Role support was web-only when introduced (`3.32-guide`), so verify
  behavior on every target rather than assuming identical platform exposure.
- Use `semanticsIdentifier` on text widgets to give accessibility and automation
  clients a stable identity without changing the spoken label (`3.32.0`).
- Use `SemanticsLabelBuilder` to combine several values into one announcement.
  Wrap a sliver in `SliverEnsureSemantics` when it must stay in the semantics tree
  while offscreen (`3.35-guide`).
- Continue accessibility indexes across independently built slivers with
  `semanticIndexOffset` on `SliverList.builder`, `SliverGrid.builder`, and
  `SliverFixedExtentList.builder` (`3.38.0`).
- Select how a semantic node participates in pointer hit testing with
  `Semantics.hitTestBehavior` (`3.41.0`):

```dart
Semantics(
  hitTestBehavior: HitTestBehavior.opaque,
  child: child,
)
```

Do not read or assign the removed `SemanticsConfiguration.elevation`,
`SemanticsConfiguration.thickness`, or corresponding `SemanticsNode` properties.

## Announcements, progress, and user preferences

On Android API 36, semantic announcement events are deprecated. Prefer a polite,
implicit announcement through a live region; text which must remain non-focusable
still has a platform limitation.

```dart
Semantics(liveRegion: true, child: Text(status))
```

Progress indicators expose native accessibility progress updates. Supply percentage
text such as `50%` through `semanticsValue` when that produces a more natural
screen-reader announcement (`3.44-guide`).

```dart
CircularProgressIndicator(value: 0.5, semanticsValue: '50%')
```

Honor these platform preferences:

- Flutter web respects user text-spacing overrides and automatically disables
  animations for `prefers-reduced-motion`. Web form-validation failures receive
  immediate screen-reader feedback through `aria-description`.
- On Windows web sessions, `ThemeData(useSystemColors: true)` can honor forced-color
  themes.
- On iOS, `AccessibilityFeatures` reports preferences for auto-playing animated
  images, auto-playing video previews, and blinking cursors.
- `WidgetsFlutterBinding.instance.ensureSemantics` can force semantics on by default
  on iOS (`3.38-guide`).

Flutter web semantics support locales. At the engine layer, `dart:ui` can set the
application-level locale, and the Android and iOS bridges carry section locales for
accessibility integrations. Keep these locale signals aligned with the localized
labels in the widget tree.

## Selection

Wrap a `SelectionArea` or `SelectableRegion` subtree in `SelectionListener`, then
observe its `SelectionListenerNotifier`. `SelectionDetails` reports subtree-relative
start and end offsets and whether the selection exists or is collapsed (`3.29.0`).
Use `SelectableRegionSelectionStatusScope.maybeOf(context)` to distinguish a changing
selection from a finalized one.

On the web, `SelectableRegion` now forwards incoming layout constraints unchanged;
it no longer unexpectedly shrinks its child. Copying multiline selections preserves
line breaks on native and web targets.

## Text fields and editing

### Shared controls

- Handle taps released outside a text field with `onTapUpOutside`.
- Set `selectAllOnFocus` on `TextField`, `TextFormField`, or `EditableText` when focus
  must not automatically select all text (`3.35.0`).
- `InputDecoration.hint` accepts a widget when `hintText` is too limited:

```dart
const InputDecoration(
  hint: Row(children: [Icon(Icons.search), Text('Search')]),
)
```

- Replace `InputDecoration.maintainHintHeight` with `maintainHintSize`.
- A `FormField` can render an arbitrary error widget. Forms also support
  `AutovalidateMode.onUserInteractionIfError`; later form-state APIs expose registered
  `fields` and let `clearError()` clear form-level or individual field errors without
  resetting values (`3.44.0`).

```dart
for (final field in formKey.currentState!.fields) {
  field.clearError();
}
```

### Platform behavior

- iOS basic text fields use `SystemContextMenu` by default. Pasting no longer shows a
  cross-application confirmation by default, although custom context-menu actions were
  initially outside that behavior. Custom iOS edit-menu actions now participate in
  secure-paste handling.
- iOS single-line fields are not user-scrollable. Native inline predictive text is an
  opt-in experiment through `TextField.enableInlinePrediction`; it is off by default
  and its visuals remain experimental.
- Android text editing recognizes Home and End. Android-only `hintLocales` supplies
  language hints to the input method.
- Desktop editing recognizes Shift-Delete, Ctrl-Insert, and Shift-Insert.

## Pointer, keyboard, focus, and stylus input

- `ScaleStartDetails` exposes its originating `PointerDeviceKind`, allowing scale
  gestures to distinguish touch, trackpad, mouse, and other sources.
- Pointer-based gesture details implement `PositionedGestureDetails`, which provides
  common position information to generic handlers.
- Material `Autocomplete` supports keyboard option traversal. `RawAutocomplete` can
  choose `OptionsViewOpenDirection.mostSpace`; see the widget reference for its
  external editing state.
- `Visibility.maintainFocusability` decides whether a maintained but hidden subtree
  remains focusable. Hidden `IndexedStack` children are excluded from focusability.
- `CupertinoActionSheetAction` can receive keyboard focus. Material buttons use the
  basic arrow cursor rather than the click cursor by default on non-web platforms.

Android 14 and newer can handwrite directly into Material and Cupertino text fields.
Disable it per field with `stylusHandwritingEnabled: false`, and replace
`SelectionChangedCause.scribble` with `SelectionChangedCause.stylusHandwriting`.

```dart
TextField(stylusHandwritingEnabled: false)
```

The Windows embedder reports stylus pressure and rotation, so drawing and handwriting
do not require a custom native bridge.

## Sensitive content

On Android API 35 and newer, `SensitiveContent` obscures the entire application screen
during media projection. Use it for UI that must not appear in a screen share; it is
not merely a per-widget blur.

## Tests and diagnostics

- Use the `isSemantics` and `accessibilityAnnouncement` matchers from `flutter_test`
  to validate semantics trees and announcements (`3.41-guide`).
- Use `flutter test --ignore-timeouts` only when an external harness or interactive
  debugger owns the run timeout.
- Use `flutter test --no-uninstall integration_test` to preserve the installed
  integration-test application on its target.
- Set `debugPaintTextLayoutBoxes = true` in a debug build to paint line and glyph
  layout boxes when diagnosing text geometry.
