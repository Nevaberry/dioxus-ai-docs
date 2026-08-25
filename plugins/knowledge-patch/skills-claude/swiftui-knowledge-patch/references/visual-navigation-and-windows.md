# Visual Design, Navigation, and Windows

The platform-transition guidance in this reference includes the
`swiftui-2025` and `swiftui-2026` batches.

## Adopt Liquid Glass

Apps rebuilt with the current SDK automatically receive Liquid Glass on current
platform releases for standard bars, sheets, popovers, and controls. Custom
backgrounds can cover both the material and scroll-edge effects; remove those
backgrounds wherever the system treatment is sufficient.

Use `glassEffect(_:in:)` sparingly for important custom controls. Test custom
colors and animation with reduced-transparency and reduced-motion accessibility
settings.

In a toolbar, separate items into glass groups with
`ToolbarSpacer(.fixed, placement: .primaryAction)`. A prominent tinted glass
item uses `.buttonStyle(.borderedProminent).tint(...)`.

## Build adaptive toolbars and search

Give important toolbar groups `visibilityPriority(_:)` so they survive shrinking
space. Put permanently secondary commands in `ToolbarOverflowMenu`, and place an
action that must never overflow at `.topBarPinnedTrailing`.

```swift
.toolbar {
    ToolbarItemGroup {
        EditButtons()
    }
    .visibilityPriority(.high)

    ToolbarOverflowMenu {
        SecondaryActions()
    }

    ToolbarItem(placement: .topBarPinnedTrailing) {
        ShareButton()
    }
}
.toolbarMinimizeBehavior(.onScrollDown, for: .navigationBar)
```

`toolbarMinimizeBehavior(_:for:)` can move the navigation bar aside
automatically while the user scrolls.

Declare a search destination as `Tab(role: .search) { ... }`. It is separated
from ordinary tabs and, when its `TabView` also uses `.searchable`, morphs into
the search field.

## Handle resizable windows

On iPadOS 26, `.commands { TextEditingCommands() }` supplies the app menu bar for
the existing scene API. `UIRequiresFullscreen` is deprecated, so layouts must
tolerate fluid window resizing.

iPhone apps become resizable on iOS 27, and Xcode 27 Live Previews expose resize
handles. In mixed UIKit and SwiftUI interfaces, base sizing decisions on size
classes rather than device idiom.

Read `@Environment(\.appearsActive)` to learn whether a window is active. On
macOS, `.windowResizeAnchor(.top)` makes a content-driven window resize animation
originate at the top edge.

## Tune tab, menu, and sheet presentation

Use `.labelStyle(.titleAndIcon)` when an important iPad or Mac menu item should
show its icon despite the platform default. `Tab(role: .prominent)` places a
distinguished tab at the bottom trailing edge.

`tabBarMinimizeBehavior(_:)` controls when a tab bar minimizes.
`TabViewBottomAccessoryPlacement` lets bottom-accessory content adapt to its
current placement within a tab view.

The `crossFade` transition fades a sheet in over its presenting content.

## Configure edges, controls, and resolved colors

`scrollEdgeEffectStyle(_:for:)` configures a scroll view's edge effect.
`backgroundExtensionEffect()` fills available safe-area edges by duplicating,
mirroring, and blurring the modified view.

A `Slider` initialized with `step` automatically displays tick marks:

```swift
Slider(value: $level, in: 0...10, step: 1)
```

`Color.ResolvedHDR` carries RGBA components together with the HDR headroom
information for a displayable color.
