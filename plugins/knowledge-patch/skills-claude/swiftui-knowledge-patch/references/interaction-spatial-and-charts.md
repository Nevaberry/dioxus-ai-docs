# Interaction, Spatial Layout, and Charts

## Reorder arbitrary repeated content

Mark repeated content with `.reorderable()` and its `List`, grid, or custom
parent with `.reorderContainer(for:)`. The callback supplies a
`ReorderDifference`; apply that difference to the data model. The same API also
supports reordering on watchOS.

## Generalize swipe actions and item-bound prompts

`swipeActions` works outside `List` when the enclosing scroll view has
`swipeActionsContainer()`, which coordinates actions across its children.

`alert` and `confirmationDialog` accept a sheet-style `item:` binding. A
non-`nil` item presents the interface and is passed into its action builder.

```swift
.confirmationDialog("Delete?", item: $stickerToDelete) { sticker in
    DeleteStickerButton(sticker)
}
```

## Implement multi-item drag and drop

On macOS, mark children with `.draggable(containerItemID:)` and their parent
with `.dragContainer(for:selection:)`. Selected transfer values are requested
lazily only when they are dropped.

Use `DragConfiguration` for move and delete support. Observe phases such as
`.ended(.delete)` with `onDragSessionUpdated`, and arrange the dragged previews
with modifiers such as `.dragPreviewsFormation(.stack)`.

## Plot three-dimensional and complex charts

`Chart3D` can host `SurfacePlot(x:y:z:)`. The familiar chart-scale pattern
extends to depth through `.chartZScale(domain:)`.

When an app back-deploys before the 2027 platform releases, a `Chart` closure
with roughly ten or more `if`/`else` or `switch` branches can exceed the type
checker's complexity limit. Extract the branches into a separate
`@ChartContentBuilder` function. This workaround is unnecessary for projects
whose minimum target is a 2027 release.

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

## Arrange and manipulate volumetric content

visionOS 26 provides `Alignment3D`, depth-aware layout variants such as
`VStackLayout().depthAlignment(...)`, and
`.spatialOverlay(alignment:)` for volumetric composition.

Apply `.manipulable()` to let people pick up and move a model. Read
`@Environment(\.surfaceSnappingInfo)` for facts such as whether content is
snapped to a table.

`SpatialContainer` aligns overlapping content in three-dimensional space.
Additional depth-aware layout APIs include
`aspectRatio3D(_:contentMode:)` and `rotation3DLayout(_:)`.
