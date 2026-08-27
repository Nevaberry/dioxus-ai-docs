# Security and Authentication

## Configure JWT middleware

### Select and type the token source

Since 4.8.0, `jwt` accepts `headerName` for reading a token from a nonstandard
header.

```ts
app.use('/api/*', jwt({
  secret,
  alg: 'HS256',
  headerName: 'X-Auth-Token',
}))
```

Set `cookie` to a cookie name when the token should come from that cookie
instead of the authorization header.

```ts
app.use('/auth/*', jwt({
  secret: 'it-is-very-secret',
  alg: 'HS256',
  cookie: 'session',
}))
```

Use `JwtVariables` as the application's `Variables` type so
`c.get('jwtPayload')` is inferred after authentication.

```ts
import { Hono } from 'hono'
import type { JwtVariables } from 'hono/jwt'

const app = new Hono<{ Variables: JwtVariables }>()
app.get('/auth/page', (c) => c.json(c.get('jwtPayload')))
```

### Verify claims in middleware

JWT middleware supports issuer (`iss`) validation from 4.9.0. The
`verifyOptions.nbf`, `verifyOptions.iat`, and `verifyOptions.exp` switches
control validation of those claims when present; all three default to `true`.

```ts
app.use('/auth/*', jwt({
  secret: 'it-is-very-secret',
  alg: 'HS256',
  verifyOptions: { nbf: true, iat: true, exp: true },
}))
```

Current patched behavior validates NumericDate claims and accepts only the
`Bearer` authorization scheme for JWT and JWK middleware.

## Configure JWK and standalone JWKS verification

`jwk` supports `allow_anon: true` for requests that should continue without a
valid token. Its `keys` and `jwks_uri` options may be context-taking functions,
which allows per-request key selection. Since 4.9.0, `headerName` can read the
token from a nonstandard header just as JWT middleware can.

Use `verifyWithJwks()` from the JWT utilities when a token must be verified
against a JWKS outside middleware.

## Pin verification algorithms

From v4.11.4, `jwt` requires a single explicit `alg`, and JWK/JWKS middleware
requires an `alg` array of asymmetric algorithms. Never derive the accepted
algorithm from an untrusted token header. Version 4.11.5 also exports
`AlgorithmTypes` for typing configured choices.

```ts
app.use('/session/*', jwt({ secret, alg: 'HS256' }))
app.use('/admin/*', jwk({
  jwks_uri: 'https://example.com/.well-known/jwks.json',
  alg: ['RS256'],
}))
```

## Run post-authentication work

In 4.12.0, Basic Auth adds an async-capable
`onAuthSuccess(c, username)` callback. It runs after either ordinary
credentials or `verifyUser` succeeds, so identity state and audit work do not
need to parse the header again.

```ts
app.use('/admin/*', basicAuth({
  username,
  password,
  onAuthSuccess: (c, name) => c.set('user', name),
}))
```

`bearerAuth` is generic over the application environment, so the context
passed to `verifyToken` can retain typed variables and bindings.

## Serialize cookies safely

Since 4.9.0, `hono/cookie` exports `generateCookie()` and
`generateSignedCookie()` for constructing ordinary and signed cookie values.
On the patched 4.12 line, control characters in cookie attributes are rejected;
do not recreate permissive serialization around these helpers.

## Protect streamed JSX with CSP

Since 4.8.0, streamed `Suspense` and `ErrorBoundary` output can nonce generated
inline scripts through `StreamingContext`. Put the same nonce in the response
CSP.

```tsx
<StreamingContext value={{ scriptNonce: nonce }}>
  <Suspense fallback={<p>Loading</p>}>
    <Page />
  </Suspense>
</StreamingContext>
```

Secure Headers supports the CSP `report-to` and `report-uri` directives as of
4.11.0. Patched 4.12 behavior also validates JSX tag and attribute names,
isolates JSX context per request, and hardens JSX/CSS SSR. Keep those checks in
place when composing custom renderers.

## Block selected user agents

`@hono/ua-blocker` supplies `uaBlocker({ blocklist })`, the `aiBots` blocklist,
and a robots.txt helper. Use middleware enforcement when requests must be
rejected; use robots.txt only to discourage cooperative crawlers.

## Keep authentication-varying responses out of shared cache

Patched cache middleware rejects responses marked `private` or `no-store` and
responses with `Vary: Authorization` or `Vary: Cookie`. This prevents
authentication-dependent responses from leaking through a shared cache. Do
not strip those signals before cache middleware sees the response.

## Allow browser preflights through CSRF middleware

Version 4.13.3 exempts `OPTIONS` from CSRF validation so browser preflight
requests do not fail CSRF checks. Keep state-changing methods protected.

## Maintain the security patch floor

### 4.11 line

Use v4.11.10 or newer. Version 4.11.7 fixes an IP-restriction bypass, prevents
caching `private` and `no-store` responses, blocks unintended access to
Cloudflare static-asset keys through user-controlled paths, and escapes
untrusted strings rendered by JSX `ErrorBoundary`. Version 4.11.10 strengthens
timing-safe comparison.

### 4.12 line

Use v4.12.28 or newer and never remain below v4.12.27. The patch line hardens:

- Lambda header and client-IP handling.
- Static-file and SSG paths.
- IP restrictions and cookies.
- SSE fields and body limits.
- CORS credentials.
- JWT/JWK verification and temporal claims.
- Authentication-sensitive cache variation.
- JSX and CSS server rendering.
- `parseBody({ dot: true })` handling of `__proto__` segments.

Current behavior rejects control characters in SSE fields and cookie
attributes, requires Bearer authentication for JWT/JWK, validates JSX tag and
attribute names, and isolates JSX context per request.
