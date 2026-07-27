# Native Modules and Integration

## Use current Modules Core capabilities

Expo Modules Core uses Swift 6 language mode in SDK 55. It can pass `ArrayBuffer` values across JavaScript/native boundaries, and module classes can expose `StaticFunction` and `StaticAsyncFunction` without first creating instances.

## Choose precompiled or source modules

Complex Expo modules ship as prebuilt iOS XCFrameworks by default in SDK 56 for both local and EAS builds. To build them from source, set the following in the environment that performs the build:

```sh
EXPO_USE_PRECOMPILED_MODULES=0
```

EAS also prebuilds major community libraries and reports per-step `xcodebuild` and Gradle timings. For Android C++ codegen, experimental precompiled-header support is available through `expo-build-properties`:

```json
{
  "expo": {
    "plugins": [["expo-build-properties", {
      "android": { "usePrecompiledHeaders": true }
    }]]
  }
}
```

## Create inline native modules

Native Expo modules can live beside application JavaScript and TypeScript in SDK 56. Prebuild adds their Swift or Kotlin sources to the native projects and autolinks them.

## Generate TypeScript interfaces from Swift

The `expo-type-information` CLI can watch Swift sources or generate interfaces:

- `module-interface` emits type, module, view, and re-export files.
- `inline-modules-interface` emits separate generated and stable files.
- `short-module-interface` targets one module.

Generated files should remain distinguishable from the stable files intended for application edits.

## Scaffold modules and platform support

`create-expo-module` supports non-interactive scaffolding in SDK 55. In SDK 56 it adds an `addPlatformSupport` subcommand and selectable platforms and features.

Local modules no longer receive an `index.ts` barrel by default. Pass `--barrel` when callers need that entry point. New application scaffolds also include `AGENTS.md`, a companion agent-instruction file, and a hidden agent-settings file.

## Select a brownfield mode

The SDK 55 `expo-brownfield` package supports two delivery modes:

- Integrated mode keeps React Native inside the native project.
- Isolated mode builds an AAR or XCFramework that a native host can consume without Node.js.

The package includes a config plugin, an artifact-building CLI, and bidirectional native/Expo messaging APIs.

## Embed multiple isolated applications

In SDK 56, one iOS host can experimentally embed multiple isolated apps by setting `multipleFrameworks: true` in the `expo-brownfield` iOS plugin configuration. Generated frameworks receive distinct Swift names and Objective-C symbol prefixes.

Host applications can register Turbo Module classes through the `turboModuleClasses` dictionary passed to `ReactNativeHostManager.initialize`.

Brownfield iOS builds use prebuilt React Native frameworks by default. Set the plugin's `buildReactNativeFromSource` option when the host integration requires source builds.

## Extend Expo development tooling

Expo modules in SDK 55 can expose CLI plugins and commands from the Shift+M menu for automatic installation into the Expo MCP server. That server can query EAS services and, when an App Store Connect key is linked, TestFlight crashes and feedback. Expo's maintained agent-skill collection also includes upgrade workflows.
