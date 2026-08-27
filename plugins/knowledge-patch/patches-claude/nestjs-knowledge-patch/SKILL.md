---
name: nestjs-knowledge-patch
description: NestJS
version: "11.1.x selected changes"
license: MIT
metadata:
  author: Nevaberry
---


# NestJS Compatibility Guide

Use this skill when migrating, reviewing, or debugging NestJS applications whose
behavior may depend on recent framework, platform-adapter, configuration, cache,
health-check, or microservice changes.

Inspect the application's manifest before applying version-sensitive advice.
Prefer the installed package versions, application code, and test results when
they disagree with this guide.

## Reference Index

| Reference | Topics |
| --- | --- |
| [Modules, Lifecycle, and Configuration](references/modules-lifecycle-and-configuration.md) | Dynamic modules, exports, reflection, shutdown hooks, middleware ordering, cache stores, configuration precedence, and health indicators |
| [Platform and Routing](references/platform-and-routing.md) | Runtime requirements, Express and Fastify migration, route matching, date parsing, WebDAV methods, and context selection |
| [Transports and Operations](references/transports-and-operations.md) | Microservice observability and configuration, logging, NATS, TCP, RabbitMQ, and WebSocket extension points |

## Breaking Changes and Deprecations

### Confirm the Runtime and HTTP Platform

- Require Node.js 20 or newer.
- Treat the default Express integration as Express 5 when auditing middleware,
  routing, error handling, and platform-specific dependencies.
- Read [Platform and Routing](references/platform-and-routing.md) before an HTTP
  platform upgrade.

### Configure Fastify CORS Methods Explicitly

With the Fastify adapter and Fastify 5, the default CORS method set contains only
safelisted methods. Explicitly include application methods such as `PUT`, `PATCH`,
and `DELETE`:

```typescript
app.enableCors({ methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'] });
```

Do not assume that a successful `GET` or `POST` preflight proves write methods
are enabled.

### Update Middleware Wildcards

Middleware matching uses the newer `path-to-regexp` syntax. Replace anonymous
`(.*)` patterns with named wildcards:

```typescript
consumer.apply(ApiMiddleware).forRoutes('*splat');
```

This migration applies to middleware matching. Do not mechanically rewrite
ordinary Fastify route wildcards.

### Reuse Dynamic-Module Objects When Deduplication Matters

Dynamic modules are compared by object identity. Construct the dynamic module
once and reuse that object when multiple imports should identify one module:

```typescript
const usersFeature = TypeOrmModule.forFeature([User]);

@Module({
  imports: [usersFeature],
})
export class AppModule {}
```

For tests that intentionally depend on metadata-based equivalence, use the
testing module's `moduleIdGeneratorAlgorithm: 'deep-hash'` option. The detailed
testing alternatives are in
[Modules, Lifecycle, and Configuration](references/modules-lifecycle-and-configuration.md).

### Export Resolved Nest Artifacts

Do not put promise values in a module's `exports` list. Export resolved providers
or module tokens instead.

### Recheck Reflector Consumers

- A single object-valued entry returned by `Reflector.getAllAndMerge()` is the
  object itself, not a one-element array.
- `getAllAndOverride()` returns `T | undefined`.
- Transformed `ReflectableDecorator` types flow through Reflector method
  inference.

Remove array-unwrapping workarounds and handle the possible `undefined` result.

### Recheck Lifecycle and Middleware Order

Shutdown hooks run in reverse initialization order. For dependencies
`A -> B -> C`, initialization is `C -> B -> A`, while `OnModuleDestroy`,
`BeforeApplicationShutdown`, and `OnApplicationShutdown` run `A -> B -> C`.
Global modules initialize first and are destroyed last.

Middleware from global modules runs before middleware from imported modules,
regardless of the global module's position in the dependency graph. Audit code
whose correctness depends on side effects from the older ordering.

### Migrate Cache Backends to Keyv Adapters

Configure external cache backends as Keyv adapters in `stores`, rather than with
the former `store` option:

```typescript
CacheModule.registerAsync({
  useFactory: async () => ({
    stores: [new KeyvRedis('redis://localhost:6379')],
  }),
});
```

Direct backend consumers must also account for raw cached records shaped as
`{ value, expires }`, including data written before a migration.

### Apply the New Configuration Precedence

`ConfigService#get()` checks sources in this order:

1. Internal configuration.
2. Validated environment values.
3. `process.env`.

Internal configuration can therefore override environment variables. Replace
deprecated `ignoreEnvVars` usage according to the intended behavior:

```typescript
ConfigModule.forRoot({
  validatePredefined: false,
  skipProcessEnv: true,
});
```

Use `validatePredefined: false` to skip validation of variables that existed
before module import. Use `skipProcessEnv: true` to prevent `get()` from
consulting `process.env`.

### Replace Deprecated Terminus Indicator APIs

Inject `HealthIndicatorService`, call `check(key)`, and return `up()` or `down()`.
The former `HealthIndicator` and `HealthCheckError` classes are deprecated and
scheduled for removal in the next major release. See the complete pattern in
[Modules, Lifecycle, and Configuration](references/modules-lifecycle-and-configuration.md).

## High-Value Features

### Emit Structured Console Logs

Use `ConsoleLogger` with JSON output when log consumers need structured events:

```typescript
const app = await NestFactory.create(AppModule, {
  logger: new ConsoleLogger({ json: true }),
});
```

### Parse Date Parameters with a Built-In Pipe

`ParseDatePipe` is exported from `@nestjs/common` and transforms an incoming
parameter into a `Date`:

```typescript
find(@Query('since', ParseDatePipe) since: Date) {}
```

### Observe and Extend Microservice Transports

- Use `status` to observe transport state.
- Use `on` to subscribe to native-driver events.
- Use `unwrap` when direct access to the underlying driver is necessary.
- Configure NATS queues per message handler and opt into graceful shutdown.
- Allow the operating system to select a TCP port and set a maximum packet-buffer
  size when those deployment controls are needed.
- Resolve microservice options through dependency injection when configuration
  depends on registered providers.
- Use RabbitMQ topic exchanges for topic-based RMQ routing.

Read [Transports and Operations](references/transports-and-operations.md) for the
transport-specific boundaries.

### Extend WebSocket Handling

WebSocket exceptions may retain a cause. The `ws` adapter also exposes a
message-parser extension point for custom wire formats.

### Route WebDAV Methods

WebDAV HTTP methods are recognized by the common, core, and Fastify packages and
can participate in Nest routing.

### Control Selected-Context Error Policy

Override `abortOnError` for a selected application context:

```typescript
const featureContext = app.select(FeatureModule, { abortOnError: false });
```

### Suppress Automatic Logging for Expected Exceptions

Use `IntrinsicException` for exceptions that Nest should not automatically log,
avoiding duplicate or unwanted framework-level log output for expected failures.

## Migration Review Order

1. Confirm the Node.js runtime and HTTP platform adapter.
2. Fix middleware patterns, CORS methods, and module exports.
3. Audit dynamic-module identity, reflection result shapes, and lifecycle order.
4. Migrate cache, configuration, and health-check integrations.
5. Verify transport observability, queueing, shutdown, and buffer controls.
6. Exercise routing, shutdown, and direct-backend data paths in tests.
