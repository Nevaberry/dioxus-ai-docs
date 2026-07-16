# Compose Multiplatform

## Compatibility and dependency migration

### Android Gradle plugin requirements

Compose Multiplatform 1.7 requires Android Gradle plugin 8.1.0 or newer, so projects on AGP 7 must upgrade first.

AGP 9.0.0 requires Compose Multiplatform 1.9.3 or 1.10.0; earlier 1.9 releases are incompatible. A separate Android application module is the recommended structure for smoother upgrades.

### Kotlin requirements

Starting with Compose Multiplatform 1.8, native and web KLIBs that depend on Compose can be consumed only with Kotlin 2.1.0 or newer. Rebuild and republish libraries with Compose 1.8 and Kotlin 2.1.x; Kotlin 2.1.20 is the recommended application version for that generation.

Compose Multiplatform 1.10 features on native or web targets require Kotlin 2.2.20 or newer.

### Dependency coordinates and aliases

Compose Multiplatform 1.8.2 no longer brings in `material-icons-core` transitively. Add it explicitly when older icon references still depend on it:

```kotlin
implementation("org.jetbrains.compose.material:material-icons-core:1.7.3")
```

`androidx.compose.runtime:runtime` publishes every Compose Multiplatform target directly. `org.jetbrains.compose.runtime:runtime` remains compatible as an alias, so shared builds can use the AndroidX coordinate.

Compose Gradle-plugin aliases such as `compose.ui` are deprecated. Replace them with direct coordinates, preferably through a version catalog.

Material 3 and the Compose Multiplatform Gradle plugin no longer need matching versions or stability levels. The stable `compose.material3` alias uses Material 3 1.9.0, whose upstream 1.4.0 base excludes public APIs marked `ExperimentalMaterial3ExpressiveApi` or `ExperimentalMaterial3ComponentOverrideApi`. Use the separate Alpha artifact and opt in for `MaterialExpressiveTheme`:

```kotlin
implementation("org.jetbrains.compose.material3:material3:1.9.0-alpha04")
```

## Compose compiler behavior

### Open, overridden, and callable composables

Open `@Composable` functions compiled with Kotlin 2.1.20 can safely have default parameter values and produce wrappers compatible with pre-1.5.8 binaries. Older producers use a warned compatibility mode that can still crash at runtime.

Overridden composables that are final or belong to final classes are restartable and skippable again. Apply `@NonRestartableComposable` when the earlier non-restartable behavior is required.

Composable function references are supported when assigned a composable function type, although they lack the skipping control of `ComposableLambda` objects:

```kotlin
val content: @Composable (String) -> Unit = ::Text
```

`PausableComposition` is enabled by default and can be disabled with `ComposeFeatureFlag.PausableComposition.disabled()`. `StrongSkipping` and `IntrinsicRemember` feature flags are deprecated.

### Source information, metrics, and mappings

The Compose compiler Gradle plugin includes source information by default on every platform. Remove equivalent settings from `freeCompilerArgs`; setting the option both there and through the plugin can fail the build.

Kotlin 2.2.10 includes parameter names in Compose source information. Multiplatform Compose metrics and reports use target-specific subdirectories.

With Compose runtime 1.10 or newer, the Compose compiler adds group-key entries to R8 mapping files so diagnostic composition stack traces from minified builds can be deobfuscated. Disable mapping tasks when necessary with:

```kotlin
composeCompiler { includeComposeMappingFile.set(false) }
```

Kotlin 2.3.10 restores stack-trace mappings for project files and lets `produceReleaseComposeMapping` process Java 25 class files. Kotlin 2.3.21 prevents `MergeMappingFileTask` from clearing R8 artifacts with AGP 9.1 or newer.

## Resources

### Migrate Java resource APIs

The `compose.ui` Java-resource functions `painterResource()`, `loadImageBitmap()`, `loadSvgPainter()`, `loadXmlImageVector()`, and `ClassLoaderResourceLoader` are deprecated. Use the multiplatform resource library for generated accessors, localization, and multimodule support.

### Android resources

Multiplatform resources are packed into Android assets. Android components such as WebViews and media players can address them with paths such as `Res.getUri("files/index.html")`.

For the AGP 8.8-or-newer `androidLibrary` target, enable generated assets or resource access can throw `MissingResourceException`:

```kotlin
kotlin {
    androidLibrary {
        androidResources.enable = true
    }
}
```

### Resource source sets and lookup

The resource DSL has `customDirectory` for associating a custom directory, including one containing downloaded files, with a source set.

