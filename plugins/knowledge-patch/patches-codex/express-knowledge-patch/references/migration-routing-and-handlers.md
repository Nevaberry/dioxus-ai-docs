# Migration, Routing, and Handlers

## Runtime and official codemods

Express 5 requires Node.js 18 or newer (5.0-migration). Upgrade the runtime
before diagnosing framework-level migration failures.

Install the major explicitly and run every available official migration:

```sh
npm install "express@5"
npx @expressjs/codemod upgrade
```

Run a single named transform when only one mechanical change is wanted:

```sh
npx @expressjs/codemod name-of-the-codemod
```

## Route-path string grammar

Route string syntax changed in 5.0-migration:

- Every wildcard must have a name.
- `/*splat` matches below the root but does not match `/`.
- `/{*splat}` also matches `/`.
- Braces replace `?` for optional path fragments.
- Regexp characters are unsupported in string paths.
- `()[]?+!` are reserved and must be escaped to match them literally.
- Parameter names must be JavaScript identifiers or quoted names.

Examples:

```js
app.get('/{*splat}', handler)
app.get('/:file{.:ext}', handler)
app.get(['/discussion/:slug', '/page/:slug'], handler)
```

Use an array of paths for explicit alternatives instead of embedding regexp
syntax in a string path.

## Rejected promises and error middleware

A rejected promise returned by request middleware or a route handler is
forwarded to error middleware as if `next(err)` had been called
(5.0-migration). The same applies when an `async` handler throws or an awaited
operation rejects.

```js
app.get('/user/:id', async (req, res) => {
  const user = await loadUser(req.params.id)
  res.json(user)
})

app.use((err, req, res, next) => {
  res.status(500).send(err.message)
})
```

Keep error middleware after the routes and middleware whose failures it must
receive.

## Native promise return values

Router handlers that return non-native promise-like values are deprecated
(5.1.0). Return a native `Promise`, or make the handler `async`, so rejected
work follows the supported error path.

## Base router exposure

`app.router` exists in 5.0-migration behavior, but it is only a reference to
the application's base Express router. It does not restore the Express 3
workflow in which the router had to be loaded explicitly.
