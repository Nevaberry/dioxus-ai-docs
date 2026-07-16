# Tooling, build, and deployment

## Contents

- [Build output](#build-output)
- [TypeScript and generated types](#typescript-and-generated-types)
- [Vite integration](#vite-integration)
- [CLI and configuration](#cli-and-configuration)
- [Hydration and deployment targets](#hydration-and-deployment-targets)

## Build output

### Omit an unused client build

When every route has client-side rendering disabled, SvelteKit skips the client
build. Disable CSR for the full route tree at its root when appropriate:

```js
// src/routes/+layout.js
export const csr = false;
```

Do not make deployment logic depend on an unused client bundle being present.

### Inline cleanly

With `bundleStrategy: 'inline'`, builds do not emit unused JavaScript bundle and
stylesheet files alongside the inlined output.

The clientless and inline build behavior is attributed to
`sveltekit-2.65.0`.

### Precompress Markdown

Prerender precompression includes `.md` and `.mdx` files. Deployments that serve
precompressed artifacts can serve compressed generated Markdown as well. This
behavior is attributed to `sveltekit-2.66.0`.

## TypeScript and generated types

SvelteKit's generated TypeScript configuration no longer adds
`types: ['node']`. A project without Node-specific code does not need
`@types/node` solely to satisfy generated configuration. This behavior is
attributed to `sveltekit-2.66.0`.

Svelte's language tools and SvelteKit support TypeScript 6. Upgrade without
adding a Svelte-specific TypeScript compatibility workaround.

## Vite integration

Options not handled directly by the `sveltekit` Vite plugin are forwarded to
`vite-plugin-svelte`. Supply its supported plugin options through
`sveltekit(...)`. This forwarding is attributed to `sveltekit-2.66.0`.

SvelteKit does not unnecessarily override a user-provided Vite 8
`codeSplitting` setting. Keep an explicit project setting when it is intentional.
This behavior is attributed to `sveltekit-2.67.0`.

## CLI and configuration

The Svelte CLI supports community add-ons. `sv create` can also scaffold a
project from a Svelte Playground, allowing a working playground example to seed
a local project.

Svelte configuration accepts function values. Use a function when configuration
behavior cannot be represented as static data.

## Hydration and deployment targets

### Content Security Policy

Svelte supports client hydration under a Content Security Policy. A protected
page does not need to treat hydration as categorically incompatible with CSP.

### Cloudflare

SvelteKit can configure its Cloudflare adapter automatically, reducing the
deployment-specific setup required for a Cloudflare target.

### Deno

The supported Svelte tooling and runtime matrix includes Deno.
