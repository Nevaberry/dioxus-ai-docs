# JavaScript APIs and observability

## Uncaught errors and promise rejections

From 0.81, uncaught JavaScript errors retain their original message and stack,
their `cause`, and a component Owner Stack. Error backends may receive more
thrown errors because some failures previously surfaced only through
`console.error`. Update parsing, grouping, redaction, and ingestion-volume
expectations.

From 0.82, uncaught promise rejections flow through `console.error` and the
JavaScript error-reporting path instead of being swallowed. An upgrade can
therefore reveal old application defects and sharply increase reports without a
new rejection being introduced.

Only the literal boolean `false` retains the special behavior of
`reportErrorsAsExceptions` in 0.86. Values such as `0`, `''`, `null`, or
`undefined` no longer act as `false`; parse external configuration to a boolean
before supplying the option.

## Performance APIs

The Web Performance subset becomes stable in 0.83. It includes:

- `performance.now()` and `timeOrigin`
- performance-entry queries
- `mark()` and `measure()`
- `PerformanceObserver`
- `event` and `longtask` entries

Observers work in production builds. The separate 0.83 canary channel adds
`IntersectionObserver`; do not infer its stable availability from the stable Web
Performance APIs.

In 0.86, `PerformanceObserver.observe({type: 'event'})` defaults
`durationThreshold` to 104 ms rather than reporting every event. Pass a threshold
when shorter events matter:

```js
observer.observe({type: 'event', durationThreshold: 16});
```

## Instrumentation hook deprecation

The second argument passed to an
`AppRegistry.setComponentProviderInstrumentationHook` callback is deprecated in
0.86 because applications cannot use it. It is now a warning stub. Define
callbacks around the first argument only and remove reads, logging, or type
assumptions involving the second.

## JavaScript API changes

From 0.82, `Appearance.setColorScheme()` no longer accepts `null` or
`undefined`. Pass `'unspecified'` to reset the override.

React Native 0.85 removes `StyleSheet.absoluteFillObject`. Use the already
constructed style `StyleSheet.absoluteFill`:

```js
Appearance.setColorScheme('unspecified');
const fillStyle = StyleSheet.absoluteFill;
```

React Native 0.84 fills gaps in `URL` and `URLSearchParams`, including standard
properties and methods such as `hash`, `host`, `pathname`, `get`, `set`, and
`delete`. Prefer these public APIs over local compatibility shims when the
project's minimum version includes them.

## DevTools diagnostics

React Native 0.83 DevTools adds network inspection for `fetch`,
`XMLHttpRequest`, and `<Image>` requests. It also adds performance traces that
combine JavaScript, React, network, and User Timing tracks. Custom networking
libraries are not captured.

Expo's separate Network panel covers Expo-specific events, but does not provide
initiators or Performance-panel integration. Choose the panel according to the
transport and diagnostic data required.

The old in-app Perf and Network tabs are removed in 0.84. From 0.85, multiple
CDP clients, such as React Native DevTools and VS Code, may connect at the same
time.

React Native 0.86 performance traces add a React Native Renderer operations
track. `Emulation.setEmulatedMedia` can emulate light or dark mode. DevTools
connections derive WebSocket details from HTTPS development-server URLs, and
iOS inspector and debugger URLs likewise follow an HTTPS bundle URL.
