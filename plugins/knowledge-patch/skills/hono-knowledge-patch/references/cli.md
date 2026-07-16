# Hono CLI

Install `@hono/cli` to add the `hono` command and its `docs`, `search`, `request`, `serve`, and `optimize` subcommands.

```sh
npm i @hono/cli
hono --help
```

## Read documentation

### Fetch a page as Markdown

`hono docs [path]` fetches a `hono.dev` documentation path and writes the page as Markdown to standard output.

```sh
hono docs /docs/api/routing
```

### Search documentation as JSON

`hono search <query>` writes matching documentation URLs and paths as JSON to standard output. Pass a returned path to `hono docs` to read the page.

```sh
hono search "basic auth"
```

## Exercise an application in-process

`hono request [file]` imports a Hono application and invokes `app.request()` without starting a server. The entry file defaults to `src/index.ts`, the method defaults to `GET`, and the result is printed as JSON.

Use `-P` for the path, `-X` for the method, and `-d` for the body.

```sh
hono request -P /api/users -X POST -d '{"name":"Alice"}' src/index.ts
```

## Serve with injected middleware

`hono serve [entry]` starts the application at `http://localhost:7070`. Repeat `--use` to apply built-in middleware or helpers without modifying the application.

```sh
hono serve --use 'logger()' --use "serveStatic({root:'./'})" src/index.ts
```

With no entry file, `serve` starts an empty application, so the served application can consist entirely of injected middleware.

## Optimize routing for deployment

`hono optimize [entry]` generates `dist/index.js` with route data precomputed for `PreparedRegExpRouter`. Deploy the generated entry directly.

```sh
hono optimize src/index.ts
wrangler deploy dist/index.js
```
