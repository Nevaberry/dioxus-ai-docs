# Auth.js v5 Migration and Next.js Integration

## Pages Router session access

Do not assume that Auth.js server-side session methods are restored for Next.js Pages Router API routes. Fetch the session REST endpoint from those API routes instead.

This limitation does not affect pages rendered with `getServerSideProps`; call `auth(ctx)` there.

| Context | Session access |
| --- | --- |
| Pages Router API route | Fetch the session REST endpoint. |
| `getServerSideProps` | Call `auth(ctx)`. |

Keep the distinction explicit during migration so a helper that works during page rendering is not copied into an API route.

## Protect routes in Next.js 16

Next.js 16 renamed `middleware.ts` to `proxy.ts` and the `middleware` export to `proxy`. Older Next.js versions must keep the middleware file and export names.

Export Auth.js `auth` under the correct convention:

```ts
// proxy.ts
export { auth as proxy } from "@/auth"
```

Configure `authorized` on the Auth.js instance:

```ts
// auth.ts
export const { auth, handlers } = NextAuth({
  callbacks: {
    authorized: async ({ auth }) => !!auth,
  },
})
```

The proxy matcher selects which routes invoke protection. The `authorized` callback then decides whether each selected request is allowed.
