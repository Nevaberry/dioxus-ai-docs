# Processes, Diagnostics, and Runtime Behavior

## Renderer and frame diagnostics

### Collect JavaScript stacks from hung renderers

Since 34.0.0, `WebFrameMain.collectJavaScriptCallStack()` can collect a JavaScript
stack from an unresponsive renderer. Both feature enablement and the renderer's
Document Policy are required:

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

Serve the renderer with:

```http
Document-Policy: include-js-call-stacks-in-crash-reports
```

### Frame lifecycle state

Since 34.0.0, `WebFrameMain.detached` identifies a frame in its unloading state,
while `WebFrameMain.isDestroyed()` reports final destruction. During unloading,
`webFrameMain.fromId(processId, frameId)` does not return a frame whose IDs differ
from those requested.

### Frame tokens

At 38.0.0, `webFrame.routingId` and `findFrameByRoutingId(routingId)` were
deprecated. Use `webFrame.frameToken` and `findFrameByToken(frameToken)`.
The main process resolves the token with
`webFrameMain.fromFrameToken(processId, frameToken)`.

## Console and performance diagnostics

### Removed plug-in crash event

At 38.0.0, the `webContents` `plugin-crashed` event was removed. Do not use it as
a crash-detection signal.

### Structured console messages

At 35.0.0, positional `level`, `message`, `line`, and `sourceId` arguments on the
`WebContents` `console-message` event were deprecated. Read them from the event
object, where `line` is `lineNumber` and `frame` is also available. `level` is one
of `info`, `warning`, `error`, or `debug`.

```js
webContents.on(
  'console-message',
  ({ level, message, lineNumber, sourceId, frame }) => {},
);
```

### Long-animation-frame attribution

Since Electron 39 and 40, and in the 41.0.0 line, enable script URL attribution
for `long-animation-frame` entries with:

```js
app.commandLine.appendSwitch('enable-features', 'AlwaysLogLOAFURL');
```

### Heap and out-of-memory evidence

Since 42.0.0, `contentTracing` can collect heap profiles, and renderer
out-of-memory diagnostics can capture a JavaScript stack trace.

## Utility processes

### Fatal V8 errors

Since 34.0.0, utility processes expose an `error` event that supports diagnostic
reports when V8 encounters a fatal error.

### Unhandled promise rejections

Since 37.0.0, an unhandled promise rejection in a utility process emits an error
warning instead of crashing the process. Restore fail-fast behavior explicitly:

```js
process.on('unhandledRejection', () => {
  process.exit(1);
});
```

### Synchronous exit

Also at 37.0.0, `process.exit()` in a utility process became synchronous, matching
Node.js. Pending output, including a preceding `console.log()`, might not flush.

### macOS TCC disclaiming

`utilityProcess` accepts a `disclaim` option for macOS TCC disclaiming in Electron
39 and 40, and in the 41.0.0 line.

## Process exits and memory

### Memory-eviction exits

Since 40.0.0, child-process exit details can report `memory-eviction` as the
reason. Exhaustive exit-reason handling must recognize this value.

### macOS system-memory fields

Since Electron 37, including 38.0.0, macOS `process.getSystemMemoryInfo()` includes
the `fileBacked` and `purgeable` fields.

## Command-line handling

### Application-specific arguments

Since 36.0.0, `app.commandLine` lowercases uppercase switches and arguments. That
API is for case-insensitive Chromium switches. Read case-sensitive,
application-specific arguments from `process.argv`.

### Additional Node.js flags

Electron 35, 36, and 37.0.0 accept:

- `--no-experimental-global-navigator`
- `--experimental-network-inspection`

Electron 39, 40, and 41.0.0 accept `--experimental-transform-types`.

Since 43.0.0, Electron also passes through
`--experimental-inspector-network-resource`.

## WebAssembly trap handlers

Since 42.0.0, enable WebAssembly trap-handler support with the
`WasmTrapHandlers` fuse.

## PDF frames and output

### PDF resources stay in the existing WebContents

Since 41.0.0, PDF resources no longer create a separate guest `WebContents`.
They render inside the existing `WebContents`; code that detects PDFs must inspect
the frame tree rather than search for a second `WebContents`.

### Per-frame PDF generation

The 41.10.5-43.4.1 patch batch adds `WebFrameMain.printToPDF()` in Electron
42.9.0 and 43.4.0. It renders one frame rather than the entire `WebContents`:

```js
const frame = browserWindow.webContents.mainFrame;
const pdf = await frame.printToPDF({});
```
