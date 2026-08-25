# Responses and Files

## MIME lookup and file response types

`express.static.mime` is removed in 5.0-migration behavior. Use `mime-types`
directly:

```js
const mime = require('mime-types')
mime.lookup('json')
```

Both static files and `res.sendFile()` use the `mime-types` mappings. Relevant
content-type changes include:

| Extension | Content type |
| --- | --- |
| `.js` | `text/javascript` |
| `.json` | `application/json` |
| `.css` | `text/css` |
| `.woff` | `font/woff` |
| `.svg` | `image/svg+xml` |

Check tests, caches, and clients that compare these response headers exactly.

## Stricter response behavior

The following rules apply after 5.0-migration:

- `res.clearCookie()` ignores any supplied `maxAge` and `expires` options.
- `res.status()` accepts only integer codes from 100 through 999.
- `res.vary()` throws instead of merely warning when its field argument is
  missing.

Validate values before calling these APIs, especially values derived from
configuration or request data.

## Binary `Uint8Array` bodies

`res.send()` accepts a `Uint8Array` as a binary response body (5.1.0):

```js
app.get('/bytes', (req, res) => {
  res.send(new Uint8Array([0x4f, 0x4b]))
})
```

## Per-file ETag control

`res.sendFile()` accepts an `etag` option for controlling ETag generation on
one file response (5.1.0):

```js
res.sendFile('/srv/public/archive.zip', { etag: false })
```

Use this when one response needs behavior different from the broader
application or static-file configuration.

## Multiple links for one relation

`res.links()` accepts an array value to emit multiple targets for the same
relation (5.1.0):

```js
res.links({
  alternate: ['/docs.en', '/docs.fi']
})
```

## Undefined redirect arguments

`res.redirect()` emits a deprecation warning when either its status argument
or URL argument is `undefined` (5.2.x). Validate dynamic destinations and pass
only a defined URL, adding an explicit status when needed:

```js
const target = getRedirectTarget(req)
if (target === undefined) return res.sendStatus(400)
res.redirect(303, target)
```
