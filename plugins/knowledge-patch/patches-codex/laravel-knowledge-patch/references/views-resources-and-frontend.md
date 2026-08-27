# Views, Resources, and Frontend Integration

Blade, resources and serialization, Vite, frontend kits, pagination views, and image or font integration.

## Backed enums as dynamic Blade components (2025-09)

The component selector passed to `<x-dynamic-component>` may be a `BackedEnum`; callers do not need to extract its backing value before rendering the selected component.

## Blade and Vite font optimization (2026-04)

The new `@fonts` Blade directive works with Vite's font-optimization runtime to provide first-party optimized font handling.

## Blade context blocks (2025-07)

The new `@context` directive renders a block when the requested context key exists and exposes its value as `$value`.

```blade
@context('trace_id')
    <span>{{ $value }}</span>
@endcontext
```

## Blade stack detection (2025-11)

The new `@hasStack` directive conditionally renders content when a named Blade stack contains pushed content.

```blade
@hasStack('scripts')
    @stack('scripts')
@endif
```

## Bootstrap 3 pagination views (13.0-upgrade)

The Bootstrap 3 pagination views are now named `pagination::bootstrap-3` and `pagination::simple-bootstrap-3`, replacing `pagination::default` and `pagination::simple-default` for direct references.

## Explicit model resource attributes (2025-09)

Models may declare their API resource and resource collection with `#[UseResource(...)]` and `#[UseResourceCollection(...)]` instead of relying only on convention-based discovery.

```php
#[UseResource(UserResource::class)]
#[UseResourceCollection(UserCollection::class)]
class User extends Model {}
```

## Extendable Vite asset paths (2025-10)

Vite asset-path generation can now be customized through inheritance, providing an extension point for applications that resolve built assets from nonstandard locations.

## First-party image processing (2026-07)

Laravel 13 adds first-party image processing, and `ImageManager::fromStorage()` accepts enum disk selectors.

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

## JSON:API resources (2026-01)

Laravel now includes a `JsonApiResource` trait for JSON:API resource serialization. Resource handling deduplicates circular references, and `ModelInspector` results now include the model's `JsonResource`.

## Limiting Vite asset preloads (2025-05)

Laravel's Vite integration can cap the number of assets preloaded for an entry point, avoiding an unbounded set of preload links for large dependency graphs.

## Model resource conversion (2025-04)

Models and Eloquent collections can convert themselves directly to their conventionally discovered API resources.

```php
return $user->toResource();
return User::all()->toResourceCollection();
```

## New application starter kits (12.0.0)

The React, Svelte, and Vue kits use Inertia 2, TypeScript, shadcn/ui, and Tailwind; the Livewire kit uses Flux UI and Volt. Each has an optional WorkOS AuthKit variant for social authentication, passkeys, and SSO, while Breeze and Jetstream will receive no further updates.

## Optional view timestamp checks (2025-04)

View compilation can be configured to ignore cached-view timestamps, which avoids filesystem timestamp checks when deployments provide an immutable precompiled view cache.

## Unescaped Unicode in JavaScript output (13.0-upgrade)

`Js::from()` now applies `JSON_UNESCAPED_UNICODE` by default, so rendered output and exact assertions contain Unicode characters instead of `\u` escape sequences.
