---
name: laravel-knowledge-patch
description: Laravel
version: 13.23.0
license: MIT
metadata:
  author: Nevaberry
---


# Laravel Knowledge Patch

Use this patch when implementing, reviewing, testing, or upgrading Laravel applications and framework extensions. Check the upgrade-sensitive notes first, then open only the topic references relevant to the work.

## Reference index

| Reference | Topics |
| --- | --- |
| [Upgrades and core](references/upgrades-and-core.md) | Runtime and dependency requirements, framework contracts, lifecycle, configuration, encryption, maintenance behavior |
| [Container, auth, and routing](references/container-auth-routing.md) | Resolution, contextual attributes, authentication, authorization, request handling, routing, middleware, context |
| [Database and schema](references/database-and-schema.md) | Connections, query builder, schema grammars, migrations, indexes, transactions, database-specific behavior |
| [Eloquent and resources](references/eloquent-and-resources.md) | Models, relationships, casts, scopes, factories, serialization, pruning, API resources |
| [Queues, concurrency, and scheduling](references/queues-concurrency-scheduling.md) | Jobs, batches, workers, queue backends, scheduling, processes, concurrency, lifecycle events |
| [Cache, filesystem, and Redis](references/cache-filesystem-redis.md) | Cache stores, locks, sessions, disks, URLs, Redis clients, failover, scoped storage |
| [HTTP, mail, and notifications](references/http-mail-notifications.md) | HTTP requests, pools and batches, mail transports, notifications, broadcasting, response hooks |
| [Validation and testing](references/validation-and-testing.md) | Validation rules, form requests, fakes, assertions, parallel tests, dependency compatibility |
| [Collections, strings, and support](references/collections-strings-support.md) | Collections, arrays, strings, numbers, URIs, JSON Schema, translations, general helpers |
| [Blade, frontend, console, and observability](references/blade-frontend-console-observability.md) | Blade, Vite, Artisan, maintenance commands, logging, health output, development tooling |

## Upgrade-critical checks

### Update the Laravel 13 platform and toolchain together

Laravel 13 requires PHP 8.3 and `laravel/framework:^13.0`. Align Tinker 3 and, where used, Boost 2, PHPUnit 12, or Pest 4. Remove legacy global helpers that collide with PHP 8.5 polyfills, such as `array_first()` and `array_last()`.

### Preserve cache and session identifiers explicitly

Laravel 13 fallback cache prefixes, Redis prefixes, and session cookie names use hyphenated slugs with new suffixes. Set `CACHE_PREFIX`, `REDIS_PREFIX`, and `SESSION_COOKIE` when an upgrade must retain existing identifiers.

### Audit custom cache stores and cached objects

Custom implementations of the cache `Store` and `Repository` contracts must implement `touch($key, $seconds)`. Object deserialization is denied by default; allow-list required classes under `cache.serializable_classes` or store non-object payloads.

### Rename direct CSRF middleware references

Use `PreventRequestForgery` and the `preventRequestForgery(...)` configuration API. The middleware also checks `Sec-Fetch-Site`; `VerifyCsrfToken` and `ValidateCsrfToken` remain deprecated aliases.

### Update custom framework contracts

Review every custom contract implementation. Notable additions include dispatch-after-response support, event-stream response creation, email-unverification, queue size metrics, paginator methods, session flashing, and streaming JSON.

### Review query behavior before deploying an upgrade

MySQL and MariaDB `upsert()` require a non-empty `uniqueBy`. Joined MySQL deletes now retain requested ordering and limits and may fail on database variants that reject that syntax. Multi-schema inspection and schema-qualified table listings may also change discovery results.

### Update low-level database extensions

Construct `Blueprint` and `Grammar` with a `Connection`. Do not call removed connection/table-prefix mutators; read the prefix from `$connection->getTablePrefix()`.

### Avoid model construction during model boot

Constructing a model of the same type while its `boot` or trait boot method is executing throws `LogicException`. Move the nested construction outside the boot cycle.

### Pin polymorphic pivot tables when names matter

Inferred tables for polymorphic custom pivot models are pluralized. Set the custom pivot model's `$table` when preserving a previously inferred singular table.

### Adapt queue integrations and listeners

Custom queue drivers must implement pending, delayed, reserved, and oldest-job metrics. Replace `QueueBusy::$connection` with `$connectionName`, and read the exception or `null` from `JobAttempted::$exception` instead of using `$exceptionOccurred`.

### Recheck routing precedence

Named-route duplicates consistently keep the first registration. Domain routes take precedence over non-domain routes regardless of registration order. Review overlaps and do not use duplicate names as an override mechanism.

### Expect authentication session rotation

