# Vue Ecosystem Tooling

## Nuxt data fetching

Nuxt 4.4 supports custom data-fetcher instances. Use separately configured
clients when an application needs different base URLs, authentication, retry
policies, or other fetch behavior instead of routing every request through one
shared default client.

## Vite 8 and Rolldown

Vite 8 replaces its esbuild-in-development and Rollup-in-production split with
Rolldown. Framework users generally inherit the bundler transition, while
tools that integrate directly with Vite should test plugin hooks, build output,
and assumptions tied to either former bundler.

## Vite+

Vite+ is an open-source, MIT-licensed toolchain built on Vite and Oxc. Its `vp`
CLI covers building, linting, formatting, type checking, packaging, testing,
Node-version management, and package management. It consolidates configuration
in `vite.config.ts`, so evaluate it as an integrated toolchain rather than only
as another Vite build command.

These items come from the `vue-ecosystem-news` batch.
