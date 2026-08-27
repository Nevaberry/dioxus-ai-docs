# Modules, Lifecycle, and Configuration

Use this reference for module identity and exports, reflection, lifecycle order,
middleware precedence, cache integration, configuration, and Terminus health
indicators.

## Dynamic-Module Identity

Migration guidance (`11.0-migration`): dynamic-module equivalence is based on
object identity rather than a predictable hash of module metadata. Two separately
created dynamic-module objects are distinct even when their metadata is equal.

Construct once and reuse the same object when imports should deduplicate:

```typescript
const usersFeature = TypeOrmModule.forFeature([User]);

@Module({
  imports: [usersFeature],
})
export class AppModule {}
```

When a test intentionally needs the previous metadata-based behavior, opt into
deep hashing for the testing module:

```typescript
const usersFeature = TypeOrmModule.forFeature([User]);

await Test.createTestingModule(
  { imports: [usersFeature] },
  { moduleIdGeneratorAlgorithm: 'deep-hash' },
).compile();
```

Other test strategies are to select the correct parent context or retrieve all
instances and choose the intended one. Do not assume equal dynamic-module
metadata implies one instance.

## Module Exports

In `11.0.0`, promise values are no longer supported in a module's `exports`
array. Export the resolved provider or a module token, not a promise that will
eventually produce one.

Audit dynamic and asynchronous modules for values that are still pending when
the module metadata is constructed.

## Reflector Return Values and Types

For a single object-valued metadata entry, `Reflector.getAllAndMerge()` returns
the object itself instead of wrapping it in an array. Code that indexes `[0]` or
blindly iterates this result may now be wrong.

`Reflector.getAllAndOverride()` returns `T | undefined`; handle missing metadata
instead of assuming a value. When a `ReflectableDecorator` transforms its value,
the transformed type is inferred across Reflector methods, so keep annotations
aligned with the transformed result rather than the decorator's input shape.

## Shutdown-Hook Order

Termination hooks run in reverse initialization order. For a dependency chain
`A -> B -> C`:

- Initialization runs `C -> B -> A`.
- `OnModuleDestroy` runs `A -> B -> C`.
- `BeforeApplicationShutdown` runs `A -> B -> C`.
- `OnApplicationShutdown` runs `A -> B -> C`.

Global modules initialize first and are destroyed last. Review teardown code for
implicit assumptions that dependencies have already shut down; a dependent can
now begin termination while its dependency is still available.

## Global-Middleware Precedence

Middleware registered by global modules executes before middleware registered by
imported modules, regardless of where the global module appears in the dependency
graph.

Where middleware shares request-scoped state, authorization context, tracing
metadata, or response mutations, test the effective sequence rather than relying
on module graph position.

## Cache Stores and Raw Records

The updated `@nestjs/cache-manager` expects external backends as Keyv adapters in
a `stores` array. Replace the former singular `store` configuration:

```typescript
CacheModule.registerAsync({
  useFactory: async () => ({
    stores: [new KeyvRedis('redis://localhost:6379')],
  }),
});
```

Raw cached data has the shape `{ value, expires }`. This is observable to code
that reads the backend directly and matters when migrating records written with
the previous representation. Keep cache-manager consumers at the abstraction
boundary where possible; when direct access is required, update decoding and
migration logic for this wrapper.

## Configuration Source Precedence

In `@nestjs/config@4`, `ConfigService#get()` resolves values in this order:

1. Internal configuration.
2. Validated environment values.
3. `process.env`.

An internal configuration value can therefore override an environment variable.
Audit applications that previously treated `process.env` as the final override.

`ignoreEnvVars` is deprecated. Choose the replacement based on the behavior you
need:

- `validatePredefined: false` skips validation of variables already present
  before the configuration module is imported.
- `skipProcessEnv: true` prevents `ConfigService#get()` from consulting
  `process.env`.

```typescript
ConfigModule.forRoot({
  validatePredefined: false,
  skipProcessEnv: true,
});
```

These options are independent: disabling predefined-variable validation does not
by itself remove `process.env` from lookup.

## Terminus Custom Health Indicators

Custom Terminus checks can inject `HealthIndicatorService`, create an indicator
result with `check(key)`, and return `up()` or `down()` with optional details:

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
scheduled for removal in the next major release. New and migrated indicators
should return the result built by `HealthIndicatorService` rather than throw a
`HealthCheckError` to represent an unhealthy check.
