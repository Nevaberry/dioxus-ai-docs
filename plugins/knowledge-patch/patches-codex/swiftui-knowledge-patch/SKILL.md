---
name: swiftui-knowledge-patch
description: SwiftUI
version: "iOS 27 beta 4 / Xcode 27 beta 4"
license: MIT
metadata:
  author: Nevaberry
---


# SwiftUI Knowledge Patch

Use this skill when implementing or reviewing SwiftUI code that depends on
recent framework behavior, source migrations, document APIs, WebKit
integration, rich-text editing, or spatial layout. Check the deployment target
and SDK before selecting an API, especially where behavior back-deploys or a
workaround depends on older targets.

## Reference index

| Reference | Topics |
| --- | --- |
| [interface-layout-and-navigation.md](references/interface-layout-and-navigation.md) | Liquid Glass, windows, toolbars, tabs, safe areas, controls, spatial layout |
| [state-concurrency-and-builders.md](references/state-concurrency-and-builders.md) | `@State`, `@Animatable`, actor isolation, sendable callbacks, `ContentBuilder`, compiler workarounds |
| [documents-interactions-and-text.md](references/documents-interactions-and-text.md) | Document I/O, creation and export, drag and drop, reordering, prompts, attributed text |
| [web-interop-and-scenes.md](references/web-interop-and-scenes.md) | WebKit, `AsyncImage`, RealityKit, AppKit/UIKit interoperability, scene bridging |
| [diagnostics-charts-and-color.md](references/diagnostics-charts-and-color.md) | SwiftUI Instruments, 3D charts, HDR color |

## Breaking changes and migration checks

### Make every app window resizable

Apps need to tolerate fluid resizing: iPadOS 26 deprecates
`UIRequiresFullscreen`, and iPhone apps become resizable on iOS 27. Use size
classes rather than device idiom for mixed UIKit and SwiftUI layout decisions.
Xcode 27 Live Previews provide resize handles for exercising these states.

On iPadOS 26, the existing scene command API supplies the new app menu bar:

```swift
.commands {
    TextEditingCommands()
}
```

For macOS content-driven window resizing,
`.windowResizeAnchor(.top)` selects the origin of the resize animation.

### Migrate macro-based State carefully

In Xcode 27, `@State` is a macro and an inline reference-type value is lazily
created once per view lifetime. This behavior back-deploys to iOS 17, macOS 14,
and aligned releases.

If `init` supplies a state value, omit its inline default; otherwise the
default wins and the initializer assignment is discarded. Initialize ordinary
stored properties before state because the synthesized state storage uses
`self`.

```swift
struct PageView: View {
    let title: String
    @State private var page: Page

    init(title: String) {
        self.title = title
        self.page = Page(title: title)
    }

    var body: some View {
        Text(title)
    }
}
```

Do not combine another property wrapper with `@State`; both wrappers synthesize
the same underscore-prefixed storage name. Private state also prevents the
formerly usable synthesized memberwise initializer, so declare the initializer
explicitly.

### Account for unified ContentBuilder

Specialized result builders are unified under unconstrained `@ContentBuilder`.
Multi-expression blocks now form `TupleContent`, not `TupleView`. Prefer opaque
`some View` results. When back-deploying before the 2027 releases, keep a
required `TupleView` constraint and construct `TupleView((first, second))`
explicitly if `TupleContent` is unavailable.

The removed `View` constraint can make deprecated non-builder `background` and
`overlay` overloads ambiguous. Select the builder overload with trailing
closure syntax:

```swift
Rectangle()
    .overlay {
        Color.blue.opacity(0.3).blendMode(.overlay)
    }
```

It can also expose colliding type or static-member names from imported modules.
Rename the local symbol or qualify the intended module, such as
`SwiftUI.Color.clear`.

With MapKit in scope, an empty nested builder can resolve to `EmptyMapContent`.
Write `EmptyContent()` or `EmptyView()` explicitly, including in an empty
conditional-compilation branch.

### Respect current concurrency boundaries

Conformance to `View` isolates the conforming type and its members to
`@MainActor`. A model created in a view declaration and a `Task` created from
the body inherit that isolation. Keep time-sensitive animation state changes in
synchronous SwiftUI action callbacks and bridge longer asynchronous work
through state.

SwiftUI may invoke `Shape.path(in:)`, `Layout` requirements, `visualEffect`,
and the transform closure of `onGeometryChange` away from the main thread.
Capture a sendable value copy instead of accessing main-actor view state
through `self`:

