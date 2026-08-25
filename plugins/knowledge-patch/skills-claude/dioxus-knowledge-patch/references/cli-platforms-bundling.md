# CLI, Platforms, Bundling, and Tooling

## Installation and diagnostics

The `dx` CLI works with Dioxus and ordinary Rust projects. It can extract
`asset!` declarations, hot-patch code, launch the debugger, and create native
bundles. Install from the project script and update in place:

```sh
curl -fsSL https://dioxus.dev/install.sh | bash
dx self-update
```

DX warns when its version is incompatible with the `dioxus` crate. Run
`dx doctor` before diagnosing mobile SDK, native system library, or Rust target
problems. `dx print` exposes the Cargo, linker, and environment arguments DX
would use so another tool can reproduce the build.

### Prerelease source installation

> **Prerelease (`0.8.0-alpha.1`):** This guidance may change before stable release.

Plain `cargo install dioxus-cli` works again; the `--locked` workaround required
by the preceding alpha is no longer necessary.

## Commands and output contracts

- `dx serve` builds and runs with development hot reload and compiled-code
  patching where supported.
- `dx run` builds and runs without hot reload.
- `dx build` creates build artifacts; `--raw-json-diagnostics` emits compiler
  diagnostics separately from normal JSON logs.
- `dx bundle` creates distributable artifacts; `--package-types` is repeatable.
- `dx check` lints the project and `dx fmt` formats RSX while respecting
  `rustfmt.toml` and `#[rustfmt::skip]`.
- `dx completions <shell>` emits a shell completion script (since `0.7.6`).
- `dx translate --file <path>` or `--raw "<html>"` converts HTML to RSX;
  `--component` wraps it in a component and `--output` writes a file.
- `dx components` manages the component registry; `dx tools` runs individual
  build stages such as `build-assets` and `hotpatch`.
- `dx config` reads or writes CLI settings. Cargo manifest flags such as
  `--locked`, `--offline`, and `--frozen` are global.

`dx new` offers bare-bones, jumpstart, and workspace starters. Select another
repository with `--template gh:owner/repo`; the default shorthand points at
`DioxusLabs/dioxus-template`.

Use `--log-to-file <PATH>` for complete diagnostics. `--json-output` applies to
all commands and guarantees the final output line is the command result. Its
`.json` field is itself a JSON string; bundle output requires `--verbose`:

```sh
dx bundle --desktop --json-output --verbose \
  | tail -1 \
  | jq -r '.json | fromjson | .BundleOutput.bundles[]'
```

CLI output has lived beneath `target/dx` since `0.6.0`; the old `outdir`
concept was removed.

## Selecting platforms and profiles

Prefer bare flags such as `dx serve --web`, `--desktop`, `--ios`, or
`--android`. `--platform` is also supported; it was accidentally missing only
in `0.7.0` and restored in `0.7.1`. `--renderer native` selects the native
renderer, and `--bundle` chooses a bundle format.

Each platform selects its Cargo feature and a dedicated profile:
`web-dev`/`web-release`, `server-dev`, `desktop-dev`, `ios-dev`, or
`android-dev`. DX detects fullstack from `dioxus/fullstack` plus a Cargo feature
literally named `server`, then runs separate client and backend Cargo builds.

Serve separate packages together when client and server live in different
workspace crates:

```sh
dx serve @client --package frontend @server --package backend
```

## Web and fullstack deployment

`dx bundle --web` writes
`target/dx/<app>/<profile>/web/`, containing both a `public/` directory and a
neighboring `server` executable. Deploying only `public` loses server functions.
Run the executable directly. Default launch code reads `IP` and `PORT` and binds
to `127.0.0.1`, so a container commonly needs:

```dockerfile
ENV PORT=8080
ENV IP=0.0.0.0
ENTRYPOINT ["/usr/local/app/server"]
```

The CLI does not install the browser target; run
`rustup target add wasm32-unknown-unknown` before a web build.

For GitHub Pages, set `[web.app].base_path` to the repository, bundle into
`docs`, move the contents out of the nested `public` directory, and copy
`index.html` to `404.html` so client routes survive refreshes.

## `Dioxus.toml` web configuration

These keys cover behaviors with no simple CLI equivalent. In particular,
`index_on_404` makes history-based client routes work in development, while
`wasm_opt.level` defaults to `"4"` (speed, not size). Proxy entries forward the
path and query without rewriting.

```toml
[application]
asset_dir = "public"
sub_package = "my-workspace-member"

[web.app]
title = "Project"
base_path = "project"

[web.watcher]
reload_html = true
index_on_404 = true

[web.resource]
style = ["./assets/main.css"]
script = ["./public/index.js"]

[[web.proxy]]
backend = "http://localhost:8000/api/"

[web]
pre_compress = true

[web.wasm_opt]
level = "z"
debug = true
```

