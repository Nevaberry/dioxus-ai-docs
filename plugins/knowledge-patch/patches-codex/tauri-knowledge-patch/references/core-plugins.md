# Core Plugins

Use this reference for dialog, filesystem, HTTP, store, and updater integration. Pair it with [configuration-security.md](configuration-security.md) when defining frontend grants.

## Contents

- [Dialog](#dialog)
- [Filesystem](#filesystem)
- [HTTP](#http)
- [Store](#store)
- [Updater signing and artifacts](#updater-signing-and-artifacts)
- [Updater endpoints and runtime controls](#updater-endpoints-and-contracts)
- [Windows updater installation](#windows-updater-installation)

## Dialog

JavaScript dialog calls are asynchronous. Rust message and file builders expose callback-based methods and `blocking_*` variants.

Android and iOS do not support folder picking. The default frontend grant enables message, open, and save. Deprecated ask and confirm permissions are aliases for `allow-message` until v3.

```rust
use tauri_plugin_dialog::DialogExt;

let picked = app.dialog().file().blocking_pick_file();
app.dialog()
    .message("Saved")
    .show(|accepted| println!("{accepted}"));
```

## Filesystem

### Paths, operations, and scope

The filesystem API rejects `..` traversal. Pass a path relative to `baseDir`, or construct an absolute path with the path API.

Frontend access needs both an operation permission and a matching path scope. Scope entries have shape `{ "path": "..." }`.

- `$APPDATA/*` covers direct children only.
- To cover the directory and every descendant, include both `$APPDATA` and `$APPDATA/**/*`.
- `fs:default` grants recursive reads and creation of application-specific directories, but not general writes.

```json
{
  "permissions": [
    "fs:default",
    "fs:allow-write-text-file",
    {
      "identifier": "fs:scope",
      "allow": [{ "path": "$APPDATA/settings.json" }]
    }
  ]
}
```

### Handles and streams

- `create()` truncates an existing file.
- `open()` is read-only by default.
- `{ append: true }` implies write access.
- `create` requires either write or append.
- `createNew` and `truncate` require write.
- `readTextFileLines()` yields an asynchronous line stream.
- `watch()` debounces events; `watchImmediate()` reports immediately.
- Directory watches are non-recursive unless recursion is explicitly requested.

### Platform prerequisites

`$RESOURCES` is not writable on Linux or macOS. Windows MSI/NSIS installations using `perMachine` or `both` require administrator access to write there. Mobile filesystem access defaults to the application folder.

Android access to audio, cache, documents, downloads, picture, public, or video directories requires `READ_EXTERNAL_STORAGE` and `WRITE_EXTERNAL_STORAGE` in `gen/android/app/src/main/AndroidManifest.xml`.

iOS requires `src-tauri/gen/apple/PrivacyInfo.xcprivacy` to declare `NSPrivacyAccessedAPICategoryFileTimestamp` with reason `C617.1`.

## HTTP

`http:default` enables the fetch command workflow but grants no origins. Add URL scope before frontend HTTP can reach a server. Deny URLs can carve exceptions out of an allowed wildcard.

```json
{
  "permissions": [{
    "identifier": "http:default",
    "allow": [{ "url": "https://*.example.com" }],
    "deny": [{ "url": "https://private.example.com" }]
  }]
}
```

## Store

`load(path, options)` inserts the store into the application resource table. Rust and JavaScript reuse one instance by path, and later options for that path are ignored. Rust can evict the shared resource with `close_resource()`.

Values crossing the Rust/JavaScript boundary must be compatible with `serde_json::Value`.

Stores save during graceful exit. Autosave uses a 100 ms debounce by default; pass a numeric delay to change it or `false` to disable debounced writes. `LazyStore` defers loading until first access.

```javascript
import { load } from "@tauri-apps/plugin-store";

const store = await load("store.json", { autoSave: false });
await store.set("theme", "dark");
await store.save();
```

## Updater signing and artifacts

Signature verification cannot be disabled.

- `plugins.updater.pubkey` contains the public key itself, not a key path or URL.
- Each server-provided `signature` contains the signature itself, not a path or URL.
- Losing the private key prevents future updates to existing installations.
- Builds read the key path or key contents from `TAURI_SIGNING_PRIVATE_KEY` and an optional password from `TAURI_SIGNING_PRIVATE_KEY_PASSWORD`; do not expect `.env` to provide these automatically.

With `createUpdaterArtifacts: true`:

- Linux signs the AppImage.
- macOS emits a signed `.app.tar.gz` and its signature.
- Windows signs MSI and NSIS installers directly.

## Updater endpoints and contracts

Production endpoints require TLS unless `dangerousInsecureTransportProtocol` is enabled. Endpoint URLs may interpolate `{{current_version}}`, `{{target}}`, and `{{arch}}`.

When multiple endpoints are configured, only a non-2xx response advances to the next one. A malformed 2xx response does not trigger fallback.

### Static manifest

A static JSON manifest requires `version`, plus a `url` and `signature` for each included `OS-ARCH` platform. Tauri validates the complete manifest before comparing its version.

### Dynamic endpoint

Return HTTP 204 when no update exists. Return HTTP 200 with `url`, `version`, and `signature` when an update exists.

## Runtime updater controls

JavaScript `check()` accepts a proxy, timeout in milliseconds, headers, and a custom target.

Rust-only updater builders may replace endpoints or the public key at runtime and customize version comparison. The default comparator accepts only versions greater than the current version, so rollbacks require a comparator. Installing an update does not inherently require an immediate restart.

```rust
use tauri_plugin_updater::UpdaterExt;

let update = app
    .updater_builder()
    .version_comparator(|current, update| update.version != current)
    .build()?
    .check()
    .await?;
```

## Windows updater installation

Windows `installMode` defaults to `passive`, which displays progress without interaction. `basicUi` requires user interaction. `quiet` cannot request elevation and works only for per-user installs or when the application is already elevated.

Installing an update automatically quits the application on Windows. Register Rust `on_before_exit` for work that must complete first.
