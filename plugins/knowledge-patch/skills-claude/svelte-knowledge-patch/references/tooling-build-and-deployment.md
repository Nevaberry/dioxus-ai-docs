# Tooling, build, and deployment

The versioned build behavior in this reference is attributed to
`sveltekit-2.65.0`, `sveltekit-2.66.0`, `sveltekit-2.67.0`, and
`svelte-5.56.5-5.56.9-kit-2.70.0-2.70.3`.

## Build output

### Clientless builds

When every route has client-side rendering disabled, SvelteKit skips the client
build instead of producing an unused client bundle. Disable CSR for the whole
route tree at the root layout when appropriate:

```js
// src/routes/+layout.js
export const csr = false;
```

### Inline bundle artifacts

With `bundleStrategy: 'inline'`, the build does not emit unused bundle and
stylesheet files beside the inlined output.

### Precompressed Markdown

Prerender precompression includes `.md` and `.mdx` files. Deployments serving
precompressed artifacts can therefore serve compressed generated Markdown too.

## TypeScript and Vite

### Generated Node typings

Generated TypeScript configuration no longer adds `types: ['node']`. A project
without Node-specific code does not need `@types/node` merely to satisfy
SvelteKit's generated configuration; add Node types explicitly when project
code needs them.

### TypeScript 6

Svelte language tools and SvelteKit support TypeScript 6. Svelte-specific
compatibility workarounds are not required for that upgrade.

### Vite plugin option forwarding

Options that the `sveltekit` Vite plugin does not consume are forwarded to
`vite-plugin-svelte`. Supply its plugin options through `sveltekit(...)` when
appropriate.

### Vite 8 code splitting

SvelteKit preserves an explicit Vite 8 `codeSplitting` setting instead of
unnecessarily replacing it.

## CLI and configuration

### Community add-ons and Playground projects

The Svelte CLI supports community add-ons. `sv create` can also scaffold a
project from a Svelte Playground.

### Function-valued configuration

Svelte configuration accepts function values, enabling configuration behavior
that cannot be represented as static data.

### Environment helper import

Import `defineEnvVars` from its package entry point:

```js
import { defineEnvVars } from '@sveltejs/kit/env';
```

### Compiler printer indentation

Svelte's `print` API accepts an `indent` option so compiler tooling can control
the indentation of printed output.

## Security and deployment targets

### CSRF in custom build environments

SvelteKit builds made with a non-production `NODE_ENV` enable CSRF protection.
Custom build environments therefore receive that protection rather than
silently omitting it.

### Cloudflare setup

SvelteKit can set up its Cloudflare adapter automatically, reducing the
deployment-specific configuration required for Cloudflare projects.

### Deno

Deno is included in Svelte's supported tooling and runtime matrix.
