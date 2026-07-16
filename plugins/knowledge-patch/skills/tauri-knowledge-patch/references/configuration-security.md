# Configuration, Capabilities, Permissions, and Security

Use this reference to migrate the application configuration hierarchy, make application and plugin commands controllable, bind grants to windows/webviews and platforms, enforce scope, and configure CSP or asset access.

## Contents

- [Configuration hierarchy](#configuration-hierarchy)
- [Security layers](#security-layers)
- [Application command registration](#register-application-commands-in-the-manifest)
- [Capabilities and filters](#capability-inclusion)
- [Permissions and scopes](#permission-files-and-identifiers)
- [Command pruning](#capability-driven-command-pruning-240)
- [Headers, asset protocol, CSP, and isolation](#webview-response-headers-210)

## Configuration hierarchy

Apply these structural moves:

- Remove the old `package` object. Put `productName`, `version`, and `identifier` at the root.
- Rename root `tauri` to `app` and move its `bundle` object to root `bundle`.
- Rename build keys to `frontendDist` and `devUrl`; `devUrl` accepts URLs only.
- Move the security pattern to `app.security.pattern` and the global frontend API flag to `app.withGlobalTauri`.
- Move updater configuration to `plugins.updater`. The old `UpdaterEvent` type is removed, so also replace code that consumed it.
- Put platform packaging under `bundle.macOS.dmg`, `bundle.linux.deb`, and `bundle.linux.appimage`.
- Put shared license settings at `bundle.license` and `bundle.licenseFile`.
- Configure file dropping with `app.window.dragDropEnabled`.

## Security layers

Treat command authorization as three distinct layers:

1. A permission determines whether a frontend invocation may reach a command.
2. A capability binds permissions and scopes to windows or webviews, platforms, and optionally remote origins.
3. The command implementation interprets and enforces the attached scope data.

Tauri core attaches configured scope to an allowed invocation but does not understand application- or plugin-specific scope semantics. Never assume that reaching a scoped command means its arguments have passed scope validation.

Native code can call `WebviewWindow::resolve_command_scope()` to resolve and check configured command scope at runtime (`2.1.0`). Plugin commands can inject typed `CommandScope` or `GlobalScope`; see [plugin-mobile-development.md](plugin-mobile-development.md).

## Register application commands in the manifest

An application command registered only through `invoke_handler()` is callable by every window and webview by default. List it in the build-time application manifest to make it subject to permissions and capabilities.

```rust
fn main() {
    tauri_build::try_build(
        tauri_build::Attributes::new()
            .app_manifest(
                tauri_build::AppManifest::new()
                    .commands(&["your_command"]),
            ),
    )
    .unwrap();
}
```

## Capability inclusion

If `app.security.capabilities` is absent or an empty list, Tauri includes every capability file under `./capabilities/`. Once the list has entries, it becomes an explicit selection: each entry is a capability identifier or an inline capability object.

```json
{
  "app": {
    "security": {
      "capabilities": [
        "main-window",
        {
          "identifier": "drag-window",
          "permissions": ["core:window:allow-start-dragging"]
        }
      ]
    }
  }
}
```

Capability files ending in `.json5` are recognized only when the Cargo `config-json5` feature is enabled. Support for this combination was corrected in `2.2.0`.

## Platform and remote-origin filters

A capability applies to every target unless `platforms` restricts it with `linux`, `macOS`, `windows`, `iOS`, or `android`.

Bundled frontend code may use granted APIs by default. Remote content may not; add `remote.urls` only to explicitly allow matching remote origins to use the capability's commands.

```json
{
  "$schema": "../gen/schemas/remote-schema.json",
  "identifier": "remote-mobile-scanner",
  "windows": ["main"],
  "remote": { "urls": ["https://*.example.com"] },
  "platforms": ["iOS", "android"],
  "permissions": ["nfc:allow-scan"]
}
```

## Generated schemas

`tauri-build` writes ACL-aware JSON schemas to `src-tauri/gen/schemas`. Point capability JSON or TOML at `../gen/schemas/desktop-schema.json` or `../gen/schemas/mobile-schema.json` for validation and permission-name completion. Remote-capability files may use the generated remote schema.

## Permission files and identifiers

Plugins define permissions in `permissions/<identifier>.json` or `.toml`. `permissions/default.json` or `.toml` defines the plugin's special default permission set. Application-owned extensions live under `src-tauri/permissions`.

Adding a plugin with the Tauri CLI adds that plugin's default permission to the application configuration. Qualified identifiers look like `<name>:default`; omit the automatically supplied `tauri-plugin-` crate prefix. A qualified identifier may contain at most 116 characters.

## Permission sets and scope precedence

Scope values are defined by the application or plugin and must be Serde-serializable. A TOML `[[set]]` can combine command permissions and scope-only permissions into one reusable grant.

```toml
[[set]]
identifier = "allow-home-read-extended"
permissions = ["fs:read-files", "fs:scope-home", "fs:allow-mkdir"]
```

A scope-only permission can extend a plugin's global scope. A scope paired with an enabled command constrains only that command. When composed scopes overlap, every deny scope takes precedence over every allow scope.

## Capability-driven command pruning (`2.4.0`)

`build.removeUnusedCommands` lets build scripts and macros remove commands unused by configured capabilities.

```json
{
  "build": {
    "removeUnusedCommands": true
  }
}
```

Dynamically added ACLs are not visible during this analysis. Do not enable pruning when a command is referenced only by a permission added at runtime, or it may be removed from the binary.

## Webview response headers (`2.1.0`)

`app.security.headers` adds headers to every HTTP response that Tauri sends to a webview. It does not alter IPC messages or error responses.

```json
{
  "app": {
    "security": {
      "headers": {
        "Cross-Origin-Opener-Policy": "same-origin"
      }
    }
  }
}
```

## Asset-protocol scope

The asset protocol accepts either a list of allowed globs or an object with `allow`, `deny`, and `requireLiteralLeadingDot`. Deny patterns take precedence. Patterns may begin with base-directory variables such as `$RESOURCE`, `$APPDATA`, and `$HOME`.

`requireLiteralLeadingDot` defaults to `true` on Unix and `false` on Windows.

```json
{
  "app": {
    "security": {
      "assetProtocol": {
        "enable": true,
        "scope": {
          "allow": ["$APPDATA/**"],
          "deny": ["$APPDATA/private/**"],
          "requireLiteralLeadingDot": true
        }
      }
    }
  }
}
```

## Content Security Policy rewriting

At compile time, Tauri parses frontend assets and adds nonce and hash sources to the configured CSP.

Set `dangerousDisableAssetCspModification` to `true` to suppress every injection, or to an array of directive names to suppress only those directives. `devCsp` replaces `csp` during development.

```json
{
  "app": {
    "security": {
      "csp": "default-src 'self'",
      "devCsp": "default-src 'self'; connect-src http://localhost:5173",
      "dangerousDisableAssetCspModification": ["style-src"]
    }
  }
}
```

## Isolation pattern

The security pattern defaults to `{ "use": "brownfield" }`. Isolation mode requires `options.dir` to point to a directory whose isolation application contains `index.html`.

```json
{
  "app": {
    "security": {
      "pattern": {
        "use": "isolation",
        "options": { "dir": "../isolation" }
      }
    }
  }
}
```
