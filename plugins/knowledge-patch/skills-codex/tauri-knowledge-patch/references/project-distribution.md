# Project Setup and Distribution

Use this reference when defining project build inputs and hooks or producing platform installers and updater artifacts. Read [configuration-security.md](configuration-security.md) for the configuration hierarchy and security settings, and [windows-webviews-runtime.md](windows-webviews-runtime.md) for per-webview settings.

## Contents

- [Product and version identity](#product-binary-and-version-identity)
- [Build inputs and hooks](#build-inputs-and-hooks)
- [Bundle resources and Apple overrides](#bundle-resources-and-local-tools)
- [Windows webview installation](#windows-webview-installation)
- [Updater artifacts and NSIS](#updater-artifact-compatibility)
- [Windows signing and WiX identity](#windows-downgrade-and-signing-behavior)
- [Project setup and packaging](#project-setup-and-packaging-workflow)

## Product, binary, and version identity

`mainBinaryName` makes `tauri build` rename Cargo's binary and makes `tauri bundle` package that renamed file. Omit the platform extension.

The root `version` accepts either a semver string or a path to `package.json`. If absent, Tauri reads the Cargo package version.

```json
{
  "productName": "Desktop Client",
  "mainBinaryName": "desktop-client",
  "version": "../package.json"
}
```

### Android version codes

`bundle.android.autoIncrementVersionCode` reads the last value from the generated Android project's `tauri.properties` and increments it for each build. Remove that file from the generated project's `.gitignore` and commit it.

Without auto-increment or an explicit `versionCode`, the derived value is:

```text
major * 1_000_000 + minor * 1_000 + patch
```

```json
{
  "bundle": { "android": { "autoIncrementVersionCode": true } }
}
```

## Build inputs and hooks

### Structured hooks

Build hooks accept a string or the `{ "script", "cwd" }` object shape. `beforeDevCommand` additionally accepts `wait`, which defaults to `false`.

```json
{
  "build": {
    "beforeDevCommand": {
      "script": "pnpm dev",
      "cwd": "../web",
      "wait": false
    }
  }
}
```

Dev, build, and bundle hooks receive these target values:

- `TAURI_ENV_PLATFORM`
- `TAURI_ENV_ARCH`
- `TAURI_ENV_FAMILY`
- `TAURI_ENV_PLATFORM_VERSION`
- `TAURI_ENV_PLATFORM_TYPE`
- `TAURI_ENV_DEBUG`

Use them instead of assuming the host and target match.

### Frontend distribution modes

`build.frontendDist` accepts:

- A directory recursively embedded into the application, with `index.html` as its entry point.
- An array of files, each placed at the embedded root.
- A custom-protocol or remote URL, which embeds no frontend assets.

If `devUrl` is absent, the CLI can serve `frontendDist` through a built-in development server with simple hot reload.

```json
{
  "build": {
    "frontendDist": ["../dist/index.html", "../dist/app.js"]
  }
}
```

## Bundle resources and local tools

An array in `bundle.resources` preserves the source directory structure. A source-to-destination map controls placement, but files matched by a map glob are flattened into its destination directory.

Set `bundle.useLocalToolsDir: true` to cache tools such as WiX and NSIS under `target/.tauri/` instead of a user-level platform cache.

```json
{
  "bundle": {
    "resources": { "docs/**/*.md": "website-docs/" },
    "useLocalToolsDir": true
  }
}
```

For AppImage audio/video support, enable `bundle.linux.appimage.bundleMediaFramework`. It adds the required GStreamer dependencies and approximately 15–35 MB to the bundle.

## Apple bundle overrides

On iOS, Tauri merges an explicit `bundle.iOS.infoPlist` and also discovers `Info.plist` and `Info.ios.plist` beside the Tauri configuration. Regenerate the iOS project after changing bundled frameworks. `APPLE_DEVELOPMENT_TEAM` overrides the configured `developmentTeam`.

On macOS, set `minimumSystemVersion` to `null` to remove both `LSMinimumSystemVersion` and `MACOSX_DEPLOYMENT_TARGET`. This setting is ignored by `tauri dev`.

## Windows webview installation

`bundle.windows.webviewInstallMode.type` supports:

Choose among these modes by balancing installation-time network availability against bundle size.

| Mode | Behavior |
| --- | --- |
| `skip` | Do not install WebView2. |
| `downloadBootstrapper` | Download the bootstrapper at install time. |
| `embedBootstrapper` | Add roughly 1.8 MB. |
| `offlineInstaller` | Add roughly 127 MB. |
| `fixedRuntime` | Add roughly 180 MB and require the extracted runtime `path`. |

Updater bundles always use `downloadBootstrapper`.

```json
{
  "bundle": {
    "windows": {
      "webviewInstallMode": { "type": "offlineInstaller", "silent": true },
      "nsis": { "minimumWebview2Version": "125.0.2535.41" }
    }
  }
}
```

## Updater artifact compatibility

`bundle.createUpdaterArtifacts` accepts a boolean or `"v1Compatible"`. The string form produces legacy zipped updater bundles and their signatures. Read [core-plugins.md](core-plugins.md) before configuring signing, endpoints, or installation behavior.

```json
{ "bundle": { "createUpdaterArtifacts": "v1Compatible" } }
```

## NSIS installation and hooks

`installMode` supports `currentUser`, `perMachine`, and `both`. The `both` mode still requires administrator access even if the user selects a per-user install.

An `installerHooks` `.nsh` file may define:

- `NSIS_HOOK_PREINSTALL`
- `NSIS_HOOK_POSTINSTALL`
- `NSIS_HOOK_PREUNINSTALL`
- `NSIS_HOOK_POSTUNINSTALL`

The hooks surround installer file, registry, and shortcut changes.

## Windows downgrade and signing behavior

Windows bundles permit downgrades by default. Set `allowDowngrades` to `false` to reject an install over a newer version.

A custom `signCommand` must include `%1`, which Tauri replaces with the binary path. Use object form when commands or arguments contain spaces, particularly with a cross-platform tool instead of Windows-only `signtool.exe`.

```json
{
  "bundle": {
    "windows": {
      "allowDowngrades": false,
      "signCommand": {
        "cmd": "osslsigncode",
        "args": ["sign", "-in", "%1"]
      }
    }
  }
}
```

### Stable WiX identity

Keep WiX `upgradeCode` unchanged between releases. Otherwise Windows treats the update as a different application. The default UUID v5 derives from `<productName>.exe.app.x64`; pin it before renaming the product. Run `tauri inspect wix-upgrade-code` to print the generated value.

## Project setup and packaging workflow

`create-tauri-app` includes a .NET frontend option with a Blazor template, alongside Rust and TypeScript/JavaScript choices.

```sh
npm create tauri-app@latest
# Choose .NET, then Blazor.
```

`tauri build` packages configured bundles by default. Separate compilation and packaging with `--no-bundle` followed by the standalone `bundle` command; the latter can select formats or merge distribution-specific configuration.

```sh
cargo tauri build --no-bundle
cargo tauri bundle --bundles app,dmg
cargo tauri bundle --bundles app --config src-tauri/tauri.appstore.conf.json
```
