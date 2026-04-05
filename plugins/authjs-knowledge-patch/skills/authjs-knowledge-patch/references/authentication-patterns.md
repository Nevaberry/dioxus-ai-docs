# Authentication Patterns

## Universal `auth()` Replaces Multiple v4 Methods

| v4 | v5 |
|---|---|
| `getServerSession(authOptions)` | `auth()` |
| `getToken(req)` | `auth(req, res)` |
| `withAuth(middleware)` | `auth` as proxy export |
| `useSession()` (client) | `useSession()` (unchanged) |
| `getServerSession(req, res, authOptions)` | `auth(req, res)` |
| `getServerSession(ctx.req, ctx.res, authOptions)` | `auth(ctx)` |

```tsx filename="app/page.tsx"
import { auth } from "@/auth"

export default async function Page() {
  const session = await auth()
  return <p>Welcome {session?.user.name}!</p>
}
```

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
