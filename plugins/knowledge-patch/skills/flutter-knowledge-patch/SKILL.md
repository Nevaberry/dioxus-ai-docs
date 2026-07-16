---
name: flutter-knowledge-patch
description: Flutter 3.44.0 compatibility. Use for Flutter work.
license: MIT
version: 3.44.0
metadata:
  author: Nevaberry
---

# Flutter Knowledge Patch

Use this skill before changing Flutter or Dart applications, packages, plug-ins,
embedders, build automation, or development tooling. Read the reference that
matches the task before choosing an API or migration path; several old flags,
generated files, properties, and platform assumptions are no longer valid.

## Reference index

| Reference | Topics |
| --- | --- |
| [accessibility-input-and-testing.md](references/accessibility-input-and-testing.md) | Semantics, accessibility preferences, selection, text input, gestures, and tests |
| [android.md](references/android.md) | Android SDK and Gradle requirements, rendering, platform views, system UI, and embedding |
| [apple-platforms.md](references/apple-platforms.md) | UIScene, Swift Package Manager, Xcode, Cupertino integration, signing, and Apple rendering |
| [dart-language.md](references/dart-language.md) | Dot shorthands, null-aware collection elements, flow analysis, constructors, and roadmap |
| [dart-tooling-and-packages.md](references/dart-tooling-and-packages.md) | Formatter, analyzer plug-ins, Pub, workspaces, build hooks, native assets, and publishing |
| [desktop-and-embedding.md](references/desktop-and-embedding.md) | Thread merging, add-to-app sizing, multi-window APIs, displays, input, and architectures |
| [migrations-and-breaking-changes.md](references/migrations-and-breaking-changes.md) | Cross-cutting removals, deprecations, callback changes, and required source migrations |
| [navigation-layout-and-animation.md](references/navigation-layout-and-animation.md) | Routes, transitions, overlays, sheets, slivers, scrolling, layout, and animation |
| [tooling-build-assets-and-plugins.md](references/tooling-build-assets-and-plugins.md) | CLI contracts, Widget Preview, builds, assets, plug-in metadata, MCP, and release artifacts |
| [web-rendering-and-graphics.md](references/web-rendering-and-graphics.md) | Web hot reload, Wasm, renderers, Impeller, shaders, images, filters, and web configuration |
| [widgets-and-theming.md](references/widgets-and-theming.md) | Material and Cupertino controls, menus, forms, themes, tooltips, and component styling |

## Working method

1. Check `pubspec.yaml`, the platform project, and CI scripts before editing.
2. Read the topic reference for every platform or API involved.
3. Apply required migrations before adding new behavior.
4. Prefer current properties and command forms; do not preserve a removed flag or
   generated artifact merely because an older project still contains it.
5. Test on every affected renderer, operating system, input mode, and accessibility
   configuration when behavior differs by target.

## Breaking changes and deprecations

### Android projects

- Use the declarative Gradle plug-in setup. The imperative Flutter Gradle script
  application mechanism is gone.
- Remove Android v1 embedding APIs and migrate applications and plug-ins to the v2
  embedding.
- Treat edge-to-edge content and resizable, orientation-flexible layouts as the
  platform baseline. Handle system-bar and large-screen insets explicitly.
- Keep the Android toolchain within Flutter's supported combination. Check the
  Android reference before adopting AGP 9 because its built-in Kotlin support
  changes both application and plug-in configuration.
- Do not rely on opting out of Impeller or restoring separate mobile UI and platform
  threads.

### Apple projects

- Migrate iOS lifecycle work and lifecycle-aware plug-ins to `UIScene`; do not assign
  the now-read-only `sceneLifeCycleDelegate`.
- Expect Swift Package Manager to manage ordinary iOS and macOS application plug-ins.
  Audit customized Xcode targets and schemes after automatic migration. Add-to-app
  hosts still require a different dependency path.
- Use supported Xcode tooling and current platform deployment minimums. Regenerate
  platform configuration after raising a plug-in's minimum OS.
- Do not depend on the iOS Skia opt-out or on SkSL warm-up build artifacts.

### Dart and package configuration

- After raising a package language constraint, run `dart pub get` before formatting.
  Use `dart fix`; `dart format --fix` no longer exists.
- Declare imported packages directly. The explicit-dependency check is unconditional.
- Replace browser work based on legacy web libraries with `dart:js_interop` and
  `package:web`, especially before enabling Wasm.
- Import generated localization code from its real output. The synthetic
  `package:flutter_gen` package is gone.
- Account for Pub enforcing the root Flutter SDK upper bound once the package opts
  into the relevant language behavior.

### Framework source migrations

- Replace deprecated `...Theme` value types with their `...ThemeData` forms and use
  the replacement component properties documented in the widget reference.
- Put shared radio value and change handling in `RadioGroup`.
- Give `DropdownMenu` a non-nullable generic type, use `initialValue` on
  `DropdownButtonFormField`, and express `DropdownButton.enabled` independently of
  its callback.
