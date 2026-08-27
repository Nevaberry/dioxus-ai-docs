# Semantics, Accessibility, and Testing

Use this reference for autofill, semantics-tree behavior, accessibility exposure, visibility observation, Compose test scheduling, and hybrid View/Compose tests.

## Semantics-based autofill (1.8.0)

Compose supports semantics-based autofill. Text autofill requires both UI and Foundation 1.8.0 or newer.

Migration details:

- legacy autofill APIs are deprecated;
- `AutofillManager` is an abstract class;
- `InputText` exposes the value before output transformation;
- `requestAutofill` is no longer a manager method;
- the text toolbar can initiate autofill;
- `LocalAutofillHighlightColor` uses `Color`.

## Semantics API migrations (1.8.0)

Use `Role.Carousel` for pager-like controls. Replace `invisibleToUser()` with `hideFromAccessibility()`.

`SemanticsNodeInteraction.semanticsId()` is removed. Fetch the node and read `fetchSemanticsNode().id`.

## Accessibility-check artifacts (1.8.0)

When `enableAccessibilityChecks()` is used without a test rule, depend on `compose:ui:ui-test-accessibility`. When it is invoked on a rule, use `compose:ui:ui-test-junit4-accessibility`.

The experimental `GlobalAssertions` API is removed; use accessibility checks instead.

## Test-host theme (1.8.0)

The `ComposeContentTestRule.setContent` host supplied by `ui-test-manifest` uses `Theme.Material.Light.NoActionBar`. This prevents an action bar from covering test content when targeting SDK 35.

To use a different theme, remove `ui-test-manifest` and declare `ComponentActivity` with the desired theme in the test manifest.

## Semantics-tree structure (1.9.0)

The `background`, `border`, and `graphicsLayer` modifier nodes implement `SemanticsModifierNode`. They can insert semantics nodes and break tests that assume an exact parent, child, or sibling structure.

Tag the intended target node directly or prefer a looser ancestor-based matcher over exact tree-position assumptions.

## Semantics bounds, shapes, and Android extras (1.9.0)

The `Shape` semantics property describes a control whose meaningful shape differs from its bounding rectangle. `SemanticsModifierNode.isImportantForBounds` can exclude a node from semantics bounds computation.

An Android-specific `SemanticsPropertyKey` factory exposes custom values through `AccessibilityNodeInfo.getExtras`.

## UI-test APIs (1.9.0)

`SemanticsNodeInteraction.performTextInputSelection` is stable. Its `relativeToOriginal` parameter chooses whether offsets apply to original or transformed text.

Experimental `runComposeUiTest` accepts a suspend block. Uncaught layout or draw exceptions can be reported without terminating the entire test suite.

## Typed semantic autofill (1.10.0)

`FillableData` supports text, Boolean, integer, list, and date values. Its factories live on the companion object, so create values with `FillableData.createFrom(value)`. Date data is read through `dateMillisValue`.

Use the `fillableData` property and `onFillData` action instead of deprecated `onAutofillText`. A composition local can customize the brush shown after a successful fill.

## Test scheduling and restoration (1.10.0)

The `effectContext` variants of `createComposeRule`, `createAndroidComposeRule`, and `createEmptyComposeRule` are stable and accept a `StandardTestDispatcher`. Call `MainTestClock.runCurrent()` to execute due scheduler work. The default dispatcher for these established APIs remains `UnconfinedTestDispatcher`.

`StateRestorationTester` always applies platform-specific state encoding. Use `isHiddenFromAccessibility()` to match hidden semantics. `SemanticsNode` finder and selector results are annotated `@CheckResult`.

## Visibility observation (1.10.0)

`onVisibilityChanged` does not call back for a node that begins invisible. It correctly emits `false` after a nonzero `minDurationMs` when the node ceases to satisfy visibility.

`onVisibilityChangedNode()` exposes the same behavior as a delegatable `Modifier.Node` for custom modifiers.

## Accessibility scrolling and merged semantics (1.11.0)

Accessibility `showOnScreen` actions can walk up through nested scrolling containers. Off-screen semantics children of a partially visible merging node remain exposed to accessibility services rather than disappearing from the tree.

## Compose UI testing v2 (1.11.0)

The `androidx.compose.ui.test.v2.run*ComposeUiTest` and `androidx.compose.ui.test.junit4.v2.create*ComposeRule` APIs use `StandardTestDispatcher` by default. Coroutines remain queued until scheduled.

`ComposeUiTestFlags.isStandardTestDispatcherSupportEnabled` is removed. Use the exposed shared `TestCoroutineScheduler`, including `runCurrent()`, to advance queued work. Deprecated test variants continue to use `UnconfinedTestDispatcher`.

## Credential Manager semantics (1.12.0)

On API 34 and newer, a text field can expose a low-level Credential Manager request through the `credentialRequest` semantics property.

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

## Espresso scoping for hybrid UIs (1.12.0)

`onRootWithViewInteraction` scopes Compose-node lookup to the View hierarchy selected by an Espresso `ViewInteraction`. Use it when repeated or embedded Compose roots make an unscoped node query ambiguous.

```kotlin
val row = onView(
    allOf(withId(R.id.row), hasDescendant(withText("Item #5"))),
)
composeTestRule.onRootWithViewInteraction(row)
    .onNodeWithTag("fav_icon")
    .performClick()
```
