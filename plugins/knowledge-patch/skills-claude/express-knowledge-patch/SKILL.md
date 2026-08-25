---
name: express-knowledge-patch
description: Express
version: 5.2.x
license: MIT
metadata:
  author: Nevaberry
---



# Express Knowledge Patch

Use this skill when upgrading, reviewing, debugging, or operating an Express
application whose behavior depends on current routing, request parsing,
response, static-file, or server-startup behavior. Check the installed Express
and Node.js versions first, then open the reference matching the work.

Prefer the application's manifest, lockfile, code, and tests when they
demonstrate behavior different from this guidance.

## Reference index

| Reference | Topics |
| --- | --- |
| [migration-routing-and-errors.md](references/migration-routing-and-errors.md) | Runtime floor, codemods, route-path grammar, router exposure, promise rejection, and handler promises |
| [requests-and-parsing.md](references/requests-and-parsing.md) | Body and query defaults, request properties, parser rollback, and Brotli request encoding |
| [responses-static-and-views.md](references/responses-static-and-views.md) | Dot-directories, MIME types, file responses, stricter response methods, redirects, links, binary bodies, and rendering |
| [server-debug-and-lifecycle.md](references/server-debug-and-lifecycle.md) | Listen errors, debug namespaces, npm install behavior, and release lifecycle phases |

## Upgrade first: runtime and codemods

Express 5 requires Node.js 18 or newer. Verify the runtime before changing the
application:

```sh
node --version
npm install "express@5"
```

Apply every available official migration transform:

```sh
npx @expressjs/codemod upgrade
```

Or run one named transform:

```sh
npx @expressjs/codemod name-of-the-codemod
```

Review transformed routing, parsing, response, and startup code against the
checks below.

## Breaking route-path changes

String route paths use a stricter grammar:

| Old intent | Current form |
| --- | --- |
| Wildcard that excludes `/` | `/*splat` |
| Wildcard that includes `/` | `/{*splat}` |
| Optional extension | `/:file{.:ext}` |
| Alternative paths | An array such as `['/discussion/:slug', '/page/:slug']` |

Every wildcard must have a name. Use braces instead of `?` for optional
segments. Regexp characters are not supported in string paths.

The characters `()[]?+!` are reserved in string paths and must be escaped when
they are meant literally. Parameter names must be JavaScript identifiers or
quoted names.

```js
app.get('/{*splat}', handler)
app.get('/:file{.:ext}', handler)
app.get(['/discussion/:slug', '/page/:slug'], handler)
```

`app.router` is available, but it is only a reference to the application's
base Express router. Do not treat it as the old explicit router-loading
mechanism.

## Promise and error behavior

A rejected promise returned by request middleware or a route handler is
forwarded to error middleware as though `next(err)` had been called. Thrown
errors and rejected `await` expressions in an `async` handler therefore use
the normal Express error path.

```js
app.get('/user/:id', async (req, res) => {
  const user = await loadUser(req.params.id)
  res.json(user)
})

app.use((err, req, res, next) => {
  res.status(500).send(err.message)
})
```

Return a native `Promise` or use an `async` handler. Returning a non-native
promise-like value from a router handler is deprecated.

## Request parsing and property changes

Recheck any code that assumed the previous defaults:

- `express.urlencoded()` defaults `extended` to `false`.
- The default query parser is `"simple"`.
- `req.query` is a getter rather than a writable property.
- Without body-parsing middleware, `req.body` is `undefined`, not `{}`.
- `req.host` retains the port number.

Do not build around the short-lived extended-query-parser behavior from
5.2.0. Express 5.2.1 fully reverted that change; the associated
CVE was rejected and there is no vulnerability tied to that behavior.
Deployments pinned to 5.2.0 should upgrade.

Express also supports Brotli request encoding when clients support it.

## Static dot-directories and MIME types

`express.static()` defaults `dotfiles` to `"ignore"`. A path such as
`/.well-known/assetlinks.json` therefore returns 404 unless it is explicitly
mounted and allowed.

```js
app.use(
  '/.well-known',
  express.static('public/.well-known', { dotfiles: 'allow' })
)
app.use(express.static('public'))
```

Allow only the intended dot-directory, and mount it before the general static
directory.

`express.static.mime` has been removed. Use `mime-types` directly. Static
files and `res.sendFile()` use its mappings, including:

- `.js` → `text/javascript`
- `.json` → `application/json`
- `.css` → `text/css`
- `.woff` → `font/woff`
- `.svg` → `image/svg+xml`

```js
const mime = require('mime-types')
mime.lookup('json')
```

## Response compatibility checks

The following response behavior is stricter:

- `res.clearCookie()` ignores supplied `maxAge` and `expires` options.
- `res.status()` accepts only integer status codes from 100 through 999.
- `res.vary()` throws if its field argument is missing.
- `res.redirect()` warns when its status or URL argument is `undefined`.
- `res.render()` behaves asynchronously even when the view engine is
  synchronous.

Validate a dynamic redirect target before calling `res.redirect()`:

```js
const target = getRedirectTarget(req)
if (target === undefined) return res.sendStatus(400)
res.redirect(303, target)
```

## Common response features

`res.send()` accepts a `Uint8Array` as a binary response body:

```js
app.get('/bytes', (req, res) => {
  res.send(new Uint8Array([0x4f, 0x4b]))
})
```

Control ETag generation for one file by passing `etag` to `res.sendFile()`:

```js
res.sendFile('/srv/public/archive.zip', { etag: false })
```

Use an array value with `res.links()` to emit multiple targets for one
relation:

```js
res.links({
  alternate: ['/docs.en', '/docs.fi']
})
```

## Server startup and debugging

`app.listen()` reports server error events to its callback instead of throwing
them. Distinguish an error from successful listening:

```js
const server = app.listen(8080, '0.0.0.0', (error) => {
  if (error) throw error
  console.log(server.address())
})
```

Router traces use `router`, `router:layer`, and `router:route` namespaces.
Enable both the Express and router families when the old wildcard's detail is
needed:

```sh
DEBUG=express:*,router,router:* node index.js
```

## Dependency selection

An unversioned npm install selects Express 5:

```sh
npm install express
```

Pin the previous major explicitly only when intentionally remaining there:

```sh
npm install "express@4"
```

Before relying on a release's support phase, read the lifecycle details in the
server and lifecycle reference.

## Review checklist

1. Confirm Node.js meets the runtime floor and identify the installed Express
   version.
2. Run the applicable codemod and inspect every changed route path.
3. Test root-inclusive wildcards, optional segments, and literal reserved
   characters.
4. Verify async failures reach the intended error middleware.
5. Recheck body, query, host, and query-parser assumptions.
6. Explicitly mount required dot-directories before general static content.
7. Audit status, cookie clearing, varying, redirects, rendering, and MIME
   behavior.
8. Handle `app.listen()` callback errors and enable the router debug
   namespaces when tracing routes.
