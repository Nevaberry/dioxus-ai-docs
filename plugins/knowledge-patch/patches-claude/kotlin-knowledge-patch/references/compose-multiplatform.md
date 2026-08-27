# Compose Multiplatform

## Version and build compatibility

- Compose Multiplatform 1.7 requires Android Gradle plugin 8.1.0 or newer.
- Native and web KLIBs depending on Compose 1.8 can be consumed only with Kotlin 2.1.0 or newer. Rebuild and republish libraries with Compose 1.8 and Kotlin 2.1.x; Kotlin 2.1.20 is the recommended application baseline for that line.
- AGP 9.0.0 requires Compose Multiplatform 1.9.3 or 1.10.0; earlier 1.9 releases are incompatible. A separate Android application module gives smoother AGP upgrades.
- Compose 1.10 features on Native and web require Kotlin 2.2.20 or newer.

Compose Multiplatform for iOS is stable and ready for production use. Compose Multiplatform for Web is Beta. Desktop Compose Hot Reload is stable.

## Compose compiler behavior

Open `@Composable` functions compiled with Kotlin 2.1.20 may safely have default parameter values and generate wrappers compatible with binaries older than Compose compiler 1.5.8. Older producers use a warning-level compatibility mode that can still crash at runtime.

Overridden composables that are final or belong to final classes are restartable and skippable again. Add `@NonRestartableComposable` only when the Kotlin 2.1.0 behavior is required.

The Compose compiler Gradle plugin includes source information by default on every platform. Remove equivalent values from `freeCompilerArgs`; setting the same option there and through the plugin can fail the build. Kotlin 2.2.10 source information includes parameter names, and multiplatform metrics and reports use target-specific subdirectories.

Composable callable references work when assigned a composable function type, although they do not expose the skipping controls of `ComposableLambda` objects:

```kotlin
val content: @Composable (String) -> Unit = ::Text
```

`PausableComposition` is enabled by default and can be turned off with `ComposeFeatureFlag.PausableComposition.disabled()`. `StrongSkipping` and `IntrinsicRemember` feature flags are deprecated.

With Compose runtime 1.10 or newer, the compiler plugin adds group keys to R8 mappings so minified composition stack traces can be deobfuscated. Disable it with `composeCompiler { includeComposeMappingFile.set(false) }` only when necessary.

Kotlin 2.3.10 restores project-file stack-trace mappings and permits `produceReleaseComposeMapping` to process Java 25 class files. Kotlin 2.3.21 stops `MergeMappingFileTask` from clearing R8 artifacts with AGP 9.1 or newer.

Compose compiler 2.4 could regress types previously inferred as `stable` to `runtime` or `Uncertain`; Kotlin 2.4.10 restores stability inference.

## Dependencies, annotations, and modules

Compose Gradle-plugin aliases such as `compose.ui` are deprecated. Use direct library coordinates, preferably through a version catalog.

Common previews should import `androidx.compose.ui.tooling.preview.Preview`. The old `org.jetbrains.compose.ui.tooling.preview.Preview` and desktop-only `androidx.compose.desktop.ui.tooling.preview.Preview` are deprecated.

`androidx.compose.runtime:runtime` publishes all Compose Multiplatform targets. `org.jetbrains.compose.runtime:runtime` remains compatible as an alias.

Material 3 versions and Compose plugin versions no longer need matching stability levels. The stable `compose.material3` alias in Compose 1.9 uses Material 3 1.9.0, whose upstream 1.4.0 base excludes public `ExperimentalMaterial3ExpressiveApi` and `ExperimentalMaterial3ComponentOverrideApi` APIs. Use the separate Alpha artifact and opt in for `MaterialExpressiveTheme`:

```kotlin
implementation("org.jetbrains.compose.material3:material3:1.9.0-alpha04")
```

Compose 1.8.2 no longer brings in `material-icons-core` transitively. Add it explicitly if existing icon references still depend on it:

```kotlin
implementation("org.jetbrains.compose.material:material-icons-core:1.7.3")
```

Material 3 adaptive layout and navigation, the adaptive navigation suite, `material3-window-size-class`, and `material-navigation` can be used from `commonMain`. `calculateWindowSizeClass()` remains platform-specific even though the classes are common.

`LocalLifecycleOwner` moved from Compose UI to the Lifecycle package. Its Compose helpers can be used without Compose UI bindings, but then receive no platform event integration.

## Resources and assets

The Java-resource APIs `painterResource()`, `loadImageBitmap()`, `loadSvgPainter()`, `loadXmlImageVector()`, and `ClassLoaderResourceLoader` are deprecated. Use the multiplatform resource library for generated accessors, localization, and multimodule support.

Multiplatform resources are packed into Android assets so Android components can address them by URI, for example `Res.getUri("files/index.html")`.

The resource DSL's `customDirectory` associates a generated or downloaded directory with a source set. Test source sets may also contain resources; they get separate generated accessors and are packaged only for tests.

Generated classes expose filename-keyed maps such as `Res.allDrawableResources` for dynamic lookup by string ID. Their class name is configurable:

