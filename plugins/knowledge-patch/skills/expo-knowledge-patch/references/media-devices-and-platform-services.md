# Media, Devices, and Platform Services

## Build audio experiences

In SDK 55, `expo-audio` adds lock-screen controls, background recording, cross-platform playlists, native preloading, iOS earpiece routing, and broader web recording and media support.

SDK 56 adds `useAudioStream` for live microphone buffers, plus status and control fields for live streams.

## Configure video playback

SDK 55 `expo-video` adds:

- `seekTolerance` and `scrubbingModeOptions`.
- Multi-view Android picture-in-picture.
- Richer track metadata.
- Android `PlayerBuilderOptions` and `buttonOptions`.

Migrate thumbnail generation from `expo-video-thumbnails` to `expo-video.generateThumbnailsAsync`. Track `bitrate` is split into `averageBitrate` and `peakBitrate`, and `allowsFullscreen` becomes `fullscreenOptions.enable`.

## Load authenticated and platform-native images

`expo-image` adds iOS HDR and SF Symbols in SDK 55. Android image requests can include cookies for authenticated resources.

## Capture camera content

`expo-camera` adds recording stabilization, an Android front-camera screen flash, and an option to disable the barcode API in SDK 55.

## Complete browser authentication

`expo-web-browser` adds universal-link callbacks for authentication in SDK 55.

## Report location accuracy

iOS location permission responses distinguish full from reduced accuracy in SDK 55. Handle reduced accuracy as a valid permission outcome rather than assuming every grant supplies precise coordinates.

## Control Apple Maps appearance

Apple Maps can force light or dark appearance in SDK 55, independently of the surrounding application theme when needed.

## Use browser haptics and 3D assets

In SDK 56, `expo-haptics` supports Safari and `expo-asset` accepts GLB models.

## Configure the development launcher

The SDK 56 `expo-dev-launcher` config plugin adds `defaultLaunchURL`, `skipOnboarding`, and `showMenuAtLaunch` options.
