# Providers and Features

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
