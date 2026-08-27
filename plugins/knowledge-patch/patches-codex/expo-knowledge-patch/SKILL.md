---
name: expo-knowledge-patch
description: Expo
version: "SDK 56"
license: MIT
metadata:
  author: Nevaberry
---


# Expo Knowledge Patch

Use this skill when upgrading, configuring, or implementing an Expo application. Confirm the installed `expo` version and inspect app config, Metro config, EAS config, package-manager overrides, and generated native projects before applying version-dependent guidance.

## Reference index

| Reference | Topics |
|---|---|
| [Runtime upgrades and tooling](references/runtime-upgrades-and-tooling.md) | React Native and React pairing, platform floors, Hermes, templates, CLI, config loading, Metro, resolvers, and scaffolding |
| [Router, UI, and web](references/router-ui-and-web.md) | Router migrations and native APIs, Expo UI, server rendering, bars, blur, DOM components, and icons |
| [Native modules and integration](references/native-modules-and-integration.md) | Modules Core, precompiled and inline modules, generated interfaces, brownfield hosts, and Expo MCP |
| [Data, files, and networking](references/data-files-and-networking.md) | File transfers and watching, SQLite, object APIs, global fetch, server adapters, and crypto |
| [Media, devices, and platform services](references/media-devices-and-platform-services.md) | Audio, video, image, camera, browser, sharing, widgets, location, maps, haptics, assets, and development launcher |
| [EAS updates and distribution](references/eas-updates-and-distribution.md) | Hermes bytecode diffs, EAS commands and integrations, build behavior, Expo Go, and development builds |

## Handle breaking changes first

### Treat the New Architecture as required

Legacy Architecture support is removed. Delete `newArchEnabled`; it is no longer a compatibility switch. Verify that native dependencies support the React Native version paired with the installed Expo SDK.

Native toolchain floors also changed. Check Xcode and deployment targets before diagnosing native compile failures. Custom Expo module podspecs must follow the application's minimum iOS target.

### Configure Hermes for the installed SDK

Hermes v1 changes from an opt-in source build to the default runtime. For the earlier opt-in, enable both source compilation and Hermes v1:

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

For npm, pnpm, or Bun, put the matching `hermes-compiler` value in `overrides`; Yarn uses `resolutions`. For the later default, use `useHermesV1: false` only for an intentional rollback. Read [Runtime upgrades and tooling](references/runtime-upgrades-and-tooling.md) for the exact compiler version and the Reanimated memory workaround.

### Migrate Router imports

Expo Router no longer provides React Navigation packages as implicit application dependencies. Replace direct imports where possible:

```sh
npx expo-codemod sdk-56-expo-router-react-navigation-replace <source-directory>
```

Audit remaining `@react-navigation/*` imports and install only dependencies the application intentionally uses.

### Await file copies and moves

`File` and `Directory` `copy()` and `move()` return promises. Await them or deliberately choose their synchronous variants:

```ts
await source.copy(destination);
await source.move(destination);
source.copySync(destination);
source.moveSync(destination);
```

### Remove rejected and obsolete app config

- Remove the top-level `notification` field; prebuild fails when it is present. Configure notifications with the `expo-notifications` config plugin.
- Remove `edgeToEdgeEnabled`.
- Move status-bar and navigation-bar build settings to their package config plugins.

### Replace removed and renamed APIs

| Old use | Replacement or current behavior |
|---|---|
| Module-level `removeSubscription` | Keep the returned subscription and call `subscription.remove()` |
| `expo-video-thumbnails` | `expo-video.generateThumbnailsAsync` |
| Video track `bitrate` | `averageBitrate` and `peakBitrate` |
| `allowsFullscreen` | `fullscreenOptions.enable` |
| Headless-tab `reset` | `resetOnFocus` |
| `experimentalBlurMethod` | `blurMethod` |
| Clipboard-listener `content` | Read the current text with `getStringAsync()` |
| `@expo/vector-icons` supplied transitively | Install it explicitly or migrate to per-set `@react-native-vector-icons/*` packages |

Mandatory Android edge-to-edge makes most imperative `expo-navigation-bar` methods and several `expo-status-bar` props and setters deprecated no-ops. Deprecated cellular carrier constants are removed; affected iOS methods return `null`.

