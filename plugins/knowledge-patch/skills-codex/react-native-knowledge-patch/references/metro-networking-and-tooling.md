# Metro, networking, and tooling

## Metro JavaScript log streaming

React Native 0.78 restores the removed Metro JavaScript-log stream as an
off-by-default, temporary compatibility option for Community CLI users:

```sh
npx @react-native-community/cli start --client-logs
```

Treat this as a migration aid rather than a durable logging interface.

## Package `exports` and `imports`

Metro 0.82, shipped with React Native 0.79, enables package `"exports"` and
`"imports"` resolution by default. An incompatible project can temporarily
disable it:

```js
module.exports = {
  resolver: {unstable_enablePackageExports: false},
};
```

From React Native 0.80, the `react-native` package itself defines an
`"exports"` map. When an export matches, Metro does not expand platform
extensions. Jest deep-import mocks may also resolve differently. Correct
package export maps and test imports before depending on the compatibility
switch long-term.

## Community CLI hooks and middleware

React Native 0.81 begins honoring custom `resolveRequest` and
`getModulesRunBeforeMainModule` options in Community CLI projects. Remove
entries that were configured only because older releases ignored them.

For framework dev-middleware integrations from 0.77 onward, express
`serverBaseUrl` relative to the middleware host.

## Android bundle compression

React Native 0.79 stores the JavaScript bundle uncompressed in the APK by
default. This trades installed size for faster startup. Native Android builds
can explicitly restore compression:

```gradle
react {
  enableBundleCompression = true
}
```

## Metro TLS and dev-server addressing

React Native 0.85 allows Metro to accept a TLS object for HTTPS and WSS
development servers:

```js
const fs = require('fs');

config.server.tls = {
  ca: fs.readFileSync('path/to/ca'),
  cert: fs.readFileSync('path/to/cert'),
  key: fs.readFileSync('path/to/key'),
};
```

Android builds can set the development-server IP through the
`reactNativeDevServerIp` Gradle property.

In 0.86.0, DevTools connections derive WebSocket details from HTTPS dev-server
URLs. iOS inspector and debugger URLs similarly follow an HTTPS bundle URL, so
do not hard-code `ws://` or plain HTTP assumptions in integrations.

## WebSocket request headers

In 0.86.0, Android no longer strips a `Cookie` header supplied through the
WebSocket constructor's `headers` option:

```js
new WebSocket(url, [], {headers: {Cookie: 'session=example'}});
```

On iOS, `SRWebSocketProvider` can selectively inject WebSocket headers. Use the
platform interception point when construction-time JavaScript headers are not
the right ownership boundary.

## DevTools network and performance panels

React Native 0.83 DevTools adds network inspection for `fetch`,
`XMLHttpRequest`, and `<Image>` requests. It also adds performance traces that
combine JavaScript, React, network, and User Timing tracks. Custom networking
libraries are not captured.

Expo's separate Network panel covers Expo-specific events but does not provide
initiators or Performance-panel integration. The old in-app Perf and Network
tabs are removed in React Native 0.84. From 0.85, multiple CDP clients, such as
React Native DevTools and VS Code, can connect simultaneously.

React Native 0.86.0 adds a React Native Renderer operations track to
performance traces and supports light/dark emulation through
`Emulation.setEmulatedMedia`.

## Optimized Android debugging

The `debugOptimized` variant retains JavaScript debugging while enabling C++
optimizations. Unlike `debug`, it cannot be used with native C++ debuggers.

```sh
npx react-native run-android --mode debugOptimized

# Expo:
npx expo run:android --variant debugOptimized
```

Choose ordinary `debug` when the investigation requires native C++ breakpoints.

## ESLint flat configuration

React Native 0.84's ESLint configuration supports the ESLint 9 flat-config
format.
