# Framework Core, Container, and Utilities

Container behavior, contextual attributes, collections, strings, numbers, helpers, and framework contracts.

## `DatePeriod` range queries (2026-02)

`whereBetween()` accepts `DatePeriod` boundaries and handles periods that do not have an end date.

## Attribute-declared interface bindings (2025-06)

Container interface-to-implementation bindings can be declared with the PHP `Bind` attribute instead of only in service-provider registration.

```php
#[Bind(RedisEventPusher::class)]
interface EventPusher {}
```

## Callback-aware single-item checks (2025-05)

`Collection::containsOneItem()` accepts a callback and returns whether exactly one item satisfies it, such as `$users->containsOneItem(fn (User $user) => $user->isAdmin())`.

## Carbon arithmetic overflow control (2026-04)

Carbon's `plus()` and `minus()` methods accept an `overflow` option for controlling rollover during date arithmetic.

## Carbon intervals for retry sleeps (2026-03-laravel-12)

Retry sleep durations accept `CarbonInterval` values in addition to numeric durations.

```php
retry(3, fn () => $client->send(), CarbonInterval::seconds(2));
```

## Closure conditions for `when()` (12.0.0)

The `when()` helper accepts a closure as its condition and evaluates the closure to choose the applicable branch.

```php
$status = when(fn () => $ready, fn () => 'ready', fn () => 'waiting');
```

## Closure selectors for collection plucks (2025-07)

Both the value and key arguments to `Collection::pluck()` may be closures, allowing computed values and keys without a preceding `map()`.

```php
$names = $users->pluck(
    fn (User $user) => $user->name,
    fn (User $user) => $user->id,
);
```

## Collection chunks without preserved keys (2025-03)

`Collection::chunk()` can reindex each chunk instead of preserving the original keys.

```php
$chunks = $items->chunk(100, preserveKeys: false);
```

## Collection reduction into an accumulator (2026-07)

Collections provide `reduceInto()` for reductions that build into an accumulator.

## Conditional container bindings (2026-07)

The `BindWhen` attribute conditionally binds services into the container.

## Container resolution respects default values (12.0-upgrade)

The container no longer injects a resolvable class into an optional class-typed constructor parameter when that parameter has a default value. For `public ?Carbon $date = null`, `resolve()` now leaves `$date` as `null`.

## Contextual injection from application context (2025-05)

The container's `Context` contextual attribute injects a value from Laravel's context repository. `#[Context('trace_id', hidden: true)]` reads from hidden context.

## Core contract additions (13.0-upgrade)

Custom contract implementations must add `Dispatcher::dispatchAfterResponse($command, $handler = null)`, the `ResponseFactory::eventStream` signature, and `MustVerifyEmail::markEmailAsUnverified()`.

## Count-aware strings (2026-07)

`Str` and `Stringable` provide `counted()` for count-aware string generation.

## Custom environment adapters (12.0.0)

`Env::extend()` provides an extension point for registering custom adapters used to load environment variables.

## Depth-limited array flattening (2026-03-laravel-12)

`Arr::dot()` accepts a depth argument for limiting how deeply nested arrays are flattened.

```php
$flattened = Arr::dot($data, depth: 2);
```

## Enum collection grouping (2025-09)

`Collection::countBy()` callbacks may return enum values, and `Collection::groupBy()` accepts `UnitEnum` values, so callers no longer need to convert enum grouping keys themselves.

## Enum collection sorting (2026-04)

Collection and `Arr` sorting operations accept the `SortDirection` enum.

## Enum keys in collections (2025-08)

`Collection::keyBy()` accepts an enum returned as the key, normalizing it into a usable array key instead of requiring callers to convert it first.

```php
$ordersByStatus = $orders->keyBy(
    fn (Order $order) => $order->status,
);
```

## Enum selectors across managers (2026-04)

Manager methods now accept enum selectors across queue, logging, cache, mail, authentication, password broker, broadcasting, notification, and concurrency drivers. Enum support also covers default-driver setters for queue, logging, and sessions, Redis purging, `RateLimitedWithRedis` limiter names, and cache `touch()` keys.

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

