# Router, UI, and Web

## Migrate the Router dependency boundary

Expo Router no longer depends on React Navigation in SDK 56. Direct `@react-navigation/*` imports generally stop working unless the application declares and configures those packages itself. Apply the migration codemod to application source:

```sh
npx expo-codemod sdk-56-expo-router-react-navigation-replace <source-directory>
```

Review any remaining direct imports instead of assuming they are transitively available.

## Build native navigation

Router additions in SDK 55 include adaptive Colors, a default-enabled Apple Zoom transition, iOS `Stack.Toolbar`, experimental SplitView, experimental Android form-sheet footers, Xcasset icons, and header and bottom-tab items.

Native Tabs handle safe-area insets automatically. They also accept `listeners` and `screenListeners`; `Stack.Screen.Title` accepts `asChild`, and `NativeTabs.Trigger` accepts `disableTransparentOnScrollEdge`.

Android experimentally supports `Stack.Toolbar` and Stack v5 in SDK 56, including Material-style headers and predictive-back behavior. Keep platform guards around experimental native-stack features.

## Implement Router rendering and data loading

Expo Web adds alpha server-side rendering and experimental data loaders in SDK 55.

SDK 56 adds streaming web SSR with `unstable_useServerRendering`. Use `generateMetadata` for initial-page metadata; `<Head>` continues to update metadata after hydration.

`createStaticLoader` receives route params without a request. `createServerLoader` always receives a request and errors if invoked during static generation. A `_layout` route can export `SuspenseFallback` to replace the default Suspense loading UI.

## Migrate the SwiftUI component names

The Expo UI SwiftUI API is beta in SDK 55 and aligns several names with platform conventions:

- `DateTimePicker` becomes `DatePicker`.
- `Switch` becomes `Toggle`.
- `CircularProgress` and `LinearProgress` become `ProgressView`.
- `Section`, `Form`, `Button`, and `Slider` also have breaking API changes; verify their current signatures while migrating.

The same API adds `ConfirmationDialog`, `ScrollView`, Markdown rendering in `Text`, more modifiers, and custom SwiftUI views and modifiers.

## Use functional Compose views

The beta Compose API in SDK 55 replaces class-based view definitions with the functional `View("MyView") { props -> }` DSL. It includes Material 3 components, SwiftUI-like `modifiers`, scoped modifiers such as `weight` and `matchParentSize`, XML Material Symbols through `<Icon>`, and `Host.matchContents` and `Host.colorScheme`.

## Use stable universal Expo UI

In SDK 56, the SwiftUI and Jetpack Compose APIs are stable, included in the default template, and available in Expo Go. Universal `Host`, layout, text, input, control, and sheet components share an API across Android and iOS; web remains experimental.

Custom SwiftUI and Compose views and modifiers remain supported. `useNativeState` bridges JavaScript state to a SwiftUI `ObservableObject` or Compose `MutableState`. `WorkletCallback` permits synchronous worklet props, including controlled `TextField` updates. Compose also adds `useMaterialColors` and the `@expo/material-symbols` catalog.

## Replace community components selectively

Compatibility APIs live under `@expo/ui/community/*`. For example:

```ts
import DateTimePicker from '@expo/ui/community/datetime-picker';
```

This can replace `@react-native-community/datetimepicker`. Replacements also cover Gorhom Bottom Sheet, masked view, menu, pager view, picker, segmented control, and slider. Unsupported or different props still require migration work; do not assume complete behavioral equivalence.

## Coordinate status and navigation bars

SDK 56 adds an `expo-navigation-bar` `<NavigationBar>` component whose props align with `<StatusBar>`, plus imperative `setStyle` and `setHidden` methods. Multiple component instances merge their settings in mount order.

`expo-status-bar` now has a config plugin, and its plugin options align with `expo-navigation-bar`. Prefer the components and plugins over APIs made ineffective by mandatory Android edge-to-edge.

## Render Android blur

`expo-blur` is stable on Android 12+ in SDK 55 and uses `RenderNode`. Wrap the background content for Android-capable blur layouts in `BlurTargetView`. Rename `experimentalBlurMethod` to `blurMethod`; older implementations remain available on the platforms they previously supported.

## Build widgets and inbound sharing

The alpha SDK 55 `expo-widgets` package creates iOS home-screen widgets and Live Activities with `@expo/ui`. Shared objects manage timelines, the Live Activity lifecycle, and push-to-start tokens.

`expo-widgets` is stable in SDK 56. Widgets and Live Activities can access the full environment without pre-rendering.

Experimental inbound `expo-sharing` support adds an iOS share-extension target and Android intent filters through a config plugin, then passes shared data into the application through deep links.

## Choose the DOM WebView implementation

DOM components use `@expo/dom-webview` by default in SDK 56 and no longer require `react-native-webview`. Opt out when the application specifically needs the previous `react-native-webview` implementation.