Test source sets can contain resources, receive generated accessors, and package those resources only for test runs.

Generated resource classes expose filename-keyed maps such as `Res.allDrawableResources` for dynamic string-ID lookup. Their class name is configurable:

```kotlin
compose.resources {
    nameOfResClass = "MyRes"
}
```

### Image decoding and preloading

`ByteArray.decodeToImageBitmap()` supports JPEG, PNG, BMP, and WEBP. `decodeToImageVector()` handles XML vectors, and `decodeToSvgPainter()` handles SVG everywhere except Android.

Web targets provide Experimental `preloadFont()`, `preloadImageBitmap()`, and `preloadImageVector()` for caching resources before display and avoiding font or image flashes.

### XCFramework embedding

Compose resources are embedded in generated XCFrameworks, allowing resource-bearing libraries to be distributed as ordinary XCFrameworks. This requires Kotlin Gradle plugin 2.2 or newer.

## Navigation and back handling

### Type-safe routes and arguments

Navigation 2.8 route-object APIs are available for compile-time-safe graphs and arguments instead of string-only routing.

Navigation 2.9 replaces `Bundle`-style argument access with `SavedState` accessors. Read arguments inside a `read` block, or prefer type-safe routes:

```kotlin
val userId = navBackStackEntry.arguments?.read {
    getStringOrNull("userid")
}
```

Compose Multiplatform 1.8.2 with `org.jetbrains.androidx.navigation:navigation-compose` 2.9.2 supports destination deep links on iOS through normal `NavController` APIs.

### Predictive back

`PredictiveBackHandler()` is deprecated in favor of the Navigation Event library. Use `NavigationBackHandler()` with mandatory event state and separate cancellation and completion callbacks. Gesture progress is in `state.transitionState`.

```kotlin
val state = rememberNavigationEventState(NavigationEventInfo.None)
NavigationBackHandler(
    state = state,
    isBackEnabled = true,
    onBackCancelled = { /* cancel animation */ },
    onBackCompleted = { /* navigate back */ },
)
```

### Navigation 3

Compose Multiplatform 1.10 adds Alpha Navigation 3 artifacts for non-Android targets:

- `org.jetbrains.androidx.navigation3:navigation3-ui`
- `org.jetbrains.androidx.lifecycle:lifecycle-viewmodel-navigation3`
- `org.jetbrains.compose.material3.adaptive:adaptive-navigation3`

Browser history and address-bar integration do not yet work with Navigation 3. iOS end-edge forward gestures are disabled by default.

## Layout, drawing, and interaction

### Drag and drop

The deprecated desktop `Modifier.onExternalDrag` is replaced by `dragAndDropSource` and `dragAndDropTarget`, and `DragData` moves to `compose.ui.draganddrop`; `onExternalDrag` is removed in 1.8.

The common modifiers work on Android and desktop in 1.7 and add iOS support in 1.8. iOS transfer data uses `UIDragItem` and currently supports `String` and `NSObject` values.

### Shared elements and graphics layers

Shared-element transition APIs animate matching content between composable scenes, including navigation destinations.

Standalone `GraphicsLayer`, available in Compose Multiplatform 1.7, can render composable content outside its original scene, unlike `Modifier.graphicsLayer`.

### Shadows

`DropShadowPainter`, `InnerShadowPainter`, and the `dropShadow` and `innerShadow` modifiers support colored shadows of arbitrary shapes, including shadow geometry as an inner-gradient mask.

```kotlin
Box(
    Modifier.size(120.dp)
        .dropShadow(RectangleShape, DropShadow(12.dp))
        .background(Color.White)
)
```

### Fonts and line height

Variable fonts are supported on every platform as of 1.8.2. `LineHeightStyle.Alignment` is implemented everywhere, and Material 3 centers text within an explicit line height by default across platforms.

### Clipboard

The synchronous `ClipboardManager` is deprecated in favor of the suspending `Clipboard` interface. The replacement works on every target, including web, whose clipboard API cannot be synchronous.

### Context menus

The new context-menu API customizes menus in `SelectionContainer` and `BasicTextField`. Initial support is complete on iOS and web but partial on desktop. Enable it at application startup:

```kotlin
ComposeFoundationFlags.isNewContextMenuEnabled = true
```

### Popup and dialog properties

`Popup` overloads without `PopupProperties` are deprecated at error level. `PopupProperties.usePlatformDefaultWidth` and `usePlatformInsets`, plus `DialogProperties.usePlatformInsets`, `useSoftwareKeyboardInset`, and `scrimColor`, are stable.

