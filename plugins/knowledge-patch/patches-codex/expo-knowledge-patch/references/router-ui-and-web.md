# Router, UI, and Web

## Router dependency migration

In SDK 56, Expo Router no longer makes React Navigation packages available as application-facing dependencies. Direct `@react-navigation/*` imports generally stop working unless the packages are installed intentionally.

Apply the supported replacement codemod, then audit anything left behind:

```sh
npx expo-codemod sdk-56-expo-router-react-navigation-replace <source-directory>
```

## Native Router surfaces

SDK 55 adds these Router capabilities:

- Adaptive Colors and a default-enabled Apple Zoom transition.
- iOS `Stack.Toolbar`.
- Experimental SplitView and experimental Android form-sheet footers.
- Xcasset icons plus header and bottom-tab items.
- Automatic safe-area handling in Native Tabs.
- `listeners` and `screenListeners` on Native Tabs.
- `asChild` on `Stack.Screen.Title`.
- `disableTransparentOnScrollEdge` on `NativeTabs.Trigger`.

SDK 56 experimentally brings `Stack.Toolbar` and Stack v5 to Android, including Material-style headers and predictive back. Treat all explicitly experimental native surfaces as opt-in and test them on each target platform.

The headless-tab option formerly named `reset` is `resetOnFocus`.

## Server rendering, loaders, and metadata

Expo Web introduces alpha server-side rendering and experimental data loaders in SDK 55. `expo-router/server` uses standard `Request` and `Response` objects rather than older custom request/response shapes.

SDK 56 adds streaming SSR through `unstable_useServerRendering` and clarifies the loader lifecycle:

- `createStaticLoader` receives route params but no request.
- `createServerLoader` always receives a request and errors during static generation.
- `generateMetadata` provides initial-page metadata.
- `<Head>` updates metadata after hydration.
- A `_layout` route can export `SuspenseFallback` to replace the default Suspense loading UI.

## Expo UI migration and maturity

### SDK 55 Compose API

The Jetpack Compose API is beta and replaces class-based view definitions with the functional `View("MyView") { props -> }` DSL. It includes Material 3 components, SwiftUI-like `modifiers`, scoped modifiers such as `weight` and `matchParentSize`, XML Material Symbols through `<Icon>`, `Host.matchContents`, and `Host.colorScheme`.

### SDK 55 SwiftUI API

The SwiftUI API is beta and aligns component names and conventions:

| Earlier name | Current name |
|---|---|
| `DateTimePicker` | `DatePicker` |
| `Switch` | `Toggle` |
| `CircularProgress` or `LinearProgress` | `ProgressView` |

`Section`, `Form`, `Button`, and `Slider` also changed. New capabilities include `ConfirmationDialog`, `ScrollView`, Markdown in `Text`, additional modifiers, and custom SwiftUI views and modifiers.

### SDK 56 universal API

The SwiftUI and Jetpack Compose APIs are stable, included in the default template, and available in Expo Go. A common API now covers `Host`, layout, text, input, controls, and sheets on Android and iOS; web support remains experimental.

Custom SwiftUI and Compose views and modifiers are supported. `useNativeState` bridges JavaScript state to SwiftUI `ObservableObject` or Compose `MutableState`. `WorkletCallback` supports synchronous worklet props, including controlled `TextField` updates. Compose adds `useMaterialColors` and the `@expo/material-symbols` catalog.

## Community-component compatibility APIs

SDK 56 provides compatibility entry points under `@expo/ui/community/*`. For example:

```ts
import DateTimePicker from '@expo/ui/community/datetime-picker';
```

This can replace `@react-native-community/datetimepicker`. Compatibility APIs also cover Gorhom Bottom Sheet, masked view, menu, pager view, picker, segmented control, and slider. Compare component props during migration because differing or unsupported props can require application changes.

## Blur on Android

`expo-blur` is stable on Android 12+ using `RenderNode`. Wrap the background content of an Android-capable blur layout in `BlurTargetView`. Rename `experimentalBlurMethod` to `blurMethod`; older blur implementations remain available on the platforms they previously supported.

## Status and navigation bars

Mandatory Android edge-to-edge makes most imperative `expo-navigation-bar` methods and several `expo-status-bar` props and setters deprecated no-ops. Their former app-config fields are deprecated; use each package's config plugin.

SDK 56 adds a `<NavigationBar>` component whose props match `<StatusBar>`, plus imperative `setStyle` and `setHidden` methods. Multiple component instances merge in mount order. `expo-status-bar` now has a config plugin, and its options align with `expo-navigation-bar`.

## DOM component WebView default

SDK 56 DOM components use `@expo/dom-webview` by default and no longer require `react-native-webview`. Opt out when the application must keep using `react-native-webview`.

## Vector icon migration

`@expo/vector-icons` is deprecated in SDK 56 and is no longer installed transitively by `expo`. Either add it explicitly to retain the old API or move to per-set `@react-native-vector-icons/*` packages:

```sh
npx @react-native-vector-icons/codemod
```