### Do not use Expo Go as proof of native compatibility

Android push notifications require a development build and error in Expo Go. `expo-av` is absent from Expo Go and no longer patched. Expo Go distribution also differs by platform; see [EAS updates and distribution](references/eas-updates-and-distribution.md).

## High-value current APIs

### Use the universal Expo UI surface

Expo UI provides common `Host`, layout, text, input, control, and sheet components across Android and iOS. Use `useNativeState` to bridge to native observable state and `WorkletCallback` for synchronous worklet interactions that should not round-trip through ordinary asynchronous React state.

Community-component compatibility entry points live under `@expo/ui/community/*`. Compare props during migration because some props differ or remain unsupported.

### Choose a native-module delivery model

- Keep app-specific Swift or Kotlin beside application code with an inline module.
- Use a regular Expo module for a reusable package.
- Use `expo-brownfield` integrated mode when React Native lives in the native host.
- Use isolated AAR or XCFramework artifacts when a host must consume the app without Node.js.

Complex Expo modules arrive as prebuilt iOS XCFrameworks by default. Set `EXPO_USE_PRECOMPILED_MODULES=0` in the actual local or EAS environment when a source build is required; a variable set only in a local shell does not configure an EAS worker.

### Use cancellable file transfers when needed

Use `File.downloadFileAsync()` with an `AbortSignal` for progress and cancellation. For resumable transfers, create upload or download tasks. Use `File.upload()` for a simple upload. Experimental `File.watch()` and `Directory.watch()` subscriptions are available when preview API risk is acceptable.

### Account for the global fetch implementation

`expo/fetch` supplies `globalThis.fetch`; manual imports are unnecessary. Set `EXPO_PUBLIC_USE_RN_FETCH=1` only to restore React Native fetch intentionally. Android decompression formats and `AbortSignal` composition are detailed in [Data, files, and networking](references/data-files-and-networking.md).

### Pin update-diff behavior when rollout consistency matters

Hermes bytecode binary diffs change from opt-in to default. Set `updates.enableBsdiffPatchSupport` explicitly to the desired boolean when reproducible update behavior matters instead of inheriting an SDK-dependent default.

## Defaults to check explicitly

### Metro file discovery

The on-demand filesystem and native Node.js watcher replace `watchFolders` and Watchman as defaults. Set `experiment.onDemandFilesystem: false` in app config to disable on-demand discovery, or set `resolver.useWatchman` in Metro config to restore Watchman. `import.meta` is enabled automatically.

### DOM components

DOM components use `@expo/dom-webview` by default and no longer require `react-native-webview`. Opt out when the application must retain the previous WebView implementation.

### Precompiled native modules

Prebuilt iOS XCFrameworks apply to local and EAS builds. Put `EXPO_USE_PRECOMPILED_MODULES=0` in the corresponding build environment when source compilation is necessary.

### Autolinking and removed resolver switches

Monorepos default to autolinking-based module resolution. Do not restore removed `EXPO_USE_FAST_RESOLVER`, alternate-resolver, or React-canary experiments.

## Router and server-rendering checks

- Verify platform support before using experimental native toolbars, Stack v5, split views, form-sheet footers, or predictive back.
- `expo-router/server` uses standard `Request` and `Response` objects.
- `createStaticLoader` receives route params without a request.
- `createServerLoader` always receives a request and errors during static generation.
- Use `generateMetadata` for initial web metadata and `<Head>` for post-hydration updates.
- Export `SuspenseFallback` from a `_layout` route to replace the default Suspense loading UI.

## Safe upgrade workflow

1. Read `package.json` and the lockfile to identify the installed Expo SDK and aligned package majors.
2. Align React Native, React, Node.js, Xcode, deployment targets, and the native module ecosystem.
3. Remove rejected config and migrate renamed, removed, or asynchronous APIs.
4. Run the Router and vector-icons codemods when their old imports are present.
5. Regenerate native projects or apply equivalent native configuration deliberately.
6. Build a development client; do not treat Expo Go as sufficient native-integration coverage.
7. Exercise updates, deep links, background media, file transfers, and server rendering on every affected platform.
8. Consult the topic references before opting out of defaults or adopting preview APIs.
