# Vue Ecosystem Tooling

## Nuxt data fetching

Nuxt 4.4 supports custom data-fetcher instances. Applications can use multiple
separately configured fetching clients instead of routing all requests through
one shared default instance.

## Vite's bundler transition

Vite 8 replaces the split esbuild-in-development and Rollup-in-production
pipeline with Rolldown. Vue framework users generally inherit this change
through Vite, while tools that integrate directly with Vite should account for
Rolldown as the bundler.

## Vite+

Vite+ is an open-source, MIT-licensed frontend toolchain built on Vite and Oxc.
Its `vp` CLI covers building, linting, formatting, type-checking, packaging,
testing, Node-version management, and package management. Configuration is
consolidated in `vite.config.ts`.
