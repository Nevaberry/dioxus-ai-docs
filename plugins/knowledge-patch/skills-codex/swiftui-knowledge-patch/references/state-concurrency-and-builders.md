# State, Concurrency, and Builders

## Synthesized animation data

The `@Animatable` macro synthesizes a type's `animatableData`
(swiftui-2025). Mark members that must remain fixed during interpolation with
`@AnimatableIgnored`.

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

## Main-actor view boundaries

Conformance to `View` isolates the conforming type and its members to
`@MainActor`. A model created in the view declaration inherits that isolation,
as does a `Task` created from the view body.

Keep time-sensitive animation state changes in synchronous SwiftUI action
callbacks. Use state to bridge from those synchronous changes to longer
asynchronous model work.

## Sendable rendering and layout callbacks

SwiftUI can invoke `Shape.path(in:)`, `Layout` requirements, `visualEffect`,
and the transform closure of `onGeometryChange` away from the main thread.
Their concurrency annotations reflect this behavior. If such a closure needs
only a value derived from main-actor view state, capture a sendable copy rather
than reaching through `self`.

```swift
.visualEffect { [pulse] content, _ in
    content.blur(radius: pulse ? 2 : 0)
}
```

## Macro-based State

In Xcode 27, `@State` is a macro whose inline value is lazy
(swiftui-2026). A reference-type value is therefore created once per view
lifetime. This behavior back-deploys to iOS 17, macOS 14, and the aligned
platform releases.

When an initializer supplies the state value, omit an inline default. If both
are present, the inline default wins and discards the initializer assignment.
Initialize ordinary stored properties first because synthesized state backing
storage uses `self`.

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

Do not compose another property wrapper with `@State`; both wrappers synthesize
the same underscore-prefixed storage name. A view containing private state no
longer receives the previously usable synthesized memberwise initializer.
Declare that initializer explicitly.

## Unified ContentBuilder

Many specialized SwiftUI result builders are unified under unconstrained
`@ContentBuilder`. It can assemble arbitrary content and delays protocol
conformance checking until the surrounding context requires it. The builder
itself works with any minimum deployment target.

Multi-expression blocks now produce `TupleContent` rather than `TupleView`.
Prefer opaque `some View` results or update concrete constraints. When
back-deploying before iOS, iPadOS, macOS, or visionOS 27 and `TupleContent` is
unavailable, retain the `TupleView` constraint and explicitly construct
`TupleView((first, second))`.

### Resolve overload and name ambiguities

Removing the `View` constraint can make shape-style modifiers passed to the
deprecated non-builder `background` or `overlay` overloads ambiguous. Select
the builder overload with trailing-closure syntax:

```swift
Rectangle()
    .overlay {
        Color.blue.opacity(0.3).blendMode(.overlay)
    }
```

The broader builder can expose same-named types or static members from imported
modules. Rename the local declaration or module-qualify the intended symbol:

```swift
SwiftUI.Color.clear
```

### Fill empty nested builders explicitly

When MapKit is in scope, an empty nested builder can resolve to
`EmptyMapContent` instead of view content. Supply `EmptyContent()` or
`EmptyView()` explicitly, including in a `#else` branch. This can happen
without a local `import MapKit` when member import visibility is disabled.

```swift
Group {
    EmptyContent()
}
```

## Back-deployed Charts type checking

With a minimum deployment target earlier than the 2027 OS releases, a `Chart`
closure with roughly ten or more `if`/`else` or `switch` branches can exceed
the type checker's complexity limit. Extract the branches into a separate
`@ChartContentBuilder` function. Projects targeting only the 2027 releases do
not need the workaround.

```swift
Chart(points) { point in
    marks(for: point)
}

@ChartContentBuilder
private func marks(for point: DataPoint) -> some ChartContent {
    if selectedMetric == .rate {
        RateMark(point)
    } else {
        DefaultMark(point)
    }
}
```
