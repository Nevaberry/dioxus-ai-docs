---
name: flutter-knowledge-patch
description: Flutter
version: 3.44.0
license: MIT
metadata:
  author: Nevaberry
---


# Flutter Knowledge Patch

Use this skill before changing Flutter or Dart applications, packages, plug-ins,
embedders, build automation, or development tooling. Read the reference matching
the work before selecting an API, flag, generated file, or migration path.

## Reference index

| Reference | Topics |
| --- | --- |
| [accessibility-input-and-testing.md](references/accessibility-input-and-testing.md) | Semantics, accessibility preferences, selection, text input, gestures, and tests |
| [android.md](references/android.md) | Android SDK and Gradle requirements, rendering, platform views, system UI, and embedding |
| [apple-platforms.md](references/apple-platforms.md) | UIScene, Swift Package Manager, Xcode, Cupertino integration, signing, and Apple rendering |
| [dart-language.md](references/dart-language.md) | Dot shorthands, null-aware collection elements, flow analysis, constructors, and language direction |
| [dart-tooling-and-packages.md](references/dart-tooling-and-packages.md) | Formatter, analyzer plug-ins, Pub, workspaces, native compilation, and publishing |
| [desktop-and-embedding.md](references/desktop-and-embedding.md) | Thread merging, add-to-app sizing, multi-window APIs, displays, input, and architectures |
| [migrations-and-breaking-changes.md](references/migrations-and-breaking-changes.md) | Cross-cutting removals, deprecations, callback changes, and required source migrations |
| [navigation-layout-and-animation.md](references/navigation-layout-and-animation.md) | Routes, transitions, overlays, sheets, slivers, scrolling, layout, and animation |
| [tooling-build-assets-and-plugins.md](references/tooling-build-assets-and-plugins.md) | CLI contracts, Widget Preview, builds, assets, plug-in metadata, MCP, and release artifacts |
| [web-rendering-and-graphics.md](references/web-rendering-and-graphics.md) | Web hot reload, Wasm, renderers, Impeller, shaders, images, filters, and web configuration |
| [widgets-and-theming.md](references/widgets-and-theming.md) | Material and Cupertino controls, menus, forms, themes, tooltips, and component styling |

## Working method

1. Inspect `pubspec.yaml`, its SDK constraints, platform projects, and CI commands.
2. Read every topic reference implicated by the change.
3. Apply required migrations before layering on new behavior.
4. Prefer current properties and command forms over removed compatibility paths.
5. Test each affected renderer, operating system, input mode, and accessibility
   preference because defaults differ across targets.

## Breaking changes and deprecations

### Android projects

- Use declarative Flutter Gradle plug-in application; the imperative script path
  and Android v1 embedding APIs are removed.
- Treat API 24, Java 17, Gradle 8.7, and AGP 8.6 as the older supported floor in
  the stream, then verify the exact combination required by the selected Flutter
  SDK. AGP 9 requires removing the separately applied Kotlin plug-in.
- Handle edge-to-edge system bars, resizing, orientation changes, display corner
  radii, and large-screen behavior explicitly.
- Do not rely on an Android Impeller opt-out or on separate UI and platform
  threads. Check HCPP requirements before enabling platform-view compositing.

### Apple projects

- Migrate applications and lifecycle-aware plug-ins to `UIScene`; do not assign
  the read-only `sceneLifeCycleDelegate`.
- Expect Swift Package Manager for ordinary iOS and macOS applications, but audit
  customized targets, schemes, flavors, and package products after migration.
  Add-to-app hosts need a different dependency path.
- Use supported Xcode tooling and regenerate platform configuration after raising
  a plug-in's minimum OS.
- Do not depend on the removed iOS Skia opt-out or SkSL warm-up artifacts.

### Dart and package configuration

- After raising a package language constraint, run `dart pub get` before
  formatting. Use `dart fix`; `dart format --fix` is removed.
- Declare every imported package directly. The explicit-dependency check cannot
  be disabled.
- Replace legacy browser libraries with `dart:js_interop` and `package:web`,
  especially before enabling Wasm.
- Import generated localization code from its real output; synthetic
  `package:flutter_gen` imports no longer work.
- Account for Pub enforcing the root Flutter SDK upper bound after the package
  opts into the applicable language behavior.

### Framework source migrations

- Replace deprecated `...Theme` value types with their `...ThemeData` forms and
  move renamed component properties to their replacements.
- Put shared radio value and change handling in `RadioGroup`.
- Give `DropdownMenu` a non-nullable generic type, use `initialValue` on
  `DropdownButtonFormField`, and express `DropdownButton.enabled` separately.
