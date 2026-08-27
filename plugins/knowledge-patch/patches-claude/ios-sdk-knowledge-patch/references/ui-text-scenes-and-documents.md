# UI, Text, Scenes, and Documents

## SwiftUI compatibility corrections

### Tint, environment invalidation, and preference closures (18.4)

A view's `tint(_:)` overrides button tint inside its alerts and confirmation
dialogs. Content updates in `NavigationStack` and `NavigationSplitView`
invalidate the environment even when no environment property changed.

The `onPreferenceChange` closure no longer needs to be `@Sendable`, preventing
unnecessary diagnostics when it reaches main-actor-isolated state.

### Control-size ranges (26.0)

`ControlSize` conforms to `Comparable`. `View.controlSize(_:)` can clamp the
environment's control size to a range rather than forcing only one value.

### Section actions (26.0)

Use `sectionActions(content:)` to add actions to a `Section`. The actions remain
trailing on macOS, but appear as individual form rows on iOS and iPadOS. Account
for this platform-specific placement when designing the section.

## Localization and writing direction

### Localized interpolation and `Text` composition (26.0)

Interpolating a nonlocalized type into `LocalizedStringResource`,
`String(localized:)`, or `AttributedString(localized:)` produces a deprecation
warning. Pass a localized value, or explicitly wrap an intentionally descriptive
value with `String(describing:)`.

SwiftUI also deprecates concatenating `Text` values with `+`. Use `Text`
interpolation so localization can reorder content.

### Content-based paragraph direction (26.0)

`Text`, `TextEditor`, and `TextField` infer each paragraph's base writing
direction from its content in apps built with the newer SDK. Use
`AttributedString.writingDirection` for per-paragraph control, or
`.writingDirection(strategy: .layoutBased)` when the layout direction should be
used.

TextKit 2 indentation in OS 26-linked apps also follows the resolved paragraph
direction. Older-SDK binaries retain UI-language-based direction in several
interfaces, so compare link SDKs when behavior differs on the same OS.

## Writing Tools and TextKit

### Multiple containers and asynchronous range requests (18.4)

The optional `UIWritingToolsCoordinatorDelegate` methods for multiple-container
support are available in iOS 18.4.
`writingToolsCoordinator:requestsRangeInContextWithIdentifierForPoint:completion:`
supports asynchronous use of its completion block.

### Plain-text replacement attributes (18.5)

When a writing-tools coordinator sets `resultOptions = [.plainText]`, proposed
replacement text retains the `NSAttributedString` attributes supplied by the
delegate through `writingToolsCoordinator(_:requestsContextsFor:completion:)`.
This also applies to the async forms.

### List marker inclusion (26.0)

`NSTextList`, `NSTextContentStorage`, and `NSWritingToolsCoordinator` expose
`includesTextListMarkers` to control whether attributed-string paragraphs
contain list-marker text. TextKit 2 omits markers. UIKit has used that behavior
since iOS 18, and AppKit adopts it with macOS 26.

## Controls, navigation, and gestures

### Button-style picker sizing (26.0)

In apps built with the iOS 26 or macOS 26 SDK, button-like `Picker` styles use
fitted sizing by default. Apply `buttonSizing(_:)` when the picker should flex to
fill its container.

### NavigationLink container values (26.0)

With the newer SDKs, `NavigationLink` produces one view rather than a view list
inside list contexts. If code relies on `ContainerValues` escaping the link
label or its `ButtonStyle`, move `containerValue(_:_:)` outside the link.

### Priority relative to native recognizers (26.0)

For OS 26 SDK builds, use `highPriorityGesture(_:isEnabled:)` when a SwiftUI
gesture must precede an existing UIKit or AppKit recognizer. Use
`simultaneousGesture(_:isEnabled:)` when it should have equal priority.

## Screens and scenes

### `UIScreen.mainScreen` deprecation (26.0)

`UIScreen.mainScreen` is formally deprecated in iOS 26, tvOS 26, and visionOS
26. Obtain the screen from the relevant window or scene context instead of
assuming one process-wide main display.
