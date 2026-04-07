# v5 Migration & Breaking Changes

## Next.js 16: proxy.ts replaces middleware.ts

As of Next.js 16, `middleware.ts` is renamed to `proxy.ts`. Auth.js middleware setup changes accordingly:

```ts filename="proxy.ts"
// Simple: just re-export auth as proxy
export { auth as proxy } from "@/auth"
```

```ts filename="proxy.ts"
// Advanced: wrap with custom logic
import { auth } from "@/auth"

export const proxy = auth((req) => {
  // req.auth contains the session
})

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
}
```

For older Next.js versions (< 16), keep using `middleware.ts` with `export { auth as middleware }`.

## idToken: false behavioral change

In v5, setting `idToken: false` on a provider no longer disables ID token processing entirely. Instead, it signals Auth.js to also visit the `userinfo_endpoint` for final user data. Previously, `idToken: false` opted out of checking the `id_token` validity at all.