### Common UI modules

Material 3 adaptive layout/navigation modules, the adaptive navigation suite, `material3-window-size-class`, and `material-navigation` can be `commonMain` dependencies. `calculateWindowSizeClass()` remains platform-specific even though window-size classes are common.

`LocalLifecycleOwner` moved from Compose UI to Lifecycle, allowing its Compose helpers without Compose UI bindings. Without those bindings, it has no platform event integration.

## Preview tooling

`@Preview` supports `name`, `group`, maximum `widthDp` and `heightDp`, `locale`, `showBackground`, and a 32-bit ARGB `backgroundColor`. IntelliJ IDEA and Android Studio recognize the parameters.

```kotlin
@Preview(
    name = "French phone",
    group = "Locales",
    widthDp = 390,
    heightDp = 844,
    locale = "fr",
    showBackground = true,
    backgroundColor = 0xFFFFFFFF,
)
@Composable
fun AppPreview() = App()
```

Common previews should import `androidx.compose.ui.tooling.preview.Preview`. The former `org.jetbrains.compose.ui.tooling.preview.Preview` and desktop `androidx.compose.desktop.ui.tooling.preview.Preview` annotations are deprecated.

## iOS

### Required frame-duration setting

An iOS app crashes when `CADisableMinimumFrameDurationOnPhone` is absent from `Info.plist` or false. Normally enable it for 120-Hz displays:

```xml
<key>CADisableMinimumFrameDurationOnPhone</key>
<true/>
```

Set `ComposeUIViewControllerConfiguration.enforceStrictPlistSanityCheck=false` only to disable enforcement.

### Touch dispatch and native interop

Starting in 1.7.3, touches over native interop views wait 150 ms. Movement beyond the threshold lets the parent composable intercept the sequence; an unmoved touch goes to the native view. In 1.8, nested native/Compose scrolling follows iOS gesture arbitration, and a non-scrollable Compose modal can be dismissed by swiping down.

`ComposeUIViewControllerDelegate` produces a deprecation error; override relevant methods on the parent `UIViewController`.

The experimental `platformLayers` option is removed because out-of-container layers for popups, dialogs, and dropdowns are the iOS default.

`SwingPanel` now derives size from its embedded component's minimum, preferred, and maximum sizes. UIKit interop views can use intrinsic fitting size, including SwiftUI hosted through `UIHostingController` and basic `UIView` subclasses that do not depend on `NSLayoutConstraints`.

Experimental UIKit interop views can render above Compose, enabling transparent backgrounds and native shader effects. The native view covers composables in the same area.

```kotlin
@OptIn(ExperimentalComposeUiApi::class)
@Composable
fun NativeOverlay() {
    UIKitViewController(
        factory = { createNativeController() },
        update = {},
        properties = UIKitInteropProperties(placedAsOverlay = true),
    )
}
```

### Accessibility

`AccessibilitySyncOptions` is removed. The semantic tree loads lazily on the first accessibility request and is disposed when interaction ends.

iOS gains RTL gestures, traversal semantics, editable text traits, VoiceOver list announcements, pointer and keyboard control. Fully transparent components no longer expose semantics.

### Frame rates and concurrent rendering

An iOS composable can request a frame-rate category or non-negative frames-per-second value with `Modifier.preferredFrameRate(FrameRateCategory.High)` or `Modifier.preferredFrameRate(30f)`. If multiple requests exist, Compose applies the highest subject to hardware limits.

The earlier opt-in separate render thread used `useSeparateRenderThreadWhenPossible` or the `parallelRendering` controller option:

```kotlin
ComposeUIViewController(configure = { parallelRendering = true }) {
    App()
}
```

Concurrent iOS rendering is enabled by default in 1.11, so rendering work uses a dedicated render thread without controller configuration.

### Keyboard and text input

Text fields pass native keyboard, autocorrection, and return-key traits through `KeyboardOptions.platformImeOptions`:

```kotlin
BasicTextField(
    value = "",
    onValueChange = {},
    keyboardOptions = KeyboardOptions(
        platformImeOptions = PlatformImeOptions {
            keyboardType(UIKeyboardTypeEmailAddress)
        }
    ),
)
```

`PlatformImeOptions` can configure `UIResponder.inputView` to replace the system keyboard and `UIResponder.inputAccessoryView` to attach an accessory view on focus.

Compose Multiplatform 1.11 adds an opt-in `UIView`-backed text-input implementation with native caret movement, gestures, selection handles, and system context-menu actions. The existing cross-platform path remains the stable default.

