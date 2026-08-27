---
name: swiftui-knowledge-patch
description: SwiftUI
version: "iOS 27 beta 4 / Xcode 27 beta 4"
license: MIT
metadata:
  author: Nevaberry
---


# SwiftUI Knowledge Patch

Use this skill when building or migrating SwiftUI interfaces whose behavior depends
on current framework APIs, platform presentation, state storage, concurrency,
documents, WebKit, rich text, spatial layout, or interaction.

## Reference index

| Reference | Topics |
| --- | --- |
| [visual-navigation-and-windows.md](references/visual-navigation-and-windows.md) | Liquid Glass, toolbars, search, tabs, windows, transitions, safe areas, controls, and color |
| [documents-web-and-text.md](references/documents-web-and-text.md) | Document creation and I/O, WebKit, image loading, attributed text, and find |
| [interaction-spatial-and-charts.md](references/interaction-spatial-and-charts.md) | Reordering, swipe actions, prompts, drag and drop, charts, and volumetric layout |
| [scenes-interoperability-and-diagnostics.md](references/scenes-interoperability-and-diagnostics.md) | Scene bridging, specialized contexts, RealityKit, AppKit, and Instruments |
| [state-concurrency-and-builders.md](references/state-concurrency-and-builders.md) | `@State`, `@Animatable`, actor isolation, sendability, and result builders |

## Breaking changes and migration traps

### Initialize macro-based State deliberately

`@State` is a macro in Xcode 27. Its inline reference-type value is lazy and is
created once for the lifetime of the view. If `init` supplies the state, omit the
inline default: an inline value wins and discards the initializer assignment.
Initialize ordinary stored properties before state because synthesized state
storage uses `self`.

```swift
struct PageView: View {
    let title: String
    @State private var page: Page

    init(title: String) {
        self.title = title
        self.page = Page(title: title)
    }

    var body: some View { Text(title) }
}
```

Do not combine another property wrapper with `@State`; both wrappers try to
synthesize the same underscore-prefixed storage. Private state also removes the
previously usable synthesized memberwise initializer, so declare the initializer.
The macro behavior back-deploys to iOS 17, macOS 14, and aligned releases.

### Account for ContentBuilder changes

Specialized SwiftUI result builders are unified under unconstrained
`@ContentBuilder`. Multi-expression blocks produce `TupleContent`, not
`TupleView`; prefer opaque `some View`. When back-deploying before the 2027
platform releases where `TupleContent` is unavailable, retain a `TupleView`
constraint and explicitly construct `TupleView((first, second))`.

The removed `View` constraint can make deprecated non-builder `background` and
`overlay` overloads ambiguous. Select the builder form with trailing-closure
syntax:

```swift
Rectangle()
    .overlay { Color.blue.opacity(0.3).blendMode(.overlay) }
```

Module-qualify newly ambiguous names such as `SwiftUI.Color.clear`. With MapKit
in scope, make an empty nested view builder explicit with `EmptyContent()` or
`EmptyView()`; otherwise it can resolve to `EmptyMapContent`.

### Design for resizable windows

Do not assume a fixed device canvas. iPad apps must tolerate fluid window
resizing, `UIRequiresFullscreen` is deprecated, and iPhone apps become resizable
on iOS 27. Use size classes rather than device idiom in mixed UIKit and SwiftUI
layouts. Xcode 27 Live Previews provide resize handles for testing.

### Respect SwiftUI concurrency boundaries

Conformance to `View` isolates the conforming type and its members to
`@MainActor`. Models created in the view declaration and tasks created from the
body inherit that isolation. Keep time-sensitive animation mutations in
synchronous SwiftUI action callbacks and use state to bridge to longer
asynchronous model work.

SwiftUI can call `Shape.path(in:)`, `Layout` requirements, `visualEffect`, and
the transform closure of `onGeometryChange` away from the main thread. Capture a
sendable value copy rather than reaching through main-actor-isolated `self`:

```swift
.visualEffect { [pulse] content, _ in
    content.blur(radius: pulse ? 2 : 0)
}
```

### Remove custom chrome that obscures system materials

Apps rebuilt with the current SDK automatically gain Liquid Glass for standard
bars, sheets, popovers, and controls on current platform releases. Custom
backgrounds can cover the material and scroll-edge effects, so remove them where
possible. Apply `glassEffect(_:in:)` sparingly to important custom controls and
test custom color and animation with reduced-transparency and reduced-motion
settings.

