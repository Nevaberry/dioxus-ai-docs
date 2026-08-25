# Media, Devices, and Platform Services

## Audio

Batch `55` adds the following `expo-audio` capabilities:

- Lock-screen controls and background recording.
- Cross-platform playlists and native preloading.
- iOS earpiece routing.
- Broader web recording and media support.

Batch `56` adds `useAudioStream` for live microphone buffers and live-stream status and control fields.

`expo-av` is removed from Expo Go and no longer receives patches. Migrate supported media work to the dedicated audio and video packages, and test native behavior in a development build.

## Video and image

`expo-video` adds `seekTolerance`, `scrubbingModeOptions`, multi-view Android picture-in-picture, richer track metadata, and Android `PlayerBuilderOptions` and `buttonOptions`.

Migrate renamed and relocated video APIs:

- Replace `expo-video-thumbnails` with `expo-video.generateThumbnailsAsync`.
- Replace track `bitrate` with `averageBitrate` and `peakBitrate`.
- Replace `allowsFullscreen` with `fullscreenOptions.enable`.

`expo-image` supports iOS HDR and SF Symbols. On Android it can send cookies with authenticated image requests.

## Camera, browser, location, maps, and haptics

`expo-camera` adds recording stabilization, an Android front-camera screen flash, and an opt-out for the barcode API.

`expo-web-browser` supports universal-link callbacks for authentication.

iOS location permission responses distinguish full from reduced accuracy. Apple Maps can force light or dark appearance.

`expo-haptics` supports Safari in SDK 56. `expo-asset` accepts GLB models.

Android push notifications error in Expo Go and require a development build.

## Widgets and Live Activities

The alpha `expo-widgets` package initially builds iOS home-screen widgets and Live Activities with `@expo/ui`. Shared objects manage timelines, Live Activity lifecycle, and push-to-start tokens.

In SDK 56, `expo-widgets` is stable. Widgets and Live Activities can access the full environment without pre-rendering.

## Inbound sharing

Experimental inbound support in `expo-sharing` adds an iOS share-extension target and Android intent filters through a config plugin. Shared data is delivered through deep links, so validate both native target generation and route handling.

## Android blur

`expo-blur` is stable on Android 12+ using `RenderNode`. Wrap background content in `BlurTargetView` for Android-capable blur layouts. Rename `experimentalBlurMethod` to `blurMethod`; the older implementations remain usable on their previously supported platforms.

## Clipboard and cellular migration

Clipboard listener events no longer contain `content`; call `getStringAsync()` to read current text after the event.

Deprecated cellular carrier constants are removed. Affected iOS methods return `null`.

## Development launcher

The `expo-dev-launcher` config plugin adds `defaultLaunchURL`, `skipOnboarding`, and `showMenuAtLaunch` options.