- Replace removed or renamed callbacks and members before changing behavior:
  `findItemIndexCallback`, `onReorderItem`, `maintainHintSize`, `Tooltip.constraints`,
  and the current Cupertino sheet builder contract.
- Do not subclass `IconData` or `TextDecoration`; use instances or composition.

### Web builds

- Do not select the removed HTML renderer. `Image.network` HTML-element fallback is
  now an explicit `webHtmlElementStrategy` decision.
- Remove obsolete hot-reload and service-worker flags. Use the current web run/build
  controls and `web_dev_config.yaml`.
- Remember that a Wasm build includes a JavaScript fallback, is single-threaded
  without cross-origin isolation, and cannot compile dependencies that retain legacy
  browser interop.
- Do not assume Impeller exists on the web; both web renderer paths remain
  Skia-backed.

## Frequently used additions

### Widget Preview

Annotate top-level widget builders with `@Preview` and keep callable wrappers and
themes publicly and statically accessible. Preview configuration supports size,
brightness, localization, grouping, multiple variants, structured custom annotation
values, IDE filtering, and Inspector integration. Treat platform-only calls as
unavailable even when their imports compile in the preview environment.

```dart
@Preview(size: Size(320, 640), brightness: Brightness.dark)
Widget previewCard() => const CardExample();
```

### Analyzer plug-ins

Configure analyzer plug-ins at the top level of `analysis_options.yaml`. Published
and path-based plug-ins can provide diagnostics, fixes, and assists; enable individual
plug-in lints under that plug-in's `diagnostics` mapping and restart analysis after
configuration changes.

```yaml
plugins:
  local_rules:
    path: tools/local_rules
    diagnostics:
      avoid_legacy_api: true
```

### Build hooks and native assets

Place a package build hook at `hooks/build.dart`. Hooks run for run, build, and test
in dependency order, receive a restricted environment, and place generated or
downloaded intermediates in the shared output directory. Give emitted native code
assets a `package:<package>/<asset>` identity and match it from `@Native` when the
library URI does not supply the same identity.

### Web development

Use stateful hot reload on Chrome and the web-server device. Put shared host, port,
TLS, headers, and same-origin proxy settings in project-root `web_dev_config.yaml`;
explicit command-line HTTPS and header settings win. Use `--base-href` when a
development run must match a deployed subpath.

### Accessibility and input

- Use semantic roles, identifiers, live regions, continuous sliver indexes, explicit
  hit-test behavior, and the semantics test matchers where appropriate.
- Honor reduced motion, forced colors, text-spacing overrides, progress semantics,
  and Apple autoplay or cursor preferences.
- Test keyboard, stylus, pointer-kind, selection, and context-menu behavior on the
  target platform; several defaults are platform-specific.

### Navigation, overlays, and sheets

- Use the predictive-back-aware Material transition unless the application explicitly
  retains its previous transition.
- Use `OverlayPortal.overlayChildLayoutBuilder` for anchor-aware placement and
  `OverlayChildLocation.rootOverlay` for root overlays.
- Coordinate Cupertino sheet scrolling and drag dismissal through
  `scrollableBuilder`; use route settings when observers need sheet identity.
- Use `Navigator.popUntilWithResult` when one result must cross several popped routes.

### Rendering and layout

- Group compatible backdrop filters with `BackdropGroup` and
  `BackdropFilter.grouped`.
- Use `ImageFilter.shader`, named shader bindings, sampler filter quality, synchronous
  texture creation, and float image formats only after checking renderer support.
- Prefer `RoundedSuperellipseBorder` and related primitives when the design calls for
  continuous corners; web support no longer falls back to ordinary rounded rectangles.
- Use shared scroll cache configuration, fixed grid main-axis extents, explicit sliver
  paint order, and custom maximum paint bounds instead of inferring geometry.

### Desktop and embedding

- Assume UI/platform thread merging on supported desktop targets and mobile.
- Gate experimental multi-window, content-sized, undecorated, popup, tooltip, and
  dialog-window behavior; unsupported regular-window implementations can throw.
- Check platform architecture support and native input details before promising a
  Windows ARM, Linux RISC-V, stylus, or monitor-management workflow.

## Verification checklist

- Run `flutter analyze` and relevant Dart analyzer plug-in diagnostics.
- Run unit, widget, semantics, and integration tests; use the documented timeout or
  installation-retention switches only when the harness needs them.
- Exercise route completion, predictive back, form reset/error clearing, keyboard
  traversal, and selection behavior affected by the change.
- Build each affected target and inspect warnings from Wasm dry runs, Gradle, Xcode,
  plug-in metadata, assets, and removed CLI options.
- Verify accessibility with the platform screen reader and user preferences enabled.
- Check profile or diagnostic tools when investigating microtasks, text layout,
  analysis-server latency, native symbols, or startup behavior.
