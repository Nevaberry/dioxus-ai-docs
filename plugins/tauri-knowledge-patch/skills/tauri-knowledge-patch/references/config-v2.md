# Config v2 Structure

`tauri.conf.json` restructured in Tauri 2.0. `tauri` key renamed to `app`. `package` removed; `productName`, `version`, `identifier` are top-level. Must add `mainBinaryName` matching `productName`. `build.distDir` replaced by `frontendDist`, `build.devPath` replaced by `devUrl`. `tauri.allowlist` removed entirely (replaced by capabilities). `tauri.systemTray` moved to `app.trayIcon`. `tauri.bundle` moved to top-level `bundle`. Plugin configs (cli, updater) moved under `plugins`.

```json
{
  "productName": "my-app",
  "version": "0.1.0",
  "identifier": "com.example.myapp",
  "mainBinaryName": "my-app",
  "build": {
    "frontendDist": "../dist",
    "devUrl": "http://localhost:5173"
  },
  "app": {
    "security": {
      "capabilities": [
        "main-capability"
      ]
    },
    "windows": [
      {
        "title": "My App",
        "width": 800,
        "height": 600
      }
    ]
  },
  "bundle": {},
  "plugins": {}
}
```

## Config Key Migration

| v1 Key | v2 Key |
|---|---|
| `tauri` | `app` |
| `package.productName` | `productName` (top-level) |
| `package.version` | `version` (top-level) |
| `build.distDir` | `build.frontendDist` |
| `build.devPath` | `build.devUrl` |
| `tauri.allowlist` | removed (use capabilities) |
| `tauri.systemTray` | `app.trayIcon` |
| `tauri.bundle` | `bundle` (top-level) |
| cli/updater config | `plugins.cli` / `plugins.updater` |
