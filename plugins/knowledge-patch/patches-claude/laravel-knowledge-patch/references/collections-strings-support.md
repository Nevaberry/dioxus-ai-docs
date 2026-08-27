# Collections, Strings, Support APIs, and JSON Schema

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

## Count-aware strings (2026-07)

`Str` and `Stringable` provide `counted()` for count-aware string generation.

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

## Flags for custom JSON encoders (2025-04)

Custom `Json::$encoder` callbacks now receive the JSON encoding flags, so replacements can honor the same options as the default encoder.

## Iterable array helpers (2026-07)

`Arr::every()`, `Arr::some()`, and `Arr::last()` support iterable inputs.

## Iterable fluent objects (2025-07)

`Illuminate\Support\Fluent` is now iterable, so its attributes can be consumed directly with `foreach` and other iterable-aware code.

## JSON-serializable URIs (2025-07)

`Illuminate\Support\Uri` now implements `JsonSerializable`, so URI instances can be passed directly to JSON encoders and JSON responses.

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

## Macroable URIs (2025-04)

`Illuminate\Support\Uri` now supports the `Macroable` extension mechanism, so applications may register custom URI operations with `Uri::macro()`.

## Multiline `Str::is()` matching (12.0.0)

`Str::is()` patterns now match across line breaks in multiline strings.

## Number parsing failures (2025-09)

The locale-aware number parsing helpers may return `false`; callers of `Number::parseInt()` and `Number::parseFloat()` must account for parse failure rather than assuming a numeric result.

## Page numbers in paginator links (2025-08)

Serialized paginator link entries now include a `page` field, giving API clients a numeric page value without having to parse it from each link URL.

## Static higher-order collection calls (2025-06)

Higher-order collection proxies can call static methods when the collection contains class strings.

```php
$labels = collect([AdminRole::class, MemberRole::class])->map->label();
```

## Typed translation access (2026-06)

Laravel's translation facilities expose typed accessors, avoiding manual narrowing of general translation results.

## Unicode-aware string trimming (2025-05)

`Str::trim()` now removes the full set of invisible characters instead of only conventional whitespace, changing results for strings containing Unicode formatting or zero-width characters.
