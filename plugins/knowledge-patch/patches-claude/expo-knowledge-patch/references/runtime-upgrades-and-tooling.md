# Runtime Upgrades and Tooling

## Runtime and architecture

### SDK 55 runtime floor

Batch `55` pairs React Native 0.83 with React 19.2. Legacy Architecture support and the `newArchEnabled` app-config option are removed.

Native iOS builds require Xcode 26, while EAS Build defaults to Xcode 26.2. The iOS minimum remains 15.1. Supported Node.js ranges are:

- `^20.19.4`
- `^22.13.0`
- `^24.3.0`
- `^25.0.0`

Expo SDK packages share the SDK major, so align packages to versions such as `expo-camera@^55.0.0` rather than carrying an older independent major.

The default template uses Native Tabs and places routes in `/src/app` rather than `/app`. Create that template explicitly with:

```sh
npx create-expo-app@latest --template default@sdk-55
```

### SDK 56 runtime floor

Batch `56` pairs React Native 0.85 with React 19.2 and makes Hermes v1 the default. Native builds require Xcode 26.4. Minimum targets are iOS/tvOS 16.4 and macOS 13.4; custom Expo module podspecs must also target iOS 16.4.

New templates use TypeScript 6.0.3. Metro can serve development bundles over HTTPS when TLS is configured.

## Hermes v1

### Opt in on SDK 55

Hermes v1 requires a React Native source build and a matching compiler override:

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

For npm, pnpm, or Bun, use:

```json
{
  "overrides": {
    "hermes-compiler": "250829098.0.4"
  }
}
```

Use `resolutions` with Yarn. Expect substantially longer native builds, and avoid this opt-in for Android monorepos unless its limitations have been evaluated.

### Default and rollback on SDK 56

Hermes v1 is enabled by default. To opt out, set `useHermesV1: false` in `expo-build-properties`.

Merely importing `react-native-reanimated` under Hermes v1 can increase memory use by 25–30%. Enable worklets bundle mode as the documented workaround.

## CLI and configuration loading

### Dynamic config and local development on SDK 55

Dynamic app config experimentally accepts `.mjs`, `.cjs`, `.cts`, and `.mts`. `app.config.ts` is transpiled with the project's own TypeScript version.

`expo start --localhost` accepts only localhost connections. The experimental native LogBox requires `EXPO_UNSTABLE_LOG_BOX=1` and a rebuilt native application. `eas update` requires `--environment <name>`, including in CI.

### Config plugins and Metro on SDK 56

Every Expo package config plugin exports typed options from `expo-<name>/plugin` for use in `app.config.ts`. Config plugins now use the same loader as app config, so plugin lists can reference local `.ts` files and `.mjs` or `.cjs` plugins.

The on-demand filesystem and native Node.js watcher replace `watchFolders` and Watchman as defaults. To opt out or restore the previous watcher:

```js
// app config
export default { expo: { experiment: { onDemandFilesystem: false } } };

// metro.config.js
config.resolver.useWatchman = true;
```

`import.meta` is enabled automatically.

## Scaffolding and icon packages

`create-expo-module` supports non-interactive scaffolding. It also provides `addPlatformSupport` with selectable platforms and features. Local modules no longer receive an `index.ts` barrel by default; pass `--barrel` to create one.

New application scaffolds include `AGENTS.md` plus additional project-level agent guidance and settings files.

`@expo/vector-icons` is deprecated in favor of per-set `@react-native-vector-icons/*` packages and is no longer installed transitively by `expo`. Either add `@expo/vector-icons` explicitly or migrate:

```sh
npx @react-native-vector-icons/codemod
```

## Removed configuration and compatibility switches

- Remove `newArchEnabled`; the Legacy Architecture is unavailable.
- Remove `edgeToEdgeEnabled`; Android edge-to-edge is mandatory.
- Remove `experiments.reactCanary`.
- Do not use `EXPO_USE_FAST_RESOLVER` or the removed alternate resolver implementation.
- In monorepos, `expo.experiments.autolinkingModuleResolution` defaults on.
- Remove the top-level `notification` app-config field because prebuild rejects it; configure notifications with the `expo-notifications` config plugin.

## General API deprecations

Event listeners should keep the returned subscription and invoke `subscription.remove()`; module-level `removeSubscription` is deprecated.

Android edge-to-edge makes most imperative `expo-navigation-bar` methods and several `expo-status-bar` props and setters deprecated no-ops. Their old app-config fields are deprecated; use each package's config plugin.

Deprecated cellular carrier constants are removed, and the affected iOS methods return `null`.
