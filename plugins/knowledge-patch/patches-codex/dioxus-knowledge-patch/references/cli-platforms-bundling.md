# CLI, Platforms, Bundling, and Tooling

Use this reference for `dx` installation and diagnostics, project
configuration, Web/Desktop/Mobile workflows, logging and debugging, release
bundles, deployment layouts, platform permissions, and installer controls.

## Installation and diagnosis

The direct installer introduced in 0.7.0 removes the former
`cargo-binstall` prerequisite:

```sh
curl -fsSL https://dioxus.dev/install.sh | bash
dx doctor
```

`dx doctor` checks platform toolchains. Desktop needs WebView2 on Windows and
WebKitGTK 4.1 plus xdotool/libxdo on Linux. iOS needs Xcode and its SDKs;
Android needs the SDK and NDK.

The installer honors `CARGO_HOME` since 0.7.3. `dx --version` reports its Git
SHA and Cargo-installed binaries carry version metadata since 0.7.9, restoring
`dx self-update` for those installations.

### Preview source installation transition

> **Prerelease (`0.8.0-alpha.0`):** This guidance may change before stable release.

The first alpha required `cargo install dioxus-cli --locked` because unlocked
resolution could select incompatible upstream dependencies.

> **Prerelease (`0.8.0-alpha.1`):** This guidance may change before stable release.

The next alpha pins `git2`, restoring ordinary source installation:

```sh
cargo install dioxus-cli
```

Use the command that matches the exact alpha being installed.

## Serving and interactive development

### Platforms and features

Renderer features moved onto the main `dioxus` crate in 0.5.0.
`dioxus::launch(App)` selects the enabled renderer, and
`dx serve --platform ...` activates the corresponding build. Fullstack builds
client and server together.

The 0.6.0 CLI made iOS and Android first-class targets using the same `main.rs`
as other platforms, simulator launch, hot reload, asset bundling, and logging.
Build output lives beneath `target/dx`; in the interactive UI, `r` rebuilds and
`v`/`t` changes log verbosity.

Target shorthands are also accepted:

```sh
dx serve --web
dx serve --desktop
dx serve --ios
dx serve --android
```

Since 0.7.0, `dx` can serve an ordinary Rust project and run named client and
server packages together. It accepts Cargo-style `--offline` and `--locked`.

```sh
dx serve @client --package client @server --package server
```

### Hot reload and file watching

RSX hot reload covers formatted strings in text, attributes, component props,
primitive literals, and nested RSX across Web, Desktop, and Mobile. CSS and
asset changes participate as described in
[assets-styling-ui.md](assets-styling-ui.md). Desktop preserves window state
across recompiles.

### Preview watcher behavior

> **Prerelease (`0.8.0-alpha.0`):** This guidance may change before stable release.

Rust hot-patching is enabled by default. The watcher responds to `Cargo.toml`,
configured `[web.watcher].watch_path` entries, and files found from Cargo
dependency metadata, so workspace and dependency changes can select reload or
rebuild without a fixed list.

## Diagnostics, debugging, and automation

The CLI captures WASM tracing and panics, and debug-symbol stack traces can link
to the editor. Press `d` during `dx serve` to attach LLDB through a supported
VS Code-style editor on Web, Desktop, or Mobile. Web debugging opens a separate
Chrome; install the DWARF symbols extension for demangled Rust symbols. Cursor
became a supported debug editor in 0.7.6.

`dx build --raw-json-diagnostics` has emitted unwrapped machine-readable
diagnostics since 0.7.1. `dx bundle --json-output` emits structured logs for CI
artifact discovery. The global `--log-to-file` captures all CLI logs regardless
of verbosity.

```sh
dx build --raw-json-diagnostics
dx bundle --json-output
dx --log-to-file dx.log serve
```

`dx print` exposes Cargo, linker, and other arguments supplied by DX so another
tool can reproduce the build context. `dx completions` generates shell
completions since 0.7.6.

## Project creation and utility commands

`dx new` offers Bare-Bones, Jumpstart, and Workspace layouts; use Workspace for
separate Web, Desktop, and Mobile crates. It also accepts a GitHub template,
while `dx init` initializes the current directory.

```sh
dx new --template gh:owner/repository
dx init
```

`dx translate` converts HTML from `--file` or `--raw` to RSX, writes stdout by
default, accepts `--output`, and wraps output with `--component`.

```sh
dx translate --file index.html --output index.rs
dx translate --raw "<div>Hello world</div>" --component
```

`dx components` manages the component registry; component installation details
are in [ecosystem-sdk-components.md](ecosystem-sdk-components.md).

The project publishes a first-party `llms.txt` generated from its
documentation, and templates may include optional condensed release prompts
for tools that cannot read it.

## Crate and launch configuration

The default `dioxus` features are `signals`, `macro`, `html`, `hooks`, and
`hot-reload`. Optional `router` re-exports the router and activates its
current-platform integration; `logger` installs the default tracing
subscriber. If defaults are disabled, explicitly restore every layer used.

