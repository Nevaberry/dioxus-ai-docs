# Types and Configuration

## Stable typed routes (`15.5.0`)

Configure typed routes with the top-level `typedRoutes` flag, not an experimental option.

```ts
const nextConfig = { typedRoutes: true }

export default nextConfig
```

## Generated route prop helpers (`15.5.0`)

Next.js generates global, import-free `PageProps`, `LayoutProps`, and `RouteContext` helpers from the route tree. Supply a route literal to receive typed parameters. `LayoutProps` also includes typed parallel-route slots.

```tsx
export default function DashboardLayout(props: LayoutProps<'/dashboard'>) {
  return <>{props.children}{props.analytics}{props.team}</>
}
```

## Standalone route type generation (`15.5.0`)

Run `next typegen` before an external TypeScript check when generated route types are needed without starting development or building. The command accepts an optional project directory.

```sh
next typegen && tsc --noEmit
```

## Linter configuration migration (`15.5.0`, `16.0.0`)

`next lint` was deprecated in 15.5.0. Use the codemod to move to the ESLint CLI:

```sh
npx @next/codemod@latest next-lint-to-eslint-cli .
```

In 15.5, `next build` still validated lint if an ESLint configuration existed. In 16.0.0, `next lint` was removed and `next build` stopped running lint. `@next/eslint-plugin-next` now defaults to ESLint Flat Config instead of the legacy format.

## Turbopack configuration location (`16.0.0`)

Move Turbopack options from `experimental.turbopack` to the top-level `turbopack` object.

```ts
const nextConfig = {
  turbopack: {
    ignoreIssue: [{ path: '**/generated/**' }],
  },
}
```

## Runtime configuration removal (`16.0.0`)

`serverRuntimeConfig` and `publicRuntimeConfig` are removed. Use environment variables for server-only and public configuration.

## Cache Components naming (`15.4.0`, `16.0-guide`)

The 15.4 canary flag `experimental.dynamicIO` was renamed. Use top-level `cacheComponents: true` before applying `use cache` in Next.js 16.

## Native TypeScript configuration stripping (`16.0.0`)

Pass `--experimental-next-config-strip-types` to `next dev`, `next build`, or `next start` to run `next.config.ts` through Node.js native TypeScript stripping.

```sh
next dev --experimental-next-config-strip-types
```

## Selected configuration transitions

| Earlier or scoped form | Later or broader form |
| --- | --- |
| `experimental.dynamicIO` | `cacheComponents` |
| `experimental.turbopack` | `turbopack` |
| `experimental.turbopackFileSystemCacheForDev` | Stable and on by default in 16.1.0 |
| `experimental.adapterPath` | Stable build adapter API in 16.2.0 |
| `experimental.appNewScrollHandler` | Enabled by default in the `release-catalogs` canary line |
| `next-browser` | `agent-browser` 0.27 or newer in 16.3.0 |

Apply these transitions according to the installed release rather than mixing configurations from different release lines.
