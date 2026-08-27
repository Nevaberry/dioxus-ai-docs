---
name: expo-knowledge-patch
description: Expo
version: "SDK 56"
license: MIT
metadata:
  author: Nevaberry
---


# Expo Knowledge Patch

Use this skill when upgrading, configuring, or implementing an Expo application whose installed SDK falls within this patch's frontmatter compatibility. Inspect the project's `expo` version, app config, native projects, and EAS configuration before applying version-dependent advice.

## Index

| Reference | Topics |
|---|---|
| [Runtime upgrades and tooling](references/runtime-upgrades-and-tooling.md) | React Native and React pairing, platform floors, Hermes, templates, CLI, config loading, Metro, resolvers, removals and deprecations |
| [Router, UI, and web](references/router-ui-and-web.md) | Expo Router migrations and native APIs, Expo UI, web rendering, status and navigation bars, blur, and DOM components |
| [Native modules and integration](references/native-modules-and-integration.md) | Modules Core, precompiled and inline modules, generated interfaces, brownfield hosts, scaffolding, and Expo MCP |
| [Data, files, and networking](references/data-files-and-networking.md) | File transfers and watching, SQLite, object APIs, global fetch, server adapters, and crypto |
| [Media, devices, and platform services](references/media-devices-and-platform-services.md) | Audio, video, image, camera, browser, location, maps, haptics, assets, widgets, sharing, and development launcher |
| [EAS updates and distribution](references/eas-updates-and-distribution.md) | Hermes bytecode diffs, EAS Build behavior, Convex integration, and Expo Go distribution |

## Establish the installed target

Read `package.json` before changing configuration. Then inspect `app.json` or the active dynamic config, `metro.config.*`, `eas.json`, package-manager overrides, and generated native projects. Do not apply a later default to an earlier SDK merely because both appear in this patch.

## Breaking changes to handle first

### Treat the New Architecture as mandatory

Legacy Architecture support is gone. Remove `newArchEnabled`; it is no longer a meaningful compatibility switch. Confirm native dependencies support the React Native version paired with the installed Expo SDK.

Native toolchain floors also moved. Check Xcode and deployment targets before diagnosing native compile errors, and update custom Expo module podspecs when the application target rises.

### Configure Hermes by SDK

Hermes v1 changes from an opt-in source build to the default runtime across the applicable SDKs. For the earlier opt-in, both source-build settings and the matching compiler override are required:

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

For npm, pnpm, or Bun, place `hermes-compiler` in `overrides`; use `resolutions` with Yarn. For the later default, set `useHermesV1: false` only when an explicit rollback is needed. Read [Runtime upgrades and tooling](references/runtime-upgrades-and-tooling.md) for the required compiler value and the documented Reanimated memory workaround.

### Migrate Router imports

Expo Router no longer supplies React Navigation packages as an implicit application-facing dependency. Replace direct `@react-navigation/*` imports where possible:

```sh
npx expo-codemod sdk-56-expo-router-react-navigation-replace <source-directory>
```

Audit any remaining direct imports and install intentional dependencies explicitly.

### Await file moves and copies

`File` and `Directory` `copy()` and `move()` return promises. Await them, or deliberately choose `copySync()` and `moveSync()`:

```ts
await source.move(destination);
source.moveSync(destination);
```

### Remove rejected app config

Do not retain the top-level `notification` app-config field; prebuild fails when it is present. Configure notifications through the `expo-notifications` config plugin. Remove `edgeToEdgeEnabled`, and move navigation-bar and status-bar build settings into their package config plugins.

### Replace removed and renamed APIs

| Old use | Replacement or behavior |
|---|---|
| Module-level `removeSubscription` | Keep the returned subscription and call `subscription.remove()` |
| `expo-video-thumbnails` | `expo-video.generateThumbnailsAsync` |
| Video track `bitrate` | `averageBitrate` and `peakBitrate` |
| `allowsFullscreen` | `fullscreenOptions.enable` |
| Headless-tab `reset` | `resetOnFocus` |
| `experimentalBlurMethod` | `blurMethod` |
| Clipboard-listener `content` | Read current text with `getStringAsync()` |
| `@expo/vector-icons` through Expo | Install it explicitly or migrate to per-set `@react-native-vector-icons/*` packages |

