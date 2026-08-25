# Database, Eloquent, and Schema

Connections, queries, Eloquent models and relationships, casts, migrations, and schema operations.

## Arbitrary SQLite pragmas (2025-09)

SQLite connection configuration can set arbitrary pragmas. A follow-up attempt to move existing options into the pragmas configuration was reverted, so this support is additive and existing option locations remain valid.

## Associative eager-loading keys (2026-02)

Eager-loaded relationships now retain associative keys instead of reindexing their related results.

## Attribute-declared named scopes (2025-03)

Eloquent now supports an attribute-based declaration for named scopes, as an alternative to relying only on the conventional scope method name.

## Attributes without query conditions (2025-03)

Eloquent's `withAttributes()` can apply pending model attributes without also adding them as `where` clauses.

```php
Post::query()
    ->withAttributes(['tenant_id' => $tenantId], asConditions: false)
    ->create(['title' => 'Draft']);
```

## Automatic relationship loading (2025-04)

Eloquent can automatically load a relationship when it is first accessed and propagate that loading across related models, reducing accidental N+1 queries. Enable it globally with `Model::automaticallyEagerLoadRelationships()` or opt a model into it with `withRelationshipAutoloading()`.

## Binary model casts (2026-01)

The new `AsBinary` castable class provides a first-party Eloquent cast for binary attributes.

```php
use Illuminate\Database\Eloquent\Casts\AsBinary;

protected function casts(): array
{
    return ['payload' => AsBinary::class];
}
```

## Caller-defined query ordering (2026-03-laravel-12)

Query builders provide `inOrderOf()` for ordering rows according to a supplied sequence of column values.

```php
$orders = Order::query()
    ->inOrderOf('status', ['pending', 'processing', 'complete'])
    ->get();
```

## Cast state after discarding changes (2025-06)

Discarding Eloquent model changes now clears cached cast values, so subsequent attribute access reflects the restored state rather than a stale cast object.

## Castable enums (2025-09)

Enum types may implement Laravel's `Castable` contract, enabling an enum to select its own custom Eloquent caster.

## Clean deadlock retries (2026-02)

A lingering PDO transaction is rolled back before Laravel retries a commit deadlock, so the retry starts from a clean transaction state.

## Closure values for Eloquent creation (2026-04)

`firstOrNew()` and `updateOrCreate()` accept a closure for their values argument.

```php
$user = User::firstOrNew(
    ['email' => $email],
    fn () => ['name' => $name],
);
```

## Combined model pruning filters (2025-07)

The `model:prune` command allows `--model` and `--except` to be used together, so an explicit model set can also be narrowed by exclusions.

```shell
php artisan model:prune --model='App\Models\Post' --except='App\Models\PinnedPost'
```

## Conditional migrations (2025-03)

A migration may define `shouldRun()` to decide at runtime whether it should execute.

```php
public function shouldRun(): bool
{
    return config('features.audit_log');
}
```

## Configurable SQLite transaction modes (2025-08)

SQLite connections may specify a transaction mode such as `DEFERRED`, `IMMEDIATE`, or `EXCLUSIVE`, allowing applications to choose when a transaction acquires its database lock.

```php
'transaction_mode' => 'IMMEDIATE',
```

## Current defaults for date and year columns (2025-05)

Schema `date` and `year` columns now support `useCurrent()`, for example `$table->date('effective_on')->useCurrent()`.

## Database reconnection handling (2025-12)

Database reconnections now dispatch `ConnectionEstablished`, and an `SSL error: unexpected eof` is recognized as a lost connection.

## Disabling SSL for MySQL schema operations (2025-05)

MySQL migration squashing and restoration can explicitly disable SSL, which is needed when client defaults request TLS but the target server does not provide it.

## Eloquent partition result type (12.0.0)

`Eloquent\Collection::partition()` now returns a base `Illuminate\Support\Collection`; code depending on an Eloquent collection result must account for the type change.

## Eloquent scope attribute rename (2025-10)

