# Native Modules and Integration

## Modules Core capabilities

SDK 55 moves Expo Modules Core to Swift 6 language mode. `ArrayBuffer` values can cross JavaScript/native boundaries, and module classes can expose `StaticFunction` and `StaticAsyncFunction` without creating module instances.

## Inline modules

SDK 56 allows native Expo modules to live directly beside application JavaScript and TypeScript. Prebuild picks up their Swift or Kotlin source, adds it to the native projects, and autolinks the module.

Use an inline module for native implementation owned by one application. Use a normal Expo module when the native implementation should be packaged and reused.

## Generated TypeScript interfaces

The `expo-type-information` CLI can watch Swift source or generate TypeScript interfaces from it.

- `module-interface` emits type declarations, a module, view declarations, and re-export files.
- `inline-modules-interface` writes separate generated and stable interface files.
- `short-module-interface` targets one module.

Keep generated and stable files separate when using the inline workflow so regeneration does not replace the application's stable entry point.

## Precompiled native packaging

Complex Expo modules use prebuilt iOS XCFrameworks by default in SDK 56 for both local and EAS builds. Set:

```sh
EXPO_USE_PRECOMPILED_MODULES=0
```

in the environment that actually performs the build when source compilation is required. Configure EAS separately from the local shell.

EAS also prebuilds major community libraries and exposes per-step `xcodebuild` and Gradle timings for build diagnosis.

Android C++ codegen can experimentally use precompiled headers through the `expo-build-properties` plugin:

```json
{
  "expo": {
    "plugins": [["expo-build-properties", {
      "android": {
        "usePrecompiledHeaders": true
      }
    }]]
  }
}
```

## Module scaffolding

`create-expo-module` supports non-interactive scaffolding from SDK 55. In SDK 56 it adds `addPlatformSupport` and selectable platforms and features.

Local modules do not receive an `index.ts` barrel by default. Pass `--barrel` to generate one.

## Brownfield delivery modes

The `expo-brownfield` package has two primary delivery models:

- Integrated mode keeps React Native inside the native project.
- Isolated mode produces an AAR or XCFramework that a host can consume without Node.js.

The package includes a config plugin, an artifact-building CLI, and bidirectional native/Expo messaging APIs.

### Multiple isolated iOS applications

SDK 56 can experimentally embed several isolated applications in one iOS host. Set `multipleFrameworks: true` in the `expo-brownfield` iOS plugin config. Generated frameworks receive distinct Swift names and Objective-C symbol prefixes.

Host applications can register Turbo Module classes with the `turboModuleClasses` dictionary passed to `ReactNativeHostManager.initialize`.

Brownfield iOS builds use prebuilt React Native frameworks by default. Set the plugin's `buildReactNativeFromSource` option when the brownfield artifacts require a React Native source build.

## Expo MCP module integration

Beginning in SDK 55, Expo modules can expose CLI plugins and Shift+M commands that install automatically into the Expo MCP server. The server can query EAS services. If an App Store Connect key is linked, it can also query TestFlight crash reports and feedback. Expo also maintains reusable upgrade-workflow skills.

## Connector-directory setup

As of `2026-08-13`, the hosted Expo MCP server can be added from the connector directory and authorized once with an Expo account. The resulting connection is available across web, desktop, mobile, and coding clients. Existing CLI and URL configuration continue to work.

In a Team workspace, a `Request` action in place of `Connect` starts administrator approval; it does not indicate that the connection failed.
