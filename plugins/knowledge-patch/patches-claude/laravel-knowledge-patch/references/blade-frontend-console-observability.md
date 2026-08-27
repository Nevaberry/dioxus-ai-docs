# Blade, Frontend, Console, and Observability

## API-aware maintenance mode (2026-07)

The `down` command now handles API and JSON routes, so non-HTML requests receive maintenance-mode handling as well.

## Artisan failure and silence behavior (2025-12)

`cache:clear` now returns a failure exit code when clearing fails, and `queue:work` respects the standard `--quiet` and `--silent` output flags.

## Backed enums as dynamic Blade components (2025-09)

The component selector passed to `<x-dynamic-component>` may be a `BackedEnum`; callers do not need to extract its backing value before rendering the selected component.

## Blade and Vite font optimization (2026-04)

The new `@fonts` Blade directive works with Vite's font-optimization runtime to provide first-party optimized font handling.

## Blade stack detection (2025-11)

The new `@hasStack` directive conditionally renders content when a named Blade stack contains pushed content.

```blade
@hasStack('scripts')
    @stack('scripts')
@endif
```

## Bootstrap 3 pagination views (13.0-upgrade)

The Bootstrap 3 pagination views are now named `pagination::bootstrap-3` and `pagination::simple-bootstrap-3`, replacing `pagination::default` and `pagination::simple-default` for direct references.

## Config file generation (2025-08)

The new `make:config` Artisan command generates a configuration file in the application's `config` directory.

```shell
php artisan make:config services
```

## Custom command discovery (2025-12)

Console command discovery exposes a `commandFileFinder` hook and excludes test files. The follow-up behavior still discovers a real `Command` class whose name ends in `Test`.

## Datetime maintenance retries (2026-01)

The `down` command's `--retry` option accepts datetime values in addition to delay values, allowing the retry time to target the planned end of maintenance.

```shell
php artisan down --retry="2026-01-28 18:00:00"
```

## Development command registry (2026-06)

Laravel 13 adds `dev` and `dev:list` Artisan commands. Registered development commands track their source, support priority ordering, and the development runner stops the other commands when one fails.

```shell
php artisan dev
php artisan dev:list
```

## Extendable Vite asset paths (2025-10)

Vite asset-path generation can now be customized through inheritance, providing an extension point for applications that resolve built assets from nonstandard locations.

## Extensible maintenance mode facade (2025-07)

The new `MaintenanceMode` facade exposes maintenance-mode driver extension, allowing applications to register custom maintenance backends through the facade.

## Function and constant imports in Blade (2025-04)

Blade's `@use` directive supports PHP `function` and `const` import modifiers in addition to class imports.

```blade
@use('function App\Support\format_money')
@use('const App\Support\DEFAULT_CURRENCY')
```

## Isolated Blade includes (2026-01)

`@includeIsolated` renders a Blade include without inheriting the surrounding template's variables; all required data must be passed explicitly.

```blade
@includeIsolated('partials.user', ['user' => $user])
```

## JSON event listings (2025-04)

The event list command can emit machine-readable output with `php artisan event:list --json`.

## Monthly log rotation (2026-07)

Laravel 13 includes a monthly log driver and a corresponding logging channel configuration.

## New application starter kits (12.0.0)

The React, Svelte, and Vue kits use Inertia 2, TypeScript, shadcn/ui, and Tailwind; the Livewire kit uses Flux UI and Volt. Each has an optional WorkOS AuthKit variant for social authentication, passkeys, and SSO, while Breeze and Jetstream will receive no further updates.

## Optional view timestamp checks (2025-04)

View compilation can be configured to ignore cached-view timestamps, which avoids filesystem timestamp checks when deployments provide an immutable precompiled view cache.

## Prohibiting additional Artisan commands (2026-05)

`queue:clear` and `key:generate` now participate in Laravel's command-prohibition mechanism, allowing production safety policies to block them.

## Refreshable maintenance options (2026-02)

Running the `down` command while the application is already in maintenance mode can refresh its options instead of retaining stale settings.

## Structured JSON logging (2026-04)

Laravel 13 introduces `JsonFormatter` for JSON log output, including exception context when the exception handler is not bound.

## Unescaped Unicode in JavaScript output (13.0-upgrade)

`Js::from()` now applies `JSON_UNESCAPED_UNICODE` by default, so rendered output and exact assertions contain Unicode characters instead of `\u` escape sequences.
