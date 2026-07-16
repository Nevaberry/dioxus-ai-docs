# Organizations, SSO, SAML, and SCIM

## Multi-team organization schema

Organization members can belong to multiple teams. Remove `teamId` from the `member` table and add the required `teamMembers` join table. Clients can infer resulting organization types from the server instance.

```ts
organizationClient({
  $inferAuth: {} as typeof auth,
})
```

## Additional fields and limits

The organization plugin defines `additionalFields` independently for organization, member, and invitation records. `maximumMembersPerTeam` enforces team size; `listUserInvitations` retrieves all invitations belonging to a user. Membership-limit options may be functions.

```ts
organization({
  schema: {
    organization: { additionalFields: { /* ... */ } },
    member: { additionalFields: { /* ... */ } },
    invitation: { additionalFields: { /* ... */ } },
  },
})
```

## Ownership and active context

Server-side organization creation with session headers always uses the session user and silently ignores `userId`. To create for another user, omit session headers deliberately.

```ts
await auth.api.createOrganization({
  body: { name: "Acme", slug: "acme", userId: targetUserId },
}); // no session headers
```

New sessions have no active organization. Organization-scoped APIs often fall back to persisted `activeOrganizationId`; keep selection in client state when separate browser tabs need different active organizations.

## Lifecycle hooks

`organizationHooks` includes before/after hooks for organization, member, invitation, team, and team-member operations. A before hook may return replacement `data` or throw `APIError` to abort. Older `organizationCreation` hooks are deprecated.

## Invitations and direct membership

`addMember` bypasses invitations but is server-only. With `requireEmailVerificationOnInvitation`, the recipient must verify before accepting or rejecting.

Re-sending an existing invitation requires `resend`. `cancelPendingInvitationsOnReInvite` replaces the pending invitation with a new one.

## Runtime organization roles

Dynamic roles require an `ac` definition, enablement on both server and client, and a migration for `organizationRole`. A creator cannot grant permissions they do not possess. Synchronous `checkRolePermission` ignores dynamic roles; use `hasPermission` for an authoritative result.

```ts
organization({ ac, dynamicAccessControl: { enabled: true } })
organizationClient({ dynamicAccessControl: { enabled: true } })
```

## SSO package

SSO lives in `@better-auth/sso` and supports OIDC and SAML 2.0. An asynchronous `providersLimit` can cap registered providers per user.

```ts
import { sso } from "@better-auth/sso";

plugins: [
  sso({
    oidc: { clientId, clientSecret },
    saml: { entryPoint, issuer, certificate },
    providersLimit: async (user) =>
      (await getUserPlan(user)).name === "pro" ? 10 : 1,
  }),
]
```

Domain verification can confirm ownership before a newly registered provider is trusted:

```ts
plugins: [sso({ domainVerification: { enabled: true } })]
```

## OIDC SSO discovery trust

Registration hydrates OIDC endpoints from `{issuer}/.well-known/openid-configuration`, but both the discovery URL and every resolved endpoint must be in `trustedOrigins`.

Registration requires authorization, token, and JWKS endpoints and supports only `client_secret_basic` or `client_secret_post`. Explicit `oidcConfig` overrides discovery metadata.

```ts
trustedOrigins: ["https://tenant.example-idp.com"]
```

## Provisioning and controlled signup

`provisionUser` runs only on first registration unless `provisionUserOnEveryLogin` is enabled. A provider linked with `organizationId` can add the user automatically using `defaultRole` or `getRole`.

With `disableImplicitSignUp`, the sign-in request must set `requestSignUp: true` to create an account. Verified SSO domains become trusted for automatic same-email linking only when the user's domain matches the verified provider domain.

## SAML logout and signing

SAML supports SP- and IdP-initiated Single Logout, signed AuthnRequests, signature/digest restrictions, configurable clock skew, multiple domains per provider, `InResponseTo` validation, OIDC audience validation, provider CRUD, and a shared OIDC redirect URI.

```ts
sso({
  saml: {
    enableSingleLogout: true,
    wantLogoutRequestSigned: true,
    wantLogoutResponseSigned: true,
  },
})
```

Configurable XML limits cap SAML response and metadata payload sizes.

## SAML assertion policy

Assertion-ID replay protection is always enabled and uses the database verification table, so it works across instances.

Timestamp conditions are checked with five minutes of clock skew when present. Missing timestamps warn but are accepted unless `requireTimestamps` is enabled. Deprecated algorithms warn by default and may be rejected.

```ts
sso({
  saml: {
    requireTimestamps: true,
    algorithms: { onDeprecated: "reject" },
  },
})
```

SP-initiated SAML validates `InResponseTo` by default; IdP-initiated SSO is unaffected. A legacy integration can explicitly set `enableInResponseToValidation: false`, sacrificing default replay protection.

```ts
sso({ saml: { enableInResponseToValidation: false } })
```

## SCIM package and routes

`@better-auth/scim` adds standards-based identity provisioning.

```ts
import { scim } from "@better-auth/scim";

export const auth = betterAuth({ plugins: [scim()] });
```

Framework routing must send `GET`, `POST`, `PUT`, `PATCH`, and `DELETE` to the auth handler. Providers use `/api/auth/scim/v2` as the base URL.

```ts
export const { GET, POST, PUT, PATCH, DELETE } = toNextJsHandler(auth);
```

SCIM supports user-owned connections, connection list/get/delete operations, and Microsoft Entra provisioning. Management endpoints require authentication.

## SCIM token authorization and storage

By default, any authenticated user can call `generateSCIMToken`. Multi-tenant applications must authorize issuance in `beforeSCIMTokenGenerated`.

Tokens require a provider and may be scoped to an organization. They are stored in plain text by default; explicitly select `hashed`, `encrypted`, or custom storage.

```ts
scim({
  storeSCIMToken: "hashed",
  beforeSCIMTokenGenerated: async ({ member }) => {
    if (member?.role !== "admin") {
      throw new APIError("FORBIDDEN", { message: "Admin role required" });
    }
  },
})
```

A configured `defaultSCIM` token is sent as base64 of `token:providerId[:organizationId]`. SCIM-created, listed, updated, and deleted users remain constrained to the provider and organization encoded in the bearer token.

## Organization-owned API keys

An organization-owned key requires organization membership plus the relevant API-key `create`, `read`, `update`, or `delete` permission. Owners receive all four actions. Other roles need explicit grants. `verifyApiKey({ permissions })` succeeds only when every requested permission is present.