### Insets and tracing

iOS supports `WindowInsetsRulers` for positioning and sizing against system bars and the on-screen keyboard. `WindowInsets.Companion.captionBar` is composable for consistent cross-platform behavior.

`enableTraceOSLog()` is stable and needs no experimental opt-in; inspect its trace output with Xcode Instruments.

### Production status

Compose Multiplatform for iOS is Stable and intended for production use.

## Web

### Accessibility

Web accessibility is enabled by default. It initially exposes description labels and accessible button navigation and activation. Interop views, scrollable or slider container views, and traversal indexes are not yet supported.

Set `isA11YEnabled = false` in `ComposeViewport`'s `configure` block only when generated accessibility support must be disabled.

### DOM elements inside Compose

`WebElementView()` embeds a DOM element as an overlay sized by Compose and intercepts input in that area. It works only with `ComposeViewport`; `CanvasBasedWindow` is deprecated.

```kotlin
WebElementView(
    factory = {
        (document.createElement("iframe") as HTMLIFrameElement)
            .apply { src = url }
    },
    modifier = Modifier.fillMaxSize(),
    update = { iframe -> iframe.src = iframe.src },
)
```

### Browser navigation

The earlier `window.bindToNavigation()` connects the main graph to browser Back/Forward, address-bar, and direct route URLs. Its optional `getBackStackEntryPath` customizes route-to-URL conversion.

The suspending `NavController.bindToBrowserNavigation()` replaces deprecated `Window.bindToNavigation()` and removes direct `window` access from shared JS/Wasm code:

```kotlin
LaunchedEffect(Unit) {
    navController.bindToBrowserNavigation()
}
```

### Browser cursors and fallback distributions

Experimental `PointerIcon.fromKeyword()` creates web pointer icons from CSS cursor keywords.

The `composeCompatibilityBrowserDistribution` Gradle task packages JS and Wasm browser distributions together, allowing a Wasm application to fall back to JS when a browser lacks required modern Wasm features.

Kotlin/Wasm applications can remove `skiko.js` from `index.html`; Kotlin/JS applications still require it.

### Lifecycle status

Compose Multiplatform for Web is Beta.

## Desktop

### Text fields and panels

Desktop adopts the stable state-based `BasicTextField`, renamed from `BasicTextField2`. It adds `TextFieldBuffer` for programmatic edits, transformation and styling APIs, and access to `UndoState`.

`ComposePanel` accepts `RenderSettings.isVsyncEnabled`; disabling VSync can reduce input-to-render latency but may cause tearing. VSync remains enabled by default.

### Window initialization

`SwingFrame()` and `SwingDialog()` add an `init` block that runs before the native window is visible, allowing one-time properties such as `java.awt.Window.setType` and early event listeners. Continue using `LaunchedEffect(window)` for properties that can change after display.

### Platforms and Hot Reload

Compose Multiplatform 1.8.2 supports JVM desktop applications on ARM64 Windows.

The Compose Multiplatform Gradle plugin bundles and enables Compose Hot Reload for desktop. Remove an explicit Hot Reload plugin declaration to use the bundled version, or keep it to override the version. With Kotlin older than 2.1.20, bundled integration is disabled.

Compose Hot Reload is Stable.

## Testing

### Idleness and clocks

Composition coroutines suspended in `delay()` count as idle, so `waitForIdle()`, `awaitIdle()`, and `runOnIdle()` do not drive them. Advance `mainClock` explicitly when a test depends on delayed work.

`runOnIdle()` runs on the UI thread without waiting again afterward. `mainClock.advanceTimeBy()` renders only when time crosses the next 16-ms virtual frame.

### Suspending test bodies

`runComposeUiTest()` accepts a suspending body, allowing direct `awaitIdle()` calls. On JVM and Native it behaves like `runBlocking` with delays skipped; on JS and Wasm it returns a `Promise` and also skips delays.

```kotlin
runComposeUiTest {
    awaitIdle()
}
```

### Compose UI testing v2

Non-Android tests gain v2 `ComposeUiTest` APIs and use `StandardTestDispatcher` by default, executing coroutines in queued order. The v2 runner accepts `effectContext`; prior `runComposeUiTest`, `runSkikoComposeUiTest`, and `runDesktopComposeUiTest` forms are deprecated.

```kotlin
@OptIn(ExperimentalTestApi::class)
@Test
fun uiTest() = runComposeUiTest(
    effectContext = motionDurationScale + StandardTestDispatcher(),
) {
    setContent { App() }
}
```