## Enum-aware integration points (2025-12)

Translator replacement values may be enums, and `Storage::fake()` accepts an enum as its disk name, avoiding manual scalar conversion at those call sites.

## Expanded enum integration (2026-01)

Session and cache APIs accept enum keys more broadly, including session `now()` / `flash()` and cache `flexible()` / `withoutOverlapping()`. Authorization ability checks accept `UnitEnum`, while `PendingBatch::onConnection()` and `Storage::persistentFake()` accept enum selectors.

## Expanded framework contracts (12.0.0)

The response factory contract now declares `streamJson()`, the cursor paginator contract declares `hasMorePages()`, the paginator contract declares `withQueryString()`, and the session contract declares `flash()`; custom implementations must provide these methods.

## Expanded PHP attributes (13.0.0)

Controllers can declare middleware and authorization checks with `#[Middleware]` and `#[Authorize]`. Queue jobs also support `#[Tries]`, `#[Backoff]`, `#[Timeout]`, and `#[FailOnTimeout]` for colocated execution policy.

```php
#[Middleware('auth')]
class CommentController
{
    #[Middleware('subscribed')]
    #[Authorize('create', [Comment::class, 'post'])]
    public function store(Post $post) {}
}
```

## First-party AI SDK (13.0.0)

Laravel's AI SDK provides provider-independent agents, tool calling, embeddings, image and audio generation, and vector-store integration through Laravel-native APIs.

```php
use App\Ai\Agents\SalesCoach;

$response = SalesCoach::make()->prompt('Analyze this sales transcript...');
```

## Flags for custom JSON encoders (2025-04)

Custom `Json::$encoder` callbacks now receive the JSON encoding flags, so replacements can honor the same options as the default encoder.

## Inherited framework attributes (2026-04)

Model `CollectedBy` attributes, including those on abstract parents, controller `Middleware` attributes, and queued `WithoutRelations` attributes are inherited. A child model's `Table` attribute overrides its parent's.

## Iterable array helpers (2026-07)

`Arr::every()`, `Arr::some()`, and `Arr::last()` support iterable inputs.

## Iterable fluent objects (2025-07)

`Illuminate\Support\Fluent` is now iterable, so its attributes can be consumed directly with `foreach` and other iterable-aware code.

## Keyed concurrency results (12.0-upgrade)

`Concurrency::run()` preserves keys when given an associative array, so callers now receive a keyed result instead of a numerically indexed one.

```php
$result = Concurrency::run([
    'first' => fn () => 2,
    'second' => fn () => 4,
]);
// ['first' => 2, 'second' => 4]
```

## Lazy and proxy object helpers (2025-12)

The support layer now includes `lazy` and `proxy` object helpers, providing first-party entry points for lazy or proxied object usage.

## Lazy collection heartbeats (2025-08)

`LazyCollection::withHeartbeat()` can invoke a heartbeat while a lazy sequence is being consumed, allowing long-running iteration to renew a lease or report liveness.

## Lazy collection timeout callbacks (2025-09)

`LazyCollection::takeUntilTimeout()` accepts a callback, allowing timeout-driven lazy iteration to trigger follow-up work when its time limit is reached.

## Lazy exceptions in `throw_if()` (2025-10)

`throw_if()` accepts a closure for lazily constructing the exception when its condition is true.

```php
throw_if($invalid, fn () => new DomainException('Invalid state'));
```

## Literal translation delimiters (2026-01)

Translation lines may now contain square brackets and curly braces without those characters being rejected simply because they resemble choice delimiters.

## Locale-aware number parsing (2025-05)

`Number::parseInt()` and `Number::parseFloat()` parse locale-formatted input, including locale-specific grouping and decimal separators; for example, `Number::parseFloat('1.234,56', locale: 'de')` returns `1234.56`.

## Manager extension callback binding (13.0-upgrade)

Closures registered through manager `extend()` methods are now bound to the manager. Values previously accessed through another object as `$this` must be captured explicitly with `use (...)`.

