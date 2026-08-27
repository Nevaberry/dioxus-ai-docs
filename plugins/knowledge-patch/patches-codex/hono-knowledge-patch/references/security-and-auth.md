# Security and Authentication

## Pin the security patch floor

For the 4.11 line, use `4.11.10` or newer. `4.11.7` fixes an IP-restriction
bypass, prevents caching of `private` and `no-store` responses, blocks unintended
Cloudflare static-asset key access through user-controlled paths, and escapes
untrusted strings rendered by JSX `ErrorBoundary`. `4.11.10` strengthens a
timing-safe comparison.

For the 4.12 line, use `4.12.28` or newer and never remain below `4.12.27`.
Patches in this line harden Lambda header and client-IP handling, static-file and
SSG paths, IP restriction, cookies, SSE fields, body limits, credentialed CORS,
JWT/JWK validation, cache variation, and JSX/CSS SSR. They also ignore
`__proto__` segments in `parseBody({ dot: true })`.

At these floors, Hono rejects control characters in SSE and cookie attributes,
validates JSX tag and attribute names, isolates JSX context per request, requires
the Bearer scheme for JWT/JWK middleware, validates NumericDate claims, and
prevents authentication-varying responses from leaking through caches.

## Require explicit verification algorithms

Starting with `4.11.4`, JWT middleware requires one explicit `alg`, while
JWK/JWKS middleware requires an `alg` array containing asymmetric algorithms.
This prevents an untrusted token header from selecting verification behavior.
`AlgorithmTypes` is exported from `4.11.5` for typing algorithm choices.

```ts
app.use('/session/*', jwt({ secret, alg: 'HS256' }))
app.use('/admin/*', jwk({
  jwks_uri: 'https://example.com/.well-known/jwks.json',
  alg: ['RS256'],
}))
```

## Choose the token source deliberately

Since `4.8.0`, JWT middleware accepts `headerName` for a nonstandard header:

```ts
app.use('/api/*', jwt({
  secret,
  alg: 'HS256',
  headerName: 'X-Auth-Token',
}))
```

Since `4.9.0`, JWK middleware has the matching `headerName` option. JWT
middleware may instead read a token from a named cookie by setting `cookie`.

```ts
app.use('/auth/*', jwt({
  secret: 'it-is-very-secret',
  alg: 'HS256',
  cookie: 'session',
}))
```

Authorization-header tokens must use the Bearer scheme. Treat custom headers and
cookies as distinct trust boundaries, and keep cache variation aligned with the
chosen credential source.

## Configure JWK lookup and anonymous access

Since `4.8.0`, `jwk({ allow_anon: true, ... })` lets a request continue when no
valid token is available. In that case `jwtPayload` is not set. Both `keys` and
`jwks_uri` may be functions receiving the context, enabling per-request or
tenant-specific key resolution.

Since `4.9.0`, `verifyWithJwks()` is available in the JWT utilities for verifying
tokens against a JWKS outside JWK middleware. Apply the same explicit algorithm,
issuer, and claim policy as middleware-based verification.

## Validate issuer and temporal claims

JWT middleware supports `iss` validation from `4.9.0`. Configure accepted
issuers instead of duplicating issuer checks in handlers.

`verifyOptions.nbf`, `verifyOptions.iat`, and `verifyOptions.exp` control
validation of those claims when present. All three default to `true`.

```ts
app.use('/auth/*', jwt({
  secret: 'it-is-very-secret',
  alg: 'HS256',
  verifyOptions: { nbf: true, iat: true, exp: true },
}))
```

## Type authenticated context

Use `JwtVariables` as the application's `Variables` type so
`c.get('jwtPayload')` is inferred after JWT authentication.

```ts
import { Hono } from 'hono'
import type { JwtVariables } from 'hono/jwt'

const app = new Hono<{ Variables: JwtVariables }>()
app.get('/auth/page', (c) => c.json(c.get('jwtPayload')))
```

Since `4.12.0`, `bearerAuth` is generic over the application environment, so the
context passed to `verifyToken` retains typed variables and bindings.

## Run post-authentication work once

Since `4.12.0`, Basic Auth accepts an async-capable
`onAuthSuccess(c, username)` callback. It runs after either direct credential
authentication or `verifyUser` succeeds, so use it to attach identity or audit
state without parsing the header again.

```ts
app.use('/admin/*', basicAuth({
  username,
  password,
  onAuthSuccess: (c, name) => c.set('user', name),
}))
```

## Generate cookie values safely

Since `4.9.0`, `hono/cookie` exports `generateCookie()` and
`generateSignedCookie()` for serializing ordinary and signed cookie values.
Prefer these helpers to handwritten attribute strings, and keep the framework at
the security floor that rejects control characters in cookie attributes.

## Protect streamed JSX with CSP

Since `4.8.0`, place streamed `Suspense` or `ErrorBoundary` output inside a
`StreamingContext` whose value contains `scriptNonce`, and allow that exact nonce
in the response CSP. Generated inline scripts otherwise conflict with a
nonce-restricted policy.

Secure Headers supports the CSP `report-to` and `report-uri` directives from
`4.11.0`, allowing violation reports to be configured in middleware.

## Block unwanted user agents

Since `4.8.0`, `@hono/ua-blocker` provides `uaBlocker({ blocklist })`, the
`aiBots` blocklist, and a robots.txt helper. Blocking rejects selected user
agents; robots guidance only requests crawler cooperation, so select the
mechanism according to the enforcement requirement.

## Allow browser preflights through CSRF middleware

In `4.13.3`, CSRF middleware exempts `OPTIONS` requests from validation. Browser
preflights should therefore reach CORS handling without a CSRF failure; continue
validating the state-changing request itself.