The old Fullstack-wide `Config` was removed in 0.6.0. Pass server, Web, and
Desktop configuration separately through `LaunchBuilder`, keeping shared
settings such as the root element consistent.

```rust
LaunchBuilder::new()
    .with_cfg(server_only! { ServeConfigBuilder::default().root_id("app") })
    .with_cfg(web! { dioxus::web::Config::default().rootname("app") })
    .launch(app);
```

`Dioxus.toml` requires `[application]`, `[web.app]`, `[web.watcher]`,
`[web.resource]`, and `[web.resource.dev]`, even when some are empty.
`asset_dir` copies a directory to output, while `sub_package` chooses a default
workspace package.

```toml
[application]
asset_dir = "public"
sub_package = "my-crate"

[web.app]
[web.watcher]
[web.resource]
[web.resource.dev]
```

## Logging and telemetry

The logger installed by `dioxus::launch` defaults to `DEBUG` in development
and `INFO` in release. For logs before launch, call
`dioxus::logger::initialize_default()`. To choose a level, call
`dioxus::logger::init(Level::INFO)` before launch.

Dioxus sends Web logs through `tracing-wasm`, Desktop/server logs through a
`FmtSubscriber`, Android logs to logcat, and iOS logs to oslog.

The CLI telemetry introduced in 0.7.0 is on by default and records anonymized
command names, build-stage timings, stripped panic/error locations, a hashed
system identifier, target triple, versions, and CI status. Disable it with:

```sh
dx config set disable-telemetry true
TELEMETRY=false dx serve
```

## Web serving and output

### Development server

`[web.watcher].index_on_404` makes DX's development server fall back to the
index for router paths. `[web.resource.dev]` injects development-only assets,
`[[web.proxy]]` forwards a backend prefix while preserving path and query, and
`[[web.https]]` can use `mkcert` or supplied credentials.

```toml
[web]
pre_compress = true

[web.watcher]
index_on_404 = true

[[web.proxy]]
backend = "http://localhost:8000/api/"

[[web.https]]
enabled = true
mkcert = true
```

Release Web assets are Brotli-precompressed by default.
`[web.wasm_opt].level` accepts `z`/`s` for size or `1`-`4` for speed and may
retain debug symbols. `keep_names` has reached the WASM build path since
0.7.4.

`dx bundle` can generate AVIF assets, compress WASM, and minify Web output.
Split-WASM chunk filenames use content hashes since 0.7.6.

### Static hosts and GitHub Pages

Set `web.app.base_path` to the repository name, bundle to `docs`, move the
generated `public` contents up, and copy `index.html` to `404.html`:

```sh
dx bundle --out-dir docs
mv docs/public/* docs
cp docs/index.html docs/404.html
```

An external host needs its own fallback; `index_on_404` affects only the DX
development server. Base-path normalization trims surrounding slashes since
0.7.2.

### Preview package registries

> **Prerelease (`0.8.0-alpha.0`):** This guidance may change before stable release.

The CLI honors `NPM_CONFIG_REGISTRY` when downloading `esbuild`, enabling
private and mirrored registries.

## Desktop workflow

Desktop can overlay child webviews onto an existing WGPU or OpenGL window,
accept an application-owned event loop, and provide system-tray integration.
`new_window` has been async since 0.7.0. Tokio-backed file dialogs have also
been async since 0.7.1.

Tray configuration can control whether clicking the icon shows the main window
since 0.7.4. Windows icons appear both under `dx serve` and in `dx bundle`
packages since 0.7.6.

## Mobile workflow and configuration

`dx serve --platform android` supports physical devices through `adb reverse`;
simulators open automatically, and iPad targets are supported. Android's
application ID follows `bundle.identifier`, and its minimum SDK became 28 in
0.7.0.

Manual target setup includes:

```sh
rustup target add aarch64-linux-android armv7-linux-androideabi i686-linux-android x86_64-linux-android
rustup target add aarch64-apple-ios aarch64-apple-ios-sim
```

Android development also needs `JAVA_HOME`, `ANDROID_HOME`, `NDK_HOME`, and the
SDK emulator/platform-tools on `PATH`.

The CLI can generate `AndroidManifest.xml`, `Info.plist`, entitlements,
permissions, icons, splash screens, URL schemes, and `MainActivity.kt`. iOS
widgets, including Live Activity extensions, can be bundled since 0.7.4.

### Unified permissions

The old `permission!()` macro is removed. Declare app permissions in the
top-level `[permissions]` table. Unified keys include location
(`fine`/`coarse`), background location, camera, microphone, notifications,
`photos.read`, `photos.write`, Bluetooth, contacts, calendar, biometrics, NFC,
motion, health, and speech. Apple notification permission remains runtime-only.

