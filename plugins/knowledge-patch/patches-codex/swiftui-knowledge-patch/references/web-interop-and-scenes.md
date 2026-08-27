# Web, Interoperability, and Scenes

## Native WebKit views and model

`WebView(url:)` displays a URL directly and reloads when that input changes
(swiftui-2025). For control and observation, own the observable `WebPage` and
pass it to `WebView`. Its loading APIs accept a `URLRequest`, an HTML string
with a base URL, or data.

```swift
@State private var page = WebPage()

WebView(page)
    .onAppear {
        page.load(URLRequest(url: url))
    }
```

Configure `WebPage` with a `NavigationDecider` to inspect a
`NavigationAction`, modify `NavigationPreferences`, and allow or cancel the
navigation. A `URLSchemeHandler` can serve bundled HTML and CSS through a
custom scheme.

`WebView` participates in `scrollBounceBehavior` and `findNavigator`. It also
provides `webViewScrollPosition` and `webViewScrollInputBehavior`, including
input behavior such as visionOS look-to-scroll.

## AsyncImage requests and HTTP caching

On the 2027 releases, `AsyncImage` uses standard HTTP caching by default,
honors server cache headers, and no longer reloads merely because an image
reappears.

Applications built with Xcode 27 can supply a `URLRequest` and install a custom
`URLSession` and `URLCache` through `asyncImageURLSession(_:)`.

```swift
AsyncImage(
    request: URLRequest(
        url: imageURL,
        cachePolicy: .returnCacheDataElseLoad
    )
)
.asyncImageURLSession(imageSession)
```

## Scene bridging and specialized contexts

Scene bridging allows UIKit- and AppKit-lifecycle applications to request
SwiftUI-only scenes such as `MenuBarExtra` and `ImmersiveSpace`, then apply
SwiftUI scene modifiers.

Specialized contexts include:

- `AssistiveAccess { ... }` on iOS 26.
- macOS `RemoteImmersiveSpace` for rendering stereo content on Vision Pro.
- Widget `@Environment(\.levelOfDetail)`, with values including `.default` and
  `.simplified`.

The platform-specific entry points for hosting and presenting SwiftUI scenes
are `UIHostingSceneDelegate` in UIKit and `NSHostingSceneRepresentation` in
AppKit.

## RealityKit presentation and observation

A RealityKit entity can store a `PresentationComponent`. Its binding,
configuration, and SwiftUI content present a popover. Observable changes to an
entity can also drive SwiftUI views.

## AppKit integration

AppKit interoperability includes SwiftUI-backed sheets and
`NSGestureRecognizerRepresentable`.
