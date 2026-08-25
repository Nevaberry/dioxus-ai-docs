# Reporting and Integrations

## Sequencers and runtime construction

A custom `TestSequencer` receives `globalConfig` and project `contexts`. Update
constructors and helpers to accept and use that configuration. (30-guide)

Code that constructs Jest `Runtime` directly must provide the newly required
`globalConfig` argument. This does not affect ordinary CLI use.

## Test-case start timestamps

The `TestCaseResultObject` passed within `onTestCaseResult` contains a
`startedAt` timestamp. Reporters and other integrations can retain the actual
test-case start time rather than approximating it from surrounding events.
(30.0.0)

## Public configuration types

The `jest` package exports the `GlobalConfig` and `ProjectConfig` TypeScript
types: (30.4.0)

```ts
import type {GlobalConfig, ProjectConfig} from 'jest';
```

`babel-jest` exports `TransformerConfig` for integrations that type Babel
transformer configuration. (30.1-30.3)

## Leak-detector heap snapshots

`jest-leak-detector` allows callers to configure how aggressively garbage
collection runs while generating V8 heap snapshots. Choose the aggressiveness
appropriate to the diagnostic rather than assuming a fixed collection mode.
(30.1-30.3)

## Coverage reporting and output

Per-project configuration accepts `coverageReporters`, and later also accepts
`collectCoverage` and `coverageProvider`. This allows projects in one Jest run
to define their own collection and reporting behavior. (30.0.0; 30.4.0)

When `--json` is combined with `--outputFile`, CLI coverage output remains
visible as of 30.3. Integrations can write JSON results without losing that
coverage output. (30.1-30.3)

`babel-jest` collects coverage from `.mts` and `.cts` files. (30.4.0)

## Coverage threshold interaction

When global coverage thresholds are combined with glob-specific or
path-specific thresholds, files unmatched by the specific rules are still
checked against the global threshold. Do not assume the presence of any path
rule exempts the remaining files. (30.4.0)

## Custom runner configuration

Pass custom runner options with the tuple form: (30.4.0)

```js
export default {
  runner: ['./runner.js', {customOption: true}],
};
```
