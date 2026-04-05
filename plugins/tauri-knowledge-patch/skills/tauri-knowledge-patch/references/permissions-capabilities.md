# Permissions & Capabilities

Replaces the v1 `tauri.allowlist`. All command access is controlled through **capabilities** (which windows get which permissions) and **permissions** (which commands are allowed, with optional scopes).

## Capability Files

Capability files go in `src-tauri/capabilities/` as JSON or TOML. All files in that directory are auto-enabled unless explicitly listed in `app.security.capabilities`.

```json
{
  "$schema": "../gen/schemas/desktop-schema.json",
  "identifier": "main-capability",
  "windows": [
    "main"
  ],
  "permissions": [
    "core:path:default",
    "core:event:default",
    "core:window:default",
    "core:app:default",
    "core:menu:default",
    "core:tray:default",
    "fs:read-files",
    "fs:scope-home"
  ]
}
```

## Platform-Specific Capabilities

Use `"platforms"` to restrict a capability to specific targets:

```json
{
  "identifier": "desktop-capability",
  "platforms": ["linux", "macOS", "windows"],
  "windows": ["main"],
  "permissions": ["shell:allow-open"]
}
```

Mobile platforms: `["iOS", "android"]`.

## Remote URL Access

Grant permissions to remote URLs instead of local windows:

```json
{
  "identifier": "remote-capability",
  "remote": { "urls": ["https://*.example.com"] },
  "permissions": ["core:event:default"]
}
```

## Custom App Permissions

Define custom permission sets in `src-tauri/permissions/<name>.toml`:

```toml
[[set]]
identifier = "allow-home-read"
description = "Read access to home directory"
permissions = ["fs:read-files", "fs:scope-home"]
```
