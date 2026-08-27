# Compose Multiplatform

## Version and build compatibility

Compose Multiplatform 1.7 requires Android Gradle plugin 8.1+. Native/web libraries consuming Compose 1.8 require Kotlin 2.1.0+ and should be republished with that baseline; Kotlin 2.1.20 was the recommended application version. Native/web features in Compose 1.10 require Kotlin 2.2.20+.

AGP 9.0.0 requires Compose Multiplatform 1.9.3 or 1.10.0; earlier 1.9 releases are incompatible. A separate Android application module is the recommended structure. For an AGP 8.8+ `androidLibrary` target, enable generated assets or resource access may throw `MissingResourceException`:

```kotlin
kotlin { androidLibrary { androidResources.enable = true } }
```

Compose resources embedded in XCFrameworks require Kotlin Gradle plugin 2.2+.

## Compose compiler behavior

Open composables compiled with Kotlin 2.1.20 may have default values and generate wrappers compatible with binaries before 1.5.8; older producers use a warning compatibility mode that can still fail at runtime. Final overridden composables are restartable and skippable again; add `@NonRestartableComposable` when the former behavior is required.

Source information is enabled by default on all platforms. Remove duplicate `freeCompilerArgs` configuration because configuring it both there and through the Compose plugin can fail. Kotlin 2.2.10 source information includes parameter names, and multiplatform metrics/reports use target-specific directories.

`@Composable` callable references work when assigned to a composable function type, although they do not expose `ComposableLambda` skipping control. `PausableComposition` is enabled by default; it may be disabled with `ComposeFeatureFlag.PausableComposition.disabled()`. `StrongSkipping` and `IntrinsicRemember` flags are deprecated.

With Compose runtime 1.10+, compiler-generated group keys are added to R8 maps for deobfuscating minified composition stack traces. Disable with `composeCompiler { includeComposeMappingFile.set(false) }`. Kotlin 2.3.10 restores project-file `produceReleaseComposeMapping` output and Java 25 mapping processing; 2.3.21 prevents `MergeMappingFileTask` from clearing R8 artifacts on AGP 9.1+.

Kotlin 2.4.10 fixes Compose 2.4 stability inference that changed formerly `stable` classes to `runtime`/`Uncertain`.

## Dependencies, resources, and graphics

### Dependency coordinates

Deprecated Gradle plugin aliases such as `compose.ui` should be replaced with direct coordinates, preferably through a version catalog. `androidx.compose.runtime:runtime` now publishes every Compose Multiplatform target; `org.jetbrains.compose.runtime:runtime` remains an alias.

Compose Multiplatform 1.8.2 no longer pulls `material-icons-core` transitively. Add an explicit dependency if existing icon references need it, for example `org.jetbrains.compose.material:material-icons-core:1.7.3`.

Material 3 and the Compose plugin can use independent versions/stability levels. Stable `compose.material3` uses Material 3 1.9.0 and excludes public APIs marked `ExperimentalMaterial3ExpressiveApi` or `ExperimentalMaterial3ComponentOverrideApi`; `MaterialExpressiveTheme` needs `org.jetbrains.compose.material3:material3:1.9.0-alpha04` and the Expressive opt-in.

### Resource migration and lookup

The Java-resource forms `painterResource()`, `loadImageBitmap()`, `loadSvgPainter()`, `loadXmlImageVector()`, and `ClassLoaderResourceLoader` are deprecated. Use multiplatform generated resources for localization and multimodule support.

Android packs multiplatform resources into assets, making files addressable by URIs such as `Res.getUri("files/index.html")`. The resource DSL supports source-set `customDirectory`; test source sets get their own resources/accessors; generated classes expose maps such as `Res.allDrawableResources`; and the generated class name can be changed with `compose.resources.nameOfResClass`.

Resources may be embedded directly in XCFrameworks. Test and Android-library resources remain target-specific; remember `androidResources.enable = true` where required.

### Images, fonts, and graphics

`ByteArray.decodeToImageBitmap()` handles JPEG, PNG, BMP, and WEBP. `decodeToImageVector()` handles XML vectors, and `decodeToSvgPainter()` handles SVG except on Android.

