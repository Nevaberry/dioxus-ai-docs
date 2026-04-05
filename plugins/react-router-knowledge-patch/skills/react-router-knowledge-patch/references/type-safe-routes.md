# Type-Safe Route Modules

The Vite plugin auto-generates types into `.react-router/types/`. Each route gets its own type file.

## Setup

Add to `tsconfig.json`:

```json
{
  "compilerOptions": {
    "rootDirs": [
      ".",
      "./.react-router/types"
    ]
  }
}
```

## Usage

Import per-route types from the generated `+types` directory:

```ts
import type { Route } from "./+types/product";

export async function loader({ params }: Route.LoaderArgs) {
  // params.pid is typed as string
  return { product: await getProduct(params.pid) };
}

export default function Product({ loaderData }: Route.ComponentProps) {
  return <div>{loaderData.product.name}</div>;
}
```

## Available Types

| Type | Purpose |
|------|---------|
| `Route.LoaderArgs` | Server loader `{ params, request, context }` |
| `Route.ActionArgs` | Server action `{ params, request, context }` |
| `Route.ClientLoaderArgs` | Client loader `{ params, serverLoader }` |
| `Route.ClientActionArgs` | Client action `{ params, serverAction }` |
| `Route.ComponentProps` | Route component `{ loaderData, actionData, params, matches }` |
| `Route.ErrorBoundaryProps` | Error boundary props |
| `Route.HydrateFallbackProps` | Hydration fallback props |

## Component Props

Route components receive typed props directly — these can replace `useLoaderData()`/`useParams()` hooks:

- `loaderData` — typed return value from loader
- `actionData` — typed return value from action
- `params` — typed URL parameters
- `matches` — parent route matches