The attribute for declaring Eloquent local scopes was renamed from `NamedScope` to `Scope`; code using the earlier attribute name must update its import and annotation.

```php
#[Scope]
protected function active(Builder $query): void
{
    $query->where('active', true);
}
```

## Eloquent subqueries in updates (2026-02)

Update statements accept Eloquent builders and relationship queries as subquery values, avoiding conversion to lower-level query builders.

## Enum database connections (2025-09)

Database manager methods and Eloquent model connection properties and methods accept enum connection selectors, avoiding manual conversion at each database call.

## Failing transactional pivot operations (2026-03-laravel-12)

`BelongsToMany` provides `*OrFail` transaction methods for pivot mutations that should fail atomically.

```php
$user->roles()->syncOrFail($roleIds);
```

## Filled bulk inserts (2025-04)

`Model::fillAndInsert()` merges model attributes before inserting multiple records, allowing bulk inserts to use filled model data.

```php
Flight::fillAndInsert([
    ['number' => 'AC100'],
    ['number' => 'AC200'],
]);
```

## Filtering by attached models (2025-04)

`whereAttachedTo()` filters an Eloquent query to models attached to a given model through a many-to-many relationship.

```php
$users = User::whereAttachedTo($role)->get();
```

## Fluent model casts (2025-06)

The `AsFluent` Eloquent cast exposes a structured model attribute as a `Fluent` value.

```php
protected function casts(): array
{
    return ['settings' => AsFluent::class];
}
```

## Force-creating related models in bulk (2025-04)

`HasOneOrMany` relationships now provide `forceCreateMany()` and `forceCreateManyQuietly()` variants, allowing bulk related-model creation without mass-assignment restrictions, with the quiet variant also suppressing events.

```php
$user->posts()->forceCreateMany($posts);
```

## HTML string casts (2025-03)

`AsHtmlString` casts model attributes to HTML string values.

```php
protected function casts(): array
{
    return ['body' => AsHtmlString::class];
}
```

## Instant column additions (2025-11)

Schema operations now support instant column additions on compatible databases, avoiding the normal table-rebuild path where the database can apply the change instantly.

## Joined MySQL delete clauses (13.0-upgrade)

MySQL joined deletes now include requested `ORDER BY` and `LIMIT` clauses instead of silently dropping them. Database variants that reject that syntax now raise `QueryException` rather than executing an unbounded delete.

## Lazy creation values (2026-02)

`firstOrCreate()` and `createOrFirst()` accept a closure for their values payload, allowing creation attributes to be computed only when an insert is needed.

## Literal values between columns (2025-07)

Query builders can test whether a literal value falls between the values of two columns with `whereValueBetween()`.

```php
$active = Reservation::query()
    ->whereValueBetween(now(), ['starts_at', 'ends_at'])
    ->get();
```

## Low-level database constructors (12.0-upgrade)

`Blueprint` and `Grammar` now require a `Connection` as their first constructor argument. `Grammar::setConnection()` and `Connection::withTablePrefix()` are removed; obtain prefixes with `$connection->getTablePrefix()` instead.

```php
$grammar = new MySqlGrammar($connection);
$prefix = $connection->getTablePrefix();
```

`Blueprint::getPrefix()` and `Grammar::getTablePrefix()` / `setTablePrefix()` are deprecated.

## Mapping collection casts (2025-04)

`AsCollection` casts can map each decoded item into an object or another value by declaring the item type with `of()`.

```php
'options' => AsCollection::of(Option::class),
```

## MariaDB UUID fallback (2025-04)

Schema UUID columns use `char(36)` on MariaDB versions older than 10.7, where the native UUID type is unavailable.

## MariaDB vector indexes (2026-06)

Laravel's schema support now includes MariaDB vector indexes.

## Mass-assigned value-object casts (2025-09)

Eloquent mass assignment now works with value-object casts, allowing cast-backed value objects to be populated through `fill()`, `create()`, and related mass-assignment paths.

## Mode-less PostgreSQL full-text search (2025-11)

PostgreSQL full-text queries may now be issued without selecting a named search mode.

