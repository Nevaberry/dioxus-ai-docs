# Text and Editing

Use this reference for text measurement and rendering, state-backed editing, output transformation, selection, menus, secure input, IME suggestions, fonts, and clipboard access.

## Text autosizing (1.8.0)

`TextAutoSize` replaces `AutoSize` and includes public APIs for custom autosizing implementations. Deprecated `AutoSize` overloads are removed; migrate callers to the matching `TextAutoSize` APIs rather than retaining the old type name.

## Start and middle ellipsis (1.8.0)

Single-line text can use `TextOverflow.StartEllipsis` and `TextOverflow.MiddleEllipsis` as well as end ellipsis. Keep `maxLines = 1` when selecting either new mode.

## Annotated text and paragraphs (1.8.0)

`Paragraph` and `ParagraphIntrinsics` receive every `AnnotatedString` annotation, not only span styles. Account for non-style annotations in custom paragraph processing.

`AnnotatedString` allows fully overlapping and nested paragraphs. Its builder methods are stable, and `AnnotatedString.fromHtml` supports `<ul>` and `<li>`.

## BasicText rendering and cursor tests (1.8.0)

`BasicText` no longer inserts an implicit `graphicsLayer`; add `Modifier.graphicsLayer()` explicitly if code depends on layer behavior.

Tests can disable cursor drawing by providing `LocalCursorBlinkEnabled`.

## Resource-font failure behavior (1.8.0)

A resource font that cannot load falls back silently to the default font instead of throwing during measurement. If a specific font is required for layout or brand fidelity, verify the resolved font rather than relying on an exception.

## Common clipboard and tooltip APIs (1.8.0)

Foundation and UI expose a common `Clipboard` interface and composition local. `BasicTooltip` is available from common Foundation code.

## Undo history for state-backed fields (1.9.0)

`TextFieldState.edit {}` creates a standalone undo entry; it no longer clears history. Call `TextFieldState.undoState.clearHistory()` explicitly after a programmatic edit that should reset the undo stack.

## Styled output and bullet lists (1.9.0)

In state-backed fields, `OutputTransformation` can style rendered output through `TextFieldBuffer.addStyle`. The interim `AnnotatedOutputTransformation` API is removed.

`AnnotatedString` also provides APIs for constructing custom bullet lists.

## Context menus and smart selection (1.9.0)

Text fields support right-click context menus and Android smart-selection items. Control smart selection with `ComposeFoundationFlags.isSmartSelectionEnabled` and supply its work context through `LocalTextClassifierCoroutineContext`.

Customize public menu behavior with:

- `Modifier.appendTextContextMenuComponents`;
- `Modifier.filterTextContextMenuComponents`;
- the text-context-menu provider, data, and component APIs;
- `ProcessTextKey` for Android `PROCESS_TEXT` actions.

## Secure text behavior (1.9.0)

`BasicSecureTextField` hoists the `ScrollState` used by its internal text field. `TextObfuscationMode.RevealLastTyped` honors Android's `TEXT_SHOW_PASSWORD` system setting.

## Mouse-wheel and word selection (1.10.0)

Mouse-wheel scrolling supports two-dimensional deltas. Double-tap word selection works in `SelectionContainer` and in the value/on-value-change `BasicTextField` API.

## Transliteration suggestion state (1.11.0)

`InputTextSuggestionState` exposes replacement-suggestion state from transliteration IMEs. `TextCompositionRange` identifies the active transliteration composition range; `null` means there is no active composition.

## Downloadable variable fonts (1.12.0)

`ui-text-google-fonts` can construct variable Google fonts with `FontVariation.Settings` while automatically using the default Google Mobile Services certificates. An app no longer needs to configure a font provider solely to supply those certificates.

```kotlin
val fontFamily = FontFamily(
    Font(
        googleFont = GoogleFont("Google Sans Flex"),
        variationSettings = FontVariation.Settings(
            FontVariation.weight(900),
            FontVariation.slant(0f),
        ),
    ),
)
```
