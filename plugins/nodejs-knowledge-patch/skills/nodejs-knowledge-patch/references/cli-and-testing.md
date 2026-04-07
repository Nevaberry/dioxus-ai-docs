# CLI And Testing

## `node --run` Is Stable

Node.js 23 marks `node --run` as stable. Use it for `package.json` scripts without invoking the package manager front-end.

```sh
node --run build
node --run test
```

## Test Runner Keeps Expanding

Important post-cutoff `node:test` changes include:

- coverage glob support
- TypeScript files in default test globs
- `env` support in runner APIs
- support for expected failures
- improved source map and watch-mode behavior

That means older guidance about always wrapping `node --test` in custom discovery logic is now outdated.

```js
import { run } from "node:test";

await run({
  globPatterns: ["test/**/*.test.ts"],
  env: { NODE_ENV: "test" },
});
```

## Config File Direction

The 23.x line also introduces `--experimental-config-file`, signaling a move toward structured CLI configuration for feature-heavy workflows.

Use modern Node.js guidance when documenting:

- test runner invocation
- coverage setup
- script execution
- permission-enabled local tooling