## Morph-map-aware model serialization (2026-02)

Serialized model identifiers now use configured morph-map aliases instead of always using concrete model class names.

## Multi-schema database inspection (12.0-upgrade)

`Schema::getTables()`, `getViews()`, and `getTypes()` now inspect every schema by default and accept `schema:` as a string or array to narrow the query. `getTableListing()` returns schema-qualified names by default; pass `schemaQualified: false` to receive unqualified names.

```php
$tables = Schema::getTables(schema: ['main', 'blog']);
$names = Schema::getTableListing(schema: 'main', schemaQualified: false);
```

The `db:table` and `db:show` commands likewise include every schema on MySQL, MariaDB, and SQLite.

## MySQL DDL locking options (2026-01)

The MySQL schema grammar can express DDL locking options, allowing supported schema changes to select MySQL's lock behavior.

## MySQL query timeouts (2026-02)

MySQL query builders now provide `timeout()` for applying a timeout to an individual query.

## Nested array notation in `loadMissing` (2025-08)

`loadMissing()` accepts nested relationship arrays in addition to flattened relationship paths.

```php
$post->loadMissing([
    'comments' => ['author'],
]);
```

## Nested model construction during boot (13.0-upgrade)

Instantiating a model while the same model is still running its `boot` or trait `boot*` methods now throws `LogicException`; move such instantiation outside the boot cycle.

## Nested relationship-loaded checks (2025-04)

`relationLoaded()` accepts nested relationship paths, allowing checks such as `$model->relationLoaded('posts.comments')`.

## Non-empty upsert keys (13.0-upgrade)

MySQL and MariaDB `upsert()` calls now require a non-empty `uniqueBy` value and throw `InvalidArgumentException` otherwise, even though those drivers use table primary and unique indexes for conflict detection.

## One-of-many through relationships (2025-03)

`HasOneThrough` relationships now support `CanBeOneOfMany`, including helpers such as `latestOfMany()`.

```php
return $this->hasOneThrough(Order::class, Customer::class)->latestOfMany();
```

## Online index creation (2025-08)

Schema index definitions can request online creation. Laravel emits concurrent index creation for PostgreSQL and online index creation for SQL Server.

```php
$table->index('email')->online();
```

## PHP virtual properties in model serialization (2025-05)

Eloquent model array and JSON serialization now includes virtual properties, including properties implemented through PHP property hooks rather than backing storage.

## Polymorphic pivot table inference (13.0-upgrade)

Inferred table names for polymorphic pivot models using custom pivot classes are now pluralized. Set the pivot model's table explicitly when retaining a previously inferred singular name.

## Positioning polymorphic columns (2025-08)

Schema blueprint `morphs()` and `nullableMorphs()` definitions accept an `after` argument, allowing both generated polymorphic columns to be positioned after an existing column.

```php
$table->morphs('commentable', after: 'body');
```

## PostgreSQL `tsvector` columns (2026-03-laravel-12)

The schema builder supports PostgreSQL `tsvector` columns directly.

```php
$table->tsvector('search_document');
```

## PostgreSQL conversion expressions (2026-07)

PostgreSQL migrations can use `->using(...)->change()` to supply a conversion expression when changing a column.

## PostgreSQL precomputed full-text vectors (2026-02)

`whereFullText()` accepts a vector option for querying precomputed `tsvector` columns instead of rebuilding the vector from source text.

## PostgreSQL transaction poolers (2026-06)

PostgreSQL connections now support transaction poolers.

## PostgreSQL unique nulls-not-distinct indexes (2025-03)

PostgreSQL unique indexes can treat null values as equal by using `nullsNotDistinct()`.

```php
$table->unique('external_id')->nullsNotDistinct();
```

## PostgreSQL virtual columns (2025-10)

The PostgreSQL schema grammar now supports virtual columns, so schema definitions using them no longer require a PostgreSQL-specific workaround.

## Previous model state after saving (2025-05)