```swift
.visualEffect { [pulse] content, _ in
    content.blur(radius: pulse ? 2 : 0)
}
```

### Recheck AsyncImage loading assumptions

On the 2027 releases, `AsyncImage` uses ordinary HTTP caching by default and
honors server cache headers. Xcode 27 also adds request-based loading and
environment-level session control:

```swift
AsyncImage(
    request: URLRequest(
        url: imageURL,
        cachePolicy: .returnCacheDataElseLoad
    )
)
.asyncImageURLSession(imageSession)
```

## High-value interface APIs

### Adopt Liquid Glass with standard structure

Apps rebuilt with the current SDK automatically receive Liquid Glass for
standard bars, sheets, popovers, and controls on current platform releases.
Remove custom backgrounds that cover the material or its scroll-edge effects.
Reserve `glassEffect(_:in:)` for important custom controls, and test custom
colors and animation with reduced-transparency and reduced-motion settings.

Create toolbar glass groups with a fixed primary-action spacer. Use a prominent
bordered button when one glass item needs more emphasis:

```swift
.toolbar {
    ToolbarSpacer(.fixed, placement: .primaryAction)
    ToolbarItem(placement: .primaryAction) {
        Button("Add") { addItem() }
            .buttonStyle(.borderedProminent)
            .tint(.accentColor)
    }
}
```

A `Tab(role: .search)` is separated from ordinary tabs and morphs into the
search field when its `TabView` uses `.searchable`.

### Keep important toolbar actions reachable

Apply `visibilityPriority(_:)` to groups that should survive shrinking space.
Put permanently secondary actions in `ToolbarOverflowMenu`, and reserve
`.topBarPinnedTrailing` for an action that must never overflow.
`toolbarMinimizeBehavior(_:for:)` can move the navigation bar aside while
scrolling.

## High-value document and interaction APIs

### Use snapshot-based document I/O

The document architecture separates model observation, snapshots, and
asynchronous I/O. Conform to `WritableDocument`, declare supported formats,
create a snapshot, and implement a `DocumentWriter`. Use `ReadableDocument`
and `DocumentReader` for the read path. An `@Observable` document invalidates
only views that read changed properties.

Place `DocumentGroup` first in the app's scene list. A writer receives the
destination URL, current and previous snapshots for incremental output, and a
consuming Foundation `Subprogress`; it may branch on the configured content
type for alternate exports.

Use `DocumentCreationSource` with `NewDocumentButton` to distinguish blank,
template, import, or other creation flows. The selected source arrives in the
creation context supplied by `DocumentGroup`.

### Generalize collection interactions

For reordering in a list, grid, or custom container, mark repeated content with
`.reorderable()` and the parent with `.reorderContainer(for:)`. Apply the
reported `ReorderDifference` to the data model; the same API supports watchOS.

Outside `List`, enable coordinated `swipeActions` by applying
`swipeActionsContainer()` to the enclosing scroll view. `alert` and
`confirmationDialog` also accept an `item:` binding and pass the non-`nil`
value into the action builder.

On macOS, multi-item drag and drop uses `.draggable(containerItemID:)` on
children and `.dragContainer(for:selection:)` on the parent. Transfer values
are requested lazily at drop time. See the interaction reference for move,
delete, session-phase, and preview controls.

## High-value media and spatial APIs

### Host and control web content natively

Use `WebView(url:)` for direct URL display; it reloads when that input changes.
For loading control and observation, own an observable `WebPage`, pass it to
`WebView`, and load a `URLRequest`, HTML plus a base URL, or data.

```swift
@State private var page = WebPage()

WebView(page)
    .onAppear {
        page.load(URLRequest(url: url))
    }
```

A `NavigationDecider` can inspect navigation actions, adjust preferences, and
allow or cancel navigation. A `URLSchemeHandler` serves bundled resources
through a custom scheme.

### Build spatial interfaces

For volumetric layout, use `Alignment3D`, depth-aware stacks,
`.spatialOverlay(alignment:)`, `SpatialContainer`,
`aspectRatio3D(_:contentMode:)`, and `rotation3DLayout(_:)`. Apply
`.manipulable()` to movable models and inspect
`@Environment(\.surfaceSnappingInfo)` for surface attachment.

For 3D data, place `SurfacePlot(x:y:z:)` inside `Chart3D` and configure the
depth domain with `.chartZScale(domain:)`.

Read the indexed reference before implementing an affected API; it contains
constraints, platform scope, and related features omitted from this quick
reference.
