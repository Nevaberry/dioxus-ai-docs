# HTTP, Routing, Requests, and Processes

HTTP client behavior, requests and responses, routing, rate limits, URLs, pagination, and processes.

## Carbon intervals for process timeouts (13.0.0)

Pending process timeouts accept `CarbonInterval` values in addition to numeric durations.

```php
Process::timeout(CarbonInterval::seconds(30))->run('php artisan report:build');
```

## Conditional CORS bypasses (2026-01)

`HandleCors::skipWhen()` accepts a callback for exempting selected requests from CORS handling.

## Controller middleware exclusions (2026-07)

Controllers can use the `WithoutMiddleware` attribute to declare middleware exclusions.

## Current-page URLs in paginator output (2025-05)

Serialized paginator data now includes `current_page_url`, so API consumers no longer need to reconstruct the URL from `path` and `current_page`.

## Custom server-sent events (2025-03)

`response()->eventStream()` now supports custom event names and start messages, allowing a stream to identify event types and send an initial message.

## Defaults for fluent request data (2025-11)

`Request::fluent()` accepts a default value for a missing input key.

```php
$filters = $request->fluent('filters', ['sort' => 'created_at']);
```

## Defaults when retrieving enum input (2025-05)

Enum retrieval from request data accepts a default enum value when the key is absent or does not yield an enum: `$request->enum('status', Status::class, Status::Draft)`.

## Deferred HTTP batches (2025-10)

HTTP client batches provide `defer()`, allowing a batch to be scheduled for deferred execution instead of being sent immediately.

## Deprecated request getter (2026-02)

`Illuminate\Http\Request::get()` is deprecated; use an accessor for the intended input source, such as `input()` or `query()`.

## Domain route precedence (13.0-upgrade)

Routes with explicit domains are now matched before routes without domains, regardless of their registration order. Applications relying on the previous precedence should review overlapping domain and non-domain routes.

## Duplicate route-name precedence (12.0-upgrade)

Cached and uncached routing now agree when routes share a name: the first registered route wins. Uncached routing previously selected the last registered route.

## Fluent asynchronous HTTP requests (2025-12)

`PendingRequest` HTTP methods may now return promises, and pools use `FluentPromise` for cleaner chaining. `Pool` and `Batch` also expose `newRequest()` for constructing requests within those coordinators.

## HTTP client lifecycle hooks (2025-12)

`PendingRequest` adds `withRequestContext()`, and the HTTP client can run callbacks after building a response, providing explicit request-context and post-construction extension points.

## HTTP pool and batch concurrency (2025-10)

`Http::pool()` and `Http::batch()` support concurrency control, allowing callers to bound the number of simultaneous outgoing requests.

## HTTP pool default concurrency (13.0.0)

Pools created from `PendingRequest` now default to a concurrency of two; specify concurrency explicitly when a different limit is required.

## HTTP query helpers (2026-07)

The HTTP client provides `Http::query()`, while HTTP tests provide `query()` and `queryJson()` helpers for working with request query data.

## HTTP request batches (2025-09)

`Http::batch()` provides first-class batching for multiple outgoing HTTP requests, avoiding manual coordination when a set of client calls should be managed together.

## HTTP response JSON flags (2026-01)

HTTP client responses accept JSON decoding flags through `Response::json()`, including flags such as `JSON_BIGINT_AS_STRING` for preserving large integer values.

```php
$data = Http::get($url)->json(flags: JSON_BIGINT_AS_STRING);
```

## HTTP response override signatures (13.0-upgrade)

Custom HTTP client response classes must keep overrides compatible with the newly declared callback parameters.

```php
public function throw($callback = null);
public function throwIf($condition, $callback = null);
```

## JSON-preferred health responses (2026-04)

The built-in health route supports JSON responses, and the application builder provides `prefersJsonResponses()` for selecting JSON-preferred response behavior.

## JSON-serializable URIs (2025-07)

`Illuminate\Support\Uri` now implements `JsonSerializable`, so URI instances can be passed directly to JSON encoders and JSON responses.

## Macroable invoked processes (2026-06)

`InvokedProcess` is now macroable, allowing applications to add project-specific helpers to invoked process instances.

## Macroable rate limiting (2026-07)

`RateLimiter` is macroable, allowing applications to add project-specific rate-limiter helpers.

## Macroable URIs (2025-04)

`Illuminate\Support\Uri` now supports the `Macroable` extension mechanism, so applications may register custom URI operations with `Uri::macro()`.

## Nested request merging (12.0-upgrade)

`Request::mergeIfMissing()` now interprets dot notation as a nested array path. A key such as `'user.last_name'` therefore populates nested `user` data instead of creating a literal top-level dotted key.

## Normalized HTTP connection exceptions (2025-06)

SSL certificate and connection failures from the HTTP client no longer leak as Guzzle exceptions; they are exposed through Laravel's HTTP client exception abstraction.

## Page numbers in paginator links (2025-08)

Serialized paginator link entries now include a `page` field, giving API clients a numeric page value without having to parse it from each link URL.

## Parameter-name route injection (2026-06)

`RouteParameter` can use the name of its attributed parameter, so route injection does not always need a separately repeated parameter name.

## Per-request HTTP exception truncation (2025-06)

An individual pending HTTP request can set its `RequestException` message truncation limit instead of relying only on the shared default.

```php
Http::truncateExceptionsAt(240)->get($url)->throw();
```

## PSR-compatible HTTP client (2026-06)

Laravel 13's HTTP client can be used directly as a PSR client, allowing integrations that require the PSR client contract to accept Laravel's client.

## Recording non-faked HTTP requests (2025-03)

The HTTP client can record real requests without faking their responses, so tests and diagnostics can inspect traffic while it is still sent normally.

```php
Http::record();
Http::get('https://example.test');
$recorded = Http::recorded();
```

## Request-aware after-response callbacks (2026-04)

After-response callbacks now receive the current request as an argument.

## Response-aware rate limiting (2025-09)

Rate limits can use an `after` callback to inspect the response and decide whether the completed request should count against the limit.

```php
Limit::perMinute(60)
    ->after(fn (Response $response) => $response->successful());
```

## Restricted route unserialization (2026-06)

Routing unserialization now restricts the classes it may instantiate; custom serialized route values can no longer assume arbitrary classes will be restored.

## Retrying HTTP middleware exceptions (2025-04)

HTTP client requests configured with `retry()` now retry when client middleware throws an exception instead of limiting retries to response and connection failures.

## Route metadata (2026-06)

Routes can carry metadata, allowing application or tooling annotations to be associated with route definitions.

## Safe malformed cursor decoding (2026-04)

`Cursor::fromEncoded()` returns `null` for a malformed payload, so callers handling untrusted cursor input should null-check the result.

## Wildcard trim exclusions (2025-12)

`TrimStrings` middleware exclusions accept wildcard patterns, allowing one pattern to preserve matching nested inputs instead of enumerating every field.
