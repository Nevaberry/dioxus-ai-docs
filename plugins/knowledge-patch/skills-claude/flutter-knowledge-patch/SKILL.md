---
name: flutter-knowledge-patch
description: Flutter
version: 3.44.0
license: MIT
metadata:
  author: Nevaberry
---


# Flutter Knowledge Patch

Use this skill before changing Flutter or Dart applications, packages, plugins,
embedders, build automation, or developer tooling. Check the project manifest,
platform projects, and CI configuration first, then read every topic reference
that touches the requested work.

Prefer the checked-out SDK, project source, generated configuration, and observed
test behavior when they disagree with compatibility guidance. Treat experiments
and main-channel APIs as gated work: verify that the selected SDK actually exposes
them before committing to an implementation.

## Reference index

| Reference | Topics |
| --- | --- |
| [accessibility-input-and-testing.md](references/accessibility-input-and-testing.md) | Semantics, accessibility preferences, selection, text input, gestures, focus, and tests |
| [android.md](references/android.md) | Android SDK and Gradle requirements, rendering, platform views, system UI, and embedding |
| [apple-platforms.md](references/apple-platforms.md) | UIScene, Swift Package Manager, Xcode, Cupertino integration, signing, and Apple rendering |
| [dart-language.md](references/dart-language.md) | Dot shorthands, null-aware elements, flow analysis, constructors, deprecations, and roadmap |
| [dart-tooling-and-packages.md](references/dart-tooling-and-packages.md) | Formatter, analyzer plugins, Pub, workspaces, build hooks, native assets, and publishing |
| [desktop-and-embedding.md](references/desktop-and-embedding.md) | Thread merging, add-to-app sizing, multi-window APIs, displays, input, and architectures |
| [migrations-and-breaking-changes.md](references/migrations-and-breaking-changes.md) | Cross-cutting removals, deprecations, callback changes, and required source migrations |
| [navigation-layout-and-animation.md](references/navigation-layout-and-animation.md) | Routes, transitions, overlays, sheets, slivers, scrolling, layout, and animation |
| [tooling-build-assets-and-plugins.md](references/tooling-build-assets-and-plugins.md) | CLI contracts, Widget Preview, builds, assets, plugin metadata, MCP, and release artifacts |
| [web-rendering-and-graphics.md](references/web-rendering-and-graphics.md) | Web hot reload, Wasm, renderers, Impeller, shaders, images, filters, and web configuration |
| [widgets-and-theming.md](references/widgets-and-theming.md) | Material and Cupertino controls, menus, forms, themes, tooltips, and component styling |

## Working method

1. Read `pubspec.yaml` and its SDK constraints. Inspect the lockfile after the
   manifest, and inspect `analysis_options.yaml` when analyzer behavior matters.
2. Read `android/`, `ios/`, `macos/`, `windows/`, `linux/`, and `web/` only for
   targets affected by the work. Customized platform projects need extra migration
   checks.
3. Search source, scripts, and CI for removed flags, generated files, old theme
   types, deprecated callbacks, and legacy embedding APIs before adding behavior.
4. Apply required migrations first. Do not keep a removed option or artifact merely
   because an old project still references it.
5. Run analysis and focused tests, then build and exercise every affected target,
   renderer, input mode, and accessibility configuration.

## Breaking changes and deprecations

### Android projects

- Use declarative Gradle plugin application and Android v2 embedding APIs.
- Keep the Android SDK, Java, Gradle, Android Gradle Plugin, Kotlin, and NDK
  combination within the selected Flutter SDK's supported range.
- Treat edge-to-edge content and resizable, orientation-flexible large-screen
  layouts as the platform baseline. Handle system-bar and display-corner insets.
- Audit AGP 9 migrations carefully: built-in Kotlin changes both application and
  plugin configuration.
- Do not design integrations around separate mobile UI and platform threads.
- Do not rely on an Impeller opt-out; renderer backend selection is device- and
  platform-dependent.

### Apple projects

- Move lifecycle code and lifecycle-aware plugins to `UIScene`; do not assign the
  read-only `sceneLifeCycleDelegate`.
- Expect Swift Package Manager for ordinary iOS and macOS application plugins.
  Audit customized targets, schemes, flavors, and generated package wiring.
- Do not use Flutter's SwiftPM integration for add-to-app hosts.
- Keep Xcode and deployment targets at supported minimums and regenerate platform
  configuration after raising a plugin's minimum OS.
- Do not depend on iOS Skia fallback, the Impeller opt-out, or SkSL warm-up build
  artifacts.

### Dart and packages

- After raising a Dart language constraint, run `dart pub get` before formatting.
  Use `dart fix`; `dart format --fix` is removed.
- Declare every imported package directly. The direct-dependency check has no
  selectable opt-out.
- Replace legacy browser libraries with `dart:js_interop` and `package:web`,
  especially before enabling Wasm.
- Import generated localization code from its real output; the synthetic
  `package:flutter_gen` package is removed.
- Account for Pub enforcing the root Flutter SDK upper bound after the package opts
  into that language behavior.

