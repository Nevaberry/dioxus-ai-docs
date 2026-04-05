# Organization Plugin

## Comprehensive Hooks System (`organizationHooks`)

New `organizationHooks` config replaces legacy `organizationCreation` hooks:

```ts
organization({
  organizationHooks: {
    beforeCreateOrganization: async ({ organization, user }) => ({ data: { ...organization, metadata: { custom: true } } }),
    afterCreateOrganization: async ({ organization, member, user }) => { /* setup */ },
    beforeAddMember: async ({ member, user, organization }) => ({ data: { ...member, role: "custom-role" } }),
    afterAddMember: async ({ member, user, organization }) => { /* notify */ },
    beforeUpdateMemberRole: async ({ member, newRole, user, organization }) => { /* validate */ },
    afterUpdateMemberRole: async ({ member, previousRole, user, organization }) => { /* log */ },
    beforeCreateInvitation: async ({ invitation, inviter, organization }) => ({ data: { ...invitation, expiresAt: customDate } }),
    afterAcceptInvitation: async ({ invitation, member, user, organization }) => { /* setup */ },
    // Also: beforeRemoveMember, beforeRejectInvitation, beforeCancelInvitation,
    //        beforeCreateTeam, afterCreateTeam, beforeAddTeamMember, etc.
  },
})
```

Throwing an error (e.g., `APIError`) in a `before` hook prevents the operation.

## Dynamic Access Control

Runtime role creation per organization, stored in `organizationRole` DB table:

```ts
organization({
  ac, // must define an ac instance
  dynamicAccessControl: {
    enabled: true,
    maximumRolesPerOrganization: 10, // or async (orgId) => number
  },
})
```

APIs: `authClient.organization.createRole({ role: "editor", permission: { project: ["create", "update"] } })`, `deleteRole`, `listOrgRoles`, `getOrgRole`, `updateOrgRole`. Only users with `ac: ["create"]` permission can create roles.

Note: `checkRolePermission` (client sync) does NOT include dynamic roles — use `hasPermission` API instead.

## Teams

Sub-groups within organizations:

```ts
organization({ teams: { enabled: true, maximumTeams: 10 } })
organizationClient({ teams: { enabled: true } })
```

APIs: `createTeam`, `listTeams`, `updateTeam`, `removeTeam`, `setActiveTeam`, `listUserTeams`, `listTeamMembers`, `addTeamMember`, `removeTeamMember`. Team hooks available via `organizationHooks`.

## Additional Fields & Type Inference

```ts
// Server
organization({
  schema: { organizationRole: { additionalFields: { color: { type: "string", defaultValue: "#fff" } } } },
})
// Client — automatic inference from server type
organizationClient({ schema: inferOrgAdditionalFields<typeof auth>() })
```

## Default AC Import Path

For org-specific access control, import from `better-auth/plugins/organization/access` (not `better-auth/plugins/admin/access`):

```ts
import { defaultStatements, adminAc } from "better-auth/plugins/organization/access";
```
