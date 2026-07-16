# CLI, Platforms, Bundling, and Tooling

## Install and inspect the toolchain

The direct installer removes the old `cargo-binstall` prerequisite and honors `CARGO_HOME`. Version mismatches produce guidance, and `dx self-update` updates the CLI. Since 0.7.9, `dx --version` includes the current Git SHA and Cargo-installed CLI binaries contain the version metadata needed by self-update.

```sh
curl -fsSL https://dioxus.dev/install.sh | bash
dx --version
dx self-update
```

`dx doctor` diagnoses missing toolchains and native prerequisites. Desktop needs WebView2 on Windows and WebKitGTK 4.1 plus xdotool/libxdo on Linux. iOS needs Xcode and its SDKs; Android needs the SDK and NDK.

The 0.8.0-alpha.0 CLI must be source-installed with locked dependencies because unconstrained resolution can choose an incompatible upstream set.

```sh
cargo install dioxus-cli --locked
```

## Create and inspect projects

`dx new` offers Bare-Bones, Jumpstart, and Workspace layouts. Workspace starts separate Web, Desktop, and Mobile crates. `dx new --template gh:owner/repository` clones a custom GitHub template, while `dx init` initializes the current directory.

```sh
dx new
dx new --template gh:dioxuslabs/dioxus-template
dx init
```

`dx print` emits structured project information, including Cargo and linker arguments, so external tools can reproduce DX's build context. `dx translate` converts HTML from a file or raw string into RSX, writes stdout unless `--output` is set, and optionally wraps the result in a component.

```sh
dx print
dx translate --file index.html --output index.rs
dx translate --raw "<div>Hello world</div>" --component
```

`dx components` manages the `dioxus-component` registry; `dx components add <name>` copies component source into the application rather than adding an opaque binary dependency.

## Cargo features and launch configuration

Renderer support is selected as features on the main `dioxus` crate, and all platforms use `dioxus::launch`. `dx serve --platform` activates the matching build feature. Fullstack builds client and server in parallel.

The default crate features are `signals`, `macro`, `html`, `hooks`, and `hot-reload`. Optional `router` both re-exports the router and enables current-platform integration; `logger` installs the default tracing subscriber. A project disabling defaults must explicitly restore every layer it uses.

```toml
[dependencies]
dioxus = { version = "0.7", default-features = false, features = [
    "signals", "macro", "html", "hooks", "hot-reload",
    "router", "logger", "web",
] }
```

The former Fullstack-wide `Config` is gone. Supply server, Web, and Desktop settings independently through `LaunchBuilder` and keep shared settings such as the root element consistent.

```rust
LaunchBuilder::new()
    .with_cfg(server_only! { ServeConfigBuilder::default().root_id("app") })
    .with_cfg(web! { dioxus::web::Config::default().rootname("app") })
    .launch(app);
```

Ordinary conditional compilation can branch to system APIs with `#[cfg(web)]`, `#[cfg(android)]`, and `#[cfg(ios)]`.

## Development server and hot reload

The rewritten CLI stores build output under `target/dx`. During `dx serve`, `r` rebuilds and `v`/`t` adjust log verbosity. WebAssembly tracing and panics are captured, and symbolized stack traces can link to the editor.

Targets can be selected with `--platform` or shorthand flags.

```sh
dx serve --web
dx serve --desktop
dx serve --platform ios
dx serve --platform android
dx serve --platform fullstack
```

Mobile serving builds the same `main.rs` used on other platforms and includes simulators, logging, hot reload, and asset bundling; the older `cdylib` entrypoint and manual binding layer are unnecessary. Simulators open automatically. Android physical-device serving uses `adb reverse`; iPad targets are supported.

DX can also serve ordinary Rust projects and run named packages as client/server peers. Cargo-style `--offline` and `--locked` are accepted.

```sh
dx serve @client --package client @server --package server
```

The 0.8.0-alpha.0 watcher enables Rust hot-patching by default and watches `Cargo.toml`, `[web.watcher].watch_path`, and files discovered from Cargo dependency data. Stable hot-patch behavior and limitations are detailed in [renderers-testing-internals.md](renderers-testing-internals.md).

## Build diagnostics, logs, and debugging

`dx build --raw-json-diagnostics` emits raw machine-readable compiler diagnostics (since 0.7.1). `dx bundle --json-output` emits structured command logs so CI can discover artifacts. The global `--log-to-file` captures all DX logs independently of verbosity.

```sh
dx build --raw-json-diagnostics
dx bundle --json-output
dx --log-to-file dx.log serve
```

Pressing `d` in `dx serve` starts an LLDB session through a VS Code-based editor on Web, Desktop, or Mobile. Web opens a separate Chrome instance, and the DWARF symbols extension provides demangled Rust names. Cursor became a supported editor in 0.7.6.

