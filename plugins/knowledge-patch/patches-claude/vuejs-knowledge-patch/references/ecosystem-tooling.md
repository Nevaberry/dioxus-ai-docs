# Vue Ecosystem Tooling

## Nuxt custom data fetchers

Nuxt 4.4 supports custom data-fetcher instances. Use separately configured
clients when a feature needs distinct base URLs, headers, authentication, or
other behavior instead of routing every request through one shared default.

## Vite 8 and Rolldown

Vite 8 replaces its esbuild-in-development and Rollup-in-production split with
Rolldown. Framework applications generally inherit the bundler transition,
while tools that integrate directly with Vite should validate their plugin,
build, and output assumptions against Rolldown.

## Vite+ unified toolchain

Vite+ is an open-source, MIT-licensed frontend toolchain based on Vite and Oxc.
Its `vp` CLI covers building, linting, formatting, type checking, packaging,
testing, Node-version management, and package management. It consolidates
toolchain configuration in `vite.config.ts`.
