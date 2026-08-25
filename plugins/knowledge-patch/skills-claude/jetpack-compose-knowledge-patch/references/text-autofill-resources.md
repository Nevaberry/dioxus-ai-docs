# Text, Autofill, and Resources

## Text Layout and Rendering

### Text autosizing (`1.8.0`)

`AutoSize` was renamed to `TextAutoSize`, with public APIs for custom sizing
implementations. Removed `AutoSize` overloads must be migrated to their
corresponding `TextAutoSize` APIs.

### Start and middle ellipsis (`1.8.0`)

Single-line text supports `TextOverflow.StartEllipsis` and
`TextOverflow.MiddleEllipsis` in addition to end ellipsis. Keep
`maxLines = 1` for either new mode.

### Annotated text and paragraphs (`1.8.0`, `1.9.0`)

`Paragraph` and `ParagraphIntrinsics` receive all `AnnotatedString`
annotations, rather than only span styles. `AnnotatedString` permits fully
overlapping and nested paragraphs, its builder APIs are stable, and
`AnnotatedString.fromHtml` understands `<ul>` and `<li>`.

Additional `AnnotatedString` builders support custom bullet lists from 1.9.0.

### `BasicText` layers and cursor tests (`1.8.0`)

`BasicText` no longer creates an implicit `graphicsLayer`. Add
`Modifier.graphicsLayer()` when the layer's isolation or rendering behavior is
required. Tests can disable cursor drawing through `LocalCursorBlinkEnabled`.

## State-Backed Text Fields

### Undo history (`1.9.0`)

`TextFieldState.edit {}` creates a standalone undo entry instead of clearing
history. When a programmatic edit should reset undo, call
`TextFieldState.undoState.clearHistory()` explicitly.

### Styled output (`1.9.0`)

For state-backed fields, style rendered output with `OutputTransformation` and
`TextFieldBuffer.addStyle`. The interim `AnnotatedOutputTransformation` API
was removed.

### Secure input (`1.9.0`)

`BasicSecureTextField` hoists the `ScrollState` used by its internal text
field. `TextObfuscationMode.RevealLastTyped` follows Android's
`TEXT_SHOW_PASSWORD` system setting.

### Transliteration state (`1.11.0`)

`InputTextSuggestionState` exposes replacement suggestions from
transliteration IMEs. `TextCompositionRange` identifies the active
transliteration composition range; `null` means no composition is active.

## Context Menus and Selection

### Menus and smart selection (`1.9.0`)

Text fields support right-click context menus and Android smart-selection
items. Control smart selection through
`ComposeFoundationFlags.isSmartSelectionEnabled` and its work context through
`LocalTextClassifierCoroutineContext`.

Customize menu content with:

- `Modifier.appendTextContextMenuComponents`;
- `Modifier.filterTextContextMenuComponents`;
- the text-context-menu provider, data, and component APIs; and
- `ProcessTextKey` for Android `PROCESS_TEXT` actions.

## Semantic Autofill

### Semantics-based autofill (`1.8.0`)

Text autofill requires UI and Foundation 1.8.0 or newer together. The old
autofill APIs are deprecated, `AutofillManager` is an abstract class, and
`requestAutofill` is no longer a manager method. The text toolbar can initiate
autofill.

`InputText` exposes the text before output transformation.
`LocalAutofillHighlightColor` now carries a `Color`.

### Typed fill data (`1.10.0`)

`FillableData` supports text, Boolean, integer, list, and date values. Its
factories live on the companion object, so construct values with
`FillableData.createFrom(value)`. Date values are available through
`dateMillisValue`.

Replace deprecated `onAutofillText` with the `fillableData` property and
`onFillData` action. A composition local can customize the highlight brush for
a successful fill.

### Autofill behavior flags (`1.11.0`)

Delete assignments to the removed `isSemanticAutofillEnabled` UI flag.
Semantic autofill is always active.

### Credential Manager requests (`1.12.0`)

On API 34 and newer, a text field can expose a low-level Credential Manager
request through `credentialRequest` semantics:

```kotlin
BasicTextField(
    value = value,
    onValueChange = onValueChange,
    modifier = Modifier.semantics {
        if (Build.VERSION.SDK_INT >= 34) {
            credentialRequest = CredentialRequestData(request, callback)
        }
    },
)
```

## Fonts and Android Resources

### Resource-font fallback (`1.8.0`)

When a resource font cannot load, Compose silently falls back to the default
font rather than throwing during measurement. Do not depend on a measurement
exception to detect packaging errors.

### Configuration-aware resources (`1.9.0`)

Use `LocalResources.current` for Android resource access that must update with
configuration changes. Reading it invalidates composition so later lookups see
the new configuration.

### Downloadable variable fonts (`1.12.0`)

`ui-text-google-fonts` can create variable Google fonts with
`FontVariation.Settings` while automatically using the default Google Mobile
Services certificates. A separate provider configuration is unnecessary when
those default certificates are sufficient.

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

## Clipboard and Tooltips

### Common APIs (`1.8.0`)

Foundation and UI expose a common `Clipboard` interface through a composition
local. `BasicTooltip` is available from common Foundation code.

## Parsing Behavior (`1.10.0`)

`TextDirection`, `TextAlign`, `Hyphens`, and `FontSynthesis` `valueOf`
functions throw `IllegalArgumentException` for unknown values. Validate or
handle untrusted serialized values explicitly.
