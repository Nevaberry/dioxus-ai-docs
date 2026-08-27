# Runtime Upgrades and Tooling

Use the application's installed SDK to select values below. The first runtime changes are from batch `55`; later defaults and floors are from batch `56`.

## Runtime, architecture, and native floors

| Concern | SDK 55 | SDK 56 |
|---|---|---|
| React Native | 0.83 | 0.85 |
| React | 19.2 | 19.2 |
| Architecture | Legacy Architecture removed; `newArchEnabled` removed | New Architecture remains mandatory |
| Hermes v1 | Opt-in source build | Default runtime |
| Xcode | Xcode 26; EAS Build defaults to 26.2 | Xcode 26.4 |
| Apple deployment targets | iOS 15.1 | iOS/tvOS 16.4 and macOS 13.4 |
| New-template TypeScript | — | 6.0.3 |

For SDK 55, the supported Node.js ranges are `^20.19.4`, `^22.13.0`, `^24.3.0`, and `^25.0.0`.

When moving to SDK 56, update custom Expo module podspecs to target iOS 16.4. Check the exact SDK before diagnosing compilation failures: an SDK 55 project still has the earlier iOS floor, while an SDK 56 native build needs the later toolchain and targets.

## Package majors and the default template

Expo SDK packages share the SDK major beginning with SDK 55. For example, an SDK 55 application uses `expo-camera@^55.0.0` rather than a package version on an unrelated major.

The SDK 55 default template uses Native Tabs and places routes in `/src/app` rather than `/app`. Create that template explicitly with:

```sh
npx create-expo-app@latest --template default@sdk-55
```

## Hermes v1

### SDK 55 opt-in

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

For npm, pnpm, or Bun:

```json
{
  "overrides": {
    "hermes-compiler": "250829098.0.4"
  }
}
```

Use `resolutions` instead of `overrides` with Yarn. The source build substantially increases native build time and is not recommended for Android monorepos at this stage.

### SDK 56 default and rollback

Hermes v1 is the default in SDK 56. To opt out intentionally, configure `useHermesV1: false` through `expo-build-properties`.

Merely importing `react-native-reanimated` with Hermes v1 can increase memory use by 25–30%. Enable worklets bundle mode as the documented workaround.

## Dynamic app config and plugin loading

SDK 55 experimentally accepts `.mjs`, `.cjs`, `.cts`, and `.mts` dynamic config. `app.config.ts` is transpiled with the project's own TypeScript.

In SDK 56, config plugins use the same loader as app config. A plugin list can therefore reference local `.ts` files and `.mjs` or `.cjs` plugins. Every Expo package config plugin exports typed options for TypeScript config from `expo-<name>/plugin`.

## CLI behavior

- `expo start --localhost` accepts only localhost connections.
- The experimental native LogBox requires `EXPO_UNSTABLE_LOG_BOX=1` and a rebuild.
- `eas update` requires `--environment <name>`, including in CI.
- Metro can serve development bundles over HTTPS when TLS is configured in SDK 56.

## Metro discovery and resolution

SDK 56 replaces `watchFolders` and Watchman defaults with an on-demand filesystem and native Node.js watcher.

- Disable on-demand discovery with `experiment.onDemandFilesystem: false` in app config.
- Restore Watchman with `resolver.useWatchman` in Metro config.
- `import.meta` is enabled automatically.

In SDK 55 monorepos, `expo.experiments.autolinkingModuleResolution` defaults on. `EXPO_USE_FAST_RESOLVER`, the alternate resolver implementation, and `experiments.reactCanary` are removed; do not carry those switches into updated configuration.

## Project and module scaffolding

`create-expo-module` supports non-interactive scaffolding. SDK 56 adds the `addPlatformSupport` subcommand and lets callers select platforms and features.

Local modules no longer receive an `index.ts` barrel by default. Pass `--barrel` when a barrel is desired.

New application scaffolds include agent-guidance files `AGENTS.md`, `CLAUDE.md`, and `.claude/settings.json`.