```toml
[bundle]
identifier = "com.example.myapp"

[permissions]
location = { precision = "fine", description = "Use location for navigation" }
camera = { description = "Take profile photos" }
```

Native plugin libraries do not inject permissions; their applications must
declare them.

### Deep links and background modes

`[deep_links]` declares schemes, universal/App Link hosts, and optional path
patterns; an empty path list matches all paths. Platform-specific schemes and
Android intent filters extend unified values.

```toml
[deep_links]
schemes = ["myapp"]
hosts = ["example.com", "*.example.com"]
paths = ["/app/*", "/share/*"]

[background]
location = true
remote-notifications = true
processing = true
```

Other unified background switches are `audio`, `fetch`, `voip`, and
`bluetooth`. Apple-specific modes live under `[ios].background_modes`, while
Android foreground service capabilities use
`[android].foreground_service_types`.

### Platform-specific extensions

Top-level `[ios]`, `[android]`, and `[macos]` extend or override unified config.

- iOS: deployment target, URL schemes, background modes, document types,
  plist, entitlements, and raw `Info.plist`.
- Android: min/target SDK, features, URL schemes, foreground services, intent
  filters and data, query packages, permissions, and raw manifest.
- macOS: minimum system version, frameworks, URL schemes, category, document
  types, plist, entitlements, and raw `Info.plist`.

Cross-platform source can use ordinary `#[cfg(web)]`, `#[cfg(android)]`, and
`#[cfg(ios)]` branches for native system APIs.

## Bundling fundamentals

`dx bundle` produces Web output, Desktop packages, Android `.apk`, and iOS
`.ipa`/`.app`. Native bundles are host-bound. Select multiple desktop formats
with repeated `--package-types`.

```sh
dx bundle --desktop --package-types macos --package-types dmg
```

Linked native dynamic libraries and frameworks are copied into bundles. The
CLI, not Cargo profile `strip`, controls stripping as of 0.7.2. macOS output is
code-signed; Linux musl targets work through vendored `libgit2`. Fullstack
servers can also target server-side `wasm32` environments since 0.7.0.

Windows on ARM gained `wasm_opt` support and an
`aarch64-pc-windows-msvc` CLI artifact in 0.7.5. That release also passes the
FIPS flag to `candle.exe`. FreeBSD `esbuild` selection works since 0.7.6, and
JavaScript snippets are correctly classified as ESM, CommonJS, UMD, or generic
JavaScript since 0.7.7.

### Preview resource directories

> **Prerelease (`0.8.0-alpha.1`):** This guidance may change before stable release.

The bundler can copy an entire resource directory rather than requiring every
file to be enumerated.

## Resources, sidecars, and Windows runtime

`[bundle].resources` accepts globs. Each `external_bin` source file has its
target triple appended for packaging but is addressed at runtime by the
unsuffixed name.

```toml
[bundle]
resources = ["main.css", "**/*.png"]
external_bin = ["bin/helper"]
```

Windows WebView2 modes include skip, download, embedded bootstrapper, offline
installer, and fixed runtime. Custom signing commands receive the binary at
`%1`; keep a WiX `upgrade_code` stable across upgrades.

Built-in Windows signing fields include certificate thumbprint, digest
algorithm, timestamp URL, and timestamping protocol.

## Installer-specific controls

### Debian

`[bundle.deb]` supports dependencies, provisions, conflicts, replacements,
section, priority, changelog, desktop template, lifecycle scripts, and a
destination-to-source `files` map. Source paths are relative to the current
working directory.

### macOS

`[bundle.macos]` supports frameworks, minimum version, signing identity and
provider, entitlements, replacement `Info.plist`, and files mapped under
`Contents`. `hardened_runtime = false` can be useful for a less-strict ad-hoc
signature.

### WiX and NSIS

`[bundle.windows.wix]` controls templates/fragments, component and merge
references, languages, licenses, artwork, elevated updates, and MSI version.
`[bundle.windows.nsis]` separately controls its template, artwork, scope,
languages/translations, start-menu folder, hooks, and minimum WebView2.

## Deployment

A Fullstack Web bundle contains a `public` client directory beside a `server`
executable. Deploy both and set `IP=0.0.0.0` in containers; the launch path
reads `IP` and `PORT`.

```sh
IP=0.0.0.0 PORT=8080 ./server
```

## Size-oriented release builds

A nightly toolchain can rebuild `std` with immediate aborts and combine
size optimization, LTO, virtual-function elimination, and reduced location
metadata. `.cargo/config.toml` profile settings override matching
`Cargo.toml` settings.

```toml
[unstable]
build-std = ["std", "panic_abort", "core", "alloc"]
build-std-features = ["panic_immediate_abort"]

[build]
rustflags = ["-Clto", "-Zvirtual-function-elimination", "-Zlocation-detail=none"]

[profile.release]
opt-level = "z"
lto = true
codegen-units = 1
panic = "abort"
```
