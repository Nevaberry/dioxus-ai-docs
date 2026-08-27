# Hono CLI

Install `@hono/cli` to provide the `hono` command.

```sh
npm i @hono/cli
```

## Discover documentation

`hono docs [path]` prints a `hono.dev` page as Markdown. `hono search <query>`
prints matching documentation URLs and paths as JSON, so a selected search
result path can be passed directly to `docs`.

```sh
hono search "basic auth"
hono docs /docs/middleware/builtin/basic-auth
```

## Make an in-process request

`hono request [file]` imports an application, invokes `app.request()` without
starting a server, and prints the response as JSON. The file defaults to
`src/index.ts` and the method defaults to `GET`. Use `-P`, `-X`, and `-d` for
the path, method, and body.

```sh
hono request -P /api/users -X POST -d '{"name":"Alice"}' src/index.ts
```

## Serve with injected middleware

`hono serve [entry]` starts the application at `http://localhost:7070` and
accepts repeatable `--use` expressions for middleware or helpers. With no
entry, it uses an empty application, so the server can be assembled entirely
from injected middleware.

```sh
hono serve --use 'logger()' --use "serveStatic({root:'./'})" src/index.ts
```

## Build a precomputed router

`hono optimize [entry]` writes `dist/index.js` with route data precomputed for
`PreparedRegExpRouter`. Deploy the generated entry rather than the original
source entry.

```sh
hono optimize src/index.ts
wrangler deploy dist/index.js
```