`[web.resource.dev]` mirrors resource injection for development only. Configure
development TLS with `enabled`, `mkcert`, `key_path`, and `cert_path` under
`web.https`. A custom `index.html` must contain `<div id="main">`; hot reload
still works with the template. Tailwind watcher paths use `tailwind_input` and
`tailwind_output`.

## Desktop prerequisites and behavior

Linux desktop builds require WebKitGTK **4.1** and `xdotool`—for Debian/Ubuntu,
`libwebkit2gtk-4.1-dev` and `libxdo-dev`; for Arch, `webkit2gtk-4.1` and
`xdotool`; for Fedora, `libxdo-devel` plus the matching WebKit package. Include
the runtime equivalents in `.deb` and `.rpm` dependency metadata.

Under WSL, set `DISPLAY=:0` and install a fallback such as `zenity` for file
dialogs; current `libEGL` warnings are expected. Windows requires WebView2,
normally present with Edge.

Desktop supports system trays, custom event loops, and child-window mode for
overlaying Dioxus on another WGPU/OpenGL renderer (restored/added in `0.6.0`).
Since `0.7.1`, `with_on_window_ready` exposes the window before webview
attachment and Tokio file dialogs are async. Tray icons can show the main window
on click, and `0.7.6` ensures the configured Windows executable icon is applied.

## Mobile prerequisites and workflow

Since `0.6.0`, iOS and Android applications use the same ordinary `main.rs` as
other platforms; the old `cdylib`, `#[no_mangle] start_app`, and manual panic
catching layer are obsolete. DX owns simulator/device serving and RSX/asset hot
reload.

Android requires Rust targets `aarch64-linux-android`,
`armv7-linux-androideabi`, `i686-linux-android`, and
`x86_64-linux-android`, plus `JAVA_HOME`, `ANDROID_HOME`, and `NDK_HOME`. Install
the SDK, command-line tools, side-by-side NDK, and CMake through Android Studio.
iOS requires `aarch64-apple-ios` and `aarch64-apple-ios-sim` plus Xcode tooling.

DX can serve real Android devices through `adb reverse`. It bundles native
`.dylib` and `-framework` dependencies automatically and, since `0.7.4`, can
bundle iOS widget extensions for Live Activities and home-screen widgets.
Android release APK signing is configured under `bundle.android`.

## Unified mobile permissions

Declare platform-neutral permissions once. The CLI maps them into Android
manifest entries and Apple usage descriptions; `description` becomes the Apple
prompt text.

```toml
[permissions]
location = { precision = "fine", description = "Show nearby places" }
camera = { description = "Take profile photos" }
```

Typed keys are `location` (`fine` or `coarse`), `background_location`, `camera`,
`microphone`, `notifications`, `photos.read`, `photos.write`, `bluetooth`,
`contacts`, `calendar`, `biometrics`, `nfc`, `motion`, `health`, and `speech`.
Put other Android capabilities under `[android.permissions]` with their complete
`android.permission.*` names. The old `permission!()`/`PermissionBuilder` API
was removed.

## Deep links and background modes

```toml
[deep_links]
schemes = ["myapp"]
hosts = ["example.com", "*.example.com"]
paths = ["/app/*"]

[background]
location = true
audio = true
fetch = true
remote-notifications = true
voip = true
bluetooth = true
processing = true
```

An empty `paths` list matches every path for the configured hosts.

Platform sections extend rather than replace unified values: Apple URL schemes
add to `deep_links.schemes`, and Apple background modes or Android foreground
service types add to `[background]`.

## Platform manifest sections

`[ios]`, `[android]`, and `[macos]` are top-level manifest configuration, not
`[bundle.*]` installer metadata. Each has typed fields and a raw escape hatch:
`[ios.raw].info_plist` and `[android.raw].manifest` splice values verbatim.
Generated platform projects use Handlebars templates and are disposable; do not
edit their generated XML/plist by hand.

```toml
[ios]
deployment_target = "15.0"

[[ios.document_types]]
name = "My Document"
extensions = ["mydoc"]
role = "Editor"

[ios.plist]
ITSAppUsesNonExemptEncryption = false

[ios.entitlements]
"com.apple.security.application-groups" = ["group.com.example.app"]

[android]
min_sdk = 24
target_sdk = 34
features = ["android.hardware.location.gps"]

[[android.intent_filters]]
actions = ["android.intent.action.VIEW"]
categories = ["android.intent.category.DEFAULT", "android.intent.category.BROWSABLE"]
auto_verify = true

[[android.intent_filters.data]]
scheme = "https"
host = "example.com"
path_prefix = "/app"

[android.queries]
packages = ["com.other.app"]

[macos]
frameworks = ["CoreLocation.framework"]
category = "public.app-category.productivity"
```

