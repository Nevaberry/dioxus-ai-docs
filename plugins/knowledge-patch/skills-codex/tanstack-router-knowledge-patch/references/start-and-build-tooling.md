# TanStack Start and Build Tooling

## Preserve punctuation in virtual route definitions

The route generator preserves dots in explicit virtual route paths and
pathless layout IDs rather than treating them as flat-file separators. Leading
and trailing underscores in virtual `route()` paths are literal URL
characters.

Physical file routes still require bracket escapes for literal underscore
segments. This includes index routes below pathless layouts, `physical()`
prefixes, and `__virtual.ts` subtrees.

## Resolve TypeScript aliases in virtual configuration

Virtual route configuration files may import through aliases declared in
`tsconfig`. The generator resolves those aliases while loading the
configuration.

## Parse plain TypeScript transforms correctly

When a filename is available, router and Start import-protection transforms
parse plain TypeScript files without JSX. Angle-bracket type assertions are no
longer misread as JSX in those files.

## Escape custom route-token assumptions

File-based generation accepts custom `routeToken` and `indexToken` values that
begin with regex metacharacters such as `+`.

## Isolate multiple plugin instances

Each router plugin instance holds explicit context instead of sharing global
route metadata. Multiple instances therefore do not cross-transform each
other's route files.

## Select supported builders and peers

`@tanstack/router-plugin` supports Rsbuild, accepts Vite 8 as a peer, and
supports `vite-plugin-solid` beginning with `3.0.0-0`.

For Rsbuild client output, module scripts are the default; IIFE output is
available for classic-script environments. A `transformAssets` script callback
receives only `{ kind: 'script', url }`, and cross-origin configuration for
script assets uses the `script` key.

## Preserve route state during HMR

React route HMR preserves state for auto-split components and functions with
lowercase names. Development transforms cover split component groups and
unsplit root shell, pending, and error options.

Aliased route imports retain generated properties, and Vite Fast Refresh
recognizes `createRootRouteWithContext` calls with type arguments. Webpack and
Rspack no longer import the optional `react-refresh/runtime` package for route
HMR.

## Import server-safe router helpers from the root

The `@tanstack/react-router` package has a `react-server` export condition. It
preserves the normal API while resolving `notFound` and `redirect` through a
server-safe entry, so React Server Components and server functions can import
them from the package root.

```tsx
import { notFound, redirect } from '@tanstack/react-router'
```

## Use intent tooling for Router and Start

`@tanstack/intent` publishes development-agent skills and CLI entry points for
TanStack Router and TanStack Start packages.
