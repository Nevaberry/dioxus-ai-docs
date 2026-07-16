# Testing, Build Tooling, and Migrations

Batch attribution: 19.0.0, 20.0.0, 21-platform-guides, 21.0.0, 22.0.0.

## Vitest progression and defaults

Angular 20 introduced the CLI's Vitest runner experimentally. Angular 21 makes Vitest the default for new CLI projects: they install Vitest and `jsdom`, and `ng test` runs in a Node DOM environment in watch mode by default. `happy-dom` is the other supported DOM emulator and can replace `jsdom`.

An Angular 20 project that adopts the experimental runner installs both packages and selects the unit-test builder:

```sh
npm install --save-dev vitest jsdom
```

```json
{
  "test": {
    "builder": "@angular/build:unit-test",
    "options": {
      "tsConfig": "tsconfig.spec.json",
      "buildTarget": "::development",
      "runner": "vitest"
    }
  }
}
```

Test files may need explicit `describe`, `it`, and `expect` imports from `vitest`.

## Configure the unit-test target

The `@angular/build:unit-test` target accepts:

- `include` and `exclude`;
- `setupFiles`;
- `providersFile`;
- `coverage`;
- `browsers`;
- `runnerConfig`;
- `outputFile` for writing test output to a file.

`include` defaults to both `**/*.spec.ts` and `**/*.test.ts`.

A `providersFile` must default-export an Angular provider array. Both provider and setup files must be included by the test TypeScript configuration.

```ts
// src/test-providers.ts
import {provideHttpClient} from '@angular/common/http';
import {
  provideHttpClientTesting,
} from '@angular/common/http/testing';

export default [
  provideHttpClient(),
  provideHttpClientTesting(),
];
```

```json
{
  "test": {
    "builder": "@angular/build:unit-test",
    "options": {
      "providersFile": "src/test-providers.ts"
    }
  }
}
```

## Run tests in real browsers

Install either the Playwright or WebdriverIO Vitest browser provider, then use the target's `browsers` option or the `--browsers` flag.

```sh
npm install --save-dev @vitest/browser-playwright playwright
ng test --browsers=chromiumHeadless
```

Browser runs are headed by default. They become headless when `CI` is set; append `Headless` to a browser name to request headless execution explicitly.

## Customize Vitest carefully

Point `runnerConfig` at a custom configuration for advanced Vitest options, or generate a starting configuration:

```sh
ng generate config vitest
```

```json
{
  "test": {
    "builder": "@angular/build:unit-test",
    "options": {
      "runnerConfig": "vitest-base.config.ts"
    }
  }
}
```

The CLI still overrides `test.projects` and `test.include`. Angular does not support the contents of the custom configuration or third-party Vitest plugins, so isolate and own that risk.

## Test zoneless applications

`TestBed` is zoneless by default when `zone.js` is absent. If ZoneJS is loaded in the test environment but production is zoneless, add `provideZonelessChangeDetection()` to align them.

Prefer `await fixture.whenStable()` to routinely forcing `fixture.detectChanges()`. Forced detection can hide an application bug where state changed without scheduling a refresh.

Use exhaustive no-change checking to find missed notifications:

```ts
import {
  provideCheckNoChangesConfig,
  provideZonelessChangeDetection,
} from '@angular/core';
import {TestBed} from '@angular/core/testing';

TestBed.configureTestingModule({
  providers: [
    provideZonelessChangeDetection(),
    provideCheckNoChangesConfig({
      exhaustive: true,
      interval: 1000,
    }),
  ],
});

const fixture = TestBed.createComponent(App);
await fixture.whenStable();
```

Classic Reactive Forms updates do not notify zoneless change detection. See [Core Reactivity](core-reactivity.md) before “fixing” those tests with unconditional detection.

## Migrate legacy test stacks

### Removed and deprecated runners

- The Protractor builder was removed in Angular 19. Move end-to-end tests to a supported tool.
- Angular 21 deprecates its experimental Jest and Web Test Runner integrations and plans to remove them in Angular 22.
- Karma and Jasmine remain fully supported.
- An application that retains Jest needs a community integration.

### Jasmine-to-Vitest schematic

After completing its documented preparation, an existing application can try the experimental Jasmine-to-Vitest refactoring schematic:

```sh
ng g @schematics/angular:refactor-jasmine-vitest
```

Review every automated test rewrite; the schematic performs the source refactoring but does not establish behavioral equivalence by itself.

### Test API removals

Angular 22 renames `TestBed.getFixture()` to `TestBed.getLastFixture()`. It removes `ChangeDetectorRef.checkNoChanges()`; use `fixture.detectChanges()` for the corresponding test workflow.

## Hot replacement during development

Style HMR is enabled by default. Template HMR began as an experimental opt-in:

```sh
NG_HMR_TEMPLATES=1 ng serve
```

Disable HMR with either:

```sh
ng serve --no-hmr
```

or the development-server option:

```json
{"hmr": false}
```

## Modernization migrations

Angular 21 expands modernization support:

- the standalone migration handles `CommonModule`;
- a migration replaces deprecated `RouterTestingModule` usage;
- schematics convert `NgClass` to class bindings;
- schematics convert `NgStyle` to style bindings.

Angular 22's `ng update` migration adds `strictTemplates` to the project TypeScript configuration. It also surfaces duplicate selector matches as compiler diagnostic `NG8023`.

## CLI MCP tools

The Angular CLI MCP server is stable as of Angular 21. Its stable tools include:

- `get_best_practices`;
- `list_projects`;
- `search_documentation`;
- `find_examples`;
- `onpush_zoneless_migration`.

`modernize` remains experimental. `ai_tutor` launches an interactive tutor intended for use with a new Angular application.

Angular 22 stabilizes `devserver.start`, `devserver.stop`, and `devserver.wait_for_build`, along with the MCP server's testing and end-to-end tools. The language service also exposes document symbols for Angular templates.

## Angular skills and browser tools

Angular 22 supplies an `angular-developer` skill with modern practices and progressively loaded references, plus an `angular-new-app` skill for preparing a new application environment. Separate contributor skills describe the framework's internal development model.

Experimental WebMCP integration can expose structured browser tools at application, route, and service scope. It can also generate tools dynamically from Signal Forms. Treat all WebMCP integration points as experimental contracts.

## Build-tool compatibility

Angular 20.2 supports TypeScript 5.9. Angular 22 supports TypeScript 6 and deprecates webpack support, including `@angular-devkit/build-angular` builders and `@ngtools/webpack`, while the application builder moves toward TSGo support.

Use the exact Node.js, TypeScript, and RxJS ranges in [Compatibility, Security, and Release Policy](compatibility-security-and-releases.md); minor Angular lines do not all share one TypeScript ceiling.