Do not confuse `[macos] minimum_system_version` and inline
`[macos.entitlements]` with `[bundle.macos]` values, where entitlements is a
path to a plist. For the complete mobile schema introduced around `0.7.4`, use
the CLI repository's `packages/cli/schema.json` rather than guessing field
names.

## Kotlin, Java, and Swift FFI

First-party mobile FFI arrived in `0.7.4`. Annotate an `extern` block with the
source directory and use the source-language ABI. Foreign objects are declared
as Rust types and may receive ordinary Rust `impl` methods.

```rust
#[manganis::ffi("/src/ios")]
extern "Swift" {
    pub type SomeSwiftObject;
    pub fn value(this: &SomeSwiftObject) -> Option<u32>;
}

#[manganis::ffi("/src/android")]
extern "Kotlin" {
    fn do_thing() -> JObject;
}
```

Calls use runtime lookup—JNI for Kotlin/Java and the Objective-C runtime for
Swift—so values must be pointer-like or cross-language coercible. The macro
emits sources as Manganis assets; extraction and native compilation happen in
the bundler after rustc. This is not a `build.rs` replacement: Rust cannot
consume headers or other outputs generated by that native compilation.
TypeScript/JavaScript bindings were only planned in `0.7.4`, not supported.

## Bundle metadata and package selection

Desktop installer metadata belongs in `Dioxus.toml`:

```toml
[bundle]
identifier = "com.example.app"
publisher = "Example"
icon = ["icons/32.png", "icons/app.icns", "icons/app.ico"]
resources = ["main.css", "**/*.png"]
category = "Utility"
external_bin = ["bin/helper"]

[bundle.macos]
frameworks = ["CoreML"]
minimum_system_version = "10.13"
entitlements = "entitlements.plist"
signing_identity = "KEYCHAIN ENTRY"
hardened_runtime = true
```

`category` is a fixed App-Store-style enum. `resources` takes globs. For a
sidecar, list the path without a target triple but ship the file with the triple
appended; access it at runtime by the bare binary name.

`--package-types` is repeatable. Valid types include macOS `macos`/`dmg`, Linux
`appimage`/`rpm`/`deb`, Windows `msi`/`nsis`, iOS `ios`, Android package output,
and `updater` where supported. Desktop bundling is host-bound, so build each OS
on its own runner.

### Whole resource directories

> **Prerelease (`0.8.0-alpha.1`):** This guidance may change before stable release.

The bundler can copy complete resource directories into a bundle, in addition
to individual resource globs and file maps.

## Windows installers and signing

`webview_install_mode` controls WebView2: `Skip`, `DownloadBootstrapper`,
`EmbedBootstrapper`, `OfflineInstaller`, or `FixedRuntime { path }`. `Skip`
leaves the app unable to run on a machine without WebView2.

A custom signing command must contain literal `%1` for the binary path, which
also allows `osslsigncode` from a non-Windows host:

```toml
[bundle.windows.sign_command]
cmd = "osslsigncode"
args = ["sign", "-in", "%1"]

[bundle.windows.nsis]
install_mode = "PerMachine"
minimum_webview2_version = "110.0.1531.0"
```

The `.exe` installer package name is `nsis`. Its settings include
`CurrentUser`/`PerMachine`/`Both`, installer hooks, and minimum WebView2.
WiX's `upgrade_code` GUID must remain stable across releases or Windows treats
an update as a separate application.

## Debian and macOS package details

Debian's section supports `depends`, `section`, `priority`, maintainer scripts,
a Handlebars desktop template, and a destination-to-source `files` map. It also
supports `provides`, `conflicts`, `replaces`, and `changelog`.

`bundle.macos.files` provides the same destination-to-source mapping outside
resource globs. macOS additionally supports `info_plist_path`,
`exception_domain`, and `provider_short_name`.

Since `0.7.4`, DX's installer implementation is vendored in-tree rather than
depending on `tauri-bundler`; remove workarounds for its formerly broken bundle
asset paths or NSIS/MSI output.

## Logging, debugger, and telemetry

`dioxus::launch` installs tracing at `Debug` in development and `Info` in
release. Override it by calling `dioxus::logger::init(Level)` before launch.
Web uses `tracing-wasm`, desktop/server use `tracing-subscriber`, Android emits
to logcat, and iOS emits to oslog.

During `dx serve`, press `d` to attach LLDB through a VSCode-family editor; web,
desktop, mobile, and Cursor are supported. Rust-level WASM debugging in Chrome
requires the DWARF-aware debugging extension.

Since `0.7.0`, CLI telemetry is enabled by default and includes stripped command
invocations, stage timings, sanitized panics, a hardware-derived identifier,
target/CI status, and DX version. Opt out with the `disable-telemetry` Cargo
feature, `TELEMETRY=false`, or:

```sh
dx config set disable-telemetry true
```
