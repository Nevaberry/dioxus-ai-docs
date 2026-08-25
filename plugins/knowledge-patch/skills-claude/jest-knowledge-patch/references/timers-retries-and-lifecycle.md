# Timers, Retries, and Lifecycle

## Unhandled rejection timing

Jest waits one extra event-loop turn before treating a rejected promise as
unhandled. This avoids failures for promises that are caught asynchronously.
Set `waitForUnhandledRejections: false` to restore the earlier timing only when
the extra wait is unacceptable. (30-guide)

## Animation frames

Modern fake timers provide `jest.advanceTimersToFrame()`. It advances time by
the amount needed to run callbacks currently scheduled with
`requestAnimationFrame`: (30.0.0)

```js
jest.useFakeTimers();
requestAnimationFrame(callback);
jest.advanceTimersToFrame();
```

## Timer tick modes

`jest-fake-timers` exposes `setTimerTickMode` to configure how fake timers
advance. Use this lower-level control when the default advancement model does
not match the integration being tested. (30.1-30.3)

## Temporal-aware fake timers

Fake timers accept Temporal values in these positions: (30.4.0)

- `advanceTimersByTime()` and its async variant accept `Temporal.Duration`.
- `setSystemTime()` accepts `Temporal.Instant` and
  `Temporal.ZonedDateTime`.
- `useFakeTimers({now})` accepts `Temporal.Instant` and
  `Temporal.ZonedDateTime`.
- Fake timers can fake `Temporal.Now.*`.

```js
jest.useFakeTimers({
  now: Temporal.Instant.from('2026-01-01T00:00:00Z'),
});
jest.advanceTimersByTime(Temporal.Duration.from({seconds: 1}));
```

## Retry scheduling

`jest.retryTimes()` supports a delay between attempts and immediate retry
before the remaining suite completes: (30-guide)

```js
jest.retryTimes(3, {waitBeforeRetry: 1000});
jest.retryTimes(3, {retryImmediately: true});
```

Choose the options deliberately: the first adds a wait before an attempt, and
the second changes retry ordering.

## Asynchronous environment setup

A module listed in `setupFilesAfterEnv` may export an async function or use
top-level `await`, matching the asynchronous behavior already available to
`setupFiles`. Ensure setup completes before relying on its state in tests.
(30-guide)

## Global cleanup lifecycle

The globals cleanup mode defaults to `'soft'`. After resolving its leak
warnings, opt into cleanup with `'on'`, disable it with `'off'`, or use
`protectProperties` from `jest-util` for intentionally shared global
properties. (30-guide)

```js
export default {
  testEnvironmentOptions: {globalsCleanup: 'on'},
};
```

