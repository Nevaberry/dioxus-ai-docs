# Configuration Options

## `resolve.tsconfigPaths` (8.0-beta)

Built-in tsconfig `paths` resolution without plugins like `vite-tsconfig-paths`. Opt-in due to a small performance cost:

```js
export default defineConfig({
  resolve: {
    tsconfigPaths: true,
  },
})
```

## `devtools` (8.0)

Enable Vite Devtools for debugging and analysis directly from the dev server:

```js
export default defineConfig({
  devtools: true,
})
```

## `server.forwardConsole` (8.0)

Forwards browser `console.log`/errors to the dev server terminal. Auto-activates when a coding agent is detected, or enable manually:

```js
export default defineConfig({
  server: {
    forwardConsole: true,
  },
})
```
