# Runtime Upgrades and Tooling

## Align the runtime and native toolchain

SDK 55 pairs React Native 0.83 with React 19.2. It removes Legacy Architecture support and the `newArchEnabled` app-config option. Expo SDK packages now share the SDK major, so compatible package constraints look like `expo-camera@^55.0.0`.

For SDK 55, native iOS builds require Xcode 26, EAS Build defaults to Xcode 26.2, and the minimum iOS version remains 15.1. Supported Node.js ranges are `^20.19.4`, `^22.13.0`, `^24.3.0`, and `^25.0.0`.

SDK 56 pairs React Native 0.85 with React 19.2. Native builds require Xcode 26.4, with minimum targets of iOS/tvOS 16.4 and macOS 13.4. Custom Expo module podspecs must also target iOS 16.4. New templates use TypeScript 6.0.3, and Metro can serve development bundles over HTTPS when TLS is configured.

## Select the template deliberately

The SDK 55 default template uses Native Tabs and places routes in `/src/app` instead of `/app`. Create that template explicitly when reproducibility matters:

```sh
npx create-expo-app@latest --template default@sdk-55
```

New app scaffolds in SDK 56 also include `AGENTS.md`, a companion agent-guidance file, and a hidden agent-settings file. Treat those files as project instructions when present.

## Configure Hermes v1

Hermes v1 is opt-in in SDK 55. It requires React Native to be built from source and the compiler package to match:

```json
{
  "expo": {
    "plugins": [["expo-build-properties", {
      "buildReactNativeFromSource": true,
      "useHermesV1": true
    }]]
  }
}
```

For npm, pnpm, or Bun, set:

```json
{
  "overrides": {
    "hermes-compiler": "250829098.0.4"
  }
}
```

Use `resolutions` with Yarn. Building React Native from source substantially increases native build time, and this opt-in is not recommended for Android monorepos.

Hermes v1 is the default in SDK 56. Opt out with `useHermesV1: false` in `expo-build-properties`. Merely importing `react-native-reanimated` under Hermes v1 can increase memory use by 25–30%; enabling worklets bundle mode is the documented workaround.

## Load app config and plugins

Dynamic app config experimentally accepts `.mjs`, `.cjs`, `.cts`, and `.mts` in SDK 55. `app.config.ts` is transpiled with the project's own TypeScript version.

In SDK 56, every Expo package config plugin exports typed options from `expo-<name>/plugin` for use in `app.config.ts`. Config plugins use the same loader as app config, so plugin arrays may reference local `.ts` files and `.mjs` or `.cjs` plugins.

## Use CLI isolation and diagnostics

- `expo start --localhost` accepts only localhost connections.
- The experimental native LogBox requires `EXPO_UNSTABLE_LOG_BOX=1` and a rebuilt native application.
- `eas update` requires `--environment <name>`, including in CI.
- `create-expo-module` supports non-interactive scaffolding.

## Understand Metro and resolver defaults

SDK 56 makes the on-demand filesystem and the native Node.js watcher the defaults in place of `watchFolders` and Watchman. Disable the on-demand filesystem with `experiment.onDemandFilesystem: false` in app config. Restore Watchman with `resolver.useWatchman` in Metro config. `import.meta` is enabled automatically.

In SDK 55 monorepos, `expo.experiments.autolinkingModuleResolution` defaults to enabled. `EXPO_USE_FAST_RESOLVER`, the alternate resolver implementation, and `experiments.reactCanary` are removed.

## Migrate removed configuration and APIs

- The top-level app-config `notification` field makes prebuild fail; use the `expo-notifications` config plugin.
- `edgeToEdgeEnabled` is removed.
- `expo-router/server` uses standard `Request` and `Response`.
- Headless-tab `reset` is renamed to `resetOnFocus`.
- `expo-video` replaces `allowsFullscreen` with `fullscreenOptions.enable`.
- Clipboard listener events no longer include `content`; call `getStringAsync()`.
- Deprecated cellular carrier constants are removed, and affected iOS methods return `null`.

## Apply deprecation migrations

Event APIs return a subscription; retain it and call `subscription.remove()` instead of a module-level `removeSubscription` function. Replace `expo-video-thumbnails` with `expo-video.generateThumbnailsAsync`. Replace video-track `bitrate` with `averageBitrate` and `peakBitrate`.

Mandatory Android edge-to-edge makes most `expo-navigation-bar` methods and several `expo-status-bar` props and setters deprecated no-ops. Their old app-config fields are also deprecated; use each package's config plugin.

`@expo/vector-icons` is deprecated in SDK 56, and `expo` no longer installs it transitively. Install it explicitly as a temporary compatibility measure, or migrate to per-set `@react-native-vector-icons/*` packages:

```sh
npx @react-native-vector-icons/codemod
```

## Know Expo Go boundaries

Android push notifications error in Expo Go as of SDK 55 and require a development build. `expo-av` has been removed from Expo Go and no longer receives patches. Use a development client when validating either behavior.
