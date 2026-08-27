# Static Assets and Pages migration

This topic-organized migration guide incorporates the `static-assets-migration`
material and the relevant Static Assets change from batch `2025`.

## Deploy assets with Worker code

`assets.directory` publishes a directory together with Worker code as one
deployment. By default, an exact asset match is served without invoking the
Worker; a miss invokes `main`. Add `assets.binding` when Worker code must
delegate to the asset service with `env.ASSETS.fetch(request)`:

```jsonc
{
  "main": "src/index.js",
  "assets": {
    "directory": "./dist",
    "binding": "ASSETS"
  }
}
```

An assets-only Worker must omit `binding`, because it is valid only with
`main`. A project using the Cloudflare Vite plugin does not need to declare
`assets.directory`.

## Configure fallback and Worker-first routes

Unlike Pages, Workers does not infer fallback behavior from `index.html` or
`404.html`. Set `assets.not_found_handling` to
`single-page-application` or `404-page`.

`assets.run_worker_first` accepts `true` or an ordered list of route patterns;
a leading `!` excludes a matching path:

```jsonc
{
  "assets": {
    "directory": "./dist",
    "not_found_handling": "single-page-application",
    "run_worker_first": ["/api/*", "!/api/docs/*"]
  }
}
```

From compatibility date `2025-04-01`, navigation requests prefer Static
Assets fallback handling even without an exact asset match. SPA `/index.html`
and custom `/404.html` responses therefore run before the Worker. This change
does not apply when `assets.run_worker_first = true`.

## Convert the Wrangler configuration

Move to a root Wrangler configuration and replace `pages_build_output_dir`
with `assets.directory`. Preserve the Pages Functions project's compatibility
date. Placement and compatibility flags can carry over:

```jsonc
{
  "name": "my-worker",
  "compatibility_date": "2026-07-28",
  "assets": { "directory": "./dist/client/" }
}
```

## Exclude upload-only files

Workers does not automatically apply Pages exclusions for `node_modules`,
`.DS_Store`, `.git`, or generated Worker files. Put `.assetsignore` inside the
configured asset directory:

```text
**/node_modules
**/.DS_Store
**/.git
_worker.js
```

## Convert Pages Functions

For an advanced-mode Pages project, move `_worker.js` outside the asset
directory or exclude it with `.assetsignore`, then point `main` at it.

A `functions/` directory must first be compiled to one Worker entrypoint:

```sh
wrangler pages functions build --outdir=./dist/worker/
```

Set `main` to `./dist/worker/index.js`. Pages `_routes.json` and middleware do
not automatically preserve function-first behavior. Configure
`assets.run_worker_first` for authentication, logging, and any other middleware
that must precede static assets.

## Change local and deployment commands

Replace `wrangler pages dev` and `wrangler pages deploy` with `wrangler dev`
and `wrangler deploy`. The default local ports differ: Pages uses 8788, while
Workers uses 8787.

Workers Builds requires connecting the repository and disabling automatic
Pages deployments. Build-time variables in Workers Builds are configured
separately from runtime Worker variables.

## Recreate preview environments

Enable `preview_urls` and non-production branch builds in Workers Builds to
approximate Pages branch previews:

```jsonc
{
  "preview_urls": true
}
```

Workers does not natively offer distinct production and non-production
bindings. Use Wrangler environments and corresponding build configuration when
that separation is required.

## Preserve headers, redirects, and routing

Workers Static Assets supports Pages-style `_headers` and `_redirects` files
when those files remain inside the asset directory.

Set `workers_dev: true` to opt into the account's `workers.dev` subdomain.
Worker custom domains require Cloudflare-managed nameservers; when only
selected paths should migrate, use a Worker route.

## Account for migration differences

- Worker-first middleware is billed as a normal Worker invocation.
- Workers Early Hints require both the zone setting and suitable `Link`
  headers.
- Non-production branch controls in Workers Builds are less configurable than
  Pages controls; custom branch aliases are not supported in this source
  version.
