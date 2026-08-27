# Modules, Configuration, and Services

Use this reference when module identity, reflection metadata, configuration,
caching, application contexts, exports, or health indicators are involved.

## Dynamic-module identity

Dynamic-module equivalence is based on object identity rather than a
predictable hash of module metadata (`11.0-migration`). Reuse the same
dynamic-module object to deduplicate repeated imports.

```typescript
const usersFeature = TypeOrmModule.forFeature([User]);
```

Tests that deliberately need the old equivalence behavior can opt into deep
hashing:

```typescript
await Test.createTestingModule(
  { imports: [usersFeature] },
  { moduleIdGeneratorAlgorithm: 'deep-hash' },
).compile();
```

When multiple instances are intentional, tests can instead select the correct
parent or retrieve every instance.

## Reflector results and inferred types

Reflector behavior and types changed in `11.0-migration`:

- With one object-valued metadata entry, `Reflector.getAllAndMerge()` returns
  the object, not an array containing that object.
- `getAllAndOverride()` returns `T | undefined`.
- Transformed `ReflectableDecorator` types are inferred across the Reflector
  methods.

Adjust callers and their annotations to the returned shape and possible
`undefined` result.

## Keyv cache stores and raw data

The updated `@nestjs/cache-manager` expects external backends in a `stores`
array as Keyv adapters (`11.0-migration`). Do not retain the former `store`
configuration.

```typescript
CacheModule.registerAsync({
  useFactory: async () => ({
    stores: [new KeyvRedis('redis://localhost:6379')],
  }),
});
```

Raw cached data now has the shape `{ value, expires }`. This affects code that
reads the backend directly and migrations of previously written data.

## Configuration lookup and environment controls

In `@nestjs/config@4`, `ConfigService#get()` resolves values in this order
(`11.0-migration`):

1. Internal configuration.
2. Validated environment values.
3. `process.env`.

Internal configuration can therefore override environment variables.

`ignoreEnvVars` is deprecated. Its replacements have distinct meanings:

- `validatePredefined: false` skips validation for variables present before
  the module is imported.
- `skipProcessEnv: true` prevents `ConfigService#get()` from consulting
  `process.env`.

```typescript
ConfigModule.forRoot({
  validatePredefined: false,
  skipProcessEnv: true,
});
```

Select only the setting or settings that implement the desired behavior.

## Application-context error policy

`NestApplicationContext.select()` accepts an `abortOnError` override for the
selected context (`11.0.0`).

```typescript
const featureContext = app.select(FeatureModule, { abortOnError: false });
```

Use the override when the selected context needs an error policy different
from the surrounding application context.

## Module exports

Promise values are no longer supported in a module's `exports` list
(`11.0.0`). Export resolved providers or module tokens rather than promises.

## Terminus custom health indicators

Custom Terminus checks can inject `HealthIndicatorService` and begin a result
with `check(key)` (`11.0-migration`). Return `up()` or `down()`; both forms can
carry optional details.

```typescript
const indicator = this.healthIndicatorService.check(key);

try {
  const healthy = await this.probe();
  return healthy ? indicator.up() : indicator.down({ reason: 'probe failed' });
} catch {
  return indicator.down('Unable to run probe');
}
```

The former `HealthIndicator` and `HealthCheckError` classes are deprecated and
scheduled for removal in the next major release. Move custom indicators to
`HealthIndicatorService` before that removal.

