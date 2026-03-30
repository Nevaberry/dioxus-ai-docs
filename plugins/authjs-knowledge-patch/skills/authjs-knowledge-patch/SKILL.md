---
name: authjs-knowledge-patch
description: Auth.js v5 changes since training cutoff — Next.js 16 proxy.ts migration, idToken behavioral change, WebAuthn/Passkeys provider setup. Load before working with Auth.js v5.
version: "5.0.0-beta"
license: MIT
metadata:
  author: Nevaberry
---

# Auth.js Knowledge Patch

Claude Opus 4.6 knows Auth.js (NextAuth.js) through v4 and early v5 betas. This skill covers v5 changes that postdate training.

## Index

| Topic | Reference | Key features |
|---|---|---|
| v5 migration | [references/v5-migration.md](references/v5-migration.md) | Next.js 16 `proxy.ts`, `idToken: false` behavioral change |
| WebAuthn / Passkeys | [references/webauthn-passkeys.md](references/webauthn-passkeys.md) | Passkey provider, SimpleWebAuthn setup, Authenticator table, custom signin |

---

## Quick Reference

### Next.js 16: proxy.ts replaces middleware.ts

Next.js 16 renames `middleware.ts` to `proxy.ts`. Auth.js setup changes accordingly:

```ts filename="proxy.ts"
// Simple
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

For Next.js < 16, keep using `middleware.ts` with `export { auth as middleware }`.

---

### idToken: false behavioral change

In v5, `idToken: false` on a provider no longer disables ID token processing entirely. It now signals Auth.js to **also** visit the `userinfo_endpoint` for final user data. Previously it opted out of `id_token` validity checking altogether.

---

### WebAuthn / Passkeys (experimental)

Requires `next-auth@5.0.0-beta.8+`, `@auth/prisma-adapter@1.3.0+`, Node 20+.

**Peer dependencies:**

```bash
npm install @simplewebauthn/server@9.0.3 @simplewebauthn/browser@9.0.1
```

`@simplewebauthn/browser` is only needed for custom signin pages.

**Auth config:**

```ts filename="auth.ts"
import Passkey from "next-auth/providers/passkey"
import { PrismaAdapter } from "@auth/prisma-adapter"

export default {
  adapter: PrismaAdapter(prisma),
  providers: [Passkey],
  experimental: { enableWebAuthn: true },
}
```

**Custom signin page** — `signIn("passkey")` to login, `signIn("passkey", { action: "register" })` to register:

```tsx filename="app/login/page.tsx"
"use client"
import { signIn } from "next-auth/webauthn"
import { useSession } from "next-auth/react"

export default function Login() {
  const { status } = useSession()
  return (
    <div>
      {status === "authenticated" ? (
        <button onClick={() => signIn("passkey", { action: "register" })}>
          Register new Passkey
        </button>
      ) : status === "unauthenticated" ? (
        <button onClick={() => signIn("passkey")}>Sign in with Passkey</button>
      ) : null}
    </div>
  )
}
```

See [references/webauthn-passkeys.md](references/webauthn-passkeys.md) for the required `Authenticator` table schema.

---

## Reference Files

| File | Contents |
|---|---|
| [v5-migration.md](references/v5-migration.md) | Next.js 16 proxy.ts setup, idToken: false behavioral change |
| [webauthn-passkeys.md](references/webauthn-passkeys.md) | Passkey provider setup, SimpleWebAuthn deps, Authenticator table DDL, custom signin page |
