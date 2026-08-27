# Requests, Middleware, and Rendering

## Parser and request-property defaults

The 5.0-migration behavior changes several request assumptions:

- `express.urlencoded()` defaults `extended` to `false`.
- The default query parser is `"simple"`.
- `req.query` is a getter rather than a writable property.
- `req.body` is `undefined` when body-parsing middleware has not populated it;
  it is no longer an empty object by default.
- `req.host` retains the port number.

Configure parser behavior explicitly when application code depends on complex
URL-encoded or query-string structures. Do not assign a replacement object to
`req.query`; consume the getter's result.

Guard access to `req.body` where a request can reach code without first
passing through the intended body parser. Include port-bearing host values in
tests for host-based routing or URL construction.

## Static dot-directories

`express.static()` defaults `dotfiles` to `"ignore"` (5.0-migration).
Requests such as `/.well-known/assetlinks.json` therefore return 404 under a
general static mount.

Allow only the intended public dot-directory and mount it before the general
static middleware:

```js
app.use(
  '/.well-known',
  express.static('public/.well-known', { dotfiles: 'allow' })
)
app.use(express.static('public'))
```

The specific mount makes a protocol directory public without exposing every
dotfile below the static root.

## Brotli request encoding

Express supports Brotli request encoding from clients that support it
(5.0-migration). When an application or its surrounding infrastructure
handles encoded request bodies, include Brotli in end-to-end tests.

## Asynchronous view rendering

`res.render()` enforces asynchronous behavior even when a view engine has a
synchronous implementation (5.0-migration). Code that depends on rendered
output must stay in the asynchronous completion path rather than assuming the
render call completes inline.
