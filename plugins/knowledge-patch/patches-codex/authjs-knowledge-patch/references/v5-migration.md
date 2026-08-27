# Auth.js v5 Migration and Next.js Integration

## Pages Router API session access

Server-side session methods have not been restored for Next.js Pages Router
API routes. Fetch the session REST endpoint from those routes instead. This
limitation does not affect pages rendered through `getServerSideProps`, which
can call `auth(ctx)`.

## Next.js 16 route protection

Next.js 16 renamed `middleware.ts` and its `middleware` export to `proxy.ts`
and `proxy`. Export Auth.js `auth` under the new name. Older Next.js versions
must retain the middleware filename and export.

The proxy matcher determines which routes are covered, while Auth.js's
`authorized` callback determines whether a selected request may proceed.

```ts
// proxy.ts
export { auth as proxy } from "@/auth"

// auth.ts
export const { auth, handlers } = NextAuth({
  callbacks: {
    authorized: async ({ auth }) => !!auth,
  },
})
```
