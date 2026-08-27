# SwiftUI, UIKit, and Text

## Localization and Text Direction

### Make Intentional Nonlocalized Interpolation Explicit

The iOS 26.0 SDK warns when a nonlocalized type is interpolated into
`LocalizedStringResource`, `String(localized:)`, or
`AttributedString(localized:)`. Supply a localized value, or wrap an intentional
description with `String(describing:)`.

SwiftUI also deprecates joining `Text` values with `+`. Use `Text` interpolation
so localization can reorder the content.

### Account for Content-Based Paragraph Direction

In applications built with the iOS 26 SDK, `Text`, `TextEditor`, and `TextField`
infer each paragraph's base writing direction from its content. Set
`AttributedString.writingDirection` per paragraph, or apply
`.writingDirection(strategy: .layoutBased)` to retain layout-based behavior.

TextKit 2 indentation in OS 26-linked applications also follows the resolved
paragraph direction. Binaries built with older SDKs retain UI-language-based
direction in several interfaces.

### Control TextKit 2 List Markers

`NSTextList`, `NSTextContentStorage`, and `NSWritingToolsCoordinator` add
`includesTextListMarkers`, which controls whether attributed-string paragraphs
contain list-marker text. TextKit 2 omits markers; UIKit has behaved that way
since iOS 18, and AppKit adopts it with macOS 26.

## SwiftUI Layout and Navigation

### Clamp Control Size and Add Section Actions

In iOS 26.0, `ControlSize` conforms to `Comparable`, and
`View.controlSize(_:)` accepts a range to clamp the environment's control size.
Use `sectionActions(content:)` to add actions to a `Section`. The actions remain
trailing on macOS but appear as individual form rows on iOS and iPadOS.

### Set Button-Like Picker Sizing Explicitly

In applications built with the iOS 26 or macOS 26 SDK, button-like `Picker`
styles use fitted sizing by default. Apply `buttonSizing(_:)` when the picker
must flex to fill its container.

### Move Escaping Container Values Outside `NavigationLink`

With the iOS 26 SDK, `NavigationLink` produces one view rather than a view list
in list contexts. If code depends on `ContainerValues` escaping the link label
or its `ButtonStyle`, place `containerValue(_:_:)` outside the link.

### Select Gesture Priority Relative to Native Recognizers

For applications built with the iOS 26 SDK, use
`highPriorityGesture(_:isEnabled:)` when a SwiftUI gesture must precede an
existing UIKit or AppKit recognizer. Use
`simultaneousGesture(_:isEnabled:)` for equal priority.

## SwiftUI Behavior Corrections

### Recheck Tint, Environment Invalidation, and Preferences

On iOS 18.4:

- A view's `tint(_:)` overrides button tint inside alerts and confirmation
  dialogs.
- Content updates in `NavigationStack` or `NavigationSplitView` invalidate the
  environment even when no environment property changed.
- An `onPreferenceChange` closure no longer needs to be `@Sendable`, avoiding
  unnecessary diagnostics when it accesses main-actor-isolated state.

## Writing Tools

### Use Multiple-Container Delegation Asynchronously

The optional `UIWritingToolsCoordinatorDelegate` methods for multiple-container
support are available in iOS 18.4. The
`writingToolsCoordinator:requestsRangeInContextWithIdentifierForPoint:completion:`
method supports asynchronous invocation of its completion block.

### Preserve Delegate-Supplied Attributes for Plain Text

On iOS 18.5, a coordinator using `resultOptions = [.plainText]` receives
proposed replacement text with the `NSAttributedString` attributes supplied by
the delegate from
`writingToolsCoordinator(_:requestsContextsFor:completion:)`. The attributes
are retained for both completion-handler and async forms.

## UIKit Display APIs

### Remove Dependencies on `UIScreen.mainScreen`

`UIScreen.mainScreen` is formally deprecated in iOS 26, tvOS 26, and visionOS
26. Audit existing uses and avoid adding new dependencies on the deprecated API.
