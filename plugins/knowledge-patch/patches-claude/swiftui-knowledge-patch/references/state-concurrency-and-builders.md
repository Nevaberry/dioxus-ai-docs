# State, Concurrency, Animation, and Builders

## Synthesize animatable data

Apply `@Animatable` to synthesize a type's `animatableData`. Mark fields that
must remain fixed during interpolation with `@AnimatableIgnored`.

```swift
@Animatable
struct LoadingArc: Shape {
    var radius: CGFloat
    @AnimatableIgnored var clockwise: Bool

    func path(in rect: CGRect) -> Path {
        Path()
    }
}
```

## Keep view work on the correct actor

Conforming to `View` isolates the conforming type and its members to
`@MainActor`. A model created in the view declaration and a `Task` created from
the view body inherit that isolation.

Keep time-sensitive animation state mutations in SwiftUI's synchronous action
callbacks. Use state as the bridge to longer asynchronous model operations.

## Write sendable layout and rendering callbacks

SwiftUI may invoke `Shape.path(in:)`, `Layout` requirements, `visualEffect`, and
the transform closure of `onGeometryChange` away from the main thread. Their
concurrency annotations expose that execution model.

When a closure needs only a value held by the main-actor view, capture a
sendable copy instead of accessing the property through `self`.

```swift
.visualEffect { [pulse] content, _ in
    content.blur(radius: pulse ? 2 : 0)
}
```

## Migrate macro-based State

In Xcode 27, `@State` is a macro. An inline reference-type value is initialized
lazily and once per view lifetime. This behavior back-deploys to iOS 17,
macOS 14, and aligned platform releases.

If an initializer supplies state, omit the inline default. An inline default
wins and discards the assignment performed by `init`. Initialize ordinary
stored properties before state because the synthesized backing storage uses
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

Do not compose another property wrapper with `@State`: both wrappers synthesize
the same underscore-prefixed backing-storage name. A view with private state no
longer receives the previously usable synthesized memberwise initializer, so
declare that initializer explicitly.

## Adapt to the unified ContentBuilder

Many specialized SwiftUI result builders are unified under unconstrained
`@ContentBuilder`. It builds arbitrary content, checks protocol conformance only
when the surrounding context requires it, and works at any minimum deployment
target.

Multi-expression blocks now produce `TupleContent` instead of `TupleView`.
Prefer an opaque `some View` result or update concrete type constraints. When
`TupleContent` is unavailable while back-deploying before iOS, iPadOS, macOS, or
visionOS 27, preserve the `TupleView` constraint and explicitly construct
`TupleView((first, second))`.

## Resolve ContentBuilder ambiguities

Without the former `View` constraint, shape-style modifiers passed to deprecated
non-builder `background` or `overlay` overloads can become ambiguous. Use
trailing-closure syntax to select the builder overload.

```swift
Rectangle()
    .overlay {
        Color.blue.opacity(0.3).blendMode(.overlay)
    }
```

The broader lookup can also expose same-named types or static members from
imported modules. Rename them or qualify them, for example with
`SwiftUI.Color.clear`.

When MapKit is in scope, an empty nested builder can resolve to
`EmptyMapContent` rather than view content. Supply `EmptyContent()` or
`EmptyView()` explicitly, including in a conditional-compilation `#else`
branch. This can happen without a local `import MapKit` when member import
visibility is disabled.

```swift
Group {
    EmptyContent()
}
```
