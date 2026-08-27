---
name: laravel-knowledge-patch
description: Laravel
version: "13.23.0"
license: MIT
metadata:
  author: Nevaberry
---


# Laravel Knowledge Patch

Use this patch when implementing, reviewing, testing, or upgrading Laravel applications and framework extensions.
Inspect `composer.json` first, then apply only guidance that exists in the application's installed framework version.
Trust the manifest, lockfile, application code, and tests when they show behavior that differs from this guidance.

## Reference index

| Reference | Topics |
| --- | --- |
| [Cache, sessions, and filesystems](references/cache-session-and-filesystem.md) | Cache stores and locks, Redis, sessions, disks, and filesystem URLs |
| [Database, Eloquent, and schema](references/database-eloquent-and-schema.md) | Queries, models, relationships, casts, migrations, indexes, and driver behavior |
| [Events, observability, and operations](references/events-observability-and-operations.md) | Logging, lifecycle events, maintenance mode, reloads, and failure reporting |
| [Framework core and container](references/framework-core-and-container.md) | Container attributes, contracts, collections, strings, context, and helpers |
| [HTTP, routing, and processes](references/http-routing-and-processes.md) | Requests, responses, routing, HTTP client, pagination, rate limits, and processes |
| [Mail, notifications, and broadcasting](references/mail-notifications-and-broadcasting.md) | Mail transports, mailables, notification lifecycle, and broadcasting |
| [Queues, jobs, and scheduling](references/queues-jobs-and-scheduling.md) | Drivers, jobs, batches, workers, deferred execution, and scheduler controls |
| [Testing, CLI, and tooling](references/testing-cli-and-tooling.md) | Test isolation, fakes, dependency compatibility, Artisan, and development commands |
| [Validation, authentication, and security](references/validation-auth-and-security.md) | Rules, login behavior, authorization, request forgery protection, and encryption |
| [Views, resources, and frontend](references/views-resources-and-frontend.md) | Blade, API resources, Vite, starter kits, fonts, and images |

## Major-upgrade triage

### Runtime and package constraints

- Laravel 13 requires PHP 8.3 and uses `laravel/framework:^13.0` plus `laravel/tinker:^3.0`.
- Relevant Laravel 13 upgrades use Boost 2, PHPUnit 12, or Pest 4 constraints.
- Laravel 12 uses `laravel/framework:^12.0`, Carbon 3, PHPUnit 11 or newer, or Pest 3.
- Laravel 12 supports PHP 8.2 through 8.5; Laravel 13 supports PHP 8.3 through 8.5.
- Beanstalkd applications moving to Laravel 13 need Pheanstalk 8; version 5 is no longer supported.

### Laravel 13 breaking changes

- Explicitly set `CACHE_PREFIX`, `REDIS_PREFIX`, and `SESSION_COOKIE` when old cache, Redis, or cookie identifiers must remain stable.
- Cache stores must implement `touch($key, $seconds)`.
- Cached PHP objects require an allow-list in `cache.serializable_classes`; the default rejects serialized classes.
- Custom contract implementations must add the new dispatcher, response-factory, and email-verification methods.
- MySQL and MariaDB `upsert()` require a non-empty `uniqueBy` argument.
- Joined MySQL deletes now retain `ORDER BY` and `LIMIT`; unsupported variants fail instead of becoming unbounded deletes.
- Do not instantiate a model recursively from its own boot or trait-boot methods.
- Set custom polymorphic pivot table names explicitly when retaining an inferred singular table name.
- Update custom HTTP response overrides so `throw()` and `throwIf()` accept callback parameters.
- `JobAttempted::$exception` replaces the boolean `exceptionOccurred` property.
- `QueueBusy::$connectionName` replaces `QueueBusy::$connection`.
- Custom queue drivers must implement pending, delayed, reserved, and oldest-pending metrics.
- Explicit-domain routes take precedence over routes without domains regardless of registration order.
- Scheduling callbacks passed to `withScheduling()` are registered when `Schedule` resolves, not immediately.
- Use `PreventRequestForgery` and `preventRequestForgery(...)`; the old CSRF middleware names are deprecated aliases.
- Capture external values explicitly in manager extension closures because those closures are bound to the manager.
- Re-register custom `Str` UUID, ULID, and random factories in each test setup that needs them.
- Expect `Js::from()` to emit unescaped Unicode.
- Remove legacy global helpers that conflict with PHP 8.5 polyfills.
- Use the renamed Bootstrap 3 pagination views for direct references.