## Multiline `Str::is()` matching (12.0.0)

`Str::is()` patterns now match across line breaks in multiline strings.

## New macro extension points (2025-09)

`RouteRegistrar` and `Illuminate\Support\Benchmark` are now macroable, so applications may add project-specific route-registration and benchmark helpers with their usual `macro()` APIs.

## Nullable defaults in method injection (13.0-upgrade)

`Container::call()` now honors a nullable class parameter's default when no binding exists, matching constructor injection behavior. A parameter such as `?Carbon $date = null` now receives `null` rather than an automatically resolved `Carbon` instance.

## Number parsing failures (2025-09)

The locale-aware number parsing helpers may return `false`; callers of `Number::parseInt()` and `Number::parseFloat()` must account for parse failure rather than assuming a numeric result.

## Optional normalization before case conversion (2026-05)

`Str::studly()` and `Str::pascal()` accept a `normalize` parameter for normalizing input before case conversion.

```php
Str::studly($value, normalize: true);
```

## Parameter-aware contextual attributes (2026-06)

A contextual attribute's resolution method receives the target reflection parameter, allowing resolution to depend on the parameter to which the attribute is attached.

## PHP 8.5 polyfill helper conflicts (13.0-upgrade)

Laravel 13 depends on `symfony/polyfill-php85`, which may define globals such as `array_first()` and `array_last()` below PHP 8.5. Remove conflicting legacy helpers and use `Arr::first()` or related `Arr` methods when callback-based behavior is required.

## Remembered context values (2025-07)

`Context::remember()` and `Context::rememberHidden()` lazily compute and store a value only when its visible or hidden context key is absent.

```php
$traceId = Context::remember('trace_id', fn () => (string) Str::uuid());
```

## Return-type-inferred container bindings (12.0.0)

The container can infer the abstract being bound from a concrete closure's declared return type.

```php
$app->bind(fn (): ServiceContract => new Service);
```

## Scoped context (2025-03)

`Context::scope()` bounds temporary context changes to a callback and restores the surrounding context afterward.

```php
Context::scope(function () {
    Context::add('tenant_id', 123);
});
```

## Server-provided application base paths (2025-09)

Application bootstrap may read `APP_BASE_PATH` from `$_SERVER`, allowing a host or bootstrap wrapper to set the base path before the application is loaded.

```php
$_SERVER['APP_BASE_PATH'] = '/srv/application';
```

## Singleton and scoped container attributes (2025-07)

The container's `Singleton` and `Scoped` attributes declare a class's lifetime without service-provider binding code.

```php
#[Singleton]
final class ExchangeRates {}

#[Scoped]
final class RequestState {}
```

## Static higher-order collection calls (2025-06)

Higher-order collection proxies can call static methods when the collection contains class strings.

```php
$labels = collect([AdminRole::class, MemberRole::class])->map->label();
```

## Stepped lazy ranges (12.0.0)

`LazyCollection::range()` accepts a step argument.

```php
LazyCollection::range(1, 5, 2)->all(); // [1, 3, 5]
```

## String bindings in `Give` (2025-11)

The container's `Give` attribute accepts string service bindings in addition to class names.

```php
public function __construct(
    #[Give('cache.store')] private Repository $cache,
) {}
```

## Timeouts for concurrent runs (2026-05)

`Concurrency::run()` supports runtime timeouts, allowing a group of concurrent tasks to be bounded.

## Typed array accessors (2025-04)

`Arr` provides typed getters for string, integer, float, boolean, and array values, allowing callers to require the expected type while reading a key.

```php
$port = Arr::integer($config, 'port');
$debug = Arr::boolean($config, 'debug');
```

## Typed translation access (2026-06)

Laravel's translation facilities expose typed accessors, avoiding manual narrowing of general translation results.

## Unicode-aware string trimming (2025-05)

`Str::trim()` now removes the full set of invisible characters instead of only conventional whitespace, changing results for strings containing Unicode formatting or zero-width characters.
