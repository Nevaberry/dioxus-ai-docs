# Processes, security, and diagnostics

Use this reference for frame and process lifecycle, privileged renderer
operations, package integrity, and failure diagnostics.

## Renderer and frame diagnostics

### Collect a JavaScript stack from an unresponsive renderer

Electron 34.0.0 adds `WebFrameMain.collectJavaScriptCallStack()`. It can collect
a JavaScript stack from a hung renderer, including from `webContents.mainFrame`
inside an `unresponsive` event handler.

Two opt-ins are required:

1. Enable the `DocumentPolicyIncludeJSCallStacksInCrashReports` feature before
   application readiness.
2. Serve the renderer with
   `Document-Policy: include-js-call-stacks-in-crash-reports`.

```js
const { app } = require('electron');

app.commandLine.appendSwitch(
  'enable-features',
  'DocumentPolicyIncludeJSCallStacksInCrashReports',
);

app.on('web-contents-created', (_event, webContents) => {
  webContents.on('unresponsive', async () => {
    console.log(await webContents.mainFrame.collectJavaScriptCallStack());
  });
});
```

### WebFrameMain lifecycle state

In Electron 34.0.0, `WebFrameMain.detached` indicates that a frame is unloading,
while `WebFrameMain.isDestroyed()` indicates that destruction has completed.
During unloading, `webFrameMain.fromId(processId, frameId)` no longer returns a
frame that does not match the requested identifiers.

### Frame token migration

Electron 38.0.0 deprecates `webFrame.routingId` and
`webFrame.findFrameByRoutingId(routingId)`. Use `webFrame.frameToken` and
`webFrame.findFrameByToken(frameToken)`. Resolve a renderer token in the main
process with `webFrameMain.fromFrameToken(processId, frameToken)`.

### Console-message payload

Electron 35.0.0 deprecates the positional `level`, `message`, `line`, and
`sourceId` arguments for the `WebContents` `console-message` event. Read the
values from the event object; `line` becomes `lineNumber`, `frame` is included,
and `level` is one of `info`, `warning`, `error`, or `debug`.

```js
webContents.on(
  'console-message',
  ({ level, message, lineNumber, sourceId, frame }) => {},
);
```

### Heap and renderer OOM diagnostics

Electron 42.0.0 allows `contentTracing` to collect heap profiles. Renderer
out-of-memory diagnostics can also capture a JavaScript stack trace.

### Long-animation-frame attribution

Electron 41.0.0 can attribute scripts in `long-animation-frame` entries when
the `AlwaysLogLOAFURL` feature is enabled. The same feature is supported in
Electron 39 and 40.

```js
app.commandLine.appendSwitch('enable-features', 'AlwaysLogLOAFURL');
```

## Utility and child processes

### Fatal V8 errors

Utility processes expose an `error` event in Electron 34.0.0. Listen for it to
capture diagnostic reports when V8 encounters a fatal error.

### Unhandled promise rejections

Starting in Electron 37.0.0, an unhandled promise rejection in a utility process
emits an error warning instead of crashing the process. Applications that need
the former fail-fast behavior must terminate explicitly:

```js
process.on('unhandledRejection', () => {
  process.exit(1);
});
```

### Synchronous exit

`process.exit()` in a utility process terminates synchronously starting in
Electron 37.0.0, matching Node.js. Pending output, including a preceding
`console.log()`, might not be flushed.

### Memory-eviction exit reason

Electron 40.0.0 child-process exit details can report `memory-eviction` as the
reason. Any exhaustive exit-reason handling must recognize the new value.

### Electron sessions in utility-process requests

In Electron 43.0.0, requests made through the `net` module from a utility
process can use an Electron session.

### macOS TCC disclaiming

The `utilityProcess` API accepts a `disclaim` option for macOS TCC disclaiming in
Electron 41.0.0. It is also available in Electron 39 and 40.

## Renderer boundaries

### Execute in the main world over the context bridge

Electron 35.0.0 adds the experimental
`contextBridge.executeInMainWorld(executionScript)` API for evaluating
JavaScript in the renderer's main world across the context bridge. Treat the
script and returned data as part of a deliberately narrow bridge surface.

### Clipboard migration

Electron 40.0.0 deprecates direct use of Electron's `clipboard` API in renderer
processes. Electron 44 removes the module from renderers. Use
`navigator.clipboard` for ordinary access, or expose only required privileged
operations from a preload:

```js
const { clipboard, contextBridge } = require('electron');

contextBridge.exposeInMainWorld('clipboardAPI', {
  readText: () => clipboard.readText(),
});
```

Electron 35.0.0 permission handling also covers
`document.executeCommand('paste')`. Do not assume the legacy command bypasses
permission policy.

### New-window security preference inheritance

Corrected releases in the 41.10.5-43.4.1 batch tighten inheritance:

- Electron 41.10.6, 42.9.2, and 43.4.1 make windows opened by a sandboxed
  top-level frame inherit the opener's sandbox restrictions.
- `<webview>` and `window.open()` inherit `nodeIntegrationInWorker` from their
  embedder, consistent with the other Node and sandbox preferences.

Do not design a child window around relaxing its opener's security settings.

## Packaged application integrity

### Stable ASAR integrity

ASAR integrity is stable in Electron 39.0.0. When enabled, Electron checks the
packaged `app.asar` against its build-time hash and forcefully terminates the
application when the hash is missing or mismatched. Electron Packager 19
separately enables ASAR packaging by default.

### macOS ASAR integrity digest

Electron 41.0.0 macOS applications can embed a digest of their ASAR Integrity
metadata so that the integrity information itself is validated at launch. With
`@electron/asar` 4.1.0 or later, enable the digest and then re-sign the app:

```bash
asar integrity-digest on /path/to/YourApp.app
```

## Runtime safety controls

### Asynchronous safe storage

Electron 42.0.0 adds asynchronous `safeStorage` functionality, enabling several
additional storage backends. Use the asynchronous path when selecting one of
those backends rather than assuming the synchronous API can reach it.

### WebAssembly trap handlers

Electron 42.0.0 can enable WebAssembly trap-handler support with the
`WasmTrapHandlers` fuse. Treat fuse configuration as part of the packaged
application's security and compatibility profile.

### Removed plugin crash event

Electron 38.0.0 removes the `webContents` `plugin-crashed` event. Remove event
listeners and do not depend on it for crash reporting.