```kotlin
compose.resources {
    nameOfResClass = "MyRes"
}
```

`ByteArray.decodeToImageBitmap()` handles JPEG, PNG, BMP, and WEBP. `decodeToImageVector()` reads XML vectors, and `decodeToSvgPainter()` reads SVG on every target except Android.

Resources are embedded in generated XCFrameworks so resource-bearing libraries can be distributed as ordinary XCFrameworks. This requires Kotlin Gradle plugin 2.2 or newer.

For the AGP 8.8-or-newer `androidLibrary` target, enable generated assets or resource lookup can throw `MissingResourceException`:

```kotlin
kotlin {
    androidLibrary {
        androidResources.enable = true
    }
}
```

Web targets can preload resources with experimental `preloadFont()`, `preloadImageBitmap()`, and `preloadImageVector()` to avoid display flashes.

## Navigation and back handling

Navigation 2.8 exposes type-safe route-object graphs and arguments across Compose Multiplatform, replacing string-only routes.

Navigation 2.9 moves argument access from `Bundle` patterns to `SavedState`. Read values in a `read` block or use type-safe routes:

```kotlin
val userId = navBackStackEntry.arguments?.read {
    getStringOrNull("userid")
}
```

Compose 1.8.2 with `org.jetbrains.androidx.navigation:navigation-compose` 2.9.2 supports iOS destination deep links through ordinary `NavController` APIs.

`PredictiveBackHandler()` is deprecated. The Navigation Event replacement requires event state and separate cancellation and completion callbacks; progress is available through `state.transitionState`.

```kotlin
val state = rememberNavigationEventState(NavigationEventInfo.None)
NavigationBackHandler(
    state = state,
    isBackEnabled = true,
    onBackCancelled = { /* cancel animation */ },
    onBackCompleted = { /* navigate back */ },
)
```

Compose 1.10 provides Alpha Navigation 3 artifacts on non-Android targets: `navigation3-ui`, `lifecycle-viewmodel-navigation3`, and `adaptive-navigation3`. Navigation 3 does not yet integrate browser history or the address bar, and iOS end-edge forward gestures are disabled by default.

## Shared UI and graphics

Cross-platform drag and drop uses `Modifier.dragAndDropSource` and `dragAndDropTarget`; desktop `Modifier.onExternalDrag` was deprecated and removed in 1.8, and `DragData` moved to `compose.ui.draganddrop`. The common modifiers work on Android and desktop from 1.7 and iOS from 1.8. iOS transfer data currently supports `String` and `NSObject` through `UIDragItem`.

Shared-element transition APIs animate matching content between composable scenes, including navigation destinations.

Standalone `GraphicsLayer` can render composable content outside its original scene, unlike `Modifier.graphicsLayer`.

Compose 1.9 adds `DropShadowPainter`, `InnerShadowPainter`, `dropShadow`, and `innerShadow` for colored arbitrary-shape shadows and inner-gradient masks.

Variable fonts work on every platform as of 1.8.2. `LineHeightStyle.Alignment` is also cross-platform, and Material 3 centers text within an explicit line height by default.

`Popup` overloads without `PopupProperties` are deprecated at error level. `PopupProperties.usePlatformDefaultWidth` and `usePlatformInsets`, plus `DialogProperties.usePlatformInsets`, `useSoftwareKeyboardInset`, and `scrimColor`, are stable.

The synchronous `ClipboardManager` is deprecated. Use the suspending, cross-platform `Clipboard` interface, including on web where clipboard access cannot be synchronous.

## Text input and context menus

Desktop uses the stable state-based `BasicTextField`, renamed from `BasicTextField2`. It includes `TextFieldBuffer` for programmatic edits, transformation and styling APIs, and `UndoState`.

The opt-in context-menu API customizes menus in `SelectionContainer` and `BasicTextField`. Initial support is complete on iOS and web and partial on desktop. Enable it at startup:

```kotlin
ComposeFoundationFlags.isNewContextMenuEnabled = true
```

On iOS, `KeyboardOptions.platformImeOptions` configures native keyboard, autocorrection, and return-key traits. Later `PlatformImeOptions` can replace `UIResponder.inputView` or attach `UIResponder.inputAccessoryView` for a focused text field.

Compose 1.11 adds an opt-in iOS text implementation backed by `UIView`, with native caret movement, gestures, selection handles, and system context-menu actions. The cross-platform implementation remains the stable default.

## Preview and testing

Multiplatform `@Preview` supports `name`, `group`, maximum `widthDp` and `heightDp`, `locale`, `showBackground`, and a 32-bit ARGB `backgroundColor` in both IntelliJ IDEA and Android Studio:

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

`runComposeUiTest()` accepts a suspending body, allowing `awaitIdle()` directly. JVM and Native behave like `runBlocking` with delays skipped; JS and Wasm return a `Promise` and also skip delays.

Composition coroutines suspended in `delay()` count as idle, so `waitForIdle()`, `awaitIdle()`, and `runOnIdle()` do not advance them. Move `mainClock` explicitly. `runOnIdle()` executes on the UI thread without another wait afterward; `mainClock.advanceTimeBy()` renders only when time crosses the next 16-ms virtual frame.