- Replace `findChildIndexCallback`, `onReorder`, `maintainHintHeight`,
  `Tooltip.height`, and deprecated Cupertino sheet builders with their current
  contracts.
- Do not subclass `IconData` or `TextDecoration`; use instances or composition.

### Web builds

- Do not select the removed HTML renderer. Choose `Image.network` HTML-element
  behavior explicitly with `webHtmlElementStrategy`.
- Remove obsolete hot-reload and service-worker flags. Use current run/build
  controls and project-root `web_dev_config.yaml`.
- A Wasm build includes a JavaScript fallback, remains single-threaded without
  cross-origin isolation, and rejects dependencies using legacy browser interop.
- Do not assume Impeller is available on web; CanvasKit and skwasm remain
  Skia-backed.

## Frequently used additions

### Widget Preview

Annotate top-level builders with `@Preview`. Keep callable wrappers and themes
publicly and statically accessible. Preview configuration supports size,
brightness, localization, grouping, multiple variants, filtering, Inspector
integration, and structured custom annotation values. Imported platform APIs may
compile but still fail if invoked by the preview.

```dart
@Preview(size: Size(320, 640), brightness: Brightness.dark)
Widget previewCard() => const CardExample();
```

### Analyzer plug-ins

Configure analyzer plug-ins at the top level of `analysis_options.yaml`. A plug-in
may come from Pub or a local path; enable its individual lints under that plug-in's
`diagnostics` mapping, qualify ignore codes with the plug-in name, and restart
analysis after configuration changes.

```yaml
plugins:
  local_rules:
    path: tools/local_rules
    diagnostics:
      avoid_legacy_api: true
```

### Build hooks and native assets

Put a package build hook at `hooks/build.dart`. Hooks run during run, build, and
test in dependency order, receive a restricted environment, and write generated
or downloaded intermediates to the shared output directory. Give emitted native
code assets a `package:<package>/<asset>` identity and match that identity from
`@Native` when the library URI does not already do so.

### Web development

Use stateful hot reload on Chrome and the web-server device. Put shared host, port,
TLS, headers, and same-origin proxy settings in `web_dev_config.yaml`; explicit
command-line HTTPS and header settings win. Use `--base-href` when a development
run must mirror a deployed subpath.

### Accessibility and input

- Use semantic roles, identifiers, live regions, continuous sliver indexes,
  explicit hit-test behavior, and semantics matchers as appropriate.
- Honor reduced motion, forced colors, text-spacing overrides, progress semantics,
  and Apple autoplay or cursor preferences.
- Test keyboard, stylus, pointer-kind, selection, focus, and context-menu behavior
  on the target platform.

### Navigation, overlays, and sheets

- Use the predictive-back-aware Material transition unless retaining a former
  transition is an explicit product choice.
- Use `OverlayPortal.overlayChildLayoutBuilder` for anchored layout and
  `OverlayChildLocation.rootOverlay` for root overlays.
- Coordinate Cupertino sheet scrolling and drag dismissal through
  `scrollableBuilder`; supply route settings when observers need sheet identity.
- Use `Navigator.popUntilWithResult` when one result must cross multiple pops.

### Rendering and layout

- Group compatible backdrop filters with `BackdropGroup` and
  `BackdropFilter.grouped`.
- Check renderer support before using `ImageFilter.shader`, named shader bindings,
  sampler filter quality, synchronous textures, or float image formats.
- Use rounded-superellipse primitives for continuous corners and explicit scroll
  cache, grid extent, sliver paint-order, and maximum-paint-bound APIs instead of
  inferring layout geometry.

### Desktop and embedding

- Assume merged UI/platform threads on supported desktop and mobile targets.
- Gate experimental multi-window, content-sized, undecorated, popup, tooltip, and
  dialog-window features; unsupported regular-window implementations can throw.
- Verify architecture and native-input support before committing to Windows ARM,
  Linux RISC-V, stylus, or monitor-management behavior.

## Verification checklist

- Run `flutter analyze` and applicable analyzer plug-in diagnostics.
- Run unit, widget, semantics, and integration tests; use timeout and installation
  retention switches only when the harness requires them.
- Exercise route completion, predictive back, form reset and error clearing,
  keyboard traversal, selection, and focus behavior touched by the change.
- Build every affected target and inspect warnings from Wasm dry runs, Gradle,
  Xcode, plug-in metadata, assets, shader processing, and removed CLI options.
- Verify accessibility with screen readers and user preferences enabled.
- Use profiling or diagnostic tools for microtasks, text layout, analysis-server
  latency, native symbols, and startup behavior.