Eloquent preserves the values from immediately before the most recent save and exposes them through `getPrevious()`, complementing the new values returned by `getChanges()`.

## Prohibiting database seeding (2025-04)

`db:seed` is now a prohibitable command, so `DB::prohibitDestructiveCommands()` can prevent seeding along with other destructive database operations.

## Query builder PDO fetch modes (12.0.0)

Query builder operations can now select PDO fetch modes when retrieving results.

## Query-builder sort directions (2026-05)

Query builder ordering APIs now accept the `SortDirection` enum, extending enum-based directions beyond collection and `Arr` sorting.

## Reporting non-unique `sole()` results (2026-06)

`MultipleRecordsFoundException` instances raised by `sole()` are now reported, affecting exception reporting when a query unexpectedly returns multiple records.

## Restored relations in serialized collections (13.0-upgrade)

When an Eloquent model collection is serialized and restored, including through a queued job, the models' eager-loaded relations are now restored with it.

## Retaining selected global scopes (2025-09)

`withoutGlobalScopesExcept()` removes every global scope except those explicitly listed, which is useful when a query must retain tenancy or security scoping while disabling other defaults.

```php
Post::withoutGlobalScopesExcept([TenantScope::class])->get();
```

## Reverted Eloquent key-disjunction helpers (2026-08)

Laravel 13.26.1 removes the Eloquent builder's `orWhereKey()` and `orWhereKeyNot()` methods. Code using either helper must stop relying on it when updating to this patch release.

## Semantic vector queries (13.0.0)

The query builder supports semantic similarity searches backed by PostgreSQL and `pgvector`, including embedding plain-language query strings through `whereVectorSimilarTo()`.

```php
$documents = DB::table('documents')
    ->whereVectorSimilarTo('embedding', 'Best wineries in Napa Valley')
    ->limit(10)
    ->get();
```

## SQLite JSON and JSONB columns (2025-03)

The SQLite schema builder now supports native JSON and JSONB column types through its existing column helpers.

```php
$table->json('payload');
$table->jsonb('snapshot');
```

## SQLite polymorphic exclusions (2025-11)

SQLite connections now support Eloquent's `whereNotMorphedTo()` relationship query, bringing that polymorphic exclusion operation in line with other database drivers.

## SQLite URI connections (2026-05)

SQLite connections now accept URI-style database names using the `file:` prefix, allowing URI connection options to be supplied in the database value.

## Subqueries as range bounds (2026-01)

Query-builder `between` conditions now accept subqueries in their boundary values and in the column-bound variant, allowing ranges whose limits are computed by another query.

## TLS credentials for MySQL schema operations (2026-02)

MySQL schema dump and load commands can use configured SSL certificate and key values.

## Touching multiple columns (2026-03-laravel-12)

`touch()` accepts multiple columns, allowing one operation to update more than one timestamp column.

```php
$query->touch(['updated_at', 'indexed_at']);
```

## Transaction rollback callbacks (2025-09)

Database connections support `afterRollback` callbacks for work that should run only after a transaction has rolled back.

```php
DB::afterRollback(fn () => releaseReservedResource());
```

## Unicode-preserving JSON casts (2025-03)

The `json:unicode` cast encodes values with `JSON_UNESCAPED_UNICODE`.

```php
protected function casts(): array
{
    return ['payload' => 'json:unicode'];
}
```

## URI model casts (2025-06)

The `AsUri` Eloquent cast converts URI-valued attributes to Laravel URI objects.

```php
protected function casts(): array
{
    return ['homepage' => AsUri::class];
}
```

## UUIDv7 model IDs (12.0-upgrade)

`HasUuids` now generates UUIDv7-compatible ordered IDs. Use `HasVersion4Uuids` to retain ordered UUIDv4 strings; the removed `HasVersion7Uuids` trait should be replaced with `HasUuids`.

## Void-returning local scopes (2025-04)

Local scope methods no longer have to return an Eloquent builder; they may mutate the supplied builder and return `void`.

```php
public function scopeActive(Builder $query): void
{
    $query->where('active', true);
}
```
