# Tooling, build, and deployment

## Build artifacts

### Clientless builds

When every route has CSR disabled, SvelteKit skips the client build entirely
(`sveltekit-2.65.0`). Disable CSR for the complete route tree from the root
layout when a fully server-rendered application is intended:

```js
// src/routes/+layout.js
export const csr = false;
```

Do not make deployment steps depend on client artifacts in this configuration.

### Inline bundles

With `bundleStrategy: 'inline'`, builds no longer emit unused bundle and
stylesheet files beside the inlined output.

### Precompressed Markdown

Prerender precompression includes `.md` and `.mdx` files
(`sveltekit-2.66.0`). Deployments that serve precompressed artifacts can serve
generated Markdown through the same path.

## TypeScript and Vite

### Add Node types only when needed

Generated TypeScript configuration no longer injects `types: ['node']`.
Projects without Node-specific source do not need `@types/node` merely to
satisfy SvelteKit's generated configuration.

Svelte language tools and SvelteKit support TypeScript 6 without Svelte-specific
compatibility workarounds.

### Forward Svelte plugin options

Options not handled by the `sveltekit` Vite plugin are forwarded to
`vite-plugin-svelte`, allowing those plugin options to be supplied through
`sveltekit(...)`.

### Preserve Vite code splitting

An explicit Vite 8 `codeSplitting` setting remains effective
(`sveltekit-2.67.0`); SvelteKit does not unnecessarily replace it.

## CLI and configuration

The Svelte CLI supports community add-ons, and `sv create` can scaffold a
project from a Svelte Playground.

Svelte configuration accepts function values, allowing behavior that cannot be
represented as static configuration data alone.

## Hydration, adapters, and runtimes

Svelte can hydrate applications under a Content Security Policy. CSP-protected
pages no longer need to treat client hydration as incompatible.

SvelteKit can set up its Cloudflare adapter automatically, reducing the amount
of deployment-specific configuration required for Cloudflare projects.

The supported tooling and runtime matrix includes Deno.

## Package and compiler-tooling updates

Import `defineEnvVars` from `@sveltejs/kit/env`
(`svelte-5.56.5-5.56.9-kit-2.70.0-2.70.3`):

```js
import { defineEnvVars } from '@sveltejs/kit/env';
```

The Svelte compiler `print` API accepts an `indent` option so compiler tooling
can control indentation in printed output.
