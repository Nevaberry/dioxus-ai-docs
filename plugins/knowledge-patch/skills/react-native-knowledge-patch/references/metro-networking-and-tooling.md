# Metro, networking, and tooling

## Temporary Metro log streaming

React Native 0.78 temporarily restores Metro JavaScript-log streaming for
Community CLI users as an off-by-default compatibility option:

```sh
npx @react-native-community/cli start --client-logs
```

Treat this as a migration aid, not a permanent logging API.

## Package exports and imports

Metro 0.82, included with React Native 0.79, enables package `"exports"` and
`"imports"` resolution by default. An incompatible project can temporarily set
`resolver.unstable_enablePackageExports` to `false`:

```js
module.exports = {
  resolver: {unstable_enablePackageExports: false},
};
```

From React Native 0.80, the `react-native` package itself has an `"exports"`
map. Metro does not expand platform extensions for a matched export, and Jest
deep-import mocks may resolve differently. Prefer fixing declared exports,
platform entry points, and mocks to leaving package exports disabled.

## Community CLI configuration

React Native 0.81 begins honoring custom Community CLI `resolveRequest` and
`getModulesRunBeforeMainModule` options. A configuration that relied on those
entries being ignored must remove them to preserve the former behavior.

Framework dev-middleware integrations from 0.77 onward should express
`serverBaseUrl` relative to the middleware host.

## Metro TLS and development-server addressing

React Native 0.85 lets Metro accept a TLS object for HTTPS and WSS development:

```js
const fs = require('fs');

config.server.tls = {
  ca: fs.readFileSync('path/to/ca'),
  cert: fs.readFileSync('path/to/cert'),
  key: fs.readFileSync('path/to/key'),
};
```

Android builds can set the development-server IP with the
`reactNativeDevServerIp` Gradle property. React Native 0.86 DevTools and iOS URL
handling follow HTTPS bundle and development-server URLs; see
[javascript-and-observability.md](javascript-and-observability.md).

## Android JavaScript bundle compression

React Native 0.79 stores the Android JavaScript bundle uncompressed in the APK
by default. This trades installed size for startup speed. Native Android builds
can explicitly restore compression:

```gradle
react {
  enableBundleCompression = true
}
```

Measure startup and installed size for the actual release artifact before
changing the default.

## Android WebSocket cookies

In 0.86, Android no longer strips a `Cookie` header supplied in the WebSocket
constructor's `headers` option:

```js
new WebSocket(url, [], {
  headers: {Cookie: 'session=example'},
});
```

Apply normal cookie-security rules; the behavioral change only means the
explicit header reaches the connection.

For iOS native HTTP, multipart, and WebSocket header interception, see
[native-extension-migrations.md](native-extension-migrations.md).

## Optimized Android debug builds

The `debugOptimized` variant enables C++ optimizations while retaining
JavaScript debugging. Unlike `debug`, it cannot be used with native C++
debuggers.

```sh
npx react-native run-android --mode debugOptimized
npx expo run:android --variant debugOptimized
```

Use the normal debug variant for breakpoints or inspection inside native C++.

## Network and performance inspection

DevTools network inspection captures `fetch`, `XMLHttpRequest`, and `<Image>`
requests, not arbitrary custom networking libraries. The performance view can
correlate JavaScript, React, network, and User Timing tracks. The deprecated
`XHRInterceptor` and `WebSocketInterceptor` are not replacements for transport
customization; use the CDP `Network` domain for inspection.

## ESLint flat configuration

React Native 0.84's ESLint configuration supports the ESLint 9 flat-config
format. Migrate configuration structure and plugin declarations together when
upgrading to ESLint 9.
