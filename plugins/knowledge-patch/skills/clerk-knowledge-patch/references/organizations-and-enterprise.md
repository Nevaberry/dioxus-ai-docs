# Organizations and enterprise

## Tenant data boundary

Organizations provide a shared user pool: one user may belong to multiple Organizations and hold a different Role in each. Store the Organization ID with tenant-owned records and include it in every scoped query.

## Active Organization is tab-local

Each browser tab remembers its own Active Organization, but the singleton session cookie reflects the Organization for the currently active browser tab. For tenant-scoped background requests, get a token in the tab and send it as a bearer token rather than trusting the cookie.

```ts
const token = await getToken()
await fetch('/api/tenant-data', {
  headers: { Authorization: `Bearer ${token}` },
})
```

## Membership-required default

Organizations stay disabled until explicitly enabled. Applications created since August 22, 2025 default to **Membership required** when Organizations are enabled. New and existing users must then complete the Organization session task before entering the application.

Older applications retain optional membership. Choosing **Membership optional** enables Personal Accounts and starts users in an individual workspace.

## Slug routing and activation checks

Organization slugs default to disabled for applications created after October 7, 2025. When enabled, components can route with `/orgs/:slug`, and Next.js middleware can synchronize matching paths.

```ts
export default clerkMiddleware((_auth, _req) => {}, {
  organizationSyncOptions: {
    organizationPatterns: [
      '/orgs/:slug',
      '/orgs/:slug/(.*)',
    ],
  },
})
```

An unknown slug or an Organization the user has not joined leaves the previous Organization active. Every tenant page must compare the route slug with authenticated `orgSlug` before rendering or querying scoped data.

## First-Organization naming

Automatic first-Organization creation and default naming are separate settings, both disabled by default.

Naming tries, in order:

1. The user's email domain.
2. A member-name template such as `{{user.first_name}}'s organization`.
3. The configured fallback.

Without auto-creation, the same rules only prefill the manual creation form.

## Membership and deletion limits

A user may join any number of Organizations. Each Organization defaults to five members. `maxAllowedMemberships: 0` means unlimited membership.

Disabling **Allow new members to delete organizations** affects only Organizations created afterward; existing Organizations keep their current deletion behavior.

## Creator and Default Role invariants

The Creator Role defaults to `org:admin` and must retain:

- `org:sys_memberships:manage`
- `org:sys_memberships:read`
- `org:sys_profile:delete`

The member Default Role defaults to `org:member` and is used for invitations and Verified Domain enrollment.

A Creator or Default Role cannot be deleted until another Role replaces it. Any Role assigned to a member must be reassigned before deletion.

## System and Custom Permissions

System Permissions such as `org:sys_memberships:manage` control FAPI operations and prebuilt Organization components, but are not emitted in session claims. Server-side `has({ permission })` must use an equivalent Custom Permission.

When Billing is enabled, a Custom Permission succeeds only while the active Organization Plan contains its corresponding Feature.

## Role Sets

An Organization's Role Set determines which application Roles its members can receive.

- Changing a Role Set immediately affects every Organization assigned to it.
- Changing the Default Role Set affects only newly created Organizations.
- Switching or deleting a set requires mapping affected members to Roles available in the replacement.
- Removing an in-use Role also requires remapping.

Organization create and update operations accept `role_set_key`; embedded Organization and membership resources also expose it.

## Role Set migration guard

`Organization.getRoles()` returns `has_role_set_migration` with the paginated Roles. While it is `true`, membership Role updates are blocked. Custom Role-management UI must wait for or complete the migration.

## Invitation requirements and redirects

Organization invitations require Email to be enabled, even if email sign-in is disabled.

Frontend `organization.inviteMember()` always routes the invitee through Account Portal and cannot select a redirect. Only a server-created invitation can set `redirect_url`; that destination must host sign-in or a custom acceptance flow.

## Invitation metadata and rate limits

When an invited user signs up through the invitation link, `OrganizationInvitation.publicMetadata` is copied to `OrganizationMembership.publicMetadata`.

Rate limits per application per hour:

- Single invitation creation: 250 requests.
- Bulk invitation creation: 50 requests.

On HTTP 429, wait for the `Retry-After` duration before retrying.

## Verified Domains

Verified Domains are enabled application-wide, not per Organization. Common and disposable domains are rejected. A domain cannot also back Enterprise SSO for the same Organization.

Each domain selects exactly one enrollment mode:

- `automatic_invitation`: a matching user can accept immediately.
- `automatic_suggestion`: creates an admin-approved membership request, currently reviewable only through `<OrganizationSwitcher />`.

## Enterprise SSO membership lifecycle

Signing in through an Organization's enterprise connection JIT-provisions the user into that Organization with its Default Role.

Removing the member is temporary while the IdP identity and connection remain valid. Moving the connection to another Organization leaves existing memberships in place and adds users to the new Organization on their next sign-in.

## Unified enterprise connections API

The Backend API manages both SAML and OIDC connections through `/v1/enterprise_connections`. Migrate from legacy `/saml_connections`, which may be phased out.

```text
POST   /v1/enterprise_connections
GET    /v1/enterprise_connections
GET    /v1/enterprise_connections/{enterpriseConnectionID}
PATCH  /v1/enterprise_connections/{enterpriseConnectionID}
DELETE /v1/enterprise_connections/{enterpriseConnectionID}
```

Creation accepts `provider`, `domains`, `name`, and `organization_id`. Listing accepts an optional `organization_id` filter and pagination.

## Collection hooks are opt-in

`useOrganization()` does not populate `memberships`, `invitations`, `membershipRequests`, or `domains` unless each collection is requested.

`useOrganizationList()` similarly leaves `userMemberships`, `userInvitations`, and `userSuggestions` unpopulated unless requested.

Passing `true` fetches page 1 with 10 records. An options object can set `pageSize` or accumulate pages with `infinite`.

```ts
const { memberships } = useOrganization({
  memberships: { pageSize: 20, infinite: true },
})

const { userInvitations } = useOrganizationList({
  userInvitations: true,
})
```

## Membership ban state

Organization membership `public_user_data` includes `banned`, preserving the user's instance-level ban status in membership reads.

## Activity reporting

An Organization's Dashboard profile includes a year-selectable daily activity report. Each day shows the percentage of members who were active. Activity history begins in January 2026.
