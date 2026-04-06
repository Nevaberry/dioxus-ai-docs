# WebAuthn / Passkeys Provider

Auth.js v5 adds experimental WebAuthn (Passkeys) support. Requires `next-auth@5.0.0-beta.8+`, `@auth/prisma-adapter@1.3.0+`, and Node 20+.

## Peer dependencies

```bash
npm install @simplewebauthn/server@9.0.3 @simplewebauthn/browser@9.0.1
```

`@simplewebauthn/browser` is only needed for custom signin pages (not the built-in Auth.js pages).

## Database requirement

An `Authenticator` table must be added:

```sql
CREATE TABLE "Authenticator" (
    "credentialID" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "providerAccountId" TEXT NOT NULL,
    "credentialPublicKey" TEXT NOT NULL,
    "counter" INTEGER NOT NULL,
    "credentialDeviceType" TEXT NOT NULL,
    "credentialBackedUp" BOOLEAN NOT NULL,
    "transports" TEXT,
    PRIMARY KEY ("userId", "credentialID"),
    CONSTRAINT "Authenticator_userId_fkey" FOREIGN KEY ("userId")
      REFERENCES "User" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);
CREATE UNIQUE INDEX "Authenticator_credentialID_key" ON "Authenticator"("credentialID");
```

## Auth config

Use `Passkey` provider with `experimental` flag:

```ts filename="auth.ts"
import Passkey from "next-auth/providers/passkey"
import { PrismaAdapter } from "@auth/prisma-adapter"

export default {
  adapter: PrismaAdapter(prisma),
  providers: [Passkey],
  experimental: { enableWebAuthn: true },
}
```

## Custom signin page

Use `signIn("passkey")` to login, `signIn("passkey", { action: "register" })` to register:

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
