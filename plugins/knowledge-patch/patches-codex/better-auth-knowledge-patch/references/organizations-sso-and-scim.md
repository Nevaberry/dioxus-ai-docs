# Organizations, SSO, SAML, and SCIM

## Organization schema and teams

Organization members can belong to multiple teams. Remove `teamId` from `member` and add the required `teamMembers` join table before deploying the multi-team model. Clients can infer organization types from the server auth instance.

```ts
organizationClient({
  $inferAuth: {} as typeof auth,
})
```

Define `additionalFields` independently for organization, member, and invitation records. `maximumMembersPerTeam` limits a team, while `listUserInvitations` returns all invitations for one user.

```ts
organization({
  schema: {
    organization: { additionalFields: { /* ... */ } },
    member: { additionalFields: { /* ... */ } },
    invitation: { additionalFields: { /* ... */ } },
  },
})
```

Functional membership limits may be computed dynamically.

## Ownership and active organization

Server-side organization creation with session headers always uses the session user and silently ignores `userId`. To create for a different user, omit session headers deliberately.

```ts
await auth.api.createOrganization({
  body: { name: "Acme", slug: "acme", userId: targetUserId },
});
```

New sessions do not select an active organization. Organization APIs often fall back to persisted `activeOrganizationId`; keep selection client-local when browser tabs must use different organizations.

## Organization hooks and membership

`organizationHooks` supplies before/after hooks for organization, member, invitation, team, and team-member operations. A before hook may return replacement `data` or throw `APIError`. Older `organizationCreation` hooks are deprecated.

`addMember` bypasses invitations and is server-only. With `requireEmailVerificationOnInvitation`, recipients must verify before accepting or rejecting. Re-sending needs `resend`; `cancelPendingInvitationsOnReInvite` replaces the prior invitation.

## Dynamic roles

Dynamic organization roles require an `ac` definition, server and client enablement, and a migration for `organizationRole`. A role creator cannot grant permissions they lack. Synchronous `checkRolePermission` ignores dynamic roles; use `hasPermission` for authoritative checks.

```ts
organization({ ac, dynamicAccessControl: { enabled: true } })
organizationClient({ dynamicAccessControl: { enabled: true } })
```

## SSO package

Import SSO from `@better-auth/sso`. It configures OIDC and SAML providers, and `providersLimit` may asynchronously enforce a per-user cap.

```ts
import { sso } from "@better-auth/sso";

plugins: [sso({
  oidc: { clientId, clientSecret },
  saml: { entryPoint, issuer, certificate },
  providersLimit: async (user) =>
    (await getUserPlan(user)).name === "pro" ? 10 : 1,
})]
```

SSO supports SP- and IdP-initiated Single Logout, signed AuthnRequests, configurable signature/digest policy and clock skew, multiple domains per provider, `InResponseTo` and OIDC audience validation, provider CRUD, and a shared OIDC redirect URI.

```ts
sso({
  saml: {
    enableSingleLogout: true,
    wantLogoutRequestSigned: true,
    wantLogoutResponseSigned: true,
  },
})
```

SAML response and metadata XML size limits can cap oversized identity-provider payloads.

## OIDC discovery trust

SSO registration discovers metadata at `{issuer}/.well-known/openid-configuration`. Allowlist both the discovery URL and every resolved endpoint in `trustedOrigins`. Authorization, token, and JWKS endpoints are required; only `client_secret_basic` and `client_secret_post` are supported. Explicit `oidcConfig` values override discovered metadata.

```ts
trustedOrigins: ["https://tenant.example-idp.com"]
```

Domain verification can prove ownership before a newly registered provider becomes trusted.

```ts
plugins: [sso({ domainVerification: { enabled: true } })]
```

## Provisioning and controlled sign-up

`provisionUser` runs only at initial SSO registration unless `provisionUserOnEveryLogin` is enabled. A provider associated with `organizationId` can add a user using `defaultRole` or `getRole`. With `disableImplicitSignUp`, a sign-in request must set `requestSignUp: true` to create an account.

Verified SSO domains become trusted for automatic same-email account linking only when the user's email domain matches. SCIM also supports user-owned connections, connection list/get/delete operations, and Microsoft Entra provisioning.

## SAML validation

Assertion-ID replay protection always uses the database verification table and therefore works across instances. Timestamp conditions use five minutes of clock skew when present; missing timestamps warn unless `requireTimestamps` is enabled. Deprecated algorithms warn by default and may be rejected.

```ts
sso({
  saml: {
    requireTimestamps: true,
    algorithms: { onDeprecated: "reject" },
  },
})
```

SP-initiated responses validate `InResponseTo` by default; IdP-initiated flows are unaffected. `enableInResponseToValidation: false` is a legacy escape hatch that removes the default response-correlation protection.

```ts
sso({ saml: { enableInResponseToValidation: false } })
```

As of 1.7.1, signatures are verified against the raw assertion rather than a parsed response. `wantAssertionsSigned` controls whether assertion signatures are mandatory, and SP metadata enforces signing policy and size limits.

## SCIM installation and routes

Install the provisioning plugin from `@better-auth/scim`.

```ts
import { scim } from "@better-auth/scim";

export const auth = betterAuth({ plugins: [scim()] });
```

All `GET`, `POST`, `PUT`, `PATCH`, and `DELETE` methods must reach the auth handler. Exporting only normal auth methods leaves provisioning incomplete. Identity providers use `/api/auth/scim/v2` as the base.

```ts
export const { GET, POST, PUT, PATCH, DELETE } = toNextJsHandler(auth);
```

SCIM management endpoints require authentication.

## SCIM token authorization and storage

By default any authenticated user can call `generateSCIMToken`; multi-tenant applications must authorize issuance in `beforeSCIMTokenGenerated`. Tokens are scoped to a required provider and optional organization but are plain by default, so choose hashed, encrypted, or custom storage.

```ts
scim({
  storeSCIMToken: "hashed",
  beforeSCIMTokenGenerated: async ({ member }) => {
    if (member?.role !== "admin") {
      throw new APIError("FORBIDDEN", {
        message: "Admin role required",
      });
    }
  },
})
```

A `defaultSCIM` token is base64 of `token:providerId[:organizationId]`. Created, listed, updated, and deleted users remain within the provider and organization encoded by the bearer token.

## Managed SCIM connections

The SCIM package can own a runtime connection and credential catalog through `managedConnections`. Trusted server code can create tenant connections and issue, rotate, or revoke bearer credentials with server-only `auth.api` methods, avoiding static code entries and an application verifier. A dynamic connection being decommissioned may retain a terminal binding before its first authenticated request when given a provisioning domain.

SCIM User string Boolean inputs are parsed case-insensitively for `active` and the `primary` subfield of emails, phone numbers, addresses, roles, and entitlements. SCIM connection IDs use a separate namespace, so an SSO provider may reuse the same ID.
