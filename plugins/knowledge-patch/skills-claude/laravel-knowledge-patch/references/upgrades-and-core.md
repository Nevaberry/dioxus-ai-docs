# Upgrades and Core Lifecycle

## `DatePeriod` range queries (2026-02)

`whereBetween()` accepts `DatePeriod` boundaries and handles periods that do not have an end date.

## Allowed URLs while preventing stray requests (2025-08)

`Http::preventStrayRequests()` accepts allowed URL patterns, so tests may block all unexpected outbound traffic while permitting selected real endpoints.

```php
Http::preventStrayRequests(allowedUrls: [
    'https://telemetry.example/*',
]);
```

## Associative eager-loading keys (2026-02)

Eager-loaded relationships now retain associative keys instead of reindexing their related results.

## Callback-aware single-item checks (2025-05)

`Collection::containsOneItem()` accepts a callback and returns whether exactly one item satisfies it, such as `$users->containsOneItem(fn (User $user) => $user->isAdmin())`.

## Callback-based exception report suppression (2025-07)

`dontReportUsing()` registers a callback that filters exceptions from reporting when a class-only `dontReport` list is not expressive enough.

## Callback-based signed URL exclusions (12.0.0)

Signed URL validation can use a closure to choose which query-string parameters to ignore.

## Core contract additions (13.0-upgrade)

Custom contract implementations must add `Dispatcher::dispatchAfterResponse($command, $handler = null)`, the `ResponseFactory::eventStream` signature, and `MustVerifyEmail::markEmailAsUnverified()`.

## Current-page URLs in paginator output (2025-05)

Serialized paginator data now includes `current_page_url`, so API consumers no longer need to reconstruct the URL from `path` and `current_page`.

## Custom environment adapters (12.0.0)

`Env::extend()` provides an extension point for registering custom adapters used to load environment variables.

## Defaults when retrieving enum input (2025-05)

Enum retrieval from request data accepts a default enum value when the key is absent or does not yield an enum: `$request->enum('status', Status::class, Status::Draft)`.

## Dependency requirements (12.0-upgrade)

Laravel 12 applications use `laravel/framework:^12.0`, PHPUnit 11, or Pest 3. Carbon 2 support is removed, so Carbon 3 is required.

## Dependency requirements (13.0-upgrade)

Laravel 13 applications use `laravel/framework:^13.0` and `laravel/tinker:^3.0`; update optional constraints to `laravel/boost:^2.0`, `phpunit/phpunit:^12.0`, or `pestphp/pest:^4.0` where applicable.

## Depth-limited array flattening (2026-03-laravel-12)

`Arr::dot()` accepts a depth argument for limiting how deeply nested arrays are flattened.

```php
$flattened = Arr::dot($data, depth: 2);
```

## Enum selectors across managers (2026-04)

Manager methods now accept enum selectors across queue, logging, cache, mail, authentication, password broker, broadcasting, notification, and concurrency drivers. Enum support also covers default-driver setters for queue, logging, and sessions, Redis purging, `RateLimitedWithRedis` limiter names, and cache `touch()` keys.

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

## Filled bulk inserts (2025-04)

`Model::fillAndInsert()` merges model attributes before inserting multiple records, allowing bulk inserts to use filled model data.

```php
Flight::fillAndInsert([
    ['number' => 'AC100'],
    ['number' => 'AC200'],
]);
```

## First-party AI SDK (13.0.0)

Laravel's AI SDK provides provider-independent agents, tool calling, embeddings, image and audio generation, and vector-store integration through Laravel-native APIs.

```php
use App\Ai\Agents\SalesCoach;

$response = SalesCoach::make()->prompt('Analyze this sales transcript...');
```

## Guided Boost upgrades (13.0-upgrade)

Laravel Boost 2 can guide an installed Laravel 12 application through the upgrade with the `/upgrade-laravel-v13` command.

## Inherited framework attributes (2026-04)

Model `CollectedBy` attributes, including those on abstract parents, controller `Middleware` attributes, and queued `WithoutRelations` attributes are inherited. A child model's `Table` attribute overrides its parent's.

## Lazy creation values (2026-02)

