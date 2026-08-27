# Router, UI, and Web

## Expo Router

### Native navigation additions in SDK 55

Batch `55` adds adaptive Colors and enables the Apple Zoom transition by default. Router also adds:

- iOS `Stack.Toolbar`.
- Experimental SplitView.
- Experimental Android form-sheet footers.
- Xcasset icons and header or bottom-tab items.
- Native Tabs safe-area handling by default.
- `listeners` and `screenListeners` on Native Tabs.
- `asChild` on `Stack.Screen.Title`.
- `disableTransparentOnScrollEdge` on `NativeTabs.Trigger`.

Headless-tab `reset` is renamed to `resetOnFocus`.

### React Navigation dependency migration in SDK 56

Batch `56` removes Expo Router's implicit application-facing dependency on React Navigation. Direct `@react-navigation/*` imports generally stop working out of the box. Run:

```sh
npx expo-codemod sdk-56-expo-router-react-navigation-replace <source-directory>
```

Then audit remaining imports and install any React Navigation packages the application intentionally uses.

### Native stacks and server rendering

Android experimentally supports `Stack.Toolbar` and Stack v5, including Material-style headers and predictive back.

Web streaming SSR uses `unstable_useServerRendering`. `generateMetadata` sets initial-page metadata, while `<Head>` updates metadata after hydration. A `_layout` route can export `SuspenseFallback` to replace the default Suspense loading UI.

Loader behavior differs by rendering mode:

- `createStaticLoader` receives route params without a request.
- `createServerLoader` always receives a request and errors during static generation.
- `expo-router/server` uses standard `Request` and `Response` objects.

## Expo UI

### Jetpack Compose beta in SDK 55

The Compose API replaces class-based view definitions with the functional `View("MyView") { props -> }` DSL. It adds Material 3 components and SwiftUI-like `modifiers`, including scoped modifiers such as `weight` and `matchParentSize`.

Use `<Icon>` for XML Material Symbols. `Host.matchContents` and `Host.colorScheme` control host sizing and color scheme.

### SwiftUI beta changes in SDK 55

The SwiftUI API adopts convention-aligned names:

| Previous | Current |
|---|---|
| `DateTimePicker` | `DatePicker` |
| `Switch` | `Toggle` |
| `CircularProgress` or `LinearProgress` | `ProgressView` |

`Section`, `Form`, `Button`, and `Slider` also changed. New capabilities include `ConfirmationDialog`, `ScrollView`, Markdown in `Text`, more modifiers, and custom SwiftUI views and modifiers.

### Stable universal UI in SDK 56

The SwiftUI and Jetpack Compose APIs are stable, included in the default template, and available in Expo Go. Universal `Host`, layout, text, input, control, and sheet components share an API across Android and iOS; web support remains experimental.

Custom SwiftUI and Compose views and modifiers are supported. `useNativeState` bridges JavaScript to SwiftUI `ObservableObject` or Compose `MutableState`. `WorkletCallback` permits synchronous worklet props, including controlled `TextField` updates. Compose also adds `useMaterialColors` and the `@expo/material-symbols` catalog.

### Community-component replacements

Compatibility APIs live under `@expo/ui/community/*`. For example, replace `@react-native-community/datetimepicker` with `@expo/ui/community/datetime-picker`.

Replacements also cover Gorhom Bottom Sheet, masked view, menu, pager view, picker, segmented control, and slider. Compare props because unsupported or different props can require migration work.

## Status, navigation, and blur

`expo-blur` is stable on Android 12+ through `RenderNode`. Wrap background content in `BlurTargetView` for Android-capable blur layouts. Rename `experimentalBlurMethod` to `blurMethod`; older implementations remain available on the platforms they previously supported.

`expo-navigation-bar` adds a `<NavigationBar>` component aligned with `<StatusBar>` props, plus imperative `setStyle` and `setHidden` methods. Multiple instances merge in mount order.

`expo-status-bar` adds a config plugin whose options align with `expo-navigation-bar`. Prefer the config plugins because mandatory edge-to-edge turns many earlier imperative methods, props, and setters into deprecated no-ops.

## Web and DOM components

Expo Web adds alpha server-side rendering and experimental data loaders in SDK 55.

DOM components use `@expo/dom-webview` by default in SDK 56 and no longer require `react-native-webview`. Opt out when the application must continue using `react-native-webview`.
