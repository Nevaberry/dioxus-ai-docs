# Metro, networking, and tooling

## Temporary Metro log streaming

React Native 0.78 restores the removed Metro JavaScript-log stream as an
off-by-default, temporary compatibility option for Community CLI users:

```sh
npx @react-native-community/cli start --client-logs
```

## Package exports and imports

Metro 0.82 in React Native 0.79 enables package `"exports"` and `"imports"`
resolution by default. Incompatible projects can temporarily disable it:

```js
module.exports = {resolver: {unstable_enablePackageExports: false}};
```

From 0.80, the `react-native` package itself has an `"exports"` map. Metro no
longer expands platform extensions for matched exports, and Jest deep-import
mocks can resolve differently. Fix package maps and test imports before
retaining the compatibility switch.

## Community CLI hooks and middleware

React Native 0.81 begins honoring custom `resolveRequest` and
`getModulesRunBeforeMainModule` options in Community CLI projects. Remove them
when a configuration depended on those entries being ignored. Framework
dev-middleware integrations from 0.77 onward should express `serverBaseUrl`
relative to the middleware host. These Metro changes belong to batch
`0.77-0.81`.

## Android JavaScript bundle compression

React Native 0.79 stores the JavaScript bundle uncompressed in the APK by
default, trading installed size for faster startup. Native Android builds can
restore compression explicitly:

```gradle
react {
  enableBundleCompression = true
}
```

## Metro TLS and dev-server addressing

React Native 0.85 lets Metro accept a TLS object for HTTPS and WSS development:

```js
const fs = require('fs');
config.server.tls = {
  ca: fs.readFileSync('path/to/ca'),
  cert: fs.readFileSync('path/to/cert'),
  key: fs.readFileSync('path/to/key'),
};
```

Android builds can set the dev-server IP through the
`reactNativeDevServerIp` Gradle property.

In 0.86.0, DevTools connections derive WebSocket details from HTTPS dev-server
URLs. iOS inspector and debugger URLs likewise follow an HTTPS bundle URL.

## WebSocket cookie headers

Android no longer strips a `Cookie` header supplied through the WebSocket
constructor's `headers` option in 0.86.0:

```js
new WebSocket(url, [], {headers: {Cookie: 'session=example'}});
```

## DevTools network inspection

React Native 0.83 DevTools inspects `fetch`, `XMLHttpRequest`, and `<Image>`
requests. Custom networking libraries are not captured. Expo's separate
Network panel covers Expo-specific events but lacks initiators and Performance
panel integration.

The old in-app Perf and Network tabs are removed in 0.84. From 0.85, multiple
CDP clients such as React Native DevTools and VS Code can connect
simultaneously. These diagnostics are from batch `0.82-0.85`.

## Optimized Android debug builds

The `debugOptimized` variant keeps JavaScript debugging while enabling C++
optimizations. Unlike `debug`, it cannot be used with native C++ debuggers.

```sh
npx react-native run-android --mode debugOptimized
# Expo:
npx expo run:android --variant debugOptimized
```

## ESLint flat configuration

React Native 0.84's ESLint configuration supports ESLint 9 flat config.
