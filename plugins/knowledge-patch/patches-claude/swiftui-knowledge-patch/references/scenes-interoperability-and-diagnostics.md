# Scenes, Interoperability, and Diagnostics

## Bridge SwiftUI scenes into UIKit and AppKit apps

Scene bridging lets apps with UIKit or AppKit lifecycles request SwiftUI-only
scenes, including `MenuBarExtra` and `ImmersiveSpace`, and apply SwiftUI scene
modifiers.

The platform-specific types for hosting and presenting these scenes are
`UIHostingSceneDelegate` for UIKit and `NSHostingSceneRepresentation` for
AppKit.

## Use specialized scene contexts

New scene contexts include:

- `AssistiveAccess { ... }` on iOS 26.
- macOS `RemoteImmersiveSpace`, which renders stereo content on Vision Pro.
- Widget `@Environment(\.levelOfDetail)`, with values including `.default` and
  `.simplified`.

## Integrate RealityKit and AppKit

A RealityKit entity can own a `PresentationComponent`. Its binding,
configuration, and SwiftUI content present a popover, and observable entity
changes can drive SwiftUI views.

AppKit integration supports SwiftUI-backed sheets and
`NSGestureRecognizerRepresentable`.

## Diagnose SwiftUI update performance

Instruments 26's SwiftUI template records traces only against a current OS. Its
timeline includes:

- Update Groups
- Long View Body Updates
- Long Representable Updates
- Other Long Updates

Orange and red events are progressively more likely to contribute to a hitch or
hang. Drill from an update into Time Profiler to inspect its CPU work.

Ordinary SwiftUI call stacks do not always reveal why work happened. Use the
Cause & Effect graph to follow gestures, state changes, creation edges, and
observation dependencies to the updates they trigger.
