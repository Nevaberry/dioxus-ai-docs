# Security and Authentication

## Contents

- [JWT and JWK algorithm policy](#jwt-and-jwk-algorithm-policy)
- [Token sources and JWK resolution](#token-sources-and-jwk-resolution)
- [Claims, payloads, and keys](#claims-payloads-and-keys)
- [Basic Auth success hooks](#basic-auth-success-hooks)
- [CSP and user-agent blocking](#csp-and-user-agent-blocking)
- [Required security patch levels](#required-security-patch-levels)

## JWT and JWK algorithm policy

From v4.11.4, JWT and JWK/JWKS middleware require explicit algorithm configuration so an untrusted JWT header cannot choose the verification algorithm. `jwt` takes one `alg`; `jwk` takes an array containing asymmetric algorithms only.

```ts
import { jwk } from 'hono/jwk'
import { jwt } from 'hono/jwt'

jwt({ secret: 'it-is-very-secret', alg: 'HS256' })
jwk({
  jwks_uri: 'https://example.com/.well-known/jwks.json',
  alg: ['RS256'],
})
```

JWT utilities also export `AlgorithmTypes`. JWKS `allowedAlgorithms` accepts values declared with `const`.

## Token sources and JWK resolution

### Read JWTs from a custom header or cookie

JWT middleware accepts `headerName` for a nonstandard request header (since 4.8.0):

```ts
jwt({ secret: 'secret-key', alg: 'HS256', headerName: 'X-Auth-Token' })
```

Set `cookie` to a cookie name to read the JWT from that cookie instead:

```ts
app.use('/auth/*', jwt({
  secret: 'it-is-very-secret',
  alg: 'HS256',
  cookie: 'access_token',
}))
```

### Configure JWK authentication

JWK middleware also accepts `headerName` for a custom token header (since 4.9.0). Its `keys` and `jwks_uri` options may be functions that receive the request context, enabling request-dependent key resolution.

With `allow_anon: true`, a request without a valid token continues and `jwtPayload` remains unset. Ensure downstream handlers explicitly support the anonymous case.

JWT utilities export `verifyWithJwks` for JWKS verification outside the JWK middleware (since 4.9.0).

JWT and JWK middleware accept only the `Bearer` authorization scheme in current 4.12 releases.

## Claims, payloads, and keys

### Validate the issuer

JWT verification supports validation of the `iss` claim (since 4.9.0). Prefer this option to a separate application-level issuer check.

### Control temporal-claim checks

`verifyOptions.nbf`, `verifyOptions.iat`, and `verifyOptions.exp` control verification of those claims when present. Every check defaults to `true`; disable one only when that claim must be ignored.

```ts
jwt({
  secret: 'it-is-very-secret',
  alg: 'HS256',
  verifyOptions: { iat: false },
})
```

Current 4.12 JWT verification rejects falsy, non-numeric, and non-finite `exp`, `nbf`, and `iat` values. `decode()` and `decodeHeader()` reject malformed token structure. JWT utilities also accept single-line PEM keys.

### Type the verified payload

Use `JwtVariables` from `hono/jwt` as the application's Hono `Variables` type so `c.get('jwtPayload')` infers the verified payload:

```ts
import { Hono } from 'hono'
import { jwt, type JwtVariables } from 'hono/jwt'

const app = new Hono<{ Variables: JwtVariables }>()
app.use('/auth/*', jwt({ secret: 'it-is-very-secret', alg: 'HS256' }))
app.get('/auth/me', (c) => c.json(c.get('jwtPayload')))
```

## Basic Auth success hooks

Basic Auth accepts an async-capable `onAuthSuccess(c, username)` callback in 4.12, including when `verifyUser` is used. Use it to record identity or audit information without reparsing the header.

```ts
basicAuth({
  username: 'hono',
  password: 'secret',
  onAuthSuccess: (c, username) => c.set('username', username),
})
```

## CSP and user-agent blocking

### Add nonces to streamed JSX scripts

Provide `StreamingContext` with `value={{ scriptNonce: nonce }}` to add a CSP nonce to inline scripts emitted by streaming `Suspense` and `ErrorBoundary` (since 4.8.0). The response's CSP header must allow the same nonce.

### Configure CSP reports

Secure Headers content-security policies support `report-to` and `report-uri` directives from 4.11.0. Use them for violation reporting instead of constructing the CSP header manually.

### Block user agents

`@hono/ua-blocker` accepts a string `blocklist` (since 4.8.0). `@hono/ua-blocker/ai-bots` exports the predefined `aiBots` list. `useAiRobotsTxt()` can serve `/robots.txt` that discourages those bots.

## Required security patch levels

### Hono 4.11

Use at least v4.11.7 when the application uses any of these features:

- IP restriction: fixes an IPv4 validation bypass.
- Cache middleware on Deno, Bun, or Node.js: prevents caching responses marked `private` or `no-store`.
- Cloudflare Workers static serving with user-controlled paths: prevents unintended internal asset-key reads.
- JSX `ErrorBoundary` with untrusted data: escapes untrusted error strings.

Use v4.11.10 or newer for the further strengthening of timing-safe comparison.

### Hono 4.12

Use at least v4.12.27 for the security fixes accumulated in the 4.12 line. They harden:

- SSE control fields.
- Cookie names and attributes.
- Dotted body parsing.
- Static and SSG paths.
- IP matching.
- JSX/CSS SSR escaping and request-context isolation.
- Body limits for streamed requests and AWS Lambda requests.
- Credentialed CORS with wildcard configuration.
- Repeated headers and cookies in AWS adapters.