### Laravel 12 breaking changes

- Convert custom `DatabaseTokenRepository` expiration arguments from minutes to seconds.
- Expect associative input to `Concurrency::run()` to return keyed results.
- Optional class-typed constructor parameters with defaults keep those defaults during container resolution.
- Construct `Blueprint` and database grammars with a `Connection`; removed prefix mutators are unavailable.
- `HasUuids` generates ordered UUIDv7 values; use `HasVersion4Uuids` when UUIDv4 must remain.
- `Request::mergeIfMissing()` treats dotted keys as nested paths.
- Duplicate route names resolve to the first registered route in cached and uncached routing.
- Configure the local disk root explicitly to retain `storage/app`; the fallback is private storage.
- Opt into SVG validation with `image:allow_svg` or `File::image(allowSvg: true)`.
- Account for `Eloquent\Collection::partition()` returning a support collection.
- Provide native MariaDB client binaries for database CLI operations.

## High-value framework behavior

### Container and core

- Closure bindings can infer their abstract from a declared return type.
- `Bind`, `BindWhen`, `Singleton`, and `Scoped` attributes reduce service-provider binding code.
- Contextual attributes can inject context, database, cache, and other manager-selected values, including enum selectors.
- Contextual attribute resolution can inspect the target reflection parameter.
- `Context::scope()` restores surrounding context after a callback.
- `Context::remember()` and `rememberHidden()` lazily populate missing values.
- Collections support closure-based `pluck()`, enum grouping and keys, `reduceInto()`, and callback-aware `containsOneItem()`.
- `LazyCollection` supports stepped ranges, heartbeats, and timeout callbacks.
- `Arr` has typed getters, depth-limited `dot()`, and iterable-aware `every()`, `some()`, and `last()`.
- Locale-aware number parsing can return `false`; handle failed parses explicitly.
- `Str::trim()` removes invisible Unicode characters, while `studly()` and `pascal()` can normalize before conversion.
- Concurrent runs accept timeouts, and process timeouts accept `CarbonInterval`.

### Database and Eloquent

- Database inspection spans all schemas by default; request schemas and qualification behavior explicitly when needed.
- PostgreSQL supports online indexes, virtual columns, `tsvector`, precomputed full-text vectors, transaction poolers, and conversion expressions for changed columns.
- MariaDB supports UUID fallback behavior and vector indexes; SQLite supports JSON, JSONB, transaction modes, pragmas, URI filenames, and polymorphic exclusions.
- MySQL schema operations support SSL credentials, DDL locks, and explicit SSL disabling for dump or restore workflows.
- Eloquent supports automatic relationship loading, one-of-many through relationships, nested `relationLoaded()`, and nested-array `loadMissing()`.
- Use the `Scope` attribute for local scopes; the earlier `NamedScope` name is obsolete.
- `withAttributes(..., asConditions: false)` supplies creation attributes without adding query predicates.
- `whereAttachedTo()`, `withoutGlobalScopesExcept()`, `whereValueBetween()`, and `inOrderOf()` cover common relationship and ordering cases.
- Creation helpers accept lazy closure values, and pivot mutation methods have transactional `*OrFail` variants.
- Value-object casts support mass assignment; first-party casts include binary, URI, fluent, HTML string, Unicode JSON, and mapped collections.
- `getPrevious()` exposes values from immediately before the last save.
- Stop using `orWhereKey()` and `orWhereKeyNot()` because current Laravel 13 patch releases removed them.

