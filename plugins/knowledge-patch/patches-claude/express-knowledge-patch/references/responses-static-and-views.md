# Responses, Static Files, and Views

## Static dot-directories

`express.static()` defaults `dotfiles` to `"ignore"`. Requests for files under
a dot-directory, such as `/.well-known/assetlinks.json`, therefore return 404
unless that directory is explicitly allowed.

Mount only the intended dot-directory with `dotfiles: 'allow'`, and place that
mount before the general static mount:

```js
app.use(
  '/.well-known',
  express.static('public/.well-known', { dotfiles: 'allow' })
)
app.use(express.static('public'))
```

This default is a migration concern from batch `5.0-migration`.

## MIME lookup and file response types

`express.static.mime` has been removed. Use the `mime-types` package directly:

```js
const mime = require('mime-types')
mime.lookup('json')
```

Static files and `res.sendFile()` now use its mappings. Notable results
include:

| Extension | Content type |
| --- | --- |
| `.js` | `text/javascript` |
| `.json` | `application/json` |
| `.css` | `text/css` |
| `.woff` | `font/woff` |
| `.svg` | `image/svg+xml` |

## Cookie, status, and vary behavior

Response validation and mutation are stricter:

- `res.clearCookie()` ignores supplied `maxAge` and `expires` options.
- `res.status()` accepts only integer codes from 100 through 999.
- `res.vary()` throws, rather than only warning, when its field argument is
  missing.

## Redirect arguments

`res.redirect()` emits a deprecation warning when either its status or URL
argument is `undefined` (since `5.2.x`). Validate a dynamic destination and
pass only a defined URL, with an explicit status when needed:

```js
const target = getRedirectTarget(req)
if (target === undefined) return res.sendStatus(400)
res.redirect(303, target)
```

## Asynchronous view rendering

`res.render()` enforces asynchronous behavior even when a view engine has a
synchronous implementation.

## Binary response bodies

`res.send()` accepts a `Uint8Array` as a binary body (since `5.1.0`):

```js
app.get('/bytes', (req, res) => {
  res.send(new Uint8Array([0x4f, 0x4b]))
})
```

## Per-file ETag control

Pass the `etag` option to `res.sendFile()` to control ETag generation for one
file response (since `5.1.0`):

```js
res.sendFile('/srv/public/archive.zip', { etag: false })
```

## Multiple links for one relation

`res.links()` accepts an array value when one relation has multiple targets
(since `5.1.0`):

```js
res.links({
  alternate: ['/docs.en', '/docs.fi']
})
```
