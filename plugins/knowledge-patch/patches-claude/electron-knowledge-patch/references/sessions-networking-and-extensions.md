# Sessions, Networking, and Extensions

## Session data and storage

### Shared-compression dictionaries

Since 34.0.0, `Session` exposes the Brotli and Zstandard shared-dictionary cache:

- `getSharedDictionaryUsageInfo()` inspects usage.
- `getSharedDictionaryInfo(options)` inspects matching dictionaries.
- `clearSharedDictionaryCache()` clears the cache.
- `clearSharedDictionaryCacheForIsolationKey(options)` clears one isolation key.

### Storage quotas

At 36.0.0, the `syncable` quota type was removed from
`session.clearStorageData(options)`, and `options.quota` was deprecated because
`temporary` was the only remaining quota type. Omit `quota`.

At 42.0.0, the upstream `quotas` object was removed entirely. Do not pass
`options.quotas` either.

### Persistent File System API grants

File System API grant status can be persisted within an Electron session since
37, including in 38.0.0 and 39.0.0.

### Cookie change causes

Since 41.0.0, the cookie `changed` event distinguishes these causes:

- A new cookie reports `inserted`.
- Explicit deletion reports `explicit`.
- Re-setting an identical cookie reports `inserted-no-change-overwrite`.
- Changing only attributes while retaining the value reports
  `inserted-no-value-change-overwrite`.

## Preload and service-worker registration

At 35.0.0, `Session.setPreloads()` and `getPreloads()` were deprecated. Use
per-script `registerPreloadScript()`, `unregisterPreloadScript()`, and
`getPreloadScripts()` so components do not replace the full registration list.
The registration `type` targets either `frame` or `service-worker`.

Attached service-worker preloads use `ipcRenderer`; the main process communicates
through `ServiceWorkerMain.ipc`. `ServiceWorkers.startWorkerForScope()` starts a
worker, and `ServiceWorkerMain` emits `running-status-changed`.

Also at 35.0.0, `session.serviceWorkers.fromVersionID(versionId)` was deprecated.
Use `getInfoFromVersionID(versionId)` for an information object or
`getWorkerFromVersionID(versionId)` for a `ServiceWorkerMain`.

Since 39.0.0, preload scripts can use dynamic `import()` when context isolation is
disabled; this behavior is also present in Electron 37 and 38.

The experimental `contextBridge.executeInMainWorld(executionScript)` API, added in
35.0.0, evaluates JavaScript in the main world across the context bridge.

## Web-request filters

### Match all URLs explicitly

Since 35.0.0, an empty `WebRequestFilter.urls` array no longer means all URLs. Use
the designated match pattern:

```js
const filter = { urls: ['<all_urls>'] };
```

Since 36.0.0, filters also accept `excludeUrls` to omit URL patterns from an
otherwise matching filter:

```js
const filter = {
  urls: ['<all_urls>'],
  excludeUrls: ['https://example.test/private/*'],
};
```

Permission handling since 35.0.0 also covers
`document.executeCommand('paste')`; permission handlers must account for that
request.

## Protocol handlers and requests

### Protocol-response sessions

At 37.0.0, the deprecated `null` value for `ProtocolResponse.session` was removed.
To approximate the former random independent session, create a uniquely named
session with `session.fromPartition(randomString)` and assign it. Single-purpose
sessions carry overhead, so use them deliberately.

### Bypass custom protocol handlers

`net.request` accepts `bypassCustomProtocolHandlers` since Electron 38 and 39,
and in the 40.0.0 line:

```js
const request = net.request({
  url: 'https://example.test/',
  bypassCustomProtocolHandlers: true,
});
```

### Legacy-protocol response opacity

Patch-line behavior in 41.10.5-43.4.1 matters: in Electron 41.10.6, 42.9.2, and
43.4.1, cross-origin `no-cors` fetches handled by `registerFileProtocol()` or
`registerHttpProtocol()` return opaque responses, matching `protocol.handle()`.
Renderer code can no longer read such responses as it could in earlier patch
releases.

### Utility-process request sessions

Since 43.0.0, requests made through the `net` module from a utility process can
use an Electron session.

## Network compatibility

### Host-resolution rules

At 39.0.0, Chromium deprecated `--host-rules`. Move configurations to
`--host-resolver-rules`.

### WebSocket authentication

Since Electron 39 and 40, and in the 41.0.0 line, WebSocket authentication is
handled through the `webContents` `login` event.

### WebUSB and Web Serial

Since 37.0.0, WebUSB and Web Serial apply Chromium's specification-defined device
blocklists. Disable them only when the application explicitly accepts the risk:

```js
app.commandLine.appendSwitch('disable-usb-blocklist');
app.commandLine.appendSwitch('disable-serial-blocklist');
```

At 39.0.0, Electron's WebUSB `USBDevice` objects gained the `configurations`
property.

## Extensions

### Session extension API

At 36.0.0, extension methods and events moved from `Session` to the `Extensions`
object at `session.extensions`. Migrate `loadExtension()`, `removeExtension()`,
`getExtension()`, and `getAllExtensions()`, plus `extension-loaded`,
`extension-unloaded`, and `extension-ready`, to that object.

### Extensions on custom protocols

Since 42.0.0, the `allowExtensions` privilege permits Chrome extensions to
operate on a custom protocol:

```js
protocol.registerSchemesAsPrivileged([
  {
    scheme: 'app',
    privileges: { standard: true, secure: true, allowExtensions: true },
  },
]);
```

### CSS injection in fallback frames

Since 43.0.0, `chrome.scripting.insertCSS()` and `removeCSS()` match Chrome for
fallback frames such as `about:blank` and `data:`. When an extension can access
the page that created the frame, injection can affect that frame too. Narrow
targets, frame IDs, or match patterns if the application relied on fallback
frames being skipped.

## WebAuthn

Since 42.0.0, macOS applications can enable the Touch ID platform authenticator:

```js
app.configureWebAuthn({ touchID: { keychainAccessGroup } });
```

Use the session's `select-webauthn-account` event to select among discoverable
credentials.

## Child-window security inheritance

The 41.10.5-43.4.1 patch-line changes include stricter inheritance in Electron
41.10.6, 42.9.2, and 43.4.1. A window opened by a sandboxed top-level frame
inherits the opener's sandbox restrictions. `<webview>` and `window.open()` also
inherit `nodeIntegrationInWorker` from the embedder, consistent with the other
Node.js and sandbox preferences.