### HTTP and routing

- `Http::record()` records real outbound requests without faking responses.
- `preventStrayRequests()` can allow selected real URL patterns.
- HTTP batches support deferred execution, lifecycle hooks, request contexts, and bounded concurrency.
- Pending HTTP methods can return fluent promises; pools and batches can construct requests with `newRequest()`.
- HTTP connection and certificate failures surface through Laravel's HTTP exception abstraction.
- `Response::json()` accepts JSON decoding flags such as `JSON_BIGINT_AS_STRING`.
- `Request::get()` is deprecated; choose `input()`, `query()`, or another source-specific accessor.
- `eventStream()` supports custom event names and initial messages.
- Route metadata, parameter-name injection, closure source locations, and middleware-filtered listings improve routing tooling.
- Malformed encoded cursors return `null`; validate the result before use.
- The health route and maintenance mode can serve JSON-aware responses.

### Queues and scheduling

- `Queue::route()` centralizes job routing; a single string means the queue name.
- Queue jobs support class attributes for tries, backoff, timeout, failure-on-timeout, delay, and inherited debounce behavior.
- Runtime queue selection overrides class-level queue attributes.
- SQS supports fair queues, named credential providers, and disk-backed overflow payloads.
- Redis Cluster works with queues and concurrency limiting.
- Failover queues and caches emit failure events that identify the originating exception or underlying store.
- Workers expose startup, idle, pause, resume, interruption, stopping, and stop-reason telemetry.
- Queue inspection returns payload and queue details without backend-specific access.
- Queue fakes inspect delayed and reserved jobs and expose before/after push hooks.
- Scheduler pause, resume, reload interruption, group callbacks, and environment-filtered listings are available.
- `schedule:list --json`, `queue:failed` JSON, and `queue:monitor` oldest-pending data support automation.

### Cache, sessions, and filesystems

- `Cache::memo()` adds request-local memoization and supports `flexible()` stale-while-revalidate reads.
- `Cache::funnel()` provides driver-independent concurrency limiting.
- Cache locks can refresh expiration; database-lock pruning can be disabled.
- Redis tagged-cache flushes are atomic and can use custom connections.
- The cache session driver uses `SESSION_DRIVER=cache` with `SESSION_STORE` selecting the store.
- Scoped disks inherit the parent disk's `throw` behavior.
- Local disks support temporary upload URLs.
- Served disks must have unique URIs, and generated filesystem URL paths are encoded.

### Validation and authentication

- `Rule::anyOf()` validates when any complete alternative rule set passes.
- `Rule::contains()` and `in_array_keys` validate required array values or keys.
- Strict boolean, numeric, integer, and form-request modes reject loose or unknown input.
- The `image` rule excludes SVG unless explicitly allowed.
- Uploaded files can be validated for character encoding.
- Fluent password rules handle `required()` and `sometimes()` consistently and can stringify themselves.
- `Auth::login()` regenerates the session identifier.
- Bcrypt can enforce its 72-byte input limit.
- Remember cookies store a MAC of the password hash, not the raw hash.
- Decryption authenticates ciphertext against all configured rotated keys.

### Views, resources, mail, and frontend

- Models and collections can discover resources through convention or explicit resource attributes.
- `JsonApiResource` supports JSON:API serialization and circular-reference deduplication.
- Blade provides context blocks, isolated includes, stack detection, function or constant imports, and optimized fonts.
- Vite can limit preloads and customize asset paths.
- Resend supports raw and inline attachments.
- Notifications expose failure transport exceptions, post-send hooks, custom queued job classes, and missing-model deletion behavior.
- Mail supports Cloudflare Email Service and SES tenants.

## Working method

1. Read the installed framework constraint and lockfile version.
2. Start with the major-upgrade checks when changing framework versions.
3. Open only the topic references relevant to the code under review.
4. Preserve exact defaults and final option names; several entries document reverted or renamed APIs.
5. Add regression tests for changed routing, serialization, queue, session, schema, and validation behavior.
