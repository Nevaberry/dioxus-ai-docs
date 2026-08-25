# Configuration and Projects

## Point `package.json` at a config file

The `jest` field in `package.json` may contain the path to a Jest configuration
file rather than an inline configuration object: (30.0.0)

```json
{"jest": "./config/jest.config.js"}
```

## Type-safe configuration helpers

`jest-config` exports `defineConfig` and `mergeConfig` for type-safe
configuration declaration and composition. Use them where configuration is
split across shared and project-specific files. (30.1-30.3)

Jest configuration files may be written in TypeScript. Native `.mts` and `.cts`
handling does not require extra extension configuration. (30-guide)

## Per-project settings

Individual project configurations accept `testTimeout`, `coverageReporters`,
and `reporters`: (30.0.0)

```js
export default {
  projects: [{
    testTimeout: 10_000,
    coverageReporters: ['text'],
    reporters: ['default'],
  }],
};
```

They also accept `verbose`, `silent`, `collectCoverage`, and `coverageProvider`.
Project-level `verbose` and `silent` override their global values for that
project. (30.4.0)

```js
export default {
  projects: [{verbose: true, collectCoverage: true}],
};
```

## Worker shutdown

Set `workerGracefulExitTimeout` to control how long workers may exit gracefully
before Jest force-kills them. Use this when a worker legitimately needs cleanup
time and the default shutdown window is insufficient. (30.4.0)

## Custom runner options

A custom runner can receive configuration through the tuple form
`['runner-path', {options}]`: (30.4.0)

```js
export default {
  runner: ['./runner.js', {customOption: true}],
};
```

## Globals cleanup

The globals cleanup mode defaults to `'soft'`, which reports leaks without
fully enabling cleanup. Resolve the warnings, then choose the intended mode:
(30-guide)

- `'on'` opts into cleanup.
- `'off'` disables the mode.
- `protectProperties` from `jest-util` protects deliberate shared globals.

Configure the mode through the test environment options:

```js
export default {
  testEnvironmentOptions: {globalsCleanup: 'on'},
};
```

