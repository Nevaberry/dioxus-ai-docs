# Migration and Configuration

## Replace workspaces with projects

Vitest 3.0.0 introduced inline workspace declarations through `test.workspace`, which removed the need for a separate workspace file. Vitest 3.2.0 then deprecated both `test.workspace` and the separate `vitest.workspace` file in favor of root-level `test.projects`.

Use the current form:

```ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    projects: ['packages/*'],
  },
})
```

Treat an old inline `workspace` declaration as a migration waypoint, not a target configuration. See [Projects and coverage](projects-and-coverage.md) for project matching, inheritance, identity, and root-only settings.

## Run a test selected by source line

Since 3.0.0, append a line number to a test-file path to select the test at that location. Both relative path forms are accepted:

```sh
vitest basic/foo.js:10
vitest ./basic/foo.js:10
```

## Trigger watch reruns for non-import dependencies

Since 3.2.0, `test.watchTriggerPatterns` maps changed files to tests that should rerun. Use it for templates, child-process inputs, generated assets, and other dependencies absent from the module import graph.

```ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    watchTriggerPatterns: [{
      pattern: /^src\/templates\/(.*)\.html$/,
      testsToRun: (_file, match) => `api/tests/mailers/${match[1]}.test.ts`,
    }],
  },
})
```

## Align Vitest with the installed Vite

Vitest 4.1.0 supports Vite 8 and uses the project's installed `vite` when possible. This avoids configuration type mismatches caused by separate Vite copies. Diagnose unexpected config typing or plugin behavior against the Vite version actually installed in the project.

## Account for corrected lifecycle concurrency

Vitest 4.1.11 again applies the global concurrency limit while test lifecycles execute. Suites that worked around the regression by adding their own throttling should re-evaluate that workaround, because test setup and teardown should no longer exceed the intended global cap.
