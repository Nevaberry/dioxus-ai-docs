# Migration, Routing, and Errors

## Runtime floor and codemods

Express 5 requires Node.js 18 or newer. Install the target major, then use the
official codemod to apply all available migrations:

```sh
npm install "express@5"
npx @expressjs/codemod upgrade
```

Run one transform by name when a narrower change is required:

```sh
npx @expressjs/codemod name-of-the-codemod
```

These migration requirements and transforms are recorded in batch
`5.0-migration`.

## Route-path string grammar

Every string-path wildcard must be named:

- `/*splat` matches through a named wildcard but excludes `/`.
- `/{*splat}` uses braces so the named wildcard also includes `/`.

Use braces instead of `?` for optional path parts. For example,
`/:file{.:ext}` makes the extension portion optional.

Regexp characters are unsupported in string paths. Pass an array of paths
when a route has alternatives:

```js
app.get(['/discussion/:slug', '/page/:slug'], handler)
```

The characters `()[]?+!` are reserved in string paths. Escape them when they
are intended as literal characters. Parameter names must be JavaScript
identifiers or quoted names.

```js
app.get('/{*splat}', handler)
app.get('/:file{.:ext}', handler)
```

## Rejected promises and error middleware

When request middleware or a route handler returns a rejected promise, Express
forwards the rejection to error-handling middleware as if the handler had
called `next(err)`. An error thrown by an `async` handler, including a rejected
`await`, follows the same path.

```js
app.get('/user/:id', async (req, res) => {
  const user = await loadUser(req.params.id)
  res.json(user)
})

app.use((err, req, res, next) => {
  res.status(500).send(err.message)
})
```

Router handlers should return a native `Promise` or be declared `async`.
Returning a non-native promise-like value is deprecated (since `5.1.0`).

## Base router exposure

`app.router` exists, but it is a reference to the application's base Express
router. Its presence does not restore the earlier explicit router-loading
behavior.
