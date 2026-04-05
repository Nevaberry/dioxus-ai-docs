---
name: authjs-knowledge-patch
description: >
  Auth.js v5 (next-auth@5) configuration, migration from v4, middleware/proxy
  patterns, edge runtime split, environment variables, WebAuthn/passkeys,
  and credential error handling. Use when writing Auth.js or next-auth v5 code.
version: "5.0.0"
license: MIT
metadata:
  author: Nevaberry
---

# Auth.js v5 Knowledge Patch

Auth.js v5 is a major rewrite. The package is now framework-agnostic (`@auth/sveltekit`, `@auth/express`, `@auth/solid-start`) with `next-auth` as the Next.js wrapper. Requires Next.js 14+. OAuth 1.0 is deprecated.

## Reference Index

- [Configuration](references/configuration.md) — Root config, edge split config, environment variables, adapter and type changes
- [Authentication Patterns](references/authentication-patterns.md) — Proxy/middleware, route protection, server-side sign in/out, authorized callback
- [Providers and Features](references/providers-and-features.md) — WebAuthn/passkeys setup, custom credential errors

## v4 to v5 Migration Quick Reference

| v4 | v5 |
|---|---|
| `getServerSession(authOptions)` | `auth()` |
| `getToken(req)` | `auth(req, res)` |
| `withAuth(middleware)` | `auth` as proxy export |
| `useSession()` (client) | `useSession()` (unchanged) |
| `getServerSession(req, res, authOptions)` | `auth(req, res)` |
| `getServerSession(ctx.req, ctx.res, authOptions)` | `auth(ctx)` |
| `NextAuthOptions` | `NextAuthConfig` |
| `@next-auth/prisma-adapter` | `@auth/prisma-adapter` |
| `NEXTAUTH_SECRET` | `AUTH_SECRET` |
| `NEXTAUTH_URL` | `AUTH_URL` (auto-detected) |
| Cookie prefix: `next-auth` | Cookie prefix: `authjs` |

## Root Config Pattern

Configuration moves from the API route to a root `auth.ts` file. `NextAuth()` returns methods used everywhere:

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

## Universal `auth()` Function

Replaces `getServerSession`, `getToken`, and `withAuth` with a single function:

```tsx filename="app/page.tsx"
import { auth } from "@/auth"

export default async function Page() {
  const session = await auth()
  return <p>Welcome {session?.user.name}!</p>
}
```

## Environment Variables

- `AUTH_SECRET` — the only required variable
- `AUTH_URL` / `NEXTAUTH_URL` — auto-detected from request headers in most environments
- `AUTH_{PROVIDER}_ID` / `AUTH_{PROVIDER}_SECRET` — auto-inferred provider credentials (e.g. `AUTH_GITHUB_ID`)
- `AUTH_TRUST_HOST=true` — set when running behind a proxy (same as `trustHost: true`)

## TypeScript

- `NextAuthOptions` is now `NextAuthConfig`
- Types like `Account`, `Session`, `User` export from `@auth/core/types` (re-exported from framework packages)
- Adapter types from `next-auth/adapters`, `@auth/sveltekit/adapters`, etc.

## Proxy / Middleware

As of Next.js 16, `middleware.ts` is renamed to `proxy.ts` and the export is `proxy` instead of `middleware`.

```ts filename="proxy.ts"
// Simple: export auth directly
export { auth as proxy } from "@/auth"

// Advanced: wrap with custom logic
import { auth } from "@/auth"

export const proxy = auth((req) => {
  if (!req.auth && req.nextUrl.pathname !== "/login") {
    const newUrl = new URL("/login", req.nextUrl.origin)
    return Response.redirect(newUrl)
  }
})

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
}
```

Use the `authorized` callback to control access:

```ts filename="auth.ts"
export const { auth, handlers } = NextAuth({
  callbacks: {
    authorized: async ({ auth }) => {
      return !!auth // logged-in users pass, others redirect to login
    },
  },
})
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

## Server-Side Sign In/Out

```tsx filename="app/components/signin-button.tsx"
import { signIn } from "@/auth"

export function SignIn() {
  return (
    <form action={async () => {
      "use server"
      await signIn("github", { redirectTo: "/dashboard" })
    }}>
      <button type="submit">Sign in</button>
    </form>
  )
}
```

## Protecting API Routes

```ts filename="app/api/admin/route.ts"
import { auth } from "@/auth"
import { NextResponse } from "next/server"

export const GET = auth(function GET(req) {
  if (req.auth) return NextResponse.json(req.auth)
  return NextResponse.json({ message: "Not authenticated" }, { status: 401 })
})
```

## Adapter Scope Change

```diff
- npm install @next-auth/prisma-adapter
+ npm install @auth/prisma-adapter
```

## WebAuthn / Passkeys (Experimental)

Requires a database adapter with an `Authenticator` table. Enable with `experimental: { enableWebAuthn: true }`.

```ts filename="auth.ts"
import Passkey from "next-auth/providers/passkey"
import { PrismaAdapter } from "@auth/prisma-adapter"

export default {
  adapter: PrismaAdapter(prisma),
  providers: [Passkey],
  experimental: { enableWebAuthn: true },
}
```

Peer deps: `@simplewebauthn/browser@9.0.1` and `@simplewebauthn/server@9.0.3`.

## Custom Credential Errors

```ts
import { CredentialsSignin } from "next-auth"

class InvalidLoginError extends CredentialsSignin {
  code = "Invalid identifier or password"
}
// Throw in authorize() → user redirected to signin?error=CredentialsSignin&code=Invalid+identifier+or+password
```
