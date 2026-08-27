# Organizations and enterprise

## Read Organization activity reports

An Organization's Dashboard profile includes a year-selectable daily activity
report. Each day shows the percentage of members who were active. History
begins in January 2026.

## Migrate to the unified enterprise-connection API

Manage SAML and OIDC connections through `/v1/enterprise_connections`. Move
callers away from legacy `/saml_connections`, which may be phased out.
Creation accepts `provider`, `domains`, `name`, and `organization_id`. Listing
supports an optional `organization_id` filter plus pagination.

```text
POST   /v1/enterprise_connections
GET    /v1/enterprise_connections
GET    /v1/enterprise_connections/{enterpriseConnectionID}
PATCH  /v1/enterprise_connections/{enterpriseConnectionID}
DELETE /v1/enterprise_connections/{enterpriseConnectionID}
```

## Never trust the shared cookie for tab-local tenancy

Each tab remembers its own Active Organization, but the singleton session
cookie reflects the Organization active in the currently focused tab. For
tenant-scoped background requests, call `getToken()` in the originating tab and
send the result as a bearer token.

```ts
const token = await getToken()
await fetch('/api/tenant-data', {
  headers: { Authorization: `Bearer ${token}` },
})
```

## Account for the membership-required default

Organizations are disabled until explicitly enabled. Applications created on
or after August 22, 2025 default to **Membership required** when Organizations
are enabled; new and existing users must complete the Organization session task
before entering the application.

Older applications retain optional membership. Explicitly choosing
**Membership optional** enables Personal Accounts and starts users in their
individual workspace.

## Validate slug activation before tenant reads

Organization slugs default to disabled for applications created after October
7, 2025. When enabled, components can route through `/orgs/:slug`, and Next.js
middleware can synchronize those routes with `organizationSyncOptions`.

```ts
export default clerkMiddleware((_auth, _req) => {}, {
  organizationSyncOptions: {
    organizationPatterns: ['/orgs/:slug', '/orgs/:slug/(.*)'],
  },
})
```

An unknown slug or an Organization the user has not joined leaves the previous
Organization active. Compare the route slug to authenticated `orgSlug` before
rendering or querying tenant data.

## Configure automatic first-Organization naming

Automatic creation of a user's first Organization and default naming rules are
separate settings, both off by default. Naming tries the email domain, then a
member template such as `{{user.first_name}}'s organization`, then the configured
fallback. Without automatic creation, the same rules only prefill the manual
creation form.

## Apply membership and deletion limits

A user may join any number of Organizations. Each Organization defaults to five
members; `maxAllowedMemberships: 0` means unlimited membership.

Turning off **Allow new members to delete organizations** changes only
Organizations created afterward. Existing Organizations keep their previous
deletion behavior.

## Preserve Creator and Default Role invariants

The Creator Role defaults to `org:admin` and must retain
`org:sys_memberships:manage`, `org:sys_memberships:read`, and
`org:sys_profile:delete`. The member Default Role defaults to `org:member` and
is used by invitations and Verified Domain enrollment.

A Creator or Default Role cannot be deleted until replaced. Any Role currently
assigned to a member must be reassigned before deletion.

## Choose the correct invitation surface

Organization invitations require Email to be enabled, even if email sign-in is
disabled. Frontend `organization.inviteMember()` always routes through Account
Portal and cannot select a redirect. A server-created invitation can supply
`redirect_url`; its target must host the sign-in or custom acceptance flow.

After invite-link sign-up, `OrganizationInvitation.publicMetadata` is copied to
`OrganizationMembership.publicMetadata`.

Single-create invitation endpoints allow 250 requests per application per hour;
bulk-create allows 50. After HTTP 429, wait for `Retry-After` before retrying.

## Select one Verified Domain enrollment mode

Verified Domains are enabled application-wide, not per Organization. Common or
disposable domains are rejected, and the same domain cannot back Enterprise SSO
for that Organization.

Each domain chooses exactly one mode:

- `automatic_invitation` lets a matching user accept immediately.
- `automatic_suggestion` creates an administrator-approved membership request,
  currently reviewable only through `<OrganizationSwitcher />`.

## Understand Enterprise SSO membership lifecycle

Signing in through an Organization's Enterprise Connection performs JIT
provisioning into that Organization with its Default Role. Removing the member
is temporary while the IdP and connection remain valid. Moving a connection
does not remove old memberships, but adds those users to the new Organization
on their next sign-in.

## Replace System Permissions in server authorization

System Permissions such as `org:sys_memberships:manage` control FAPI and
prebuilt Organization components but are absent from session claims. A
server-side `has({ permission })` check must use an equivalent Custom Permission.

## Propagate and remap Role Sets

An Organization's Role Set controls which application-level Roles its members
may receive. Editing a set immediately affects all assigned Organizations;
changing the Default Role Set affects only Organizations created afterward.

Switching or deleting a set, or removing an in-use Role, requires mapping
affected members to Roles present in the replacement set.

`Organization.getRoles()` returns `has_role_set_migration`. While it is true,
membership Role updates are blocked. Custom Role-management UI must wait for or
complete the migration.

## Opt into Organization hook collections

`useOrganization()` does not populate `memberships`, `invitations`,
`membershipRequests`, or `domains` unless requested. `useOrganizationList()`
does the same for `userMemberships`, `userInvitations`, and `userSuggestions`.
Passing `true` fetches page 1 with 10 records; an options object can set page
size or accumulate results with `infinite`.

```ts
const { memberships } = useOrganization({
  memberships: { pageSize: 20, infinite: true },
})
const { userInvitations } = useOrganizationList({ userInvitations: true })
```

## Synchronize Google Workspace directories

A Google SAML connection can import users, groups, and memberships directly
from Workspace through a service account instead of waiting for sign-in.
Configure the connection's **Directory sync** tab with a domain-wide-delegated
service-account key and an administrator to impersonate.

Synchronized groups can map to Clerk Roles. Attribute mappings support standard
paths such as `organizations.title`, custom-schema paths such as
`customSchemas.EmployeeInfo.costCenter`, and multi-valued array paths. Disabling
sync retains stored credentials for later re-enablement.

## Enable self-service OIDC for Organizations

When self-service enterprise SSO is enabled for an Organization, its customers
can configure an OIDC connection from the **Security** tab of
`<OrganizationProfile />`. The administrator needs
`org:sys_entconns:manage`.

The flow verifies each domain through a DNS TXT record. It accepts either OIDC
discovery or explicit authorization, token, and user-info endpoints plus client
credentials. Clerk reads `sub` and `email` from the ID token and, when present,
`given_name` and `family_name`. A test must succeed before activation, and the
resulting connection is scoped to that Organization.