Mandatory Android edge-to-edge makes many imperative `expo-navigation-bar` methods and several `expo-status-bar` props and setters deprecated no-ops. Deprecated cellular carrier constants are removed; affected iOS methods return `null`.

### Do not rely on Expo Go for every native feature

Android push notifications error in Expo Go and require a development build. `expo-av` is absent from Expo Go and no longer patched. The later Expo Go build also has platform-specific distribution constraints; see [EAS updates and distribution](references/eas-updates-and-distribution.md).

## High-value current APIs

### Use the universal Expo UI surface

Expo UI provides common `Host`, layout, text, input, control, and sheet components across Android and iOS. Native state and synchronous worklet callbacks cover interactions that should not round-trip asynchronously through ordinary React state. Community-component compatibility entry points live under `@expo/ui/community/*`; compare props before treating them as drop-in replacements.

### Choose the right native-module delivery model

Use inline modules when native Swift or Kotlin belongs beside one application. Use a regular Expo module for a reusable package. Use `expo-brownfield` integrated mode when React Native lives in the host project, or isolated AAR/XCFramework artifacts when the host must consume it without Node.js.

Complex modules can arrive as precompiled XCFrameworks. Set `EXPO_USE_PRECOMPILED_MODULES=0` in the actual local or EAS environment when a source build is required; do not assume a local shell setting reaches EAS.

### Use cancellable file transfers

For progress and cancellation, use `File.downloadFileAsync()` with an `AbortSignal`, or create resumable upload/download tasks. Use `File.upload()` for a simple upload. Experimental file and directory watchers are available when the lifecycle can tolerate a preview API.

### Account for the global fetch implementation

`expo/fetch` supplies `globalThis.fetch`; manual imports are unnecessary. Set `EXPO_PUBLIC_USE_RN_FETCH=1` only to restore React Native fetch intentionally. Android response decompression and modern `AbortSignal` composition are described in [Data, files, and networking](references/data-files-and-networking.md).

### Configure update diffs explicitly when reproducibility matters

Hermes bytecode binary diffs change from opt-in to default. Pin `updates.enableBsdiffPatchSupport` to the desired boolean instead of relying on an SDK-dependent default when rollout behavior must remain stable.

## Defaults worth checking explicitly

### Metro file discovery

The on-demand filesystem and native Node.js watcher replace `watchFolders` and Watchman as defaults. Set `experiment.onDemandFilesystem: false` in app config to disable the former, or set `resolver.useWatchman` in Metro config to restore Watchman. `import.meta` is enabled automatically.

### DOM components

DOM components use `@expo/dom-webview` by default and no longer require `react-native-webview`. Opt out when the application must keep the previous WebView implementation.

### Precompiled native modules

Complex Expo modules use prebuilt iOS XCFrameworks by default for local and EAS builds. Source builds require `EXPO_USE_PRECOMPILED_MODULES=0` in the corresponding build environment.

## Router and server-rendering checks

- On native stacks, verify platform support before using experimental toolbars, split views, form-sheet footers, predictive back, or Stack v5.
- `expo-router/server` uses standard `Request` and `Response` objects.
- `createStaticLoader` receives route params without a request.
- `createServerLoader` always receives a request and fails during static generation.
- Use `generateMetadata` for initial web metadata; use `<Head>` for post-hydration updates.
- Export `SuspenseFallback` from a `_layout` route to replace the default Suspense loading UI.

## Safe upgrade workflow

1. Confirm the installed Expo SDK and package-manager lockfile.
2. Align React Native, React, Node.js, Xcode, deployment targets, and Expo package majors.
3. Remove rejected config and migrate renamed or asynchronous APIs.
4. Run the Router and vector-icons codemods when their old imports are present.
5. Regenerate native projects or apply the equivalent native configuration deliberately.
6. Build a development client; do not use Expo Go as proof that native integrations work.
7. Exercise updates, deep links, background media, file transfers, and server rendering on every affected platform.
8. Review the linked topic references before changing preview APIs or opting out of new defaults.
