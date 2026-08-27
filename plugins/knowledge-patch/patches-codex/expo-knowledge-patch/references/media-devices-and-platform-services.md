# Media, Devices, and Platform Services

## Event subscription migration

For package event listeners, retain the returned subscription and call:

```ts
subscription.remove();
```

Module-level `removeSubscription` is deprecated.

## Audio

SDK 55 expands `expo-audio` with lock-screen controls, background recording, cross-platform playlists, native preloading, iOS earpiece routing, and broader web recording and media support.

SDK 56 adds `useAudioStream` for live microphone buffers and live-stream status and control fields.

`expo-av` is no longer patched and is absent from Expo Go. Do not treat Expo Go as a test environment for an application that still depends on it.

## Video

SDK 55 adds these `expo-video` capabilities:

- `seekTolerance` and `scrubbingModeOptions`.
- Multiple Android picture-in-picture views.
- Richer track metadata.
- Android `PlayerBuilderOptions` and `buttonOptions`.

Migrate related APIs as follows:

| Earlier use | Replacement |
|---|---|
| `expo-video-thumbnails` | `expo-video.generateThumbnailsAsync` |
| Track `bitrate` | `averageBitrate` and `peakBitrate` |
| `allowsFullscreen` | `fullscreenOptions.enable` |

## Images and assets

`expo-image` adds iOS HDR rendering and SF Symbols, plus Android cookies for authenticated image requests.

`expo-asset` accepts GLB model assets in SDK 56.

## Camera and browser

`expo-camera` adds recording stabilization, Android front-camera screen flash, and an option to disable the barcode API.

`expo-web-browser` adds universal-link callbacks for authentication flows.

## Blur on Android

`expo-blur` is stable on Android 12+ and uses `RenderNode`. Wrap background content in `BlurTargetView` for Android-capable blur layouts. Rename `experimentalBlurMethod` to `blurMethod`; the older implementations remain available on their previously supported platforms.

## Widgets and Live Activities

The alpha SDK 55 `expo-widgets` package builds iOS home-screen widgets and Live Activities with `@expo/ui`. Shared objects manage timelines, Live Activity lifecycle, and push-to-start tokens.

In SDK 56, `expo-widgets` is stable. Widgets and Live Activities can access the full environment without pre-rendering.

## Inbound sharing

Experimental inbound support in `expo-sharing` adds an iOS share-extension target and Android intent filters through a config plugin. Shared input reaches the application through deep links.

## Location and maps

iOS location permission results report full versus reduced accuracy.

Apple Maps can force a light or dark appearance.

## Clipboard and cellular information

Clipboard listener events no longer carry `content`. Call `getStringAsync()` to read the current clipboard text.

Deprecated cellular carrier constants are removed. The affected iOS methods return `null`.

## Haptics and development launcher

`expo-haptics` supports Safari in SDK 56.

The `expo-dev-launcher` config plugin adds `defaultLaunchURL`, `skipOnboarding`, and `showMenuAtLaunch`.

## Notifications and Android edge-to-edge

The top-level `notification` app-config field causes prebuild to fail. Use the `expo-notifications` config plugin.

Remove `edgeToEdgeEnabled`. Under mandatory Android edge-to-edge, most `expo-navigation-bar` methods and several `expo-status-bar` props and setters are deprecated no-ops. Use the packages' config plugins for build-time status and navigation bar settings.
