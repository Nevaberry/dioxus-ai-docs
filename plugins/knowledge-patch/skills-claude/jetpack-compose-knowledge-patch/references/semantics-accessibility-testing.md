# Semantics, Accessibility, and Testing

## Semantics API Migrations

### Roles, hidden nodes, and IDs (`1.8.0`)

Use `Role.Carousel` for pager-like controls. Replace
`invisibleToUser()` with `hideFromAccessibility()`.
`SemanticsNodeInteraction.semanticsId()` was removed; retrieve the ID with
`fetchSemanticsNode().id`.

### Tree changes from visual modifiers (`1.9.0`)

The `background`, `border`, and `graphicsLayer` modifier nodes implement
`SemanticsModifierNode`. They can insert nodes and change exact parent, child,
or sibling relationships. Tag the actual target node or use a looser
ancestor-based matcher instead of encoding incidental tree structure.

### Bounds, shapes, and Android extras (`1.9.0`)

The `Shape` semantics property describes a control whose meaningful shape
differs from its bounding rectangle. Set
`SemanticsModifierNode.isImportantForBounds` to exclude a node from semantics
bounds calculation.

On Android, a platform-specific `SemanticsPropertyKey` factory publishes
custom values through `AccessibilityNodeInfo.getExtras`.

## Accessibility Behavior

### Nested show-on-screen (`1.11.0`)

Accessibility `showOnScreen` actions can traverse nested scrolling containers.
Off-screen semantics children of a partially visible merging node remain
visible to accessibility services rather than disappearing from the exposed
tree.

## Accessibility Checks

### Artifact split (`1.8.0`)

When calling `enableAccessibilityChecks()` without a test rule, depend on
`compose:ui:ui-test-accessibility`. When invoking it on a rule, use
`compose:ui:ui-test-junit4-accessibility`.

The experimental `GlobalAssertions` API was removed; migrate those checks to
the accessibility-check APIs.

## Test Hosts

### Default test activity theme (`1.8.0`)

The host used by `ComposeContentTestRule.setContent` from `ui-test-manifest`
uses `Theme.Material.Light.NoActionBar`. This prevents an action bar from
covering content when tests target SDK 35.

To choose another theme, remove `ui-test-manifest` and declare
`ComponentActivity` with the intended theme in the test manifest.

## Interaction and Assertion APIs

### Text selection and suspend tests (`1.9.0`)

`SemanticsNodeInteraction.performTextInputSelection` is stable. Its
`relativeToOriginal` parameter determines whether offsets refer to original or
transformed text.

Experimental `runComposeUiTest` accepts a suspend block. A test harness can
report uncaught layout or draw exceptions without terminating the full suite.

### Restoration and result usage (`1.10.0`)

`StateRestorationTester` always applies platform-specific state encoding.
`isHiddenFromAccessibility()` matches hidden semantics. `SemanticsNode` finder
and selector results carry `@CheckResult`, so consume returned interactions
rather than accidentally discarding them.

## Coroutine Scheduling

### Configurable rule dispatchers (`1.10.0`)

The `effectContext` variants of `createComposeRule`,
`createAndroidComposeRule`, and `createEmptyComposeRule` are stable and accept
a `StandardTestDispatcher`. Use `MainTestClock.runCurrent()` to run scheduler
work that is due. The default for these older rule APIs remains
`UnconfinedTestDispatcher`.

### Compose UI testing v2 (`1.11.0`)

The following new API families use `StandardTestDispatcher` by default, so
coroutines remain queued until the scheduler advances:

- `androidx.compose.ui.test.v2.run*ComposeUiTest`
- `androidx.compose.ui.test.junit4.v2.create*ComposeRule`

The shared `TestCoroutineScheduler` is exposed for operations such as
`runCurrent()`. Deprecated test variants retain `UnconfinedTestDispatcher`.
The temporary `ComposeUiTestFlags.isStandardTestDispatcherSupportEnabled` flag
was removed.

## Hybrid View and Compose Tests

### Espresso-scoped roots (`1.12.0`)

`onRootWithViewInteraction` scopes Compose node lookup to the View hierarchy
selected by an Espresso `ViewInteraction`. This disambiguates repeated Compose
content embedded in rows or containers of a hybrid interface.

```kotlin
val row = onView(
    allOf(withId(R.id.row), hasDescendant(withText("Item #5"))),
)
composeTestRule.onRootWithViewInteraction(row)
    .onNodeWithTag("fav_icon")
    .performClick()
```
