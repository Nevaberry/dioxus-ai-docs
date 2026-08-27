# Interface, Layout, and Navigation

## Liquid Glass

Apps rebuilt with the current SDK automatically gain Liquid Glass on current
platform releases for standard bars, sheets, popovers, and controls
(swiftui-2025). Custom backgrounds can obscure both the material and
scroll-edge effects, so remove them where possible. Apply
`glassEffect(_:in:)` sparingly to important custom controls. Test custom color
and animation choices with reduced-transparency and reduced-motion settings.

Use `ToolbarSpacer(.fixed, placement: .primaryAction)` to split toolbar items
into glass groups. A glass item gains extra prominence with
`.buttonStyle(.borderedProminent).tint(...)`.

A search destination declared with `Tab(role: .search) { ... }` is visually
separated from ordinary tabs. When the surrounding `TabView` uses
`.searchable`, that destination morphs into the search field.

## Resizable interfaces

iPadOS 26 deprecates `UIRequiresFullscreen`; applications must support fluid
window resizing. The existing scene command API produces the new iPad app menu
bar:

```swift
.commands {
    TextEditingCommands()
}
```

On macOS, `.windowResizeAnchor(.top)` chooses where a content-driven
window-resize animation originates.

iPhone applications become resizable on iOS 27, and Xcode 27 Live Previews
provide resize handles. In mixed UIKit and SwiftUI layouts, use size classes
instead of device idiom to drive size-dependent structure.
`@Environment(\.appearsActive)` reports whether the window is active.

## Toolbars, menus, and navigation prominence

Apply `visibilityPriority(_:)` to keep important toolbar groups visible as
space contracts. Place permanently secondary actions in
`ToolbarOverflowMenu`. A `ToolbarItem` placed at `.topBarPinnedTrailing` never
overflows. `toolbarMinimizeBehavior(_:for:)` can automatically move the
navigation bar aside during scrolling.

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

Menus on iPad and Mac can omit icons for ordinary items. Apply
`.labelStyle(.titleAndIcon)` when an important menu item should retain both its
title and icon.

`Tab(role: .prominent)` places a distinguished tab on the bottom trailing
edge. `tabBarMinimizeBehavior(_:)` controls when a tab bar minimizes.
`TabViewBottomAccessoryPlacement` allows a bottom accessory to vary its content
according to its current placement.

## Safe-area and scroll-edge effects

Use `scrollEdgeEffectStyle(_:for:)` to choose a scroll view's edge effect.
`backgroundExtensionEffect()` fills available safe-area edges by duplicating,
mirroring, and blurring the modified view.

## Presentation

The `crossFade` transition makes a sheet fade in over its presenting content.

## Controls

A `Slider` initialized with a `step` automatically displays tick marks:

```swift
Slider(value: $level, in: 0...10, step: 1)
```

## Spatial layout and manipulation

visionOS 26 provides `Alignment3D`, depth variants such as
`VStackLayout().depthAlignment(...)`, and
`.spatialOverlay(alignment:)` for volumetric layout. Apply `.manipulable()` to
let people pick up and move a model. Read
`@Environment(\.surfaceSnappingInfo)` for details such as whether the model is
snapped to a table.

`SpatialContainer` aligns overlapping content in three-dimensional space.
Depth-aware layout also provides `aspectRatio3D(_:contentMode:)` and
`rotation3DLayout(_:)`.
