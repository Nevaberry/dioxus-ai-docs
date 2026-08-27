# JavaScript and observability

## Error reporting semantics

### Uncaught errors

From 0.81, uncaught JavaScript errors include their original message and stack,
their `cause`, and a component Owner Stack. Error backends may receive more
thrown errors because older releases surfaced some of them only through
`console.error`; review grouping and ingestion-volume assumptions during an
upgrade.

### Unhandled promise rejections

From 0.82, uncaught promise rejections are reported through `console.error` and
the JavaScript error-reporting path instead of being swallowed. An upgrade can
therefore expose old rejections and cause a sudden increase in backend reports.
Fix the rejections rather than suppressing the new signal.

### `reportErrorsAsExceptions`

In 0.86.0, only the literal boolean `false` retains the special behavior of
`reportErrorsAsExceptions`. Other falsey values do not behave as `false`.
Normalize configuration values before passing them to this option.

## Instrumentation callbacks

The second argument passed to an
`AppRegistry.setComponentProviderInstrumentationHook` callback is deprecated in
0.86.0 because apps cannot use it. The argument is now a warning stub. Update
callbacks to rely only on their first argument.

## Web Performance APIs

React Native 0.83 stabilizes a Web Performance subset:

- `performance.now()` and `timeOrigin`
- Performance entry queries
- `mark()` and `measure()`
- `PerformanceObserver`
- `event` and `longtask` entries

Observers work in production builds. The 0.83 canary channel separately adds
`IntersectionObserver`; do not mistake that canary addition for the same stable
API commitment.

### Event Timing threshold

In 0.86.0, `PerformanceObserver.observe({type: 'event'})` defaults
`durationThreshold` to 104 ms instead of reporting every event. Pass an
explicit threshold to collect shorter events:

```js
observer.observe({type: 'event', durationThreshold: 16});
```

## DevTools diagnostics

React Native 0.83 DevTools adds performance traces combining JavaScript,
React, network, and User Timing tracks. React Native 0.86.0 adds a React Native
Renderer operations track to those traces.

DevTools in 0.86.0 can use `Emulation.setEmulatedMedia` to emulate light or
dark mode. This is useful for diagnosis, but app behavior should still be
tested against real platform appearance changes.

Network inspection captures `fetch`, `XMLHttpRequest`, and `<Image>` traffic,
not arbitrary custom networking libraries. See the tooling reference for the
removed in-app panels, Expo differences, and multi-client connections.

## Appearance reset value

From 0.82, `Appearance.setColorScheme()` no longer accepts `null` or
`undefined`. Reset the override with:

```js
Appearance.setColorScheme('unspecified');
```

## Removed StyleSheet value

React Native 0.85 removes `StyleSheet.absoluteFillObject`. Use the supported
replacement:

```js
const fillStyle = StyleSheet.absoluteFill;
```

## URL standard-library coverage

React Native 0.84 fills in missing `URL` and `URLSearchParams` properties and
methods, including `hash`, `host`, `pathname`, `get`, `set`, and `delete`.
Remove compatibility shims only after confirming that the app's pinned release
contains every method it uses.

## React APIs

React Native 0.83 includes React 19.2's `<Activity>` and `useEffectEvent` APIs.
A hidden Activity preserves state, hides children, unmounts effects, and defers
updates. In 0.85, hidden `Pressable` descendants retain their event listeners.
