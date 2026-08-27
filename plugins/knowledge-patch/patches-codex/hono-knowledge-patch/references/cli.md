# Hono CLI

Install `@hono/cli` to provide the `hono` executable.

```sh
npm i @hono/cli
```

## Discover documentation

`hono docs [path]` prints a `hono.dev` page as Markdown. `hono search <query>`
prints matching documentation URLs and paths as JSON, so a path returned by
`search` can be passed directly to `docs`.

```sh
hono search "basic auth"
hono docs /docs/middleware/builtin/basic-auth
```

## Make in-process application requests

`hono request [file]` imports an application, invokes `app.request()` without
starting a server, and prints the response as JSON. The file defaults to
`src/index.ts` and the method to `GET`. Use `-P`, `-X`, and `-d` for the path,
method, and body.

```sh
hono request -P /api/users -X POST -d '{"name":"Alice"}' src/index.ts
```

Because this command uses `app.request()`, provide validator-compatible
`Content-Type` headers whenever the target route expects JSON or form parsing.

## Serve with injected middleware

`hono serve [entry]` starts the application at `http://localhost:7070` and
accepts repeatable `--use` expressions for middleware or helpers. With no entry
file, it uses an empty application, so an entire server can be assembled from
injected middleware.

```sh
hono serve --use 'logger()' --use "serveStatic({root:'./'})" src/index.ts
```

Treat `--use` expressions as executable configuration and keep user-controlled
text out of them.

## Build a precomputed router

`hono optimize [entry]` writes `dist/index.js` with route data precomputed for
`PreparedRegExpRouter`. Deploy the generated entry instead of the original one.

```sh
hono optimize src/index.ts
wrangler deploy dist/index.js
```

Regenerate the optimized entry whenever route declarations change.
