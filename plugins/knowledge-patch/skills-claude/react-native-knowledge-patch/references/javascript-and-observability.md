# JavaScript APIs and observability

## Uncaught error reporting

React Native 0.81 reports uncaught JavaScript errors with their original
message and stack, `cause`, and a component Owner Stack. Error backends may
receive more thrown errors that older releases surfaced only through
`console.error`; update ingestion assumptions. This change is from batch
`0.77-0.81`.

From 0.82, uncaught promise rejections go through `console.error` and the
JavaScript error-reporting path instead of being swallowed. An upgrade can
expose old rejections and sharply increase backend error volume. This behavior
is part of batch `0.82-0.85`.

## Exact false for exception reporting

In 0.86.0, only the literal boolean `false` retains the special behavior of
`reportErrorsAsExceptions`. Other falsey values no longer behave like `false`.
Validate or normalize configuration before passing it.

## Component-provider instrumentation hook

The second argument to an
`AppRegistry.setComponentProviderInstrumentationHook` callback is deprecated
in 0.86.0 because applications cannot use it. It is a warning stub; callbacks
should rely only on their first argument.

## Stable Web Performance subset

In 0.83, the Web Performance subset becomes stable: `performance.now()`,
`timeOrigin`, entry queries, `mark()` and `measure()`, `PerformanceObserver`,
and `event` and `longtask` entries. Observers work in production builds. The
0.83 canary channel separately adds `IntersectionObserver`.

In 0.86.0, `PerformanceObserver.observe({type: 'event'})` defaults
`durationThreshold` to 104 ms rather than reporting every event. Specify a
lower threshold to collect shorter events:

```js
observer.observe({type: 'event', durationThreshold: 16});
```

## JavaScript API changes

From 0.82, `Appearance.setColorScheme()` rejects `null` and `undefined`; use
`'unspecified'` to reset it. Version 0.85 removes
`StyleSheet.absoluteFillObject`; use `StyleSheet.absoluteFill`.

```js
Appearance.setColorScheme('unspecified');
const fillStyle = StyleSheet.absoluteFill;
```

React Native 0.84 fills gaps in `URL` and `URLSearchParams`, including
properties and methods such as `hash`, `host`, `pathname`, `get`, `set`, and
`delete`.

## DevTools performance and emulation

React Native 0.83 performance traces combine JavaScript, React, network, and
User Timing tracks. React Native 0.86.0 adds a React Native Renderer operations
track. It also adds `Emulation.setEmulatedMedia` for light- or dark-mode
emulation.