### Framework source

- Replace deprecated component theme value types with their `...ThemeData` forms.
- Put radio group value and change handling in `RadioGroup`.
- Give `DropdownMenu` a non-nullable type, use `initialValue` on
  `DropdownButtonFormField`, and express `DropdownButton.enabled` independently.
- Replace removed or renamed members, including `findItemIndexCallback`,
  `onReorderItem`, `maintainHintSize`, `Tooltip.constraints`, and the current
  Cupertino sheet builder contract.
- Do not subclass `IconData` or `TextDecoration`; use instances or composition.
- Treat route removal as completion and audit futures or custom route lifecycle
  code that assumed otherwise.

### Web projects

- Do not select the removed HTML renderer. Choose `Image.network` HTML-element
  behavior explicitly with `webHtmlElementStrategy`.
- Remove obsolete hot-reload, service-worker, and renderer flags. Use current
  run/build controls and project-root `web_dev_config.yaml`.
- A Wasm build includes a JavaScript fallback, is single-threaded without
  cross-origin isolation, and rejects dependencies that retain legacy browser
  interop.
- Both available web renderer paths remain Skia-backed; Impeller is not a web
  renderer.

## Frequently used additions

### Widget Preview

Annotate top-level widget builders with `@Preview`. Keep wrappers, themes, and other
callable annotation arguments publicly and statically accessible. Preview
configuration supports size, brightness, localization, grouping, multiple variants,
structured custom values, IDE filtering, Inspector integration, and machine or web
server command modes.

```dart
@Preview(size: Size(320, 640), brightness: Brightness.dark)
Widget previewCard() => const CardExample();
```

Preview code can compile transitive platform imports, but invoking unavailable
platform APIs still fails. Use web-compatible conditional paths.

### Analyzer plugins

Configure analyzer plugins at the top level of `analysis_options.yaml`. Published
and path-based plugins can provide diagnostics, fixes, and assists; enable
individual plugin lints under the plugin's `diagnostics` mapping and restart
analysis after configuration changes.

```yaml
plugins:
  local_rules:
    path: tools/local_rules
    diagnostics:
      avoid_legacy_api: true
```

### Build hooks and native assets

Put a package hook at `hooks/build.dart`. Hooks run for run, build, and test in
dependency order, receive a restricted environment, and put generated or downloaded
intermediates in the shared output directory. Give emitted native code assets a
`package:<package>/<asset>` identity and match that identity from `@Native` when
the library URI does not already do so.

### Web development

Use stateful hot reload on Chrome and the web-server device. Put shared host, port,
TLS, headers, and same-origin proxy settings in project-root
`web_dev_config.yaml`; explicit command-line HTTPS and header settings win. Use
`--base-href` when development must match a deployed subpath.

### Accessibility and input

- Use semantic roles, identifiers, live regions, continuous sliver indexes,
  explicit hit-test behavior, and semantics matchers where appropriate.
- Honor reduced motion, forced colors, text-spacing overrides, progress semantics,
  and Apple autoplay or cursor preferences.
- Test keyboard, stylus, pointer-kind, selection, focus, and context-menu behavior
  on each target; several defaults differ by platform.

### Navigation, overlays, and sheets

- Use predictive-back-aware Material transitions unless the application explicitly
  retains its earlier transition.
- Use `OverlayPortal.overlayChildLayoutBuilder` for anchor-aware placement and
  `OverlayChildLocation.rootOverlay` for root overlays.
- Coordinate Cupertino sheet scrolling and drag dismissal through
  `scrollableBuilder`; supply route settings when observers need sheet identity.
- Use `Navigator.popUntilWithResult` when one value must cross several popped
  routes.

### Rendering and layout

- Share compatible backdrop work through `BackdropGroup` and
  `BackdropFilter.grouped`.
- Check renderer support before using shader image filters, named bindings, sampler
  quality, synchronous textures, float formats, or wide-gamut color.
- Use rounded-superellipse primitives for continuous corners.
- Prefer explicit scroll caching, fixed grid extents, sliver paint order, and
  maximum paint bounds over inferred geometry.

### Desktop and embedding

- Assume merged UI and platform threads on supported mobile and desktop embedders.
- Gate experimental multi-window, content-sized, undecorated, popup, tooltip, and
  dialog-window behavior. Unsupported regular-window implementations can throw.
- Check target architecture and native input support before promising Windows ARM,
  Linux RISC-V, stylus, or monitor-management behavior.

## Verification checklist

- Run `flutter analyze` and any configured analyzer-plugin diagnostics.
- Run focused unit, widget, semantics, and integration tests.
- Exercise route completion, predictive back, form reset and error clearing,
  keyboard traversal, focus, text selection, and context menus when affected.
- Build every target in scope and inspect warnings about Wasm compatibility,
  Gradle, Xcode, plugin metadata, assets, and removed CLI options.
- Test with platform screen readers and relevant accessibility preferences.
- Use inspector, logging, text-layout, microtask, analysis-server, startup, or native
  symbol diagnostics when investigating those layers.
