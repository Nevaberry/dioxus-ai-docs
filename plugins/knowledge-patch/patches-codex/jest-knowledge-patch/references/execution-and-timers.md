# Execution and timers

Use this reference for unhandled rejections, retries, asynchronous setup, fake
timers, global cleanup, leak detection, and worker exit behavior.

## Unhandled rejection timing

Jest waits one extra event-loop turn before treating a rejected promise as
unhandled. This avoids failures when code attaches a handler asynchronously.

Set:

```js
export default {
  waitForUnhandledRejections: false,
};
```

to restore earlier timing when the extra turn is unacceptable. Before opting
out, determine whether the suite relies on a legitimately delayed handler or
is hiding a rejection that should be awaited.

## Configurable retries

`jest.retryTimes()` accepts a delay between attempts:

```js
jest.retryTimes(3, {waitBeforeRetry: 1000});
```

It can also retry a failure immediately instead of waiting until the rest of
the suite completes:

```js
jest.retryTimes(3, {retryImmediately: true});
```

Choose one according to the system under test. A delay can help with external
readiness; immediate retry shortens feedback but changes when repeated setup
and teardown occur relative to other tests.

## Animation-frame timers

Modern fake timers expose `jest.advanceTimersToFrame()`. It advances by the
amount needed to run callbacks currently scheduled with
`requestAnimationFrame`:

```js
jest.useFakeTimers();
requestAnimationFrame(callback);
jest.advanceTimersToFrame();
expect(callback).toHaveBeenCalled();
```

Use it instead of guessing a frame duration with `advanceTimersByTime()`.

## Fake-timer tick modes

`jest-fake-timers` provides `setTimerTickMode` to configure how fake timers
advance. When an integration owns a fake-timer instance, set the intended tick
mode explicitly and test microtask and timer ordering around each advancement.

## Temporal-aware fake timers

The timer APIs added in `30.4.0` accept Temporal values:

- `advanceTimersByTime()` and its async variant accept `Temporal.Duration`;
- `setSystemTime()` accepts `Temporal.Instant` and
  `Temporal.ZonedDateTime`;
- `useFakeTimers({now})` accepts `Temporal.Instant` and
  `Temporal.ZonedDateTime`;
- fake timers can fake `Temporal.Now.*`.

For example:

```js
jest.useFakeTimers({
  now: Temporal.Instant.from('2026-01-01T00:00:00Z'),
});
jest.advanceTimersByTime(Temporal.Duration.from({seconds: 1}));
```

Prefer Temporal values when the application contract is Temporal-based; keep
numeric millisecond tests for numeric APIs.

## Asynchronous environment setup

Modules in `setupFilesAfterEnv` may export an asynchronous function or use
top-level `await`, matching asynchronous `setupFiles` behavior.

Await initialization fully and surface setup rejection directly. Do not start
detached work that can race with the first test.

## Global cleanup mode

Globals cleanup defaults to `'soft'`, which reports potential leaks without
fully cleaning them. Resolve the warnings, then opt into cleanup:

```js
export default {
  testEnvironmentOptions: {
    globalsCleanup: 'on',
  },
};
```

Use `'off'` to disable the mode. Protect intentional shared globals with
`protectProperties` from `jest-util`; do not protect incidental leaks simply
to silence warnings.

## Leak-detector garbage collection

In the `30.1-30.3` update, `jest-leak-detector` gains control over how
aggressively it runs garbage collection while generating V8 heap snapshots.
Tune this when snapshot generation cost or collection behavior affects leak
diagnostics, and keep the setting isolated from normal application GC policy.

## Worker shutdown timeout

`workerGracefulExitTimeout` specifies how long a worker may exit gracefully
before Jest force-kills it.

Use a longer value for known asynchronous teardown that cannot complete within
the default window. A forced exit still warrants checking open handles,
unclosed servers, pending timers, and incomplete setup or teardown.

## Execution checklist

- Await promises that are logically part of a test.
- Decide deliberately whether to keep the extra rejection turn.
- Choose delayed or immediate retry based on fixture behavior.
- Use frame advancement for animation-frame callbacks.
- Verify microtask ordering when changing timer tick modes.
- Exercise synchronous and asynchronous timer advancement.
- Use the correct Temporal type for duration versus clock time.
- Await `setupFilesAfterEnv` initialization.
- Fix global leak warnings before enabling cleanup.
- Protect only deliberate globals.
- Tune leak-detector GC only for heap-snapshot diagnostics.
- Investigate open handles before extending worker exit time.
