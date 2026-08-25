# Database, Query Builder, Schema, and Transactions

## Additional JSON Schema constraints (2026-02)

Numeric schema types support `multipleOf`, while array schema types support `uniqueItems`.

## Arbitrary SQLite pragmas (2025-09)

SQLite connection configuration can set arbitrary pragmas. A follow-up attempt to move existing options into the pragmas configuration was reverted, so this support is additive and existing option locations remain valid.

## Attributes without query conditions (2025-03)

Eloquent's `withAttributes()` can apply pending model attributes without also adding them as `where` clauses.

```php
Post::query()
    ->withAttributes(['tenant_id' => $tenantId], asConditions: false)
    ->create(['title' => 'Draft']);
```

## Caller-defined query ordering (2026-03-laravel-12)

Query builders provide `inOrderOf()` for ordering rows according to a supplied sequence of column values.

```php
$orders = Order::query()
    ->inOrderOf('status', ['pending', 'processing', 'complete'])
    ->get();
```

## Castable enums (2025-09)

Enum types may implement Laravel's `Castable` contract, enabling an enum to select its own custom Eloquent caster.

## Collision-free migration timestamps (2026-07)

`make:migration` generates collision-free, ordered timestamp prefixes when migrations are created close together.

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

## Enum database connections (2025-09)

Database manager methods and Eloquent model connection properties and methods accept enum connection selectors, avoiding manual conversion at each database call.

## Failing transactional pivot operations (2026-03-laravel-12)

`BelongsToMany` provides `*OrFail` transaction methods for pivot mutations that should fail atomically.

```php
$user->roles()->syncOrFail($roleIds);
```

## Filtering by attached models (2025-04)

`whereAttachedTo()` filters an Eloquent query to models attached to a given model through a many-to-many relationship.

```php
$users = User::whereAttachedTo($role)->get();
```

## Instant column additions (2025-11)

Schema operations now support instant column additions on compatible databases, avoiding the normal table-rebuild path where the database can apply the change instantly.

## Iterable database-empty assertions (2026-07)

`assertDatabaseEmpty()` accepts an iterable, allowing one assertion to verify multiple database targets.

## Joined MySQL delete clauses (13.0-upgrade)

MySQL joined deletes now include requested `ORDER BY` and `LIMIT` clauses instead of silently dropping them. Database variants that reject that syntax now raise `QueryException` rather than executing an unbounded delete.

## JSON schema contract (2025-11)

Laravel's JSON schema facilities now expose a contract alongside schema-generation improvements, allowing extensions to depend on an abstraction rather than a concrete implementation.

## JSON Schema dependencies (2025-12)

Laravel's JSON Schema facilities can now express dependencies between schema members instead of requiring dependent requirements to be modeled outside the schema.

## JSON Schema deserialization and composition (2026-06)

Illuminate JSON Schema can deserialize array schemas and multi-type unions, and schemas may use `anyOf` composition.

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

## MariaDB UUID fallback (2025-04)

Schema UUID columns use `char(36)` on MariaDB versions older than 10.7, where the native UUID type is unavailable.

## MariaDB vector indexes (2026-06)

Laravel's schema support now includes MariaDB vector indexes.

## Migration and locale event data (2025-12)

Laravel dispatches a `MigrationSkipped` event for skipped migrations, and `LocaleUpdated` now includes the previous locale for listeners that need both sides of the change.

## Migration names in lifecycle events (2026-05)

`MigrationStarted` and `MigrationEnded` now include the migration name, allowing listeners to identify the migration being run.

## Mode-less PostgreSQL full-text search (2025-11)

PostgreSQL full-text queries may now be issued without selecting a named search mode.

## More prohibitable commands (2026-06)

`cache:clear` and `queue:flush` now participate in Laravel's command-prohibition mechanism.

## Multi-schema database inspection (12.0-upgrade)

`Schema::getTables()`, `getViews()`, and `getTypes()` now inspect every schema by default and accept `schema:` as a string or array to narrow the query. `getTableListing()` returns schema-qualified names by default; pass `schemaQualified: false` to receive unqualified names.

```php
$tables = Schema::getTables(schema: ['main', 'blog']);
$names = Schema::getTableListing(schema: 'main', schemaQualified: false);
```

The `db:table` and `db:show` commands likewise include every schema on MySQL, MariaDB, and SQLite.

## MySQL query timeouts (2026-02)

MySQL query builders now provide `timeout()` for applying a timeout to an individual query.

## Native MariaDB CLI integration (12.0.0)

Database CLI operations for MariaDB now use native MariaDB commands, so environments invoking those operations must provide the corresponding binaries.

## Non-empty upsert keys (13.0-upgrade)

MySQL and MariaDB `upsert()` calls now require a non-empty `uniqueBy` value and throw `InvalidArgumentException` otherwise, even though those drivers use table primary and unique indexes for conflict detection.

## Online index creation (2025-08)

Schema index definitions can request online creation. Laravel emits concurrent index creation for PostgreSQL and online index creation for SQL Server.

```php
$table->index('email')->online();
```

## Parallel-test pre-migration setup (2025-12)

Parallel database testing has a pre-migration hook, allowing database preparation to run after a test database is selected but before its migrations execute.

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

## Prohibitable schema dumps (2025-11)

The database schema dump command can now be blocked by Laravel's destructive-command prohibition.

## Prohibiting database seeding (2025-04)

`db:seed` is now a prohibitable command, so `DB::prohibitDestructiveCommands()` can prevent seeding along with other destructive database operations.

## Query builder PDO fetch modes (12.0.0)

Query builder operations can now select PDO fetch modes when retrieving results.

## Query-builder sort directions (2026-05)

Query builder ordering APIs now accept the `SortDirection` enum, extending enum-based directions beyond collection and `Arr` sorting.

## Reporting non-unique `sole()` results (2026-06)

`MultipleRecordsFoundException` instances raised by `sole()` are now reported, affecting exception reporting when a query unexpectedly returns multiple records.

## Schema dumps without migration data (2026-06)

The schema dump command accepts `--without-migration-data` to omit migration data from the dump.

```shell
php artisan schema:dump --without-migration-data
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

## Unsetting JSON Schema flags (2026-05)

Fluent JSON Schema boolean flags can now be unset after being enabled, which helps when refining or reusing a schema definition.
