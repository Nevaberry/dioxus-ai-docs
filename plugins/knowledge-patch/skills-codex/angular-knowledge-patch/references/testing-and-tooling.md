# Testing, Build Tooling, and Migrations

## Vitest progression and defaults

The v20 experimental `@angular/build:unit-test` builder ran Vitest with `jsdom`
after installing both packages and selecting `runner: "vitest"`; test files
could need explicit `describe`, `it`, and `expect` imports (`20.0.0`).

New Angular 21 CLI projects install Vitest and `jsdom`. `ng test` uses the Node
DOM environment and watches by default; `happy-dom` is the other supported DOM
emulator. (`21-platform-guides`)

The unit-test target accepts `include`, `exclude`, `setupFiles`, `providersFile`,
`coverage`, and `browsers`; `include` defaults to `**/*.spec.ts` and
`**/*.test.ts`. `providersFile` must default-export an Angular provider array.
It and setup files must be included by the test TypeScript configuration.
(`21-platform-guides`)

```ts
// src/test-providers.ts
import {provideHttpClient} from '@angular/common/http';
import {provideHttpClientTesting} from '@angular/common/http/testing';

export default [provideHttpClient(), provideHttpClientTesting()];
```

```json
{"test":{"builder":"@angular/build:unit-test","options":{"providersFile":"src/test-providers.ts"}}}
```

For real-browser runs, install the Playwright or WebdriverIO Vitest browser
provider and set `browsers` or pass `--browsers`. Runs are headed by default,
become headless when `CI` is set, and accept an explicit `Headless` suffix.
(`21-platform-guides`)

```sh
npm install --save-dev @vitest/browser-playwright playwright
ng test --browsers=chromiumHeadless
```

Point `runnerConfig` to a custom Vitest configuration or generate a base with
`ng generate config vitest`. The CLI still overrides `test.projects` and
`test.include`, and Angular does not support the custom file's contents or its
third-party plugins. (`21-platform-guides`)

The runner also accepts `outputFile` to write results to a file (`21.0.0`).

## Zoneless tests

`TestBed` is zoneless by default when `zone.js` is absent. If it is loaded, add
`provideZonelessChangeDetection()` to mirror production. Prefer
`await fixture.whenStable()` to unconditional `fixture.detectChanges()`, which
can hide missed notifications. An exhaustive no-change check exposes bindings
that changed without scheduling refresh. (`21-platform-guides`)

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

## Migrations and test integrations

The built-in Protractor builder was removed, so dependent projects must migrate
to a supported end-to-end tool (`19.0.0`). Experimental Jest and Web Test Runner
integrations were deprecated for removal in v22; Karma and Jasmine remained
supported, while retained Jest suites require a community integration
(`21.0.0`).

After its preparatory steps, try the experimental Jasmine-to-Vitest schematic
to refactor an existing suite (`21.0.0`):

```sh
ng g @schematics/angular:refactor-jasmine-vitest
```

The standalone migration supports `CommonModule`. Other schematics replace
deprecated `RouterTestingModule`, convert `NgClass` to class bindings, and
convert `NgStyle` to style bindings (`21.0.0`). The v22 `ng update` migration
adds `strictTemplates` to the TypeScript configuration (`22.0.0`).

## Removed and renamed test APIs

`TestBed.getFixture()` is renamed to `TestBed.getLastFixture()`.
`ChangeDetectorRef.checkNoChanges()` is removed; use `fixture.detectChanges()`
in tests instead. (`22.0.0`)

## Development server and HMR

Style HMR is enabled by default. Template HMR was experimental and enabled with
`NG_HMR_TEMPLATES=1 ng serve`; use `ng serve --no-hmr` or development-server
option `"hmr": false` to disable HMR. (`19.0.0`)

## Compiler and language-service assistance

The CLI warns about unused standalone component imports and the language service
can remove them. Suppress the check only when needed (`19.0.0`):

```json
{"extendedDiagnostics":{"checks":{"unusedStandaloneImports":"suppress"}}}
```

The Angular 22 language service exposes document symbols for Angular templates
(`22.0.0`).

## Angular CLI tools

The Angular CLI MCP server is stable. Its tools include `get_best_practices`,
`list_projects`, `search_documentation`, `find_examples`, and
`onpush_zoneless_migration`. `modernize` remains experimental, while `ai_tutor`
starts an interactive tutor intended for a new Angular application. (`21.0.0`)

The development-server tools `devserver.start`, `devserver.stop`, and
`devserver.wait_for_build` are stable in Angular 22, as are its testing and
end-to-end tools (`22.0.0`).

The `angular-developer` skill provides modern application practices and
progressively loaded references; `angular-new-app` guides setup of a new
environment. Separate contributor skills cover framework internals. (`22.0.0`)

Angular also has experimental WebMCP support for application-, route-, and
service-scoped structured browser tools, including tools generated from dynamic
Signal Forms (`22.0.0`).

## Build integration changes

Webpack support is deprecated, including `@angular-devkit/build-angular`
webpack-based builders and `@ngtools/webpack`, while the application builder
moves toward TSGo support (`22.0.0`). The built-in Hammer.js integration is
removed; applications needing gestures must provide an implementation
(`22.0.0`).