Variable fonts work on every platform from 1.8.2. `LineHeightStyle.Alignment` is cross-platform, and Material 3 centers text within explicit line height by default.

Standalone `GraphicsLayer`, unlike `Modifier.graphicsLayer`, can render composable content outside its original scene. Compose 1.9 adds `DropShadowPainter`, `InnerShadowPainter`, `dropShadow`, and `innerShadow` for colored, arbitrary-shape shadows, including shadow geometry used as an inner-gradient mask.

## Common UI, input, and navigation

Shared-element transitions animate matching content across composable scenes, including navigation destinations. Cross-platform drag/drop uses `dragAndDropSource` and `dragAndDropTarget`; `DragData` moved to `compose.ui.draganddrop`, and removed desktop `Modifier.onExternalDrag` must not be used. The common modifiers work on Android/desktop from 1.7 and iOS from 1.8, where transfer data uses `UIDragItem` and currently supports `String` and `NSObject` values.

Material 3 adaptive layout/navigation, adaptive navigation suite, `material3-window-size-class`, and `material-navigation` are available to `commonMain`; `calculateWindowSizeClass()` remains platform-specific.

`LocalLifecycleOwner` moved from Compose UI to Lifecycle. Without UI bindings its helpers do not receive platform lifecycle events.

The synchronous `ClipboardManager` is deprecated. Use suspending `Clipboard`, which also fits the asynchronous web clipboard.

The new `SelectionContainer` / `BasicTextField` context-menu API is opt-in through `ComposeFoundationFlags.isNewContextMenuEnabled = true`; initial support is complete on iOS/web and partial on desktop.

`Popup` overloads without `PopupProperties` are error-deprecated. Stable properties are `PopupProperties.usePlatformDefaultWidth`, `PopupProperties.usePlatformInsets`, `DialogProperties.usePlatformInsets`, `DialogProperties.useSoftwareKeyboardInset`, and `DialogProperties.scrimColor`.

### Navigation

Navigation 2.8 supplies type-safe route objects and arguments. Navigation 2.9 replaces Bundle-like arguments with `SavedState`; use its `read` block or type-safe routes. On iOS, `org.jetbrains.androidx.navigation:navigation-compose` 2.9.2 supplies deep links.

`PredictiveBackHandler()` is deprecated. Use Navigation Event's `NavigationBackHandler()` with mandatory event state, separate cancel/complete callbacks, and progress from `state.transitionState`.

Compose 1.10 adds Alpha Navigation 3 artifacts for non-Android targets: `org.jetbrains.androidx.navigation3:navigation3-ui`, `org.jetbrains.androidx.lifecycle:lifecycle-viewmodel-navigation3`, and `org.jetbrains.compose.material3.adaptive:adaptive-navigation3`. It lacks browser history/address-bar integration, and iOS forward gestures are off by default.

## iOS

### Mandatory configuration and rendering

Set `CADisableMinimumFrameDurationOnPhone` to `true` in `Info.plist`; the app otherwise crashes under the sanity check. Disable `ComposeUIViewControllerConfiguration.enforceStrictPlistSanityCheck` only as a deliberate escape hatch.

Compose 1.8 can opt into a separate render thread with `useSeparateRenderThreadWhenPossible` or controller `parallelRendering`. Compose 1.11 enables concurrent rendering by default.

An iOS composable may request a frame-rate category or non-negative FPS with `Modifier.preferredFrameRate(FrameRateCategory.High)` or `Modifier.preferredFrameRate(30f)`; the highest request wins within hardware limits.

Compose Multiplatform for iOS is Stable and production-ready.

### Native interop and view controllers

From 1.7.3, native-view touches wait 150 ms: movement lets the parent intercept, while an unmoved touch reaches the native view. In 1.8 nested scrolling follows iOS arbitration and a non-scrollable Compose modal can be dismissed by swiping down.

`ComposeUIViewControllerDelegate` is an error-level deprecation; override its behavior on the parent `UIViewController`. The `platformLayers` option is removed because popups, dialogs, and dropdowns use out-of-container layers by default.