The default subscriber initialized by `dioxus::launch` logs at `DEBUG` in development and `INFO` in release. Call `dioxus::logger::initialize_default()` to log before launch, or use `dioxus::logger::init` to choose a level. Web uses `tracing-wasm`, Desktop/server use `FmtSubscriber`, Android sends to logcat, and iOS sends to oslog.

```rust
fn main() {
    dioxus::logger::init(tracing::Level::INFO)
        .expect("failed to init logger");
    dioxus::launch(App);
}
```

DX telemetry is enabled by default and includes anonymized command names, stage timings, stripped error locations, a hashed system ID, target triple, version, and CI status. Disable it persistently, at runtime, or at compile time.

```sh
dx config set disable-telemetry true
TELEMETRY=false dx serve
```

Generate shell completions with the 0.7.6 `completions` subcommand.

```sh
dx completions
```

## `Dioxus.toml` foundations

The `[application]`, `[web.app]`, `[web.watcher]`, `[web.resource]`, and `[web.resource.dev]` tables are required even when empty. `asset_dir` is copied to the output; `sub_package` chooses the default workspace package.

```toml
[application]
asset_dir = "public"
sub_package = "my-crate"

[web.app]
[web.watcher]
[web.resource]
[web.resource.dev]
```

Configured icon paths resolve relative to the crate, not the CLI working directory (since 0.7.2). The CLI overrides Cargo profile `strip` and performs stripping itself with LLVM tooling. Web base paths are normalized by trimming surrounding slashes.

## Web serving and release output

`Dioxus.toml` can make the development server fall back to the index for routes, inject development-only resources, proxy a backend prefix while retaining path and query, and serve HTTPS through `mkcert` or supplied certificates. Release assets are Brotli-precompressed by default. `[web.wasm_opt]` accepts `z`/`s` for size or `1`–`4` for speed and can retain debug symbols.

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

