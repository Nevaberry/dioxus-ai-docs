# Static Assets and Pages Migration

Use this reference to deploy assets with a Worker, control asset-versus-code
routing, or convert a Pages project to Workers Static Assets and Workers Builds.

Relevant source batches: `2025` and `static-assets-migration`.

## Deploy assets with Worker code

`assets.directory` publishes a directory together with Worker code in one
deployment. By default, an exact asset match is served without invoking the
Worker; a miss invokes `main`.

Add `assets.binding` when Worker code must delegate to the asset service with
`env.ASSETS.fetch(request)`:

```jsonc
{
  "main": "src/index.js",
  "assets": {
    "directory": "./dist",
    "binding": "ASSETS"
  }
}
```

An assets-only Worker must omit `binding`, which is valid only when `main` is
present. Projects using the Workers Vite plugin do not need to declare
`assets.directory`.

Wrangler v4 removes `legacy_assets`; use Static Assets. Workers Sites is also
deprecated in favor of Static Assets.

## Configure fallback explicitly

Pages inferred fallback behavior from `index.html` or `404.html`. Workers
requires `assets.not_found_handling` to be either
`single-page-application` or `404-page`.

From compatibility date `2025-04-01`, navigation requests prefer Static Assets
fallback handling even without an exact asset match. An SPA `/index.html` or a
custom `/404.html` therefore runs before the Worker. This date gate has no
effect when `assets.run_worker_first = true`.

## Run selected routes through the Worker first

`assets.run_worker_first` accepts `true` or an ordered list of route patterns.
A leading `!` excludes a matching path:

```jsonc
{
  "assets": {
    "directory": "./dist",
    "not_found_handling": "single-page-application",
    "run_worker_first": ["/api/*", "!/api/docs/*"]
  }
}
```

Use Worker-first routing for authentication, logging, and middleware that must
run before static content. Each Worker-first request is billed as a normal
Worker invocation.

## Replace the Pages project configuration

Move from `pages_build_output_dir` to `assets.directory` in a root Wrangler
configuration. Preserve the Pages Functions project's compatibility date.
Placement and compatibility flags can also carry over:

```jsonc
{
  "name": "my-worker",
  "compatibility_date": "2026-07-28",
  "assets": { "directory": "./dist/client/" }
}
```

Review environment-specific settings rather than assuming Pages and Workers
use the same binding model.

## Add explicit upload exclusions

Workers does not automatically apply Pages' exclusions for `node_modules`,
`.DS_Store`, `.git`, and similar files. Put `.assetsignore` inside the
configured asset directory:

```text
**/node_modules
**/.DS_Store
**/.git
_worker.js
```

Also exclude generated Worker files when the build places them under the asset
directory.

## Convert Pages Functions

For an advanced-mode Pages project, move `_worker.js` outside the asset
directory or exclude it with `.assetsignore`, then set `main` to that file.

A `functions/` directory must first be compiled into one Worker entrypoint:

```sh
wrangler pages functions build --outdir=./dist/worker/
```

Then set `main` to `./dist/worker/index.js`.

Pages `_routes.json` and middleware do not retain function-first behavior
automatically. Translate those requirements to `assets.run_worker_first`.

## Change development and deployment commands

Replace:

| Pages command | Workers command |
| --- | --- |
| `wrangler pages dev` | `wrangler dev` |
| `wrangler pages deploy` | `wrangler deploy` |

The default local port also changes from 8788 for Pages to 8787 for Workers.

For Workers Builds, connect the repository and disable Pages automatic
deployments. Build-time variables in Workers Builds are configured separately
from Worker runtime variables.

## Recreate preview environments

Enable `preview_urls` and non-production branch builds in Workers Builds to
approximate Pages branch previews:

```jsonc
{
  "preview_urls": true
}
```

Workers does not natively give production and non-production deployments
separate bindings. Use Wrangler environments and matching build configuration
when that separation is required.

Workers Builds has less configurable non-production branch controls than
Pages. Custom branch aliases are not supported in this guidance.

## Preserve headers and redirects

Workers Static Assets supports Pages-style `_headers` and `_redirects` files as
long as they remain inside the configured asset directory.

## Configure hostnames and routes

Set `workers_dev: true` to use the account's `workers.dev` subdomain. Worker
custom domains require Cloudflare-managed nameservers. When only selected paths
should move, configure a Worker route instead of a custom domain.

## Review platform caveats

- Worker-first middleware incurs a normal Worker invocation.
- Workers Early Hints requires both the zone setting and suitable `Link`
  headers.
- Non-production branch controls are less configurable than Pages.
- Build-time variables and Worker runtime variables are separate.
- Preview binding separation requires explicit environments and build setup.
