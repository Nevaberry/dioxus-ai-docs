---
name: nestjs-knowledge-patch
description: NestJS
version: 11.1.x selected changes
license: MIT
metadata:
  author: Nevaberry
---


# NestJS Knowledge Patch

Load this skill when upgrading, reviewing, debugging, or writing a NestJS
application that may depend on current framework, platform-adapter,
microservice, configuration, caching, health-check, or logging behavior.

Start by inspecting the application's `package.json` and platform adapter.
Use the installed package versions and the application's tests as the final
authority, then apply the relevant guidance below and in the topic references.

## Reference index

| Reference | Topics |
| --- | --- |
| [Platform, HTTP, and lifecycle](references/platform-http-and-lifecycle.md) | Runtime and Express requirements, Fastify migration, middleware, lifecycle hooks, WebDAV, WebSockets, and date parsing |
| [Modules, configuration, and services](references/modules-configuration-and-services.md) | Dynamic modules, Reflector typing, cache stores, configuration precedence, application contexts, exports, and Terminus |
| [Microservices and observability](references/microservices-and-observability.md) | Transport status and native access, dependency-injected options, NATS, TCP, RabbitMQ, JSON logging, and intrinsic exceptions |

## Breaking changes and migration hazards

### Confirm the runtime and HTTP platform

NestJS 11 requires Node.js 20 or newer. The default Express integration uses
Express 5. Check both the runtime deployed in every environment and any code
whose behavior depends on the underlying Express version.

### Expand Fastify CORS methods explicitly

With `@nestjs/platform-fastify` v11 and Fastify v5, the default CORS methods
are only the safelisted methods. Include methods such as `PUT`, `PATCH`, and
`DELETE` when the application exposes them.

```typescript
app.enableCors({ methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'] });
```

### Replace legacy middleware catch-all syntax

Middleware route matching uses the latest `path-to-regexp`. Replace `(.*)`
with a named wildcard. This migration applies to middleware matching; ordinary
Fastify route wildcards do not change.

```typescript
consumer.apply(ApiMiddleware).forRoutes('*splat');
```

### Reuse dynamic-module objects when deduplicating

Dynamic-module equivalence uses object identity instead of a predictable hash
of module metadata. Create the dynamic module once and reuse that same object
when imports are intended to resolve to one module instance.

```typescript
const usersFeature = TypeOrmModule.forFeature([User]);

await Test.createTestingModule(
  { imports: [usersFeature] },
  { moduleIdGeneratorAlgorithm: 'deep-hash' },
).compile();
```

Use `moduleIdGeneratorAlgorithm: 'deep-hash'` only when a test intentionally
needs the earlier deep-hashing behavior. Tests can instead select the correct
parent or retrieve every instance when multiple instances are intentional.

### Update Reflector result assumptions

For one object-valued metadata entry, `Reflector.getAllAndMerge()` returns the
object itself, not a one-element array. `getAllAndOverride()` returns
`T | undefined`. Transformed `ReflectableDecorator` types are inferred across
the Reflector methods, so update annotations and callers rather than retaining
the old result shapes.

### Export resolved tokens, not promises

A module's `exports` list no longer supports promise values. Export resolved
providers or module tokens.

### Account for reverse shutdown order

Termination hooks execute in reverse initialization order. Given dependencies
`A -> B -> C`, initialization runs `C -> B -> A`, while
`OnModuleDestroy`, `BeforeApplicationShutdown`, and
`OnApplicationShutdown` run `A -> B -> C`. Global modules initialize first and
are destroyed last.

### Expect global middleware first

Middleware registered by global modules runs before middleware from imported
modules, regardless of where the global module sits in the dependency graph.
Audit ordering-sensitive authentication, tracing, and request mutation.

### Migrate cache backends to Keyv adapters

`@nestjs/cache-manager` accepts external backends as Keyv adapters in a
`stores` array rather than through the former `store` configuration.

```typescript
CacheModule.registerAsync({
  useFactory: async () => ({
    stores: [new KeyvRedis('redis://localhost:6379')],
  }),
});
```

Direct backend consumers must also handle raw cached data shaped as
`{ value, expires }`. Include that shape in migrations of existing cached
data.

### Re-evaluate configuration precedence

In `@nestjs/config@4`, `ConfigService#get()` checks internal configuration,
then validated environment values, then `process.env`. Internal configuration
can therefore override an environment variable.

`ignoreEnvVars` is deprecated. Use the settings according to the behavior
needed:

- `validatePredefined: false` skips validation of variables that existed
  before module import.
- `skipProcessEnv: true` prevents `get()` from consulting `process.env`.

```typescript
ConfigModule.forRoot({
  validatePredefined: false,
  skipProcessEnv: true,
});
```

### Replace deprecated Terminus indicator classes

Custom health indicators can inject `HealthIndicatorService`, call
`check(key)`, and return `up()` or `down()` with optional details. The former
`HealthIndicator` and `HealthCheckError` classes are deprecated and scheduled
for removal in the next major release.

```typescript
const indicator = this.healthIndicatorService.check(key);

try {
  const healthy = await this.probe();
  return healthy ? indicator.up() : indicator.down({ reason: 'probe failed' });
} catch {
  return indicator.down('Unable to run probe');
}
```

## High-value current APIs

### Observe and access microservice transports

Microservice client and server abstractions expose `status`, `on`, and
`unwrap`. Use them to observe transport state, subscribe to native-driver
events, and access the underlying driver while retaining the Nest abstraction.

### Resolve transport options through dependency injection

Microservice configuration can be obtained through the dependency-injection
container. Prefer this when transport options depend on registered providers
instead of constructing all options outside Nest.

### Emit structured console logs

Construct `ConsoleLogger` with `json: true` and pass it to the application.

```typescript
const app = await NestFactory.create(AppModule, {
  logger: new ConsoleLogger({ json: true }),
});
```

### Parse dates with the built-in pipe

`ParseDatePipe` is exported by `@nestjs/common` and transforms an incoming
parameter to a `Date`.

```typescript
find(@Query('since', ParseDatePipe) since: Date) {}
```

### Use transport-specific additions deliberately

- NATS handlers can select queues individually, and the transporter supports
  an optional graceful-shutdown path.
- TCP supports an operating-system-selected port and a configurable maximum
  packet-buffer size.
- RabbitMQ supports topic exchanges for topic-based routing.
- WebSocket errors can retain a cause, and the `ws` adapter provides a
  message-parser extension point for custom wire formats.

## Upgrade review workflow

1. Read the installed `@nestjs/*` package versions and identify the HTTP,
   cache, health-check, WebSocket, and microservice adapters in use.
2. Check the breaking-change sections first: runtime, routing syntax, module
   identity, reflection results, exports, lifecycle order, cache storage, and
   configuration precedence.
3. Open the relevant topic reference and trace each affected call site or
   configuration object.
4. Exercise ordering-sensitive middleware and shutdown hooks in tests.
5. Test direct cache-backend consumers and previously persisted cache data.
6. Test transport startup, state transitions, native event subscriptions, and
   shutdown behavior for each configured microservice transporter.
7. Keep platform-specific behavior explicit in configuration so adapter
   changes are visible during later upgrades.

