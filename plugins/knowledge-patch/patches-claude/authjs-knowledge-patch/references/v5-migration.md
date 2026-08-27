# Auth.js v5 Migration and Next.js Integration

## Pages Router API routes

Auth.js server-side session methods are not currently restored for Next.js Pages Router API routes. Fetch the session REST endpoint from those routes.

This limitation does not apply to pages rendered with `getServerSideProps`; continue to call `auth(ctx)` there.

## Next.js 16 route protection

Next.js 16 renamed the request-interception file and export from `middleware.ts` and `middleware` to `proxy.ts` and `proxy`. Export Auth.js `auth` under the new name.

```ts
// proxy.ts
export { auth as proxy } from "@/auth"
```

The proxy matcher selects the routes to which protection applies. The Auth.js `authorized` callback decides whether each matching request can continue.

```ts
// auth.ts
export const { auth, handlers } = NextAuth({
  callbacks: {
    authorized: async ({ auth }) => !!auth,
  },
})
```

Keep `middleware.ts` and the `middleware` export on older Next.js versions.
