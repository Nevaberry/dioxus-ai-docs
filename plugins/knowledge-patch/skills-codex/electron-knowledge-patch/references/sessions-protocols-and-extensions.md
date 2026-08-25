# Sessions, protocols, and extensions

Use this reference for session state, preload registration, service workers,
request interception, storage, device APIs, custom protocols, and Chrome
extensions.

## Session state

### Shared-compression dictionaries

Electron 34.0.0 sessions can inspect and clear shared dictionaries used by
Brotli and Zstandard compression:

- `getSharedDictionaryUsageInfo()`
- `getSharedDictionaryInfo(options)`
- `clearSharedDictionaryCache()`
- `clearSharedDictionaryCacheForIsolationKey(options)` for an isolation-key
  scoped clear

### Storage quota option migration

Electron 36.0.0 removes the `syncable` quota type from
`session.clearStorageData(options)` and deprecates the singular `options.quota`
property. Because `temporary` is then the only quota type, callers should omit
`quota`.

Electron 42.0.0 removes the `quotas` object from
`Session.clearStorageData(options)` with its upstream Chromium implementation.
Do not pass `options.quotas` either.

### Persistent File System API grants

Electron 39.0.0 can persist File System API grant status within an Electron
session. The support is also available in Electron 37 and 38. Choose the
session or partition deliberately when persistence boundaries matter.

### Cookie change causes

Electron 41.0.0 refines the cookie `changed` event's causes:

- Setting a new cookie reports `inserted`.
- Deletion remains `explicit`.
- Re-setting an identical cookie reports `inserted-no-change-overwrite`.
- Changing only attributes while preserving the value reports
  `inserted-no-value-change-overwrite`.

Update exhaustive cause handling and avoid treating all insertions as value
changes.

## Preload scripts and service workers

### Per-script preload registration

Electron 35.0.0 deprecates `Session.setPreloads()` and `getPreloads()`. Use:

- `registerPreloadScript()`
- `unregisterPreloadScript()`
- `getPreloadScripts()`

Per-script registration prevents libraries from replacing the entire preload
list. A registration's `type` can target `service-worker` as well as `frame`
contexts.

Attached service-worker preloads use `ipcRenderer`; the main process
communicates through `ServiceWorkerMain.ipc`. Service-worker support also adds
`ServiceWorkers.startWorkerForScope()` and the `running-status-changed` event.

### Service-worker version lookup

Electron 35.0.0 deprecates
`session.serviceWorkers.fromVersionID(versionId)`. Use
`getInfoFromVersionID(versionId)` for the information object or
`getWorkerFromVersionID(versionId)` for the `ServiceWorkerMain` object.

### Dynamic ESM imports in preloads

Electron 39.0.0 preload scripts can use dynamic `import()` when context
isolation is disabled. This support is also present in Electron 37 and 38. This
does not remove the security reasons for retaining context isolation where
possible.

## Web request filtering

### Match every URL explicitly

In Electron 35.0.0, an empty `WebRequestFilter.urls` array no longer matches
every URL. Use the explicit match pattern:

```js
const filter = { urls: ['<all_urls>'] };
```

### Exclude URL patterns

Electron 36.0.0 adds `WebRequestFilter.excludeUrls`. Use it to omit matching URL
patterns from an otherwise broader request filter.

## Extensions

### Session extension API migration

Electron 36.0.0 moves extension methods and events from `Session` to the
`Extensions` object at `session.extensions`. Migrate these methods:

- `session.loadExtension()`
- `session.removeExtension()`
- `session.getExtension()`
- `session.getAllExtensions()`

Use their `session.extensions` counterparts. Move listeners for
`extension-loaded`, `extension-unloaded`, and `extension-ready` to the same
object.

### Extensions on custom protocols

Electron 42.0.0 adds the `allowExtensions` scheme privilege. It lets Chrome
extensions operate on a custom protocol registered with
`protocol.registerSchemesAsPrivileged()`:

```js
protocol.registerSchemesAsPrivileged([
  {
    scheme: 'app',
    privileges: { standard: true, secure: true, allowExtensions: true },
  },
]);
```

### CSS injection in fallback frames

Electron 43.0.0 makes `chrome.scripting.insertCSS()` and `removeCSS()` match
Chrome for fallback frames such as `about:blank` and `data:`. When an extension
can access the page that created the frame, injection can also affect that
frame. Applications that relied on fallback frames being skipped must narrow
targets, frame IDs, or match patterns.

## Device and authentication APIs

### WebUSB configurations

Electron 39.0.0 exposes the `configurations` property on Electron WebUSB
`USBDevice` objects.

### WebUSB and Web Serial blocklists

Electron 37.0.0 applies Chromium's specification-defined WebUSB and Web Serial
device blocklists. Disable them only when the application has a deliberate
device policy:

```js
const { app } = require('electron');

app.commandLine.appendSwitch('disable-usb-blocklist');
app.commandLine.appendSwitch('disable-serial-blocklist');
```

### Touch ID WebAuthn on macOS

Electron 42.0.0 enables the Touch ID platform authenticator with
`app.configureWebAuthn({ touchID: { keychainAccessGroup } })`. Handle the new
session `select-webauthn-account` event when the user must choose among
discoverable credentials.

### WebSocket authentication

Electron 41.0.0 routes WebSocket authentication through the `login` event on
`webContents`. This behavior is also available in Electron 39 and 40.

## Protocol requests and responses

### Protocol-response sessions

Electron 37.0.0 removes the deprecated `null` value for
`ProtocolResponse.session`. To reproduce the former random independent-session
behavior, create a uniquely named session with
`session.fromPartition(randomString)` and assign it. Avoid unnecessary
single-purpose sessions because each adds overhead.

### Bypass custom protocol handlers

Electron 40.0.0 adds `bypassCustomProtocolHandlers` to `net.request` for a
request that must skip registered custom protocol handlers. The option is also
available in Electron 38 and 39.

### Opaque legacy-protocol responses

The 41.10.5-43.4.1 corrections change cross-origin `no-cors` fetches handled by
`registerFileProtocol()` or `registerHttpProtocol()`:

- Electron 41.10.6
- Electron 42.9.2
- Electron 43.4.1

These fetches now return opaque responses, matching `protocol.handle()`.
Renderer code can no longer read their bodies as it could in earlier patch
releases.

### Linux protocol application information

Electron 43.0.0 supports `app.getApplicationInfoForProtocol()` on Linux.