Non-Android UI tests now have v2 `ComposeUiTest` APIs and use `StandardTestDispatcher` by default, running coroutines in queued order. The v2 runner accepts `effectContext`; earlier `runComposeUiTest`, `runSkikoComposeUiTest`, and `runDesktopComposeUiTest` APIs are deprecated.

```kotlin
@OptIn(ExperimentalTestApi::class)
@Test
fun uiTest() = runComposeUiTest(
    effectContext = motionDurationScale + StandardTestDispatcher(),
) {
    setContent { App() }
}
```

## iOS application configuration and rendering

Set `CADisableMinimumFrameDurationOnPhone` to `true`; absence or `false` can crash the app under the strict sanity check:

```xml
<key>CADisableMinimumFrameDurationOnPhone</key>
<true/>
```

Set `ComposeUIViewControllerConfiguration.enforceStrictPlistSanityCheck=false` only when intentionally disabling enforcement.

Touch sequences over native interop views wait 150 ms from Compose 1.7.3: movement beyond the threshold lets the Compose parent intercept, while a stationary touch goes to the native view. In 1.8, nested native/Compose scrolling follows iOS gesture arbitration and a non-scrollable Compose modal can be dismissed by swiping down.

`ComposeUIViewControllerDelegate` now produces a deprecation error. Override the relevant methods on the parent `UIViewController`.

The old experimental `platformLayers` option is removed because out-of-container iOS layers for popups, dialogs, and dropdowns are always enabled.

Experimental UIKit interop may place a native view over Compose, enabling transparent backgrounds and native shader effects; the native view covers composables in that area.

```kotlin
UIKitViewController(
    factory = { createNativeController() },
    update = {},
    properties = UIKitInteropProperties(placedAsOverlay = true),
)
```

`SwingPanel` derives size from the embedded component's minimum, preferred, and maximum size. UIKit interop may use intrinsic fitting size, including SwiftUI via `UIHostingController` and basic `UIView` subclasses without `NSLayoutConstraints`.

An iOS composable can request a frame-rate category or non-negative FPS with `Modifier.preferredFrameRate(FrameRateCategory.High)` or `Modifier.preferredFrameRate(30f)`. Compose chooses the highest request in a tree subject to hardware limits.

`WindowInsetsRulers` position and size iOS content against system bars and the keyboard. `WindowInsets.Companion.captionBar` is composable for cross-platform behavior.

Concurrent rendering was opt-in through `useSeparateRenderThreadWhenPossible` or `parallelRendering`:

```kotlin
ComposeUIViewController(configure = { parallelRendering = true }) { App() }
```

Compose 1.11 enables it by default, placing rendering work on a dedicated thread without controller configuration.

iOS accessibility loads the semantic tree lazily on first request and disposes it when interaction ends; removed `AccessibilitySyncOptions` is unnecessary. Support includes RTL gestures, traversal semantics, editable-text traits, VoiceOver list announcements, pointer and keyboard control, and omission of semantics for fully transparent components.

`enableTraceOSLog()` is stable; inspect its traces in Xcode Instruments.

## Web applications

Web accessibility is enabled by default and initially exposes descriptions plus accessible button navigation and activation. Interop views, scrollable and slider container views, and traversal indexes are not yet supported. Disable with `isA11YEnabled=false` in the `ComposeViewport` configuration only when necessary.

Use `ComposeViewport` rather than deprecated `CanvasBasedWindow`. `WebElementView()` embeds a DOM overlay sized by Compose and intercepts input in its area; it works only with `ComposeViewport`.

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

Use suspending `NavController.bindToBrowserNavigation()` for browser Back/Forward, address-bar, and direct-route integration. It replaces deprecated `Window.bindToNavigation()` and removes direct `window` access from shared JS/Wasm code.

```kotlin
LaunchedEffect(Unit) {
    navController.bindToBrowserNavigation()
}
```

The earlier `window.bindToNavigation()` accepted `getBackStackEntryPath` to customize route-to-URL conversion. Preserve equivalent routing policy when migrating.

`PointerIcon.fromKeyword()` creates experimental web pointer icons from CSS cursor keywords.

Kotlin/Wasm pages no longer need `skiko.js` in `index.html`; Kotlin/JS pages still do.

Use `composeCompatibilityBrowserDistribution` to bundle JS and Wasm browser distributions so JS can serve as a fallback when modern Wasm features are unavailable.

## Desktop platforms

`ComposePanel` accepts `RenderSettings.isVsyncEnabled`. VSync remains on by default; disabling it can reduce latency but may cause tearing.

`SwingFrame()` and `SwingDialog()` accept an `init` block that runs before the window appears, suitable for one-time properties such as `Window.setType` and early listeners. Continue using `LaunchedEffect(window)` for values that change after display.

JVM desktop applications run on Windows ARM64 starting with Compose 1.8.2.

The Compose plugin bundles and enables Hot Reload for desktop. Remove an explicit Hot Reload plugin to use the bundled version, or retain it to override the version. Bundled integration is disabled with Kotlin older than 2.1.20.
