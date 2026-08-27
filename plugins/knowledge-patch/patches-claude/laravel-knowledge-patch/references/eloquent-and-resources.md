# Eloquent Models, Relationships, Casts, and Resources

## Attribute-declared named scopes (2025-03)

Eloquent now supports an attribute-based declaration for named scopes, as an alternative to relying only on the conventional scope method name.

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

## Cast state after discarding changes (2025-06)

Discarding Eloquent model changes now clears cached cast values, so subsequent attribute access reflects the restored state rather than a stale cast object.

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

## Direct factory inserts (2025-11)

Model factories now provide `insert()` for persisting generated rows. Hidden attributes and array-cast attributes are handled by this insertion path.

```php
User::factory()->count(100)->insert();
```

## Disabling factory parent expansion globally (2025-07)

`Factory::dontExpandRelationshipsByDefault()` globally prevents model factories from automatically expanding parent relationship definitions.

```php
Factory::dontExpandRelationshipsByDefault();
```

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

## Explicit model resource attributes (2025-09)

Models may declare their API resource and resource collection with `#[UseResource(...)]` and `#[UseResourceCollection(...)]` instead of relying only on convention-based discovery.

```php
#[UseResource(UserResource::class)]
#[UseResourceCollection(UserCollection::class)]
class User extends Model {}
```

## Factory sequence context (2025-09)

Factory `Sequence` callbacks now receive the pending `$attributes` and `$parent` arguments, allowing each sequence value to depend on the model data and parent being created.

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

## JSON:API resources (2026-01)

Laravel now includes a `JsonApiResource` trait for JSON:API resource serialization. Resource handling deduplicates circular references, and `ModelInspector` results now include the model's `JsonResource`.

## Mapping collection casts (2025-04)

`AsCollection` casts can map each decoded item into an object or another value by declaring the item type with `of()`.

```php
'options' => AsCollection::of(Option::class),
```

## Mass-assigned value-object casts (2025-09)

Eloquent mass assignment now works with value-object casts, allowing cast-backed value objects to be populated through `fill()`, `create()`, and related mass-assignment paths.

## Model resource conversion (2025-04)

Models and Eloquent collections can convert themselves directly to their conventionally discovered API resources.

```php
return $user->toResource();
return User::all()->toResourceCollection();
```

## Morph-map-aware model serialization (2026-02)

Serialized model identifiers now use configured morph-map aliases instead of always using concrete model class names.

## Nested model construction during boot (13.0-upgrade)

Instantiating a model while the same model is still running its `boot` or trait `boot*` methods now throws `LogicException`; move such instantiation outside the boot cycle.

## Nested relationship-loaded checks (2025-04)

`relationLoaded()` accepts nested relationship paths, allowing checks such as `$model->relationLoaded('posts.comments')`.

## One-of-many through relationships (2025-03)

`HasOneThrough` relationships now support `CanBeOneOfMany`, including helpers such as `latestOfMany()`.

```php
return $this->hasOneThrough(Order::class, Customer::class)->latestOfMany();
```

## PHP virtual properties in model serialization (2025-05)

Eloquent model array and JSON serialization now includes virtual properties, including properties implemented through PHP property hooks rather than backing storage.

## Previous model state after saving (2025-05)

Eloquent preserves the values from immediately before the most recent save and exposes them through `getPrevious()`, complementing the new values returned by `getChanges()`.

## Restored relations in serialized collections (13.0-upgrade)

When an Eloquent model collection is serialized and restored, including through a queued job, the models' eager-loaded relations are now restored with it.

## Retaining selected global scopes (2025-09)

`withoutGlobalScopesExcept()` removes every global scope except those explicitly listed, which is useful when a query must retain tenancy or security scoping while disabling other defaults.

```php
Post::withoutGlobalScopesExcept([TenantScope::class])->get();
```

## Reverted Eloquent key-disjunction helpers (2026-08)

Laravel 13.26.1 removes the Eloquent builder's `orWhereKey()` and `orWhereKeyNot()` methods. Code using either helper must stop relying on it when updating to this patch release.

## Scoped context (2025-03)

`Context::scope()` bounds temporary context changes to a callback and restores the surrounding context afterward.

```php
Context::scope(function () {
    Context::add('tenant_id', 123);
});
```

## Singleton and scoped container attributes (2025-07)

The container's `Singleton` and `Scoped` attributes declare a class's lifetime without service-provider binding code.

```php
#[Singleton]
final class ExchangeRates {}

#[Scoped]
final class RequestState {}
```

## Suppressing factory callbacks (2026-02)

Factories provide `withoutAfterMaking()` and `withoutAfterCreating()` to bypass their respective lifecycle callbacks for a factory operation.

## Test-scoped string factories (13.0-upgrade)

Custom UUID, ULID, and random string factories registered through `Str` are reset during test teardown; configure them in each applicable test or setup hook.

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
