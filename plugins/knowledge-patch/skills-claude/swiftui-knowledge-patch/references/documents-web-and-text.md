# Documents, Web Content, Images, and Text

## Offer distinct document creation paths

Define `DocumentCreationSource` values and associate them with
`NewDocumentButton`. The source selected at launch reaches the creation context
passed by `DocumentGroup`, allowing separate blank, template, import, or other
creation flows.

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

## Use snapshot-based document I/O

The document architecture separates observable editing state from asynchronous
serialization:

- A `WritableDocument` declares its supported formats and produces its snapshot
  asynchronously.
- A `DocumentWriter` writes that snapshot.
- `ReadableDocument` and `DocumentReader` provide the corresponding read path.
- An `@Observable` document invalidates only views that read changed properties.

Declare `DocumentGroup` as the first scene in the app. A writer receives the
destination URL, the current and previous snapshots for incremental output, and
a consuming Foundation `Subprogress` for reporting work. It can branch on its
configured content type to export alternate formats such as PNG.

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

For a simpler file-wrapper implementation, use `FileWrapperDocumentReader` and
`FileWrapperDocumentWriter`. `URLDocumentConfiguration` exposes the document URL
and last modification date and coordinates access to additional files.

The
`fileExporter(isPresented:document:contentType:defaultFilename:onCompletion:onCancellation:)`
overload exports a `WritableDocument`.

## Display and control web content

`WebView(url:)` directly displays a URL and reloads when the URL input changes.
For observation and control, own an observable `WebPage`, pass it into
`WebView`, and invoke its load APIs with a `URLRequest`, an HTML string and base
URL, or data.

```swift
@State private var page = WebPage()

WebView(page)
    .onAppear {
        page.load(URLRequest(url: url))
    }
```

Initialize a `WebPage` with a `NavigationDecider` to inspect each
`NavigationAction`, modify `NavigationPreferences`, and allow or cancel the
navigation. A `URLSchemeHandler` can serve bundled HTML and CSS through a custom
scheme.

`WebView` participates in `scrollBounceBehavior` and `findNavigator`. Use
`webViewScrollPosition` for its scroll position and
`webViewScrollInputBehavior` to configure input such as visionOS
look-to-scroll.

## Control AsyncImage requests and caching

On the 2027 platform releases, `AsyncImage` uses standard HTTP caching by
default and respects server cache headers rather than reloading every time an
image reappears.

Apps built with Xcode 27 can pass a `URLRequest` and install a custom
`URLSession` and `URLCache` with `asyncImageURLSession(_:)`.

```swift
AsyncImage(
    request: URLRequest(
        url: imageURL,
        cachePolicy: .returnCacheDataElseLoad
    )
)
.asyncImageURLSession(imageSession)
```

## Edit attributed text

`TextEditor` accepts a binding to `AttributedString` and provides built-in
rich-text controls. Apps can customize paragraph styles, transform attributes,
and restrict which attributes editing permits. Rich text can be persisted with
SwiftData and exported through `Transferable`.

```swift
@Binding var comment: AttributedString

TextEditor(text: $comment)
```

Use `AttributedTextSelection` to represent attributed-text selections and
`AttributedTextFormattingDefinition` to define the styling allowed in a given
context. `FindContext` creates a find navigator for views that support text
editing.
