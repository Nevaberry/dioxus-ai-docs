# Container, Authentication, Routing, and Context

## Attribute-declared interface bindings (2025-06)

Container interface-to-implementation bindings can be declared with the PHP `Bind` attribute instead of only in service-provider registration.

```php
#[Bind(RedisEventPusher::class)]
interface EventPusher {}
```

## Closure locations in route listings (2026-03-laravel-12)

`route:list` displays the source file path and line number for closure routes, making those routes traceable from CLI output.

## Conditional container bindings (2026-07)

The `BindWhen` attribute conditionally binds services into the container.

## Container resolution respects default values (12.0-upgrade)

The container no longer injects a resolvable class into an optional class-typed constructor parameter when that parameter has a default value. For `public ?Carbon $date = null`, `resolve()` now leaves `$date` as `null`.

## Contextual injection from application context (2025-05)

The container's `Context` contextual attribute injects a value from Laravel's context repository. `#[Context('trace_id', hidden: true)]` reads from hidden context.

## Controller middleware exclusions (2026-07)

Controllers can use the `WithoutMiddleware` attribute to declare middleware exclusions.

## Defaults for fluent request data (2025-11)

`Request::fluent()` accepts a default value for a missing input key.

```php
$filters = $request->fluent('filters', ['sort' => 'created_at']);
```

## Deprecated request getter (2026-02)

`Illuminate\Http\Request::get()` is deprecated; use an accessor for the intended input source, such as `input()` or `query()`.

## Domain route precedence (13.0-upgrade)

Routes with explicit domains are now matched before routes without domains, regardless of their registration order. Applications relying on the previous precedence should review overlapping domain and non-domain routes.

## Duplicate route-name precedence (12.0-upgrade)

Cached and uncached routing now agree when routes share a name: the first registered route wins. Uncached routing previously selected the last registered route.

## Enum selectors in container attributes (2025-08)

The `Bind` attribute accepts a `UnitEnum` for its environment selector, and the `Database` contextual attribute accepts an enum for its connection selector.

```php
#[Bind(RedisEventPusher::class, environments: AppEnvironment::Production)]
interface EventPusher {}

public function __construct(
    #[Database(DatabaseConnection::Analytics)]
    private Connection $connection,
) {}
```

## JSON-preferred health responses (2026-04)

The built-in health route supports JSON responses, and the application builder provides `prefersJsonResponses()` for selecting JSON-preferred response behavior.

## Macroable rate limiting (2026-07)

`RateLimiter` is macroable, allowing applications to add project-specific rate-limiter helpers.

## Manager extension callback binding (13.0-upgrade)

Closures registered through manager `extend()` methods are now bound to the manager. Values previously accessed through another object as `$this` must be captured explicitly with `use (...)`.

## Middleware-filtered route listings (2025-11)

`route:list` accepts a `--middleware` filter for narrowing its output to routes using a given middleware.

```shell
php artisan route:list --middleware=auth
```

## Nested policy discovery (12.0.0)

Policy auto-discovery now follows parallel nested model and policy namespaces; for example, `App\Models\Admin\User` can discover `App\Policies\Admin\UserPolicy`.

## Nested request merging (12.0-upgrade)

`Request::mergeIfMissing()` now interprets dot notation as a nested array path. A key such as `'user.last_name'` therefore populates nested `user` data instead of creating a literal top-level dotted key.

## Parameter-aware contextual attributes (2026-06)

A contextual attribute's resolution method receives the target reflection parameter, allowing resolution to depend on the parameter to which the attribute is attached.

## Parameter-name route injection (2026-06)

`RouteParameter` can use the name of its attributed parameter, so route injection does not always need a separately repeated parameter name.

## Password reset token expiry units (12.0-upgrade)

`DatabaseTokenRepository` now expects its `$expires` constructor argument in seconds rather than minutes; custom instantiation must convert existing minute values.

## Remembered context values (2025-07)

`Context::remember()` and `Context::rememberHidden()` lazily compute and store a value only when its visible or hidden context key is absent.

```php
$traceId = Context::remember('trace_id', fn () => (string) Str::uuid());
```

## Request forgery protection (13.0-upgrade)

The CSRF middleware is now `PreventRequestForgery` and also validates request origin through `Sec-Fetch-Site`. `VerifyCsrfToken` and `ValidateCsrfToken` remain deprecated aliases; update direct middleware references and use the new `preventRequestForgery(...)` configuration API.

## Response-aware rate limiting (2025-09)

Rate limits can use an `after` callback to inspect the response and decide whether the completed request should count against the limit.

```php
Limit::perMinute(60)
    ->after(fn (Response $response) => $response->successful());
```

## Restricted route unserialization (2026-06)

Routing unserialization now restricts the classes it may instantiate; custom serialized route values can no longer assume arbitrary classes will be restored.

## Return-type-inferred container bindings (12.0.0)

The container can infer the abstract being bound from a concrete closure's declared return type.

```php
$app->bind(fn (): ServiceContract => new Service);
```

## Route metadata (2026-06)

Routes can carry metadata, allowing application or tooling annotations to be associated with route definitions.

## Selective log-context removal (2025-03)

`Log::withoutContext()` accepts keys to remove only selected values from subsequent log context.

```php
Log::withoutContext(['tenant_id', 'trace_id']);
```

## Server-provided application base paths (2025-09)

Application bootstrap may read `APP_BASE_PATH` from `$_SERVER`, allowing a host or bootstrap wrapper to set the base path before the application is loaded.

```php
$_SERVER['APP_BASE_PATH'] = '/srv/application';
```

## String bindings in `Give` (2025-11)

The container's `Give` attribute accepts string service bindings in addition to class names.

```php
public function __construct(
    #[Give('cache.store')] private Repository $cache,
) {}
```
