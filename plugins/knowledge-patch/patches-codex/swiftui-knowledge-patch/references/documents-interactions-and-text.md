# Documents, Interactions, and Text

## Document creation sources

Define `DocumentCreationSource` values and pair them with
`NewDocumentButton`. The selected source arrives in the creation context
passed by `DocumentGroup`, allowing distinct blank, template, import, or other
flows.

```swift
extension DocumentCreationSource {
    static let blank = Self(id: "blank")
    static let photo = Self(id: "photo")
}

DocumentGroupLaunchScene("Create a Page") {
    NewDocumentButton("Blank Page", source: .blank)
    NewDocumentButton("Page from Photo…", source: .photo)
}
```

## Snapshot-based document I/O

The document architecture in swiftui-2026 uses `WritableDocument` with a list
of formats, an asynchronous snapshot, and a `DocumentWriter`.
`ReadableDocument` and `DocumentReader` provide the corresponding read path.
An `@Observable` document updates only views that read the properties that
changed.

Declare `DocumentGroup` as the app's first scene. A writer receives the
destination URL, current and previous snapshots for incremental writes, and a
consuming Foundation `Subprogress`. It can branch on its configured content
type to export another representation, such as PNG.

```swift
struct PageWriter: DocumentWriter {
    typealias Snapshot = PageSnapshot

    nonisolated func write(
        snapshot: sending PageSnapshot,
        to destination: URL,
        previous: sending PageSnapshot?,
        progress: consuming Subprogress
    ) async throws {
        // Write changed parts and report progress.
    }
}
```

For simpler custom I/O backed by file wrappers, use
`FileWrapperDocumentReader` and `FileWrapperDocumentWriter`.
`URLDocumentConfiguration` exposes the document URL and last modification date
and coordinates additional access to the file.

The
`fileExporter(isPresented:document:contentType:defaultFilename:onCompletion:onCancellation:)`
overload exports a `WritableDocument`.

## Multi-item drag and drop

On macOS, identify draggable children with `.draggable(containerItemID:)` and
make the parent a `.dragContainer(for:selection:)`. Selected transfer values
are requested lazily at drop time.

Use `DragConfiguration` to support moves or deletion.
`onDragSessionUpdated` observes phases such as `.ended(.delete)`, while
`.dragPreviewsFormation(.stack)` controls how multiple previews are arranged.

## Reordering arbitrary containers

Apply `.reorderable()` to repeated content and
`.reorderContainer(for:)` to its list, grid, or custom parent. The callback
provides a `ReorderDifference`; apply that difference to the data model. These
APIs also enable reordering on watchOS.

## Swipe actions and item-bound prompts

`swipeActions` works outside `List` when the enclosing scroll view has
`swipeActionsContainer()`, which coordinates swipe actions across its children.

`alert` and `confirmationDialog` accept a sheet-style `item:` binding. A
non-`nil` value presents the interface and is passed to the action builder.

```swift
.confirmationDialog(
    "Delete?",
    item: $stickerToDelete
) { sticker in
    DeleteStickerButton(sticker)
}
```

## Attributed-string editing and persistence

`TextEditor` accepts a binding to `AttributedString`, providing built-in
rich-text controls. Applications can customize paragraph styles, transform
attributes, and restrict the attributes editing permits. Rich text can be
persisted with SwiftData and exported through `Transferable`.

```swift
@Binding var comment: AttributedString

TextEditor(text: $comment)
```

Use `AttributedTextSelection` to represent a selection in attributed text.
`AttributedTextFormattingDefinition` defines the styling allowed in a
particular context. `FindContext` creates a find navigator for views that
support text editing.
