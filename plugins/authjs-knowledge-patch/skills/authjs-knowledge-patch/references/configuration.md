# Configuration

## Root Config with Destructured Exports

Configuration moves from the API route to a root `auth.ts` file. `NextAuth()` returns methods you use everywhere.

```ts filename="auth.ts"
import NextAuth from "next-auth"
import GitHub from "next-auth/providers/github"

export const { auth, handlers, signIn, signOut } = NextAuth({
  providers: [GitHub],
})
```

```ts filename="app/api/auth/[...nextauth]/route.ts"
import { handlers } from "@/auth"
export const { GET, POST } = handlers
```

## Edge Split Config

When using a database adapter not compatible with Edge, split config into two files:

```ts filename="auth.config.ts"
import GitHub from "next-auth/providers/github"
import type { NextAuthConfig } from "next-auth"

export default { providers: [GitHub] } satisfies NextAuthConfig
```

```ts filename="auth.ts"
import NextAuth from "next-auth"
import { PrismaAdapter } from "@auth/prisma-adapter"
import { PrismaClient } from "@prisma/client"
import authConfig from "./auth.config"

const prisma = new PrismaClient()

export const { auth, handlers, signIn, signOut } = NextAuth({
  adapter: PrismaAdapter(prisma),
  session: { strategy: "jwt" },
  ...authConfig,
})
```

```ts filename="proxy.ts"
import authConfig from "./auth.config"
import NextAuth from "next-auth"

export const { auth: proxy } = NextAuth(authConfig)
```

## Environment Variables

- Use `AUTH_` prefix (not `NEXTAUTH_`). `AUTH_SECRET` is the only required variable.
- `AUTH_URL` / `NEXTAUTH_URL` is auto-detected from request headers in most environments.
- Provider credentials auto-infer from `AUTH_{PROVIDER}_ID` and `AUTH_{PROVIDER}_SECRET` (e.g. `AUTH_GITHUB_ID`).
- `AUTH_TRUST_HOST=true` when running behind a proxy (same as `trustHost: true`).

## Adapter Scope Change

```diff
- npm install @next-auth/prisma-adapter
+ npm install @auth/prisma-adapter
```

## TypeScript

- `NextAuthOptions` is now `NextAuthConfig`
- Types like `Account`, `Session`, `User` export from `@auth/core/types` (re-exported from framework packages)
- Adapter types from `next-auth/adapters`, `@auth/sveltekit/adapters`, etc.

## Cookie Prefix

The cookie prefix changed from `next-auth` to `authjs`.