[web.wasm_opt]
level = "z"
debug = false
```

A custom `index.html` must keep `<div id="main"></div>` as the mount point; custom templates still hot-reload.

For GitHub Pages, set `web.app.base_path` to the repository, bundle into `docs`, move `docs/public` contents upward, and copy `index.html` to `404.html`. `index_on_404` affects DX's server only; external hosts need their own SPA fallback.

```sh
dx bundle --out-dir docs
mv docs/public/* docs
cp docs/index.html docs/404.html
```

## Desktop and mobile application settings

Desktop `new_window` is asynchronous as of 0.7.0. File-dialog operations using Tokio became asynchronous in 0.7.1; await both rather than consuming results synchronously. Desktop configuration can decide whether clicking the tray icon shows the main window (since 0.7.4).

`Dioxus.toml` can drive generated Android manifests, Apple property lists and entitlements, permissions, icons, splash screens, URL schemes, and `MainActivity.kt`. Android's application ID follows `bundle.identifier`, and the minimum SDK default moved to 28. Windows application icons are applied during both `dx serve` and `dx bundle` as of 0.7.6.

Manual Android setup installs all four supported Rust targets and configures `JAVA_HOME`, `ANDROID_HOME`, `NDK_HOME`, emulator, and platform-tools paths. iOS uses separate device and Apple-silicon simulator targets.

```sh
rustup target add aarch64-linux-android armv7-linux-androideabi i686-linux-android x86_64-linux-android
rustup target add aarch64-apple-ios aarch64-apple-ios-sim
```

Dioxus can package iOS widgets, including Live Activity extensions, alongside the primary app as of 0.7.4.

## Unified permissions, links, and background modes

The `permission!()` macro is removed. Put application permissions in top-level `[permissions]`; the CLI maps unified entries to Android names and Apple usage-description keys. Entries include `location` (`fine` or `coarse`), `background_location`, `camera`, `microphone`, `notifications`, `photos.read`, `photos.write`, `bluetooth`, `contacts`, `calendar`, `biometrics`, `nfc`, `motion`, `health`, and `speech`. Apple notification permission remains runtime-only. Native-plugin libraries cannot inject permissions and must tell the app which entries to add.

```toml
[bundle]
identifier = "com.example.myapp"

[permissions]
location = { precision = "fine", description = "Use location for navigation" }
camera = { description = "Take profile photos" }
```

`[deep_links]` declares custom schemes, universal/App Link hosts, and path patterns; an empty path list matches all paths. Platform-specific URL schemes and Android intent filters extend unified values. Unified `[background]` switches include `location`, `remote-notifications`, `processing`, `audio`, `fetch`, `voip`, and `bluetooth`. Apple background modes and Android foreground-service types extend them.

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

Top-level `[ios]`, `[android]`, and `[macos]` tables extend or override unified configuration:

- iOS: `deployment_target`, `url_schemes`, `background_modes`, `[[ios.document_types]]`, `[ios.plist]`, `[ios.entitlements]`, and `[ios.raw].info_plist`.
- Android: `min_sdk`, `target_sdk`, `features`, `url_schemes`, `foreground_service_types`, `[[android.intent_filters]]`, `[[android.intent_filters.data]]`, `[android.queries].packages`, `[android.permissions]`, and `[android.raw].manifest`.
- macOS: `minimum_system_version`, `frameworks`, `url_schemes`, `category`, `[[macos.document_types]]`, `[macos.plist]`, `[macos.entitlements]`, and `[macos.raw].info_plist`.

## Bundles and deployment

`dx bundle` emits Desktop installers, Android `.apk`, iOS `.ipa`/`.app`, and Web output. Native dynamic libraries and frameworks are copied automatically, and Fullstack server builds may target server-side `wasm32` environments. Desktop formats are host-platform and host-architecture only, selected with repeatable `--package-types`.

```sh
dx bundle --desktop --package-types macos --package-types dmg
```

`[bundle].resources` accepts globs. Each `external_bin` source file must have the target triple appended on disk but is addressed at runtime by the unsuffixed name.

```toml
[bundle]
resources = ["main.css", "**/*.png"]
external_bin = ["bin/helper"]
```

For Fullstack Web, `dx bundle --web` writes a `public` client directory beside a server executable. Deploy both, run the executable, and set `IP=0.0.0.0` in a container; `dioxus::launch` reads `IP` and `PORT`.

```sh
IP=0.0.0.0 PORT=8080 ./server
```

## Linux and macOS packaging

Linux musl targets use a vendored `libgit2` as of 0.7.2. FreeBSD is detected when choosing esbuild tooling as of 0.7.6.

`[bundle.deb]` controls dependencies, provisions, conflicts, replacements, section, priority, changelog, desktop template, lifecycle scripts, and payload files. File-map keys are package destinations; values are sources relative to the current working directory.

```toml
[bundle.deb]
section = "utils"
priority = "optional"
post_install_script = "packaging/post-install.sh"
files = { "/usr/share/example/default.toml" = "packaging/default.toml" }
```

macOS apps are code-signed during build and packaging. `[bundle.macos]` can add frameworks, set the minimum OS, identity/provider, entitlements, replacement `Info.plist`, files under `Contents`, and hardened runtime. Disable hardened runtime when a less-strict ad-hoc signature is needed.

```toml
[bundle.macos]
minimum_system_version = "12.0"
entitlements = "packaging/entitlements.plist"
info_plist_path = "packaging/Info.plist"
hardened_runtime = false
files = { "Resources/default.toml" = "packaging/default.toml" }
```

## Windows packaging

Windows WebView2 installation modes include skip, download, embedded bootstrapper, offline installer, and fixed runtime. A custom signing command receives the binary at `%1`; a WiX `upgrade_code` must remain stable across releases.

Built-in signing under `[bundle.windows]` takes a certificate thumbprint, digest algorithm, timestamp URL, and explicit timestamp protocol.

```toml
[bundle.windows]
certificate_thumbprint = "A1B2C3D4E5F6..."
digest_algorithm = "sha-256"
timestamp_url = "http://timestamp.digicert.com"
tsp = true
```

WiX and NSIS have separate configuration. WiX supports templates/fragments, component/feature/merge refs, languages, licensing, artwork, elevated updates, and an MSI version. NSIS independently controls templates/artwork, install scope, translations, start-menu folder, hooks, and minimum WebView2.

```toml
[bundle.windows.wix]
license = "packaging/license.rtf"
banner_path = "packaging/banner.bmp"
enable_elevated_update_task = true

[bundle.windows.nsis]
license = "packaging/license.txt"
display_language_selector = true
start_menu_folder = "Example"
installer_hooks = "packaging/hooks.nsh"
```

Windows on ARM gained `wasm_opt` support and an `aarch64-pc-windows-msvc` CLI artifact in 0.7.5. That release also passes the FIPS flag to `candle.exe` for compliant bundling.

## Release-size tuning

For a minimum-size release, a nightly `.cargo/config.toml` can rebuild `std` with immediate aborts and combine size optimization, LTO, virtual-function elimination, and reduced location metadata. Config-file profile values override corresponding `Cargo.toml` profile settings.

```toml
[unstable]
build-std = ["std", "panic_abort", "core", "alloc"]
build-std-features = ["panic_immediate_abort"]

[build]
rustflags = ["-Clto", "-Zvirtual-function-elimination", "-Zlocation-detail=none"]

[profile.release]
opt-level = "z"
debug = false
lto = true
codegen-units = 1
panic = "abort"
incremental = false
```

## Documentation context and ecosystem pointers

Dioxus publishes a first-party `llms.txt` generated from its documentation, and current templates can include condensed release context. The documented internationalization helper is `dioxus-i18n`.