UIKit views can use intrinsic fitting size, including SwiftUI via `UIHostingController` and basic `UIView` subclasses that do not depend on `NSLayoutConstraints`; `SwingPanel` similarly derives from component min/preferred/max sizes. Experimental `UIKitViewController` interop can set `placedAsOverlay = true`, causing the native view to cover composables in the same area.

Compose 1.10 adds `WindowInsetsRulers`, composable `WindowInsets.Companion.captionBar`, and `PlatformImeOptions` for custom `UIResponder.inputView` / `UIResponder.inputAccessoryView`. UIKit keyboard/autocorrect/return-key traits are also configurable through `KeyboardOptions.platformImeOptions`.

Compose 1.11's experimental UIView-backed text input adds native caret movement, gestures, selection handles, and menus; the cross-platform implementation remains stable/default.

### Accessibility, links, and platform services

The semantic tree loads lazily on the first accessibility request and disposes afterward; removed `AccessibilitySyncOptions` is unnecessary. iOS supports RTL gestures, traversal, editable traits, VoiceOver lists, pointer/keyboard control, and hides semantics for fully transparent components.

Navigation 2.9.2 with Compose 1.8.2 supports iOS destination deep links through normal `NavController` APIs. `enableTraceOSLog()` is stable for Xcode Instruments.

## Web

Kotlin/Wasm applications no longer include `skiko.js`; Kotlin/JS applications still require it.

Web accessibility is enabled by default in `ComposeViewport`, initially covering labels and accessible button navigation/activation. Interop views, scrollable/slider containers, and traversal indexes remain limited; set `isA11YEnabled = false` only when required. Compose Multiplatform for Web is Beta.

Use `WebElementView()` with `ComposeViewport` to overlay a sized DOM element that intercepts local input. `CanvasBasedWindow` is deprecated.

Use suspending `NavController.bindToBrowserNavigation()` instead of deprecated `Window.bindToNavigation()`, keeping shared JS/Wasm code free of direct `window` access. Earlier `window.bindToNavigation()` connected the graph to browser Back/Forward, address-bar, and direct URLs and supported a custom `getBackStackEntryPath` route mapper.

Experimental `PointerIcon.fromKeyword()` creates cursors from CSS keywords. `preloadFont()`, `preloadImageBitmap()`, and `preloadImageVector()` cache web assets before display.

Use `composeCompatibilityBrowserDistribution` for one JS/Wasm browser package with a JS fallback.

## Desktop and previews

Desktop state-based `BasicTextField` (formerly `BasicTextField2`) provides `TextFieldBuffer`, transformations/styling, and `UndoState`. `ComposePanel` accepts `RenderSettings.isVsyncEnabled`; VSync defaults on, while disabling it lowers latency but can tear.

`SwingFrame()` and `SwingDialog()` provide an `init` block before display for one-time native properties such as `java.awt.Window.setType` and early listeners. Continue using `LaunchedEffect(window)` for changing properties.

Compose 1.8.2 supports JVM desktop on ARM64 Windows. The Compose plugin bundles/enables Hot Reload for desktop; remove an explicit plugin to use the bundled version or keep it to override. Bundling is disabled below Kotlin 2.1.20, while Compose Hot Reload itself is Stable.

Use common `androidx.compose.ui.tooling.preview.Preview`; `org.jetbrains.compose.ui.tooling.preview.Preview` and `androidx.compose.desktop.ui.tooling.preview.Preview` are deprecated. `@Preview` parameters include `name`, `group`, `widthDp`, `heightDp`, `locale`, `showBackground`, and ARGB `backgroundColor`.

## UI testing

Composition coroutines suspended in `delay()` count as idle, so `waitForIdle()`, `awaitIdle()`, and `runOnIdle()` do not drive them; call `mainClock.advanceTimeBy()` explicitly. `runOnIdle()` runs on the UI thread without waiting again, and advancing time renders only when crossing the next 16-ms virtual frame.

Compose 1.9 allows a suspending `runComposeUiTest()` body. JVM/native behave like `runBlocking` with delays skipped; JS/Wasm return a Promise and skip delays.

The v2 non-Android runner uses `StandardTestDispatcher` and queued coroutine order and accepts `effectContext`. Earlier `runComposeUiTest`, `runSkikoComposeUiTest`, and `runDesktopComposeUiTest` forms are deprecated.
