---
name: express-knowledge-patch
description: Express
version: 5.2.x
license: MIT
metadata:
  author: Nevaberry
---


# Express Knowledge Patch

Use this skill when upgrading an Express application, reviewing route syntax,
debugging request or response behavior, or adopting current file-response and
handler features.

Prefer the application's manifest, code, and tests when they disagree with
general guidance. Check the installed Express version before applying behavior
that changed in a patch release.

## Reference Index

| Reference | Topics |
| --- | --- |
| [Migration, routing, and handlers](references/migration-routing-and-handlers.md) | Runtime floor, codemods, route-path grammar, rejected promises, native promises, and `app.router` |
| [Requests, middleware, and rendering](references/requests-middleware-and-rendering.md) | Parser defaults, request properties, dot-directories, Brotli requests, and asynchronous views |
| [Responses and files](references/responses-and-files.md) | MIME mappings, stricter response APIs, binary bodies, file ETags, links, and redirects |
| [Operations and release behavior](references/operations-and-release-behavior.md) | Listen failures, debug namespaces, npm lifecycle policy, and the query-parser reversion |

## Migration Priorities

Start with the changes most likely to prevent an application from starting or
matching requests:

1. Run on Node.js 18 or newer.
2. Install the desired Express major explicitly during migration.
3. Run the official upgrade codemod, then review its changes.
4. Rewrite route strings that use unnamed wildcards, question-mark optionals,
   or regexp characters.
5. Recheck parser assumptions, writable request properties, and static
   dot-directory access.
6. Exercise asynchronous failure paths and server-startup failures.

Install and run all available migrations:

```sh
npm install "express@5"
npx @expressjs/codemod upgrade
```

Run one named transform when a focused migration is preferable:

```sh
npx @expressjs/codemod name-of-the-codemod
```

Codemods handle mechanical changes. Keep integration tests around routes,
middleware ordering, parsing, static assets, errors, and startup because those
areas also contain behavior changes.

## Route-Path Grammar

Name every wildcard. Use `/*splat` when the root path must not match, and use
`/{*splat}` when it must:

```js
app.get('/{*splat}', handler)
```

Replace `?` optionals with braces:

```js
app.get('/:file{.:ext}', handler)
```

String paths no longer accept regexp characters. Use an array for explicit
alternatives:

```js
app.get(['/discussion/:slug', '/page/:slug'], handler)
```

The characters `()[]?+!` are reserved in string paths and must be escaped when
they are literal. Parameter names must be valid JavaScript identifiers or
quoted names.

## Asynchronous Error Handling

Returned rejected promises reach error middleware as if the handler had called
`next(err)`. An `async` handler can therefore throw or let an awaited promise
reject:

```js
app.get('/user/:id', async (req, res) => {
  const user = await loadUser(req.params.id)
  res.json(user)
})

app.use((err, req, res, next) => {
  res.status(500).send(err.message)
})
```

Return native promises from router handlers. Non-native promise-like return
values are deprecated. Prefer `async` handlers or an actual `Promise`.

## Parser and Request Defaults

Audit code that depended on older parser behavior:

- `express.urlencoded()` defaults `extended` to `false`.
- The default query parser is `"simple"`.
- `req.query` is a getter rather than a writable property.
- Without body-parsing middleware, `req.body` is `undefined`.
- `req.host` retains the port number.

Do not infer complex query parsing from the presence of nested-looking query
keys. Configure the intended parser behavior explicitly when the application
depends on it.

## Static Dot-Directories

`express.static()` defaults `dotfiles` to `"ignore"`. A URL under a directory
such as `/.well-known` therefore returns 404 unless it is intentionally
allowed.

Mount only the required dot-directory before the general static middleware:

```js
app.use(
  '/.well-known',
  express.static('public/.well-known', { dotfiles: 'allow' })
)
app.use(express.static('public'))
```

Avoid allowing all dotfiles merely to expose one public protocol directory.

## Startup Errors

`app.listen()` reports server error events to its callback. Treat a callback
argument as failure and use the server only after that check:

```js
const server = app.listen(8080, '0.0.0.0', (error) => {
  if (error) throw error
  console.log(server.address())
})
```

Test port conflicts or other bind failures so deployment code does not mistake
a failed listener for a successful startup.

## Response Tightening

Review response calls for stricter behavior:

- `res.clearCookie()` ignores supplied `maxAge` and `expires` options.
- `res.status()` accepts only integer status codes from 100 through 999.
- `res.vary()` throws when its field argument is missing.
- `res.redirect()` warns when its status or URL argument is `undefined`.

Validate dynamic redirect targets before calling `res.redirect()`:

```js
const target = getRedirectTarget(req)
if (target === undefined) return res.sendStatus(400)
res.redirect(303, target)
```

## File and Binary Responses

`res.send()` accepts a `Uint8Array` as a binary response body:

```js
res.send(new Uint8Array([0x4f, 0x4b]))
```

Control ETag generation for an individual file with the `etag` option:

```js
res.sendFile('/srv/public/archive.zip', { etag: false })
```

Use array values with `res.links()` to send multiple targets for one relation:

```js
res.links({
  alternate: ['/docs.en', '/docs.fi']
})
```

For MIME lookup, import `mime-types`; `express.static.mime` no longer exists.
Static files and `res.sendFile()` use the `mime-types` mappings.

## Operational Checks

To retain detailed router traces, enable both the Express and router debug
namespace families:

```sh
DEBUG=express:*,router,router:* node index.js
```

Do not rely on the brief extended-query-parser behavior from the initial 5.2.0
release. Upgrade a deployment pinned there and verify query behavior against
the installed patch version.

`res.render()` always behaves asynchronously, even if the view engine exposes
a synchronous implementation. Keep post-render logic in the asynchronous
completion path.

Request bodies may use Brotli encoding when sent by clients that support it.
Include encoded-request coverage when middleware or infrastructure handles
content encoding.

## Verification Checklist

- Confirm the Node.js runtime meets the minimum.
- Search route strings for wildcards, optionals, regexp syntax, and reserved
  characters.
- Exercise root and non-root wildcard matching separately.
- Verify rejected async work reaches the final error middleware.
- Confirm handlers return native promises.
- Test simple and application-configured query parsing.
- Check behavior when no body parser has populated `req.body`.
- Verify host-dependent logic with an explicit port.
- Request intended `/.well-known` assets and unrelated dotfiles.
- Simulate a listener bind error.
- Validate status, cookie-clearing, `Vary`, and redirect calls.
- Check MIME-sensitive static and file responses.
- Verify binary responses, per-file ETags, and repeated link relations.
- Run render completion logic through its asynchronous path.
- Enable the router namespaces when comparing routing traces.

Use the linked references for the complete compatibility details and precise
batch attribution.
