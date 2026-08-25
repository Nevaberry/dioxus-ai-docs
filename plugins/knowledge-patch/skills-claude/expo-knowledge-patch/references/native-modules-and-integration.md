# Native Modules and Integration

## Expo Modules Core

Batch `55` moves Modules Core to Swift 6 language mode. Modules can pass `ArrayBuffer` values across JavaScript/native boundaries, and module classes can expose `StaticFunction` and `StaticAsyncFunction` without creating instances.

## Native module delivery models

### Brownfield integrated and isolated modes

The `expo-brownfield` package offers two integration styles:

- Integrated mode keeps React Native inside the native host project.
- Isolated mode builds an AAR or XCFramework that the host can consume without Node.js.

The package includes a config plugin, an artifact-building CLI, and bidirectional native/Expo messaging APIs.

### Precompiled packages in SDK 56

Batch `56` makes complex Expo modules available as prebuilt iOS XCFrameworks in local and EAS builds. Set `EXPO_USE_PRECOMPILED_MODULES=0` in the relevant local or EAS environment to build them from source. A variable set only in a local shell does not change an EAS environment.

EAS also prebuilds major community libraries and reports per-step `xcodebuild` and Gradle timings.

Android C++ codegen can experimentally use precompiled headers through `expo-build-properties`:

```json
{
  "expo": {
    "plugins": [["expo-build-properties", {
      "android": { "usePrecompiledHeaders": true }
    }]]
  }
}
```

### Inline application modules

Native Expo modules can live beside application JavaScript and TypeScript. Prebuild adds their Swift or Kotlin sources and autolinks them. Use inline modules for application-specific native code; use a separately packaged module for reusable code.

`expo-type-information` can watch or generate Swift-derived TypeScript interfaces:

- `module-interface` emits types, module, view, and re-export files.
- `inline-modules-interface` emits separate generated and stable files.
- `short-module-interface` targets one module.

## Brownfield multi-app hosts

One iOS host can experimentally embed multiple isolated applications by setting `multipleFrameworks: true` in the `expo-brownfield` iOS plugin config. Generated frameworks receive distinct Swift names and Objective-C symbol prefixes.

Host applications can register Turbo Module classes with the `turboModuleClasses` dictionary passed to `ReactNativeHostManager.initialize`.

Brownfield iOS builds use prebuilt React Native frameworks by default. Set the plugin's `buildReactNativeFromSource` option when the integration requires a source build.

## Project and module scaffolding

`create-expo-module` supports non-interactive scaffolding and adds an `addPlatformSupport` subcommand with selectable platforms and features. Local modules do not receive an `index.ts` barrel by default; pass `--barrel` when a barrel is desired.

## Expo MCP

### Module commands and EAS access

Expo modules can expose CLI plugins and commands from the Shift+M menu for automatic installation into the Expo MCP server. The server can query EAS services and, when an App Store Connect key is linked, retrieve TestFlight crashes and feedback. Expo also maintains agent skills with upgrade workflows.

### Connector-directory setup

Batch `2026-08-13` adds the hosted Expo MCP server to the connector directory. Authorize it once with an Expo account to make the connection available across web, desktop, mobile, and coding clients. Existing manual CLI or URL configuration remains valid.

In Team workspaces, a `Request` action instead of `Connect` indicates an administrator-approval workflow; it does not mean the connection failed.
