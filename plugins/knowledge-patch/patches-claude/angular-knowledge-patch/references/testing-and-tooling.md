# Testing, Build Tooling, and Migrations

## Development-server HMR

Style hot replacement is enabled by default (`19.0.0`). Template HMR remains experimental and is enabled through an environment variable:

```sh
NG_HMR_TEMPLATES=1 ng serve
```

Disable all HMR with `ng serve --no-hmr` or development-server option `"hmr": false`.

## Removed Protractor builder

The built-in Protractor builder was removed in v19 (`19.0.0`). Projects that still use it must adopt a supported end-to-end test tool before upgrading.

## Vitest evolution

The v20 experimental unit-test builder could run Vitest in Node with jsdom (`20.0.0`). It required explicit installation, the unit-test builder, and sometimes explicit imports of `describe`, `it`, and `expect`:

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

For new v21 CLI projects, Vitest and `jsdom` are the default (`21-platform-guides`). `ng test` runs in a Node DOM environment and watches by default. `happy-dom` is the supported alternative emulator.

## Unit-test target

`@angular/build:unit-test` accepts `include`, `exclude`, `setupFiles`, `providersFile`, `coverage`, and `browsers`. `include` defaults to `**/*.spec.ts` and `**/*.test.ts`.

Use a default-exported provider array to configure global Angular providers. Include the file in the test TypeScript configuration, as with setup files:

```ts
// src/test-providers.ts
import {provideHttpClient} from '@angular/common/http';
import {provideHttpClientTesting} from '@angular/common/http/testing';

export default [provideHttpClient(), provideHttpClientTesting()];
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

## Real-browser tests

Install the Playwright or WebdriverIO Vitest browser provider, then set `browsers` or pass `--browsers` (`21-platform-guides`):

```sh
npm install --save-dev @vitest/browser-playwright playwright
ng test --browsers=chromiumHeadless
```

Browser runs are headed by default. Setting `CI` makes them headless; appending `Headless` to the browser name requests it explicitly.

## Custom Vitest configuration

Point `runnerConfig` at an advanced Vitest configuration or generate a base with `ng generate config vitest`. The Angular CLI still overrides `test.projects` and `test.include`, and does not support the contents of a custom configuration or its third-party plugins.

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

The runner also supports `outputFile` for writing test results (`21.0.0`).

## Zoneless tests

`TestBed` is zoneless by default when `zone.js` is absent. If tests still load ZoneJS while production is zoneless, add `provideZonelessChangeDetection()` (`21-platform-guides`). Prefer `await fixture.whenStable()` over unconditional `fixture.detectChanges()`, which can hide a missing change-notification path.

Use exhaustive no-change checks to expose bindings that changed without scheduling a refresh:

```ts
TestBed.configureTestingModule({
  providers: [
    provideZonelessChangeDetection(),
    provideCheckNoChangesConfig({exhaustive: true, interval: 1000}),
  ],
});

const fixture = TestBed.createComponent(App);
await fixture.whenStable();
```

## Test API changes

In v22, `TestBed.getFixture()` became `TestBed.getLastFixture()` and `ChangeDetectorRef.checkNoChanges()` was removed (`22.0.0`). Use the fixture-level APIs; call `fixture.detectChanges()` when the test explicitly needs a synchronous detection pass, but do not use repeated detection to conceal missing production notifications.

## Test migrations and deprecated runners

After its required preparation, the experimental schematic can refactor Jasmine tests to Vitest (`21.0.0`):

```sh
ng g @schematics/angular:refactor-jasmine-vitest
```

Experimental Jest and Web Test Runner integrations are deprecated and were planned for removal in v22. Karma and Jasmine remained supported at the time of that guidance; applications retaining Jest need a community integration.

## Modernization schematics

Angular 21 migrations (`21.0.0`) include:

- standalone conversion with `CommonModule` support;
- replacement of deprecated `RouterTestingModule` use;
- conversion from `NgClass` to class bindings; and
- conversion from `NgStyle` to style bindings.

Angular 22's update migration adds `strictTemplates` to the project TypeScript configuration (`22.0.0`). Diagnostic NG8023 also turns duplicate selector matches into a compile-time error.

## Build-tool deprecations

Webpack support is deprecated in v22, including `@angular-devkit/build-angular` webpack-based builders and `@ngtools/webpack` (`22.0.0`). Plan migration to the application builder as Angular moves toward TSGo support.

The built-in Hammer.js integration is removed. Applications requiring gesture recognition must supply their own implementation.

## Angular CLI tools

The Angular CLI's project tool server is stable (`21.0.0`). Its tools include `get_best_practices`, `list_projects`, `search_documentation`, `find_examples`, and `onpush_zoneless_migration`. `modernize` remains experimental; `ai_tutor` starts an interactive tutor intended for a new Angular application.

In v22, `devserver.start`, `devserver.stop`, and `devserver.wait_for_build` are stable, along with testing and end-to-end tools (`22.0.0`). The language service also provides Angular-template document symbols.

## Angular Agent Skills

The `angular-developer` skill contains modern practices and progressively loaded references, while `angular-new-app` guides preparation of a new Angular environment (`22.0.0`). Separate contributor skills describe internal framework development. Treat these as Angular-maintained workflow guidance, not application runtime dependencies.

## Experimental WebMCP

Angular can experimentally expose structured browser tools at application, route, and service scope (`22.0.0`). It can also derive tools dynamically from Signal Forms. Keep this integration behind an explicit experimental boundary and review what application capabilities it exposes.
