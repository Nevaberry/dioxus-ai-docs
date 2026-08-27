# Platform and Routing

Use this reference for runtime and HTTP-platform migration, middleware paths,
request parsing, WebDAV routing, and application-context selection.

## Runtime and Default HTTP Platform

As of `11.0.0`, NestJS requires Node.js 20 or newer; Node.js 16 and 18 are no
longer supported. Align local development, CI, container images, and deployment
runtimes before diagnosing framework behavior.

The default Express platform integration uses Express 5. Recheck code and
dependencies that depend on Express-specific middleware, routing, or error
handling behavior.

## Fastify Adapter Migration

With `@nestjs/platform-fastify` v11 and Fastify v5, CORS permits only safelisted
methods by default. Explicitly configure every non-safelisted method the
application accepts, including `PUT`, `PATCH`, and `DELETE` when applicable:

```typescript
app.enableCors({ methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'] });
```

Test browser preflights for each configured write method; successful routing on
the server does not establish that the browser's CORS check will allow it.

## Middleware Path Matching

Nest middleware matching uses the latest `path-to-regexp` behavior. Replace an
anonymous `(.*)` catch-all with a named wildcard:

```typescript
consumer.apply(ApiMiddleware).forRoutes('*splat');
```

This change applies to Nest middleware matching. Ordinary Fastify route
wildcards remain unchanged, so distinguish middleware declarations from native
Fastify route patterns during migration.

## Built-In Date Parsing

`ParseDatePipe` is exported by `@nestjs/common`. Apply it to transform an
incoming parameter into a `Date` before the handler runs:

```typescript
find(@Query('since', ParseDatePipe) since: Date) {}
```

Use the handler's `Date` type to reflect the transformed value rather than
leaving the parameter typed as its incoming string representation.

## WebDAV Method Recognition

WebDAV HTTP methods are recognized consistently by the common, core, and Fastify
packages. They can participate in Nest routing instead of being rejected as
unknown methods.

When exposing WebDAV endpoints, verify that any platform adapter, proxy, CORS
configuration, and middleware path also accepts the desired method; framework
recognition does not configure those external layers.

## Selecting an Application Context

`NestApplicationContext.select()` can override `abortOnError` for the selected
context:

```typescript
const featureContext = app.select(FeatureModule, { abortOnError: false });
```

Use the option when failure policy for the selected module context should differ
from the surrounding application context.
