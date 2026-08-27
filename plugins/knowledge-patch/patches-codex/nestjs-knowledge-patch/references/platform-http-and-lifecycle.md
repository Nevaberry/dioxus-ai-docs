# Platform, HTTP, and Lifecycle

Use this reference when upgrading the Node.js runtime or HTTP adapter, changing
route and middleware matching, relying on lifecycle ordering, or working with
HTTP and WebSocket request handling.

## Runtime and default HTTP platform

NestJS 11 requires Node.js 20 or newer; Node.js 16 and 18 are no longer
supported. Its default Express platform integration uses Express 5
(`11.0.0`).

Treat the runtime and platform adapter as separate upgrade checks: confirm the
deployed Node.js version and identify code that depends on the underlying
Express integration.

## Fastify adapter migration

These adapter changes belong to the `11.0-migration` batch.

### CORS methods

With `@nestjs/platform-fastify` v11 and Fastify v5, CORS defaults to only
safelisted methods. Explicitly enable non-safelisted methods that the API uses,
including `PUT`, `PATCH`, and `DELETE`.

```typescript
app.enableCors({ methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'] });
```

### Middleware catch-all paths

Middleware matching uses the latest `path-to-regexp`. The former `(.*)`
catch-all must become a named wildcard.

```typescript
consumer.apply(ApiMiddleware).forRoutes('*splat');
```

This change is specific to middleware matching. Ordinary Fastify route
wildcards remain unchanged.

## Middleware ordering

Middleware registered by global modules executes before middleware registered
by imported modules (`11.0-migration`). Its order no longer depends on where
the global module appears in the dependency graph.

When behavior depends on sequencing, test the effective order of global and
imported middleware after the upgrade.

## Shutdown hook ordering

Termination hooks run in reverse initialization order (`11.0-migration`). For
dependencies `A -> B -> C`:

- Initialization runs `C -> B -> A`.
- `OnModuleDestroy` runs `A -> B -> C`.
- `BeforeApplicationShutdown` runs `A -> B -> C`.
- `OnApplicationShutdown` runs `A -> B -> C`.

Global modules initialize first and are destroyed last. Check resource
ownership and cleanup dependencies against this order.

## WebDAV method recognition

WebDAV HTTP methods are recognized consistently across the common, core, and
Fastify packages (`11.0.0`). They can participate in Nest routing rather than
being treated as unknown methods.

## WebSocket extension points

WebSocket errors can retain a cause (`11.0.0`). Preserve the cause when a
caller needs the underlying failure alongside the WebSocket error.

The `ws` adapter also exposes a message-parser extension point for custom wire
formats. Use that extension point when the adapter's message input requires
application-specific parsing.

## Built-in date parsing

`ParseDatePipe` is exported by `@nestjs/common` (`11.0.0`). It can transform an
incoming parameter into a `Date`.

```typescript
find(@Query('since', ParseDatePipe) since: Date) {}
```