`firstOrCreate()` and `createOrFirst()` accept a closure for their values payload, allowing creation attributes to be computed only when an insert is needed.

## Local temporary upload URLs (2026-02)

The local filesystem driver supports `temporaryUploadUrl()`, extending temporary upload URL generation beyond remote object-store disks.

## Named event arguments (2026-02)

Event classes can be dispatched or broadcast with named constructor arguments, so callers no longer have to supply every event argument positionally.

```php
OrderShipped::dispatch(order: $order, notify: true);
```

## Nested array notation in `loadMissing` (2025-08)

`loadMissing()` accepts nested relationship arrays in addition to flattened relationship paths.

```php
$post->loadMissing([
    'comments' => ['author'],
]);
```

## New macro extension points (2025-09)

`RouteRegistrar` and `Illuminate\Support\Benchmark` are now macroable, so applications may add project-specific route-registration and benchmark helpers with their usual `macro()` APIs.

## Nullable defaults in method injection (13.0-upgrade)

`Container::call()` now honors a nullable class parameter's default when no binding exists, matching constructor injection behavior. A parameter such as `?Carbon $date = null` now receives `null` rather than an automatically resolved `Carbon` instance.

## Opting listeners out of discovery (2026-05)

Auto-discovered event listeners can opt out of discovery when they should only be registered explicitly.

## Optional normalization before case conversion (2026-05)

`Str::studly()` and `Str::pascal()` accept a `normalize` parameter for normalizing input before case conversion.

```php
Str::studly($value, normalize: true);
```

## PHP 8.5 polyfill helper conflicts (13.0-upgrade)

Laravel 13 depends on `symfony/polyfill-php85`, which may define globals such as `array_first()` and `array_last()` below PHP 8.5. Remove conflicting legacy helpers and use `Arr::first()` or related `Arr` methods when callback-based behavior is required.

## PHP support window (12.0.0)

Laravel 12 supports PHP 8.2 through 8.5. Bug fixes are scheduled through August 13, 2026, and security fixes through February 24, 2027.

## PHP support window (13.0.0)

Laravel 13 requires PHP 8.3 and supports PHP 8.3 through 8.5. Bug fixes are scheduled through Q3 2027 and security fixes through March 17, 2028.

## Readable encrypted environment files (2026-01)

`env:encrypt --readable` keeps environment key names visible in the encrypted output.

```shell
php artisan env:encrypt --readable
```

## Remember-cookie payloads (2026-01)

Remember cookies now store a MAC of the user's password hash instead of the hash itself. Custom code that reads or creates these cookies must not expect the raw password hash.

## Request-aware after-response callbacks (2026-04)

After-response callbacks now receive the current request as an argument.

## Safe malformed cursor decoding (2026-04)

`Cursor::fromEncoded()` returns `null` for a malformed payload, so callers handling untrusted cursor input should null-check the result.

## Semantic vector queries (13.0.0)

The query builder supports semantic similarity searches backed by PostgreSQL and `pgvector`, including embedding plain-language query strings through `whereVectorSimilarTo()`.

```php
$documents = DB::table('documents')
    ->whereVectorSimilarTo('embedding', 'Best wineries in Napa Valley')
    ->limit(10)
    ->get();
```

## Stepped lazy ranges (12.0.0)

`LazyCollection::range()` accepts a step argument.

```php
LazyCollection::range(1, 5, 2)->all(); // [1, 3, 5]
```

## Subqueries as range bounds (2026-01)

Query-builder `between` conditions now accept subqueries in their boundary values and in the column-bound variant, allowing ranges whose limits are computed by another query.

## Typed array accessors (2025-04)

`Arr` provides typed getters for string, integer, float, boolean, and array values, allowing callers to require the expected type while reading a key.

```php
$port = Arr::integer($config, 'port');
$debug = Arr::boolean($config, 'debug');
```

## Updated dependency compatibility (2025-11)

Laravel 12 now allows Resend 1.x and supports Symfony 7.4.

## Wildcard trim exclusions (2025-12)

`TrimStrings` middleware exclusions accept wildcard patterns, allowing one pattern to preserve matching nested inputs instead of enumerating every field.