### Revisit AsyncImage caching assumptions

On the 2027 platform releases, `AsyncImage` uses standard HTTP caching and honors
server cache headers rather than reloading whenever an image reappears. Builds
with Xcode 27 can provide a `URLRequest` and install a custom `URLSession` and
`URLCache` through `asyncImageURLSession(_:)`.

```swift
AsyncImage(
    request: URLRequest(
        url: imageURL,
        cachePolicy: .returnCacheDataElseLoad
    )
)
.asyncImageURLSession(imageSession)
```

## High-value visual and navigation APIs

Separate toolbar glass groups with
`ToolbarSpacer(.fixed, placement: .primaryAction)`. Give a primary glass action
extra prominence with `.buttonStyle(.borderedProminent).tint(...)`.

As horizontal space contracts, use `visibilityPriority(_:)` for important
groups, `ToolbarOverflowMenu` for permanently secondary actions, and
`.topBarPinnedTrailing` for an action that must never overflow.

```swift
.toolbar {
    ToolbarItemGroup { EditButtons() }.visibilityPriority(.high)
    ToolbarOverflowMenu { SecondaryActions() }
    ToolbarItem(placement: .topBarPinnedTrailing) { ShareButton() }
}
.toolbarMinimizeBehavior(.onScrollDown, for: .navigationBar)
```

Use `Tab(role: .search)` for a dedicated search destination that separates from
other tabs and morphs into the search field when the `TabView` is searchable.
Use `Tab(role: .prominent)` for a distinguished bottom-trailing tab.

## High-value document APIs

Model distinct new-document paths with `DocumentCreationSource` and
`NewDocumentButton`; the selected source reaches the creation context supplied
by `DocumentGroup`.

The snapshot-based architecture separates the observable document model from
asynchronous I/O. A `WritableDocument` declares formats and creates snapshots;
a `DocumentWriter` receives the destination URL, current and previous snapshots,
a consuming Foundation `Subprogress`, and the selected content type. Use
`ReadableDocument` and `DocumentReader` for the read path. Place `DocumentGroup`
first in the app's scene list.

```swift
nonisolated func write(
    snapshot: sending PageSnapshot,
    to destination: URL,
    previous: sending PageSnapshot?,
    progress: consuming Subprogress
) async throws {
    // Write changed parts and report progress.
}
```

Use `FileWrapperDocumentReader` and `FileWrapperDocumentWriter` for the simpler
file-wrapper path. `URLDocumentConfiguration` supplies the URL, last modification
date, and coordinated access to additional files.

## High-value interaction APIs

Add `.reorderable()` to repeated content and `.reorderContainer(for:)` to its
list, grid, or custom parent. Apply the callback's `ReorderDifference` to the
model. This also enables reordering on watchOS.

Outside `List`, place `swipeActions` children in a scroll view carrying
`swipeActionsContainer()`. Bind `alert` or `confirmationDialog` with `item:` to
present for a non-`nil` item and pass that value into the action builder.

```swift
.confirmationDialog("Delete?", item: $stickerToDelete) { sticker in
    DeleteStickerButton(sticker)
}
```

## High-value web, text, spatial, and diagnostics APIs

Use `WebView(url:)` for direct URL display. Own an observable `WebPage` when the
app needs navigation control, observation, or explicit loading of requests,
HTML, or data. Configure a `NavigationDecider` or `URLSchemeHandler` when policy
or custom-scheme content is required.

`TextEditor` accepts `Binding<AttributedString>` and supplies built-in rich-text
controls. `AttributedTextSelection` represents its selection,
`AttributedTextFormattingDefinition` constrains allowed styling, and
`FindContext` creates a find navigator for compatible editors.

For volumetric interfaces, use `Alignment3D`, depth-aware stacks,
`spatialOverlay`, `SpatialContainer`, `aspectRatio3D`, and `rotation3DLayout`.
Use `.manipulable()` for direct model movement and read
`surfaceSnappingInfo` for surface attachment.

When diagnosing hitches, record with the SwiftUI Instruments template on a
current OS. Start with the long-update lanes, drill an update into Time Profiler
for CPU work, and use Cause & Effect to connect gestures, state changes,
creation edges, and observation dependencies.

Read the indexed reference for constraints and related APIs before implementing
an affected area.
