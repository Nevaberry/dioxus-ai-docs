# Organizations, SSO, SAML, and SCIM

## Organization teams and fields

Members may belong to multiple teams (since 1.3.0). Remove `member.teamId`, add `teamMembers`, migrate membership data, and regenerate client types. Organization, member, and invitation records each accept independent `additionalFields`. `maximumMembersPerTeam` limits team size, and `listUserInvitations` retrieves all invitations for a user.

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

Server-side organization creation with session headers always uses the session user and ignores `userId`. To create for another user, omit session headers. New sessions have no active organization. Organization-scoped APIs commonly fall back to persisted `activeOrganizationId`; keep selection client-side when separate tabs need separate organizations.

## Lifecycle, invitation, and membership boundaries

`organizationHooks` includes before/after hooks for organization, member, invitation, team, and team-member operations. Before hooks may replace `data` or throw `APIError`; old `organizationCreation` hooks are deprecated.

`addMember` bypasses invitations but is server-only. With `requireEmailVerificationOnInvitation`, users must verify before accepting or rejecting. Re-sending requires `resend`; `cancelPendingInvitationsOnReInvite` cancels the old invitation and creates another.

## Dynamic roles

Dynamic roles require an `ac` definition, server and client enablement, and migration for `organizationRole`. A creator cannot grant permissions they lack. Synchronous `checkRolePermission` ignores dynamic roles; use `hasPermission`.

```ts
organization({ ac, dynamicAccessControl: { enabled: true } })
organizationClient({ dynamicAccessControl: { enabled: true } })
```

## SSO package and provider controls

SSO lives in `@better-auth/sso` and supports OIDC and SAML 2.0 (since 1.3.0). Async `providersLimit` can cap providers per user. Providers support CRUD, multiple domains, a shared OIDC redirect URI, and signed AuthnRequests.

```ts
sso({
  providersLimit: async (user) =>
    (await getUserPlan(user)).name === "pro" ? 10 : 1,
})
```

Domain verification can validate ownership before a new provider is trusted (since 1.4.0). Verified domains also permit automatic same-email account linking only for users whose email domain matches. `provisionUser` normally runs only at first SSO registration; `provisionUserOnEveryLogin` changes that. Organization-linked providers can auto-add users with `defaultRole` or `getRole`. Under `disableImplicitSignUp`, sign-in must set `requestSignUp: true`.

## OIDC discovery trust

SSO discovers metadata at `{issuer}/.well-known/openid-configuration`, but both that URL and every resolved endpoint must be in `trustedOrigins`. Registration requires authorization, token, and JWKS endpoints and supports only `client_secret_basic` or `client_secret_post`. Explicit `oidcConfig` overrides discovery.

## SAML logout and policy

Both SP- and IdP-initiated Single Logout are supported (since 1.5-guide), including signed logout requests/responses. Configure signature and digest restrictions, clock skew, OIDC audience validation, and `InResponseTo`.

Assertion-ID replay protection always uses the database verification table, so it works across instances. Timestamp conditions allow five minutes of skew when present; missing timestamps warn unless `requireTimestamps` is enabled. Deprecated algorithms warn by default and can be rejected. XML response and metadata size limits cap oversized payloads (since 1.5.0).

SP-initiated responses validate `InResponseTo` by default (since 1.6.0). IdP-initiated SSO is unaffected. Disabling `enableInResponseToValidation` gives up the default response-correlation protection.

As of 1.7.1, assertion signatures are verified against the raw assertion, `wantAssertionsSigned` determines whether they are required, and signing policy plus size limits apply to SP metadata.

## SCIM installation and routing

`@better-auth/scim` provides provisioning (since 1.4.0). Route `GET`, `POST`, `PUT`, `PATCH`, and `DELETE` to the auth handler; exporting only usual auth methods leaves provisioning incomplete. Identity providers use `/api/auth/scim/v2`.

```ts
export const { GET, POST, PUT, PATCH, DELETE } = toNextJsHandler(auth);
```

Management endpoints require authentication (since 1.6.0).

## SCIM authorization and token storage

By default any authenticated user can call `generateSCIMToken`; multi-tenant apps must authorize issuance in `beforeSCIMTokenGenerated`. A token is restricted to a required provider and optional organization, but plaintext is the default. Choose hashed, encrypted, or custom storage.

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

`defaultSCIM` sends base64 of `token:providerId[:organizationId]`. Created/listed/updated/deleted users remain confined to the provider and organization encoded by the bearer token.

SCIM also supports user-owned connections, connection list/get/delete operations, and Microsoft Entra provisioning (since 1.5-guide).

## Managed runtime connections

`managedConnections` lets `@better-auth/scim` own runtime connection and credential catalogs (since 1.7.1). Trusted server code can create tenant connections and issue, rotate, or revoke bearer credentials through server-only `auth.api` methods without defining each connection in code or providing an application verifier. A decommissioning dynamic connection can retain a terminal binding before its first authenticated request when the caller supplies a provisioning domain.

SCIM parses User string booleans case-insensitively for `active` and the `primary` sub-attribute of emails, phones, addresses, roles, and entitlements. Connection IDs no longer share the auth-provider namespace, so an SSO provider may reuse an ID.