`Auth::login()` regenerates the session identifier. Update manual-login flows and tests that assume the old identifier remains stable.

### Convert password-reset expiry values

`DatabaseTokenRepository` accepts its expiry constructor argument in seconds. Convert custom values that were previously supplied in minutes.

### Make filesystem and image-validation intent explicit

An implicit local disk uses `storage/app/private`; configure an explicit root to retain another location. The `image` validation rule rejects SVG by default, so opt in only with `image:allow_svg` or `File::image(allowSvg: true)` after assessing SVG safety.

### Choose UUID behavior deliberately

`HasUuids` produces ordered UUIDv7-compatible identifiers. Use `HasVersion4Uuids` to retain ordered UUIDv4 strings, and replace the removed `HasVersion7Uuids` trait with `HasUuids`.

## High-value implementation patterns

### Use first-party AI and vector APIs

Laravel's AI SDK supports agents, tools, embeddings, media generation, and vector stores. Query-builder semantic search can embed a plain-language query and search PostgreSQL `pgvector` data with `whereVectorSimilarTo()`.

### Centralize queue routing

Use `Queue::route()` to choose a job class's default connection and queue. A single string is interpreted as the queue name; use named arguments when selecting both connection and queue.

### Bound concurrent and remote work

Set runtime timeouts on `Concurrency::run()`, explicit concurrency on HTTP pools and batches, and process timeouts with `CarbonInterval`. Pending-request pools default to two concurrent requests.

### Prefer the HTTP coordinator APIs

Use `Http::batch()` for managed groups, `defer()` for deferred batch execution, and the fluent promise APIs for asynchronous requests. The Laravel 13 HTTP client can also satisfy PSR client integrations directly.

### Combine cache resilience features

`Cache::memo()` avoids repeated backend reads within one execution. Failover stores provide backend fallback, `Cache::funnel()` supplies driver-independent concurrency limiting, and refreshable locks support long-running ownership.

### Use model resource discovery or explicit attributes

Models and Eloquent collections can call `toResource()` and `toResourceCollection()`. Use `#[UseResource]` and `#[UseResourceCollection]` when convention-based discovery is not appropriate.

### Opt into relationship autoloading carefully

Enable automatic relationship loading globally with `Model::automaticallyEagerLoadRelationships()` or on a model with `withRelationshipAutoloading()`. Treat it as an N+1 mitigation, not a substitute for reviewing query volume.

### Use lazy creation values

Creation helpers accept closures for values that should be computed only when insertion is required. This includes `firstOrCreate()`, `createOrFirst()`, `firstOrNew()`, and `updateOrCreate()` at their applicable framework points.

### Prefer the final scope attribute name

Declare attribute-based local scopes with `#[Scope]`; the earlier `NamedScope` name was replaced. Scope methods may mutate the supplied builder and return `void`.

### Use modern schema capabilities directly

Available schema operations include PostgreSQL `tsvector` and virtual columns, MariaDB vector indexes, online index creation, instant column additions, SQLite JSON/JSONB and URI connections, and MySQL DDL locking options.

### Make validation semantics explicit

Use `boolean:strict` and `numeric:strict` when strings must not pass as booleans or numbers. `Rule::anyOf()` validates complete alternative rule sets; `Rule::contains()` and `in_array_keys` express array content requirements.

### Scope request and application context

`Context::scope()` restores surrounding context after its callback. `Context::remember()` and `rememberHidden()` lazily initialize values. The contextual `#[Context]` attribute can inject visible or hidden context values.

### Use enum selectors without manual scalar conversion

Enum selectors are accepted across manager drivers, database connections, cache and session keys, storage fakes, scheduler stores, container attributes, and several queue APIs. Prefer the typed selector where the receiving API supports it.

### Inspect queues through framework APIs

Use queue job inspection methods and the richer `InspectedJob` payload/queue data instead of reaching directly into a backend. Queue fakes can inspect delayed and reserved jobs and expose push hooks.

### Use machine-readable operational output

Automation can consume JSON from event, schedule, and failed-job listings. Queue monitoring exposes the oldest pending job, and worker stopping telemetry includes processed-job count, last-job time, and memory usage.

## Working method

1. Identify the application's pinned Laravel and PHP versions from `composer.json` and its lockfile.
2. Read the upgrade and core reference before changing major versions or custom framework contracts.
3. Open the subsystem reference for every framework API touched by the change.
4. Prefer application code, dependency constraints, tests, and observed behavior when they are more specific than general guidance.
5. Add focused regression tests for changed defaults, serialization, queue events, routing precedence, and database-specific SQL.
6. Recheck deployment binaries and services when adopting native MariaDB CLI operations, queue backends, mail transports, or database extensions.
